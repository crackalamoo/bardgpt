from transformers import AutoTokenizer
import eng_to_ipa as ipa
import numpy as np
from preprocess import NEWLINE, TITLE

VOCAB_SIZE = 4096
NGRAM_N = 4

file = open("data/join.txt", "r")
text = file.read()
file.close()

tokens = text.split(" ")
for i in reversed(range(len(tokens))):
    if tokens[i] == '':
        tokens.pop(i)
counts = {}
for token in tokens:
    if not token in counts:
        counts[token] = 0
    counts[token] += 1
words = list(counts.keys())
words.sort(reverse=True, key=lambda word: counts[word])
counts['<unk>'] = 0
for word in words:
    if word.endswith('y') and word[:-1]+'iest' in words[:VOCAB_SIZE]:
        print(word, word[:-1]+'iest')
    if word in words[:VOCAB_SIZE]:
        continue
    counts['<unk>'] += counts[word]
words = list(counts.keys())
words.sort(reverse=True, key=lambda word: counts[word])

vocab = set(words[:VOCAB_SIZE])
def pretty_tokens(tokens):
    s_dict = np.load('lemmas/s.npy', allow_pickle=True).item()
    ed_dict = np.load('lemmas/ed.npy', allow_pickle=True).item()
    er_dict = np.load('lemmas/er.npy', allow_pickle=True).item()
    est_dict = np.load('lemmas/est.npy', allow_pickle=True).item()
    ing_dict = np.load('lemmas/ing.npy', allow_pickle=True).item()
    dicts = {'=s': s_dict, '=ed': ed_dict, '=er': er_dict, '=est': est_dict, '=ing': ing_dict}
    res = []
    i = 0
    def includeSpace(this):
        nonlocal res
        punct = set(['.', ',', '!', '?', ':', ';', '-'])
        quote = set(["'", '"'])
        nospace = set(['\n','-'])
        prev = res[len(res)-1] if len(res) > 0 else None
        prev2 = res[len(res)-2] if len(res) > 1 else None
        space = not prev in nospace\
            and not this in punct and not this == '\n'\
            and not (this.startswith("'") and this != "'")
        if prev in quote and not prev2 in punct:
            space = False
        elif this in quote and prev in punct:
            space = False
        return space
    while i < len(tokens):
        this = tokens[i]
        if this == NEWLINE.lower()[1:-1]:
            this = '\n'
        elif this == TITLE.lower()[1:-1]:
            this = '\n༄༄༄ '
        elif not this in vocab:
            this = " <unk>"
            if not includeSpace(this):
                this = "<unk>"
            res.append(this)
            i += 1
            continue
        if i+1 < len(tokens):
            next = tokens[i+1]
            while next.startswith('='):
                if next == "=nt":
                    if tokens[i] == 'can':
                        this = this[:-1]
                    this = this+"n't"
                else:
                    if tokens[i] in dicts[next]:
                        this = dicts[next][this]
                    else:
                        if next[1] == 'e' and this.endswith('e'):
                            this = this[:-1]
                        this = this+next[1:]
                i += 1
                next = tokens[i+1] if i+1 < len(tokens) else ''
        if this.startswith('='):
            this = this[1:]
        elif includeSpace(this):
            this = " "+this
        res.append(this)
        i += 1
    res = ''.join(res)
    res = res[1:] if res.startswith(' ') else res
    return res

if __name__ == '__main__':
    for i in range(NGRAM_N-1):
        tokens.append(None)
        tokens.insert(0, None)
    words.remove('<unk>')
    for i in reversed(range(len(tokens))):
        if tokens[i] in vocab:
            tokens[i] = words.index(tokens[i])
        else:
            tokens[i] = -1
    ngrams = []
    for i in range(len(tokens)-NGRAM_N):
        ngrams.append(tokens[i:i+NGRAM_N])
    train_x = []
    train_y = []
    for ngram in ngrams:
        sample = ngram[:NGRAM_N]
        train_x.append(sample[:NGRAM_N-1])
        train_y.append(sample[NGRAM_N-1])
    print(list(zip(train_x, train_y))[:15])

    np.savez_compressed('data/ngram_train.npz', x=train_x, y=train_y)
    np.save('lemmas/lemmas.npy', words[:VOCAB_SIZE])