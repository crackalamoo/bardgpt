import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense, Flatten, Dropout, Embedding,\
    Add, MultiHeadAttention, LayerNormalization, Input, Softmax

from constants import *
from tokens import pretty_tokens, rhymeMeterFromTokens

N = NGRAM_N if MODEL_TYPE == 'n' else TRANSFORMER_N
EMBED_DIM = 512
TRANSFORMER_LAYERS = 4
TRANSFORMER_HEADS = 4
TRANSFORMER_DFF = 1024
RHYME_METER_DFF = 32 # 128
WARMUP_STEPS = 1 #800
VOCAB = list(np.load('lemmas/lemmas.npy'))

def sampleVocab(dist, temperature):
    temperature = 1e-8 if temperature == 0 else temperature
    dist = np.power(dist, temperature)
    dist /= np.sum(dist)
    sample = np.random.choice(np.arange(VOCAB_SIZE), p=dist)
    return sample

def genTokens(model, tokens, temperature=0.7, untitled=False):
    res = [VOCAB.index(TITLE.lower()[1:-1])]
    if untitled:
        res.append(VOCAB.index(NEWLINE.lower()[1:-1]))
    for _ in range(tokens):
        pred = model.generate(res, temperature)
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
        x = tf.one_hot(input, VOCAB_SIZE)
        x = self.seq(x)
        return x

    def generate(self, fullContext, temperature=0.7):
        context = fullContext[-(N-1):]
        while len(context) > NGRAM_N-1:
            context.pop(0)
        while len(context) < NGRAM_N-1:
            context.append(-1)
        context = np.asarray([context])
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

class TransformerModel(keras.Model):
    def __init__(self, *, num_layers=TRANSFORMER_LAYERS, num_heads=TRANSFORMER_HEADS, dff=TRANSFORMER_DFF):
        super(TransformerModel, self).__init__()
        self.vocab = VOCAB
        self.embed = InputEmbedding()
        self.decoder = Decoder(num_layers=num_layers, num_heads=num_heads, dff=dff)
        self.out = Dense(VOCAB_SIZE, activation='softmax')

    def call(self, input):
        x = self.embed(input) # context x embedding
        x = self.decoder(x) # context x embedding
        x = self.out(x) # context x vocab size
        try:
            del x._keras_mask
        except AttributeError:
            pass

        return x

    def generate(self, fullContext, temperature=0.7):
        context = fullContext[-N:]
        lastToken = len(context)-1
        while len(context) > TRANSFORMER_N:
            context.pop(0)
        while len(context) < TRANSFORMER_N:
            context.append(-1)
        context = np.asarray([context])+1
        pred = self.call(context)[0]
        pred = pred[lastToken]
        pred = sampleVocab(pred, temperature)
        return pred


def rhyme_meter_encoding(input):
    vowels = input[:,:,:RHYME_STACK_SIZE]
    consonants = input[:,:,RHYME_STACK_SIZE:RHYME_STACK_SIZE*2]
    meter = input[:,:,-METER_STACK_SIZE:]
    print("v", vowels)
    print("c", consonants)
    vowels = tf.one_hot(vowels, VOWEL_TYPES)
    consonants = tf.one_hot(consonants, CONSONANT_TYPES)
    vowels = tf.reshape(vowels, [tf.shape(vowels)[0], tf.shape(vowels)[1], -1])
    consonants = tf.reshape(consonants, [tf.shape(consonants)[0], tf.shape(consonants)[1], -1])
    rhyme = tf.concat([vowels, consonants], axis=2)
    meter = tf.cast(meter, tf.float32)
    rhyme_meter = tf.concat([rhyme, meter], axis=2)
    return rhyme_meter

