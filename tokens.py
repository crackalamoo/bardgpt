from transformers import AutoTokenizer
import eng_to_ipa as ipa
from preprocess import NEWLINE, TITLE

VOCAB_SIZE = 4096

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

def toText(word, prev=None):
    if word == NEWLINE.lower()[1:-1]:
        return '\n'
    if word == TITLE.lower()[1:-1]:
        return ' ༄༄༄ '
    if prev is None:
        if word.startswith('='):
            return word[1:]
        return word
    punct = set([',', '.', ';', ':', '-', '!', '?'])
    if word.startswith("'") or word in punct:
        return word
    if word.startswith('='):
        if word == '=s' and (prev.endswith('s') or prev.endswith('sh')):
            return 'es'
        if word[1] == 'e' and prev.endswith('e'):
            return word[2:]
        return word[1:]
    return ' '+word

prev = None
for word in tokens[:10000]:
    if word in words[:VOCAB_SIZE]:
        print(toText(word, prev), end="")
    else:
        print(" <unk>", end="")
    prev = word