import urllib.request
import os

files = [
    ('https://www.gutenberg.org/cache/epub/12242/pg12242.txt', 'dickinson-raw'),
    ('https://www.gutenberg.org/files/59824/59824-0.txt', 'frost-raw'),
    ('https://www.gutenberg.org/cache/epub/23684/pg23684.txt', 'keats-raw'),
    ('https://www.gutenberg.org/cache/epub/4800/pg4800.txt', 'shelley-raw'),
    ('https://www.gutenberg.org/files/50852/50852-0.txt', 'poe-raw'),
    ('https://www.gutenberg.org/cache/epub/8861/pg8861.txt', 'byron-raw'),
    ('https://www.gutenberg.org/files/21700/21700-0.txt', 'byron-raw-juan'),
    ('https://www.gutenberg.org/files/9622/9622-0.txt', 'ballads-raw'),
    ('https://www.gutenberg.org/files/56913/56913-0.txt', 'tennyson-raw'),
    ('https://www.gutenberg.org/cache/epub/12843/pg12843.txt', 'emerson-raw'),
    ('https://www.gutenberg.org/cache/epub/574/pg574.txt', 'blake-raw'),
    ('https://www.gutenberg.org/cache/epub/25153/pg25153.txt', 'longfellow-raw'),
    ('https://www.gutenberg.org/cache/epub/7400/pg7400.txt', 'holmes-raw'),
    ('https://www.gutenberg.org/files/1057/1057-0.txt', 'wilde-raw'),
    ('https://www.gutenberg.org/cache/epub/33363/pg33363.txt', 'browning-raw-ii'),
    ('https://www.gutenberg.org/cache/epub/31015/pg31015.txt', 'browning-raw-iv'),
    ('https://www.gutenberg.org/cache/epub/38877/pg38877.txt', 'yeats-raw'),
    ('https://www.gutenberg.org/cache/epub/7164/pg7164.txt', 'tagore-raw-gitanjali'),
    ('https://www.gutenberg.org/cache/epub/6686/pg6686.txt', 'tagore-raw-gardener'),
    ('https://www.gutenberg.org/files/53206/53206-0.txt', 'modern-raw'),
    ('https://www.gutenberg.org/cache/epub/1041/pg1041.txt', 'shakespeare-raw'),
    ('https://www.gutenberg.org/cache/epub/16341/pg16341.txt', 'bryant-raw'),
    ('https://www.gutenberg.org/cache/epub/9580/pg9580.txt', 'whittier-raw'),
    ('https://www.gutenberg.org/cache/epub/6130/pg6130.txt', 'iliad-raw'),
    ('https://www.gutenberg.org/files/3160/3160-0.txt', 'odyssey-raw'),
    ('https://www.gutenberg.org/files/57068/57068-0.txt', 'rumi-raw'),
    ('https://www.gutenberg.org/cache/epub/26/pg26.txt', 'milton-raw'),
    ('https://www.gutenberg.org/cache/epub/19630/pg19630.txt', 'mahabharata-raw'),
]

DIR = 'data'
if not os.path.exists(DIR):
    os.makedirs(DIR)
for file in files:
    print("Downloading " + file[0])
    urllib.request.urlretrieve(file[0], DIR + '/' + file[1] + '.txt')
print("Downloads complete")