class BardModel(keras.Model):
    def __init__(self, *, num_layers=TRANSFORMER_LAYERS, num_heads=TRANSFORMER_HEADS, dff=TRANSFORMER_DFF):
        super(BardModel, self).__init__()
        self.vocab = VOCAB
        self.tl = VOCAB.index(TITLE.lower()[1:-1])
        self.rhyme_types = max(VOWEL_TYPES, CONSONANT_TYPES)
        self.embed = InputEmbedding()
        self.decoder = Decoder(num_layers=num_layers, num_heads=num_heads, dff=dff)
        self.transformer_pred = Dense(VOCAB_SIZE)
        self.rhyme_meter_pred = keras.Sequential([
            # input is context x rhyme/meter encoding
            Dense(RHYME_METER_DFF, activation='relu'), # context x dff
            Dense(RHYME_METER_DFF, activation='relu'),
            Dense(VOCAB_SIZE) # context x vocab size (to match transformer output)
        ], name='rhyme_meter')
        self.add = Add()
        self.softmax = Softmax()
    
    def call(self, input):
        x = self.embed(input[0])
        x = self.decoder(x)
        x = self.transformer_pred(x)
        try:
            del x._keras_mask
        except AttributeError:
            pass
        rhyme_meter = rhyme_meter_encoding(input[1])
        rhyme_meter_x = self.rhyme_meter_pred(rhyme_meter)
        # x = self.add([x, rhyme_meter_x])
        x = rhyme_meter_x # ablation
        x = self.softmax(x)
        return x
    
    def generate(self, fullContext, temperature=0.7):
        context = fullContext[-N:]
        lastToken = len(context)-1
        while len(context) > TRANSFORMER_N:
            context.pop(0)
        while len(context) < TRANSFORMER_N:
            context.append(-1)
        context = np.asarray([context])+1
        rm = rhymeMeterFromTokens(fullContext, len(fullContext), self.tl, self.vocab)
        rm = np.asarray([rm])
        pred = self.call([context, rm])[0]
        pred = pred[lastToken]
        pred = sampleVocab(pred, temperature)
        return pred



class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
  def __init__(self, d_model, warmup_steps=WARMUP_STEPS):
    super().__init__()

    self.d_model = d_model
    self.d_model = tf.cast(self.d_model, tf.float32)

    self.warmup_steps = warmup_steps

  def __call__(self, step):
    step = tf.cast(step, dtype=tf.float32)
    arg1 = tf.math.rsqrt(step)
    arg2 = step * (self.warmup_steps ** -1.5)

    return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)


def sparse_loss(y_true, y_pred):
    loss_obj = keras.losses.SparseCategoricalCrossentropy(ignore_class=-1, reduction='none')
    loss = loss_obj(y_true, y_pred)
    return loss
def sparse_perplexity(y_true, y_pred):
    return tf.math.exp(tf.math.reduce_mean(sparse_loss(y_true, y_pred)))

if __name__ == '__main__':
    fname = {'n': 'inputs/ngram_train.npz',
        't': 'inputs/transformer_train.npz',
        'b': 'inputs/bard_train.npz'
    }[MODEL_TYPE]
    print("Loading data from", fname)
    loaded = np.load(fname)
    train_x = loaded['x']
    train_y = loaded['y']
    if MODEL_TYPE == 'b':
        train_x = [tf.convert_to_tensor(train_x), tf.convert_to_tensor(loaded['rm'])] # rhyme and syllables
    if MODEL_TYPE == 'n':
        train_x = tf.convert_to_tensor(train_x, tf.int32)
    del loaded
    
    if MODEL_TYPE != 'b':
        print("X:", train_x[10:14])
    else:
        print("X:", train_x[0][10:14])
        print("RM:", train_x[1][10:14][1])
    print("Y:", train_y[10:14])
    if MODEL_TYPE != 'b':
        print("X shape:", train_x.shape)
    print("Y shape:", train_y.shape)

    print("Initializing model")
    models = {'n': LinearModel, 't': TransformerModel, 'b': BardModel}
    model = models[MODEL_TYPE]()
    print(model)
    if MODEL_TYPE != 'b':
        print(model(train_x[:1]))
    else:
        x0 = train_x[0][:1]
        x1 = train_x[1][:1]
        print(model([x0, x1]))
    print(model.summary())

    print("Compiling model")
    learning_rate = CustomSchedule(EMBED_DIM)
    loss = sparse_loss
    metric = sparse_perplexity
    model.compile(optimizer=keras.optimizers.Adam(learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9),
                  loss=loss, metrics=[metric])

    print("Generating sample from baseline")
    print(pretty_tokens(genTokens(model, 50)))

    print("Training model")
    model.fit(train_x, train_y, batch_size=256, validation_split=0.2, epochs=2)

    print("Sample outputs")

    print("Generating sample from trained model")
    for i in range(10):
        print(pretty_tokens(genTokens(model, 100, untitled=True)))
    print(pretty_tokens(genTokens(model, 500)))
    print(pretty_tokens(genTokens(model, 500)))
