from transformers import AutoTokenizer
import eng_to_ipa as ipa
import numpy as np
from preprocess import NEWLINE, TITLE

VOCAB_SIZE = 4096
NGRAM_N = 5

file = open("data/join.txt", "r")
text = file.read()
file.close()

tokens = text.split(" ")
for i in reversed(range(len(tokens))):
    if tokens[i] == '':
        tokens.pop(i)
#print(' '.join(tokens))
counts = {}
for token in tokens:
    if not token in counts:
        counts[token] = 0
    counts[token] += 1
words = list(counts.keys())
words.sort(reverse=True, key=lambda word: counts[word])
counts['<unk>'] = 0
for word in words:
    if word in words[:VOCAB_SIZE]:
        continue
    counts['<unk>'] += counts[word]
print(len(words))
print(len(tokens))
words = list(counts.keys())
words.sort(reverse=True, key=lambda word: counts[word])
print({word: counts[word] for word in words[:VOCAB_SIZE]})
print(len(tokens))


def pretty_tokens(tokens):
    s_dict = np.load('lemmas/s.npy', allow_pickle=True).item()
    ed_dict = np.load('lemmas/ed.npy', allow_pickle=True).item()
    er_dict = np.load('lemmas/er.npy', allow_pickle=True).item()
    est_dict = np.load('lemmas/est.npy', allow_pickle=True).item()
    ing_dict = np.load('lemmas/ing.npy', allow_pickle=True).item()
    dicts = {'=s': s_dict, '=ed': ed_dict, '=er': er_dict, '=est': est_dict, '=ing': ing_dict}
    vocab = set(words[:VOCAB_SIZE])
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
                next = tokens[i+1]
        if this.startswith('='):
            this = this[1:]
        elif includeSpace(this):
            this = " "+this
        res.append(this)
        i += 1
    res = ''.join(res)
    return res

ngrams = []
for i in range(len(tokens)-NGRAM_N):
    ngrams.append(tokens[i:i+NGRAM_N])
print(ngrams[:10])