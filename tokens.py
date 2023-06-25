from transformers import AutoTokenizer
import eng_to_ipa as ipa

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
for word in words:
    if word+"s" in words:
        print(word, word+"s")
print(len(words))
print({word: counts[word] for word in words[:VOCAB_SIZE]})
for word in tokens:
    if word in words[:VOCAB_SIZE]:
        print(word, end=" ")
    else:
        print("<unk>", end=" ")