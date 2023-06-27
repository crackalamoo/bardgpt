import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Flatten, Input

from tokens import VOCAB_SIZE, NGRAM_N, pretty_tokens

class LinearModel(keras.Model):
    def __init__(self):
        super(LinearModel, self).__init__()
        self.vocab = np.load('lemmas/lemmas.npy')
        self.seq = keras.Sequential([
            Input(shape=(NGRAM_N-1, VOCAB_SIZE)),
            Flatten(),
            Dense(1024, activation='relu'),
            Dense(512, activation='relu'), # perplexity without: 128
            Dense(VOCAB_SIZE, activation='softmax')
        ])
    
    def call(self, input):
        x = self.seq(input)
        return x
    
    def genTokens(self, tokens, temperature=0.75):
        res = []
        temperature = 1e-8 if temperature == 0 else temperature
        for i in range(tokens):
            context = res[-(NGRAM_N-1):]
            while len(context) < NGRAM_N-1:
                context.insert(0, -1)
            context = tf.one_hot([context], VOCAB_SIZE)
            pred = self.call(context)[0]
            pred = np.power(pred, temperature)
            pred /= np.sum(pred)
            pred = np.random.choice(np.arange(VOCAB_SIZE), p=pred)
            res.append(pred)
        res = list(map(lambda token: self.vocab[token], res))
        return res

def perplexity(y_true, y_pred):
    return tf.math.exp(tf.math.reduce_mean(tf.keras.losses.categorical_crossentropy(y_true, y_pred)))

if __name__ == '__main__':
    loaded = np.load('data/ngram_train.npz')
    train_x = tf.one_hot(loaded['x'], VOCAB_SIZE)
    train_y = tf.one_hot(loaded['y'], VOCAB_SIZE)
    print(train_x[:2])
    print(train_y[:2])
    print(train_x.shape)
    print(train_y.shape)
    model = LinearModel()
    print(model(train_x[:1]))
    print(model.summary())
    print(pretty_tokens(model.genTokens(50)))
    model.compile(optimizer=keras.optimizers.Adam(),
                  loss=keras.losses.CategoricalCrossentropy(),
                  metrics=[perplexity])
    model.evaluate(train_x, train_y, batch_size=128)
    model.fit(train_x, train_y, batch_size=128, validation_split=0.2, epochs=2)
    print(pretty_tokens(model.genTokens(50)))