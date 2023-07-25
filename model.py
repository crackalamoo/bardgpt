import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense, Flatten, Dropout, Embedding,\
    Add, MultiHeadAttention, LayerNormalization, Input, Softmax
import sys

from constants import *
from tokens import pretty_tokens, rhymeMeterFromTokens

EPOCHS = 10
WARMUP_STEPS = 800
EMBED_DIM = 512
TRANSFORMER_LAYERS = 8
TRANSFORMER_DFF = 1024
RHYME_METER_DFF = 64
TRANSFORMER_HEADS = 4
VAL_SPLIT = 0.2
BATCH_SIZE = 256
SAVE_AT_END = False
VERBOSE = False
TRAINING = True

if '--epochs' in sys.argv:
    EPOCHS = int(sys.argv[sys.argv.index('--epochs')+1])
if '--warmup-steps' in sys.argv:
    WARMUP_STEPS = int(sys.argv[sys.argv.index('--warmup-steps')+1])
if '--embed-dim' in sys.argv:
    EMBED_DIM = int(sys.argv[sys.argv.index('--embed-dim')+1])
if '--transformer-layers' in sys.argv:
    TRANSFORMER_LAYERS = int(sys.argv[sys.argv.index('--transformer-layers')+1])
if '--transformer-dff' in sys.argv:
    TRANSFORMER_DFF = int(sys.argv[sys.argv.index('--transformer-dff')+1])
if '--rhyme-meter-dff' in sys.argv:
    RHYME_METER_DFF = int(sys.argv[sys.argv.index('--rhyme-meter-dff')+1])
if '--transformer-heads' in sys.argv:
    TRANSFORMER_HEADS = int(sys.argv[sys.argv.index('--transformer-heads')+1])
if '--val-split' in sys.argv:
    VAL_SPLIT = float(sys.argv[sys.argv.index('--val-split')+1])
if '--batch-size' in sys.argv:
    BATCH_SIZE = int(sys.argv[sys.argv.index('--batch-size')+1])
if '--save-at-end' in sys.argv:
    SAVE_AT_END = True
if '--verbose' in sys.argv:
    VERBOSE = True
if '--load' in sys.argv:
    TRAINING = False

N = NGRAM_N if MODEL_TYPE == 'n' else TRANSFORMER_N
VOCAB = list(np.load('lemmas/lemmas.npy'))
TEST_PROMPT = '<title> stop =ing by woods on a snowy evening <newline> '+\
    'whose woods these are i think i know <newline> '+\
    'his house is in the village though <newline> he'

def sampleVocab(dist, temperature):
    temperature = 1e-8 if temperature == 0 else temperature
    dist = np.power(dist, temperature)
    dist /= np.sum(dist)
    sample = np.random.choice(np.arange(VOCAB_SIZE), p=dist)
    return sample

def genTokens(model, tokens, temperature=0.7, prompt=None):
    res = [model.vocab.index(TITLE.lower()[1:-1])]
    if prompt is not None:
        res = [model.vocab.index(x) for x in prompt.split(' ') if x in model.vocab]
    for _ in range(tokens):
        pred = model.generate(res, temperature)
        assert pred is not None
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
        for _ in range(num_layers):
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
    vowels = input[:,:,:RHYME_STACK_SIZE-1]
    consonants = input[:,:,RHYME_STACK_SIZE-1:(RHYME_STACK_SIZE-1)*2]
    rhyme_match = input[:,:,(RHYME_STACK_SIZE-1)*2:(RHYME_STACK_SIZE-1)*3]
    vowels = tf.cast(vowels, tf.int8)
    consonants = tf.cast(consonants, tf.int8)
    vowels = tf.one_hot(vowels, depth=VOWEL_TYPES)
    consonants = tf.one_hot(consonants, depth=CONSONANT_TYPES)
    vowels = tf.reshape(vowels, shape=(tf.shape(vowels)[0], tf.shape(vowels)[1], -1))
    consonants = tf.reshape(consonants, shape=(tf.shape(consonants)[0], tf.shape(consonants)[1], -1))
    meter = input[:,:,-METER_STACK_SIZE:]
    vowels = tf.cast(vowels, tf.float32)
    consonants = tf.cast(consonants, tf.float32)
    rhyme_match = tf.cast(rhyme_match, tf.float32)
    meter = tf.cast(meter, tf.float32)
    rhyme = tf.concat([vowels, consonants, rhyme_match], axis=2)
    return rhyme, meter

