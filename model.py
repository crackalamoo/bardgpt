import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Flatten, Dropout, Embedding,\
    Add, MultiHeadAttention, LayerNormalization, Input

from tokens import VOCAB_SIZE, NGRAM_N, TRANSFORMER_N, MODEL_TYPE, TITLE, pretty_tokens
N = NGRAM_N if MODEL_TYPE == 'n' else TRANSFORMER_N
EMBED_DIM = 256
TRANSFORMER_LAYERS = 2
TRANSFORMER_HEADS = 4
TRANSFORMER_DFF = 1024
VOCAB = list(np.load('lemmas/lemmas.npy'))

def sampleVocab(dist, temperature):
    temperature = 1e-8 if temperature == 0 else temperature
    dist = np.power(dist, temperature)
    dist /= np.sum(dist)
    sample = np.random.choice(np.arange(VOCAB_SIZE), p=dist)
    return sample

def genTokens(model, tokens, temperature=0.75):
    res = [VOCAB.index(TITLE.lower()[1:-1])]
    for i in range(tokens):
        context = res[-(N-1):] if MODEL_TYPE == 'n' else res[-N:]
        pred = model.generate(context, temperature)
        res.append(pred)
    res = list(map(lambda token: model.vocab[token], res))
    return res

class LinearModel(keras.Model):
    def __init__(self):
        super(LinearModel, self).__init__()
        self.vocab = VOCAB
        self.seq = keras.Sequential([
            Input(shape=(NGRAM_N-1, VOCAB_SIZE)),
            Flatten(),
            Dense(1024, activation='relu'),
            Dense(1024, activation='relu'),
            Dense(2048, activation='relu'),
            Dropout(0.2),
            Dense(VOCAB_SIZE, activation='softmax')
        ])

    def call(self, input):
        x = self.seq(input)
        return x

    def generate(self, context, temperature=0.75):
        while len(context) > NGRAM_N-1:
            context.pop(0)
        while len(context) < NGRAM_N-1:
            context.append(-1)
        context = tf.one_hot([context], VOCAB_SIZE)
        pred = self.call(context)[0]
        pred = sampleVocab(pred, temperature)
        return pred


def positional_encoding(length, depth):
    depth = depth / 2
    positions = np.arange(length)[:, np.newaxis]
    depths = np.arange(depth)[np.newaxis, :]/depth
    angle_rates = 1 / (10000**depths)
    angle_rads = positions * angle_rates
    pos_encoding = np.concatenate(
        [np.sin(angle_rads), np.cos(angle_rads)],
        axis=-1)
    return tf.cast(pos_encoding, dtype=tf.float32)

class InputEmbedding(keras.layers.Layer):
    def __init__(self):
        super().__init__()
        self.embed = Embedding(input_dim=VOCAB_SIZE+1, output_dim=EMBED_DIM)
        self.pos = positional_encoding(length=TRANSFORMER_N, depth=EMBED_DIM)
        self.add = Add()
        self.dropout = Dropout(0.1)
    def call(self, input):
        length = tf.shape(input)[1]
        x = self.embed(input)
        x *= tf.math.sqrt(tf.cast(EMBED_DIM, tf.float32))
        x = self.add([x, self.pos[tf.newaxis, :length, :]])
        x = self.dropout(x)
        return x

