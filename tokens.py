import numpy as np
from preprocess import NEWLINE, TITLE, KAGGLE
if __name__ == '__main__':
    import eng_to_ipa as ipa
    from threading import Thread

VOCAB_SIZE = 4096
NGRAM_N = 4
TRANSFORMER_N = 32
MODEL_TYPE = 't' # n: ngram, t: transformer
TOKEN_SKIP = 1 if MODEL_TYPE == 'n' else (11 if KAGGLE else 3)
BANNED_TOKENS = ['1','2','3','y','e','l','maud','olaf','lorenzo','de','oscar',
                 'r','d','f','p','agnes','eulalie','kate','niam','thel',
                 '+++++++++++++','c','j','h','4','5','6','7','8','9','10',
                 '11','12','*','x','b','/','k','g','ii','s','u','da','el',
                 'le','que','~','000','m','thu','thir','13','14','15','16','17',
                 '18','19','20','30','th','bu','ri','w','v','al','iv','wi',
                 'la','las','t','ma','ha','mee','ne','em','ry','di','st',
                 'yr','ful','iii','bo','faire','tos','ai','en','et','sug',
                 'ga','wel','hee','hon','n','wan','ut','te','ad','hym','na']
N_THREADS = 16

if __name__ == '__main__':
    file = open("data/join.txt" if not KAGGLE else "data/join-kaggle.txt", "r")
    text = file.read()
    file.close()

    tokens = text.split(" ")
    tokens = [x for x in tokens if x != '']
    print("Total number of tokens:", len(tokens))
    print("Counting words")
    counts = {}
    for token in tokens:
        if not token in counts:
            counts[token] = 0
        counts[token] += 1
    words = list(counts.keys())
    words.sort(reverse=True, key=lambda word: counts[word])

    for token in BANNED_TOKENS:
        if token in words:
            words.remove(token)
            words.append(token)
    counts['<unk>'] = 0
    for word in words:
        if word in words[:VOCAB_SIZE]:
            continue
        counts['<unk>'] += counts[word]
    words = list(counts.keys())
    words.sort(reverse=True, key=lambda word: counts[word])
    for token in BANNED_TOKENS:
        if token in words:
            words.remove(token)
            words.append(token)

    vocab = set(words[:VOCAB_SIZE])
else:
    print("Loading vocab")
    vocab = set(list(np.load('lemmas/lemmas.npy')))

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
            this = '\n ༄༅༅ '
        elif not this in vocab:
            this = " <unk>"
            if not includeSpace(this):
                this = "<unk>"
            res.append(this)
            i += 1
            continue
        vowels = set(['a','e','i','o','u'])
        if i+1 < len(tokens):
            next = tokens[i+1]
            while next.startswith('='):
                if next == "=nt":
                    if tokens[i].endswith('n'):
                        this = this[:-1]
                    if tokens[i] == 'will':
                        this = 'wo'
                    this = this+"n't"
                else:
                    if tokens[i] in dicts[next]:
                        this = dicts[next][this]
                    else:
                        if next[1] == 'e' or next[1] == 'i':
                            if this.endswith('e'):
                                this = this[:-1]
                            elif this.endswith('c'):
                                this = this+'k'
                            if this.endswith('y') and next[1] == 'e' and len(this) > 2 and not this[-2] in vowels:
                                this = this[:-1]+'i'
                        if next[1] == 's':
                            if this.endswith('s') or this.endswith('sh') or this.endswith('x') or this.endswith('ch'):
                                this = this+'e'
                            if this.endswith('y') and len(this) > 2 and not this[-2] in vowels:
                                this = this[:-1]+'ie'
                        
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
    N = NGRAM_N if MODEL_TYPE == 'n' else TRANSFORMER_N+1
    for i in range(N-1):
        tokens.append(None)
    words.remove('<unk>')
    print({word: counts[word] for word in words[:VOCAB_SIZE]})
    print("Masking unknown tokens")
    tokens = [(words.index(x) if x in vocab else -1) for x in tokens]
    
    print("Splitting poems with masked dividers")
    title_token = words.index(TITLE.lower()[1:-1])
    mask_list = [-1]*N
    splits = []
    chunk_size = len(tokens)//N_THREADS
    for i in range(N_THREADS):
        splits.append(
            tokens[i*chunk_size : (i+1)*chunk_size if i < N_THREADS-1 else len(tokens)])

    results = [None] * N_THREADS
    threads = []

    def add_dividers(thread_index, split):
        i = 1
        while i < len(split):
            if split[i] == title_token:
                split = split[:i] + mask_list + split[i:]
                i += N+5
            i += 1
        results[thread_index] = split
        return split
    for i in range(N_THREADS):
        t = Thread(target=add_dividers, args=(i, splits[i],))
        threads.append(t)
        t.start()
    tokens = []
    for i in range(N_THREADS):
        threads[i].join()
        tokens += results[i]

    print("Creating sets of ngrams")
    ngrams = []
    for i in range(0, len(tokens)-N, TOKEN_SKIP):
        ngrams.append(tokens[i:i+N])
    train_x = []
    train_y = []
    for ngram in ngrams:
        sample = ngram[:N]
        train_x.append(sample[:N-1])
        if MODEL_TYPE != 'n':
            train_y.append(sample[1:])
        else:
            train_y.append(sample[N-1])
    print("Converting arrays")
    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y)
    if MODEL_TYPE != 'n':
        train_x += 1 # x in [0, VOCAB_SIZE] since 0 is for <unk>
                     # y in [-1, VOCAB_SIZE-1] with VOCAB_SIZE tokens, one for each vocabulary item, and -1 for <unk>
    
    print("Saving data")
    fname = 'data/ngram_train.npz' if MODEL_TYPE == 'n' else 'data/transformer_train.npz'
    np.savez_compressed(fname, x=train_x, y=train_y)
    np.save('lemmas/lemmas.npy', words[:VOCAB_SIZE])