class RhymeMeterLayer(keras.layers.Layer):
    def __init__(self):
        super().__init__()
        self.dense_r1 = Dense(RHYME_METER_DFF, activation='relu')
        self.dense_m1 = Dense(RHYME_METER_DFF//2, activation='relu')
        self.dense_r2 = Dense(RHYME_METER_DFF, activation='relu')
        # self.dense_m2 = Dense(RHYME_METER_DFF//2, activation='relu')
        self.dense_3 = Dense(RHYME_METER_DFF*2, activation='relu')
        self.dense_final = Dense(VOCAB_SIZE)
    def call(self, input):
        rhyme, meter = rhyme_meter_encoding(input)
        rhyme = self.dense_r1(rhyme)
        rhyme = self.dense_r2(rhyme)
        meter = self.dense_m1(meter)
        # meter = self.dense_m2(meter)
        x = tf.concat([rhyme, meter], axis=2)
        x = self.dense_3(x)
        x = self.dense_final(x)
        return x

class BardModel(keras.Model):
    def __init__(self, *, num_layers=TRANSFORMER_LAYERS, num_heads=TRANSFORMER_HEADS, dff=TRANSFORMER_DFF):
        super(BardModel, self).__init__()
        self.vocab = VOCAB
        self.tl = VOCAB.index(TITLE.lower()[1:-1])
        self.rhyme_types = max(VOWEL_TYPES, CONSONANT_TYPES)
        self.embed = InputEmbedding()
        self.decoder = Decoder(num_layers=num_layers, num_heads=num_heads, dff=dff)
        self.transformer_pred = Dense(VOCAB_SIZE)
        self.rhyme_meter_pred = RhymeMeterLayer()
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

        rhyme_meter_x = self.rhyme_meter_pred(input[1])
        x = self.add([x, rhyme_meter_x])
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
    if TRAINING:
        print("Loading data from", fname)
        loaded = np.load(fname)
        train_x = loaded['x']
        train_y = loaded['y']
        if MODEL_TYPE == 'b':
            train_x = [tf.convert_to_tensor(train_x), tf.convert_to_tensor(loaded['rm'])] # rhyme and syllables
        if MODEL_TYPE == 'n':
            train_x = tf.convert_to_tensor(train_x, tf.int32)
        del loaded
    
        if VERBOSE:
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
    if MODEL_TYPE != 'b':
        x0 = np.zeros((1,NGRAM_N-1 if MODEL_TYPE=='n' else TRANSFORMER_N), np.int32)
        res = model(x0)
    else:
        x0 = np.zeros((1,TRANSFORMER_N))
        x1 = np.zeros((1,TRANSFORMER_N,(RHYME_STACK_SIZE-1)*2+(RHYME_STACK_SIZE-1)+METER_STACK_SIZE))
        res = model([x0, x1])
    if VERBOSE:
        print(model)
        print(res)
    print(model.summary())

    if TRAINING:
        print("Compiling model")
        learning_rate = CustomSchedule(EMBED_DIM)
        model.compile(optimizer=keras.optimizers.Adam(learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9),
                    loss=sparse_loss, metrics=[sparse_perplexity])

        print("Generating sample from baseline")
        print(pretty_tokens(genTokens(model, 25)))

        print("Training model")
        min_perplexity = None
        if not os.path.exists('saved_models'):
            os.mkdir('saved_models')
        class TrainCallback(keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                global min_perplexity
                perplexity = logs['val_sparse_perplexity'] if VAL_SPLIT > 0 else logs['sparse_perplexity']
                print("\rGenerating sample from model in training: "+
                    "epoch "+str(epoch+1)+", perplexity "+str(round(perplexity, 2)), end='')
                print(pretty_tokens(genTokens(model, 75)))
                if (min_perplexity is None or perplexity <= min_perplexity) and not SAVE_AT_END:
                    min_perplexity = perplexity
                    print("Saving model weights")
                    model.save_weights('saved_models/'+MODEL_TYPE+'_model.h5') # no such file or directory right now

        model.fit(train_x, train_y,
                batch_size=BATCH_SIZE, validation_split=VAL_SPLIT, epochs=EPOCHS,
                callbacks=[TrainCallback()])

        if SAVE_AT_END:
            print("Saving final model weights")
            model.save_weights('saved_models/'+MODEL_TYPE+'_model.h5')
        
        print("Generating samples from final model")
        if VERBOSE:
            for i in range(10):
                print(pretty_tokens(genTokens(model, 100)))
            print(pretty_tokens(genTokens(model, 150, prompt=TEST_PROMPT)))
            print(pretty_tokens(genTokens(model, 500)))
        print(pretty_tokens(genTokens(model, 500)))
    
    else:
        print("Loading weights")
        model.load_weights('saved_models/'+MODEL_TYPE+'_model.h5')

        while True:
            temp = 0.7
            print("Commands:\ng: generate sample with 250 tokens\nl: generate sample with custom length\np: generate sample with prompt\nt: set temperature\nq: quit")
            cmd = input("Enter command: ")
            try:
                if cmd == 'g':
                    print("Generating sample...")
                    print(pretty_tokens(genTokens(model, 250, temperature=temp)))
                if cmd == 'l':
                    length = int(input("Enter length: "))
                    print("Generating sample...")
                    print(pretty_tokens(genTokens(model, length, temperature=temp)))
                if cmd == 'p':
                    prompt = ""
                    print("Enter prompt as tokens separated by spaces and newlines.")
                    print("Example: <title> stop =ing by woods on a snowy evening\nwhose woods these are i think i know")
                    print("All tokens not in the vocabulary will be ignored.")
                    while not prompt.endswith('\n\n\n'):
                        prompt += input("")+'\n'
                    while prompt.startswith(' ') or prompt.startswith('\n'):
                        prompt = prompt[1:]
                    while prompt.endswith(' ') or prompt.endswith('\n'):
                        prompt = prompt[:-1]
                    prompt = prompt.replace('\n', NEWLINE.lower())
                    length = int(input("Enter length: "))
                    print("Generating sample...")
                    print(pretty_tokens(genTokens(model, length, temperature=temp, prompt=prompt)))
                if cmd == 't':
                    print("Current temperature:", temp)
                    temp = float(input("New temperature: "))
                    print("Temperature set to", temp)
                if cmd == 'q':
                    sys.exit(0)
            except Exception as e:
                print("Error:", e)