class AttentionBlock(keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__()
        self.mha = MultiHeadAttention(**kwargs)
        self.dropout = Dropout(0.1)
        self.norm = LayerNormalization()
        self.add = Add()
    def call(self, input):
        x = self.mha(query=input, value=input, key=input, use_causal_mask=True)
        x = self.dropout(x)
        x = self.add([input, x])
        x = self.norm(x)
        return x

class FeedForward(keras.layers.Layer):
    def __init__(self, dff):
        super().__init__()
        self.seq = keras.Sequential([
            Dense(dff, activation='relu'),
            Dense(EMBED_DIM),
            Dropout(0.1)
        ])
        self.add = Add()
        self.norm = LayerNormalization()
    def call(self, input):
        x = self.add([input, self.seq(input)])
        x = self.norm(x)
        return x

class Decoder(keras.layers.Layer):
    def __init__(self, *, num_layers, num_heads, dff):
        super(Decoder, self).__init__()
        attention = []
        for i in range(num_layers):
            attention.append(AttentionBlock(num_heads=num_heads, key_dim=EMBED_DIM, dropout=0.1))
        self.attn_seq = keras.Sequential(attention)
        self.ffn = FeedForward(dff)
    def call(self, input):
        x = self.attn_seq(input)
        x = self.ffn(x)
        return x

class Transformer(keras.Model):
    def __init__(self, *, num_layers=TRANSFORMER_LAYERS, num_heads=TRANSFORMER_HEADS, dff=TRANSFORMER_DFF):
        super(Transformer, self).__init__()
        self.vocab = VOCAB
        self.embed = InputEmbedding()
        self.decoder = Decoder(num_layers=num_layers, num_heads=num_heads, dff=dff)
        self.out = Dense(VOCAB_SIZE, activation='softmax')

    def call(self, input):
        x = self.embed(input)
        x = self.decoder(x)
        x = self.out(x)
        try:
            del x._keras_mask
        except AttributeError:
            pass

        return x

    def generate(self, context, temperature=0.75):
        lastToken = len(context)-1
        while len(context) > TRANSFORMER_N:
            context.pop(0)
        while len(context) < TRANSFORMER_N:
            context.append(0)
        context = np.asarray([context])+1
        pred = self.call(context)[0]
        pred = pred[lastToken]
        pred = sampleVocab(pred, temperature)
        return pred



class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
  def __init__(self, d_model, warmup_steps=400):
    super().__init__()

    self.d_model = d_model
    self.d_model = tf.cast(self.d_model, tf.float32)

    self.warmup_steps = warmup_steps

  def __call__(self, step):
    step = tf.cast(step, dtype=tf.float32)
    arg1 = tf.math.rsqrt(step)
    arg2 = step * (self.warmup_steps ** -1.5)

    return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)

def perplexity(y_true, y_pred):
    return tf.math.exp(tf.math.reduce_mean(tf.keras.losses.categorical_crossentropy(y_true, y_pred)))

def sparse_loss(y_true, y_pred):
    loss_obj = keras.losses.SparseCategoricalCrossentropy(ignore_class=-1, reduction='none')
    loss = loss_obj(y_true, y_pred)
    return loss
def sparse_perplexity(y_true, y_pred):
    return tf.math.exp(tf.math.reduce_mean(sparse_loss(y_true, y_pred)))

if __name__ == '__main__':
    fname = 'data/ngram_train.npz' if MODEL_TYPE == 'n' else 'data/transformer_train.npz'
    print("Loading data from", fname)
    loaded = np.load(fname)
    train_x = tf.one_hot(loaded['x'], VOCAB_SIZE) if MODEL_TYPE == 'n' else loaded['x']
    train_y = tf.one_hot(loaded['y'], VOCAB_SIZE) if MODEL_TYPE == 'n' else loaded['y']
    del loaded
    print("X:", train_x[:2])
    print("Y:", train_y[:2])
    print("X shape:", train_x.shape)
    print("Y shape:", train_y.shape)

    print("Initializing model")
    models = {'n': LinearModel, 't': Transformer}
    model = models[MODEL_TYPE]()
    print(model)
    print(model(train_x[:1]))
    print(model.summary())

    print("Compiling model")
    learning_rate = CustomSchedule(EMBED_DIM)
    loss = keras.losses.CategoricalCrossentropy() if MODEL_TYPE == 'n' else sparse_loss
    metric = perplexity if MODEL_TYPE == 'n' else sparse_perplexity
    model.compile(optimizer=keras.optimizers.Adam(learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9),
                  loss=loss, metrics=[metric])

    train_sample = np.random.choice(np.arange(0, train_x.shape[0]), 20)
    #for sample in train_sample[:10]:
    #    feed = np.array([train_x[sample,:]])
    #    res = np.argmax(model(feed)[0])
    #    print("sample:", pretty_tokens(list(map(lambda t: "<unk>" if t == 0 else VOCAB[t-1], train_x[sample]))),
    #         "Truth:", train_y[sample], VOCAB[train_y[sample]], "Output:", res, VOCAB[res])

    print("Evaluating baseline")
    #model.evaluate(train_x, train_y, batch_size=1024)
    print(pretty_tokens(genTokens(model, 50)))

    print("Training model")
    model.fit(train_x, train_y, batch_size=256, validation_split=0.2, epochs=1)

    print("Sample outputs")
    #for sample in train_sample:
    #    feed = np.array([train_x[sample,:]])
    #    res = np.argmax(model(feed)[0])
    #    print("sample:", pretty_tokens(list(map(lambda t: "<unk>" if t == 0 else VOCAB[t-1], train_x[sample]))),
    #          "Truth:", train_y[sample], VOCAB[train_y[sample]], "Output:", res, VOCAB[res])

    print("Generating sample from trained model")
    print(pretty_tokens(genTokens(model, 1000)))
    print(pretty_tokens(genTokens(model, 1000)))
    for i in range(10):
        print(pretty_tokens(genTokens(model, 100)))