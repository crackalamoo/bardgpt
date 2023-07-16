import numpy as np
from constants import *
if __name__ == '__main__':
    from threading import Thread

N_THREADS = 32

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

def pretty_tokens(tokens, mask=True):
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
        quote = set(["'", '"'])
        nospace = set(['\n','-'])
        prev = res[len(res)-1] if len(res) > 0 else None
        prev2 = res[len(res)-2] if len(res) > 1 else None
        space = not prev in nospace\
            and not this in PUNCT and not this == '\n'\
            and not (this.startswith("'") and this != "'")
        if prev in quote and not prev2 in PUNCT:
            space = False
        elif this in quote and prev in PUNCT:
            space = False
        return space
    while i < len(tokens):
        this = tokens[i]
        if this == NEWLINE.lower()[1:-1]:
            this = '\n'
        elif this == TITLE.lower()[1:-1]:
            this = '\n ༄༅༅ '
        elif mask and not this in vocab:
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
                            if this.endswith('y') and next[1] == 'e' and len(this) > 2 and not this[-2] in VOWELS:
                                this = this[:-1]+'i'
                        if next[1] == 's':
                            if this.endswith('s') or this.endswith('sh') or this.endswith('x') or this.endswith('ch'):
                                this = this+'e'
                            if this.endswith('y') and len(this) > 2 and not this[-2] in VOWELS:
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

def getRhyme(line):
    # rhyme format:
    # final vowel (short AEIO, schwa, long AEIOU, OW, OI, A/schwa before R; total 14)
    # final consonant (R, L, N/M/NG, P/B, T/D, F/V, S/SH/Z/ZH/TH, K/G, CH/J; total 9)
    if line is None or len(line) == 0:
        return [-1, -1]
    nl = NEWLINE.lower()[1:-1]
    tl = TITLE.lower()[1:-1]
    if line[0] == tl:
        return [-1, -1]
    while line[-1] == nl or line[-1] in PUNCT or line[-1] == '"' or line[-1] == "'" or line[-1] is None:
        line = line[:-1]
        if len(line) == 0:
            return [-1, -1]
    word = line[-1]+''
    long_vowel = False
    vowel_type = None
    vowel_map = {'a': 0, 'e': 1, 'i': 2, 'o': 3, 'u': 4, 'ow': 5, 'ou': 5, 'oi': 6, 'oy': 6,
                 'ay': 7, 'ai': 7, 'au': 3, 'aw': 3, 'ea': 8, 'ee': 8, 'eu': 11, 'ew': 11,
                 'oa': 10, 'oo': 11, 'y': 9, 'ey': 7, 'ei': 9}
    
    # vowel type format:
    # 0: A, 1: E, 2: I, 3: O, 4: U, 5: OW, 6: OI
    # short U is schwa
    # OW, OI are always long
    # before R: short E/I become schwa, schwa/short A get their own vowel type, short O becomes long O
    consonant_type = -1
    cons_map = {'r': 0, 'l': 1, 'n': 2, 'm': 2, 'ng': 2,
                'p': 3, 'b': 3, 't': 4, 'd': 4, 'f': 5,
                'v': 5, 's': 6, 'sh': 6, 'z': 6, 'zh': 6,
                'th': 6, 'k': 7, 'ch': 8, 'j': 8}
    # consonant type format:
    # 0: R, 1: L, 2: N/M/NG, 3: P/B, 4: T/D, 5: F/V, 6: S/SH/Z/ZH/TH, 7: K/G, 8: CH/J
    # total 9 consonant types

    # full vowel type list: (L=long, S=short, R=before R)
    # 0: AS (bat), 1: ES (bet), 2: IS (bit), 3: OS (bot), 4: US/schwa (but)
    # 5: OW (bout), 6: OI (boil)
    # 7: AL (bait), 8: EL (beat), 9: IL (bite), 10: OL (boat), 11: UL (boot)
    # 12: AR (bar), 13: schwa_R (butter, bird, burn)
    # total 14 vowel types
    def getVowel(type, isLong, beforeR):
        if beforeR and not isLong:
            if type == 0:
                return 12
            if type ==1 or type == 2 or type == 4:
                return 13
            if type == 3:
                return 10
        if isLong and 0 <= type <= 4:
            return type+7
        return type

    lock_consonant = -1
    if len(line) > 1:
        if word == '=ed':
            if line[-2].endswith('t') or line[-2].endswith('d'):
                return [0, 4]
            lock_consonant = 4
            word = line[-2]
        if word == '=s' or word == "'s":
            if line[-2].endswith('s') or line[-2].endswith('z') or line[-2].endswith('ch') or line[-2].endswith('sh') or line[-2].endswith('x'):
                return [4, 6]
            lock_consonant = 6
            word = line[-2]
        elif word == "'re":
            lock_consonant = 0
            word = line[-2]
        elif word == "'ve":
            lock_consonant = 5
            word = line[-2]
        elif word == "'ll":
            lock_consonant = 1
            word = line[-2]
        elif word == "'d":
            lock_consonant = 4
            word = line[-2]
        elif word == "'m":
            lock_consonant = 2
            word = line[-2]
        elif word == "=nt'":
            lock_consonant = 4
            word = line[-2]
    if word in DEFINED_RHYMES:
        vowel_type = DEFINED_RHYMES[word][0]
        consonant_type = DEFINED_RHYMES[word][1] if lock_consonant == -1 else lock_consonant
        return [vowel_type, consonant_type]
    
    if word.endswith('o'):
        return [10, lock_consonant]
    if word.endswith('bble') or word.endswith('ggle'):
        return [4, 1 if lock_consonant == -1 else lock_consonant]
    if word.endswith('old'):
        return [10, 1 if lock_consonant == -1 else lock_consonant]
    if word.endswith('ance'):
        return [0, 6 if lock_consonant == -1 else lock_consonant]
    if word.endswith('ense') or word.endswith('ence'):
        return [1, 6 if lock_consonant == -1 else lock_consonant]
    if word.endswith('ince'):
        return [2, 6 if lock_consonant == -1 else lock_consonant]
    if word.endswith('ture') or word.endswith('sure'):
        return [13, 0 if lock_consonant == -1 else lock_consonant]
    if word.endswith('all'):
        return [3, 1 if lock_consonant == -1 else lock_consonant]
    if word.endswith('row') or word.endswith('low'):
        return [10, lock_consonant]
    if word.endswith('le') and len(word) >= 3 and not word[-3] in VOWELS:
        return [4, 1 if lock_consonant == -1 else lock_consonant]
    if word.endswith('on') and len(word) > 3 and not word.endswith('oon'):
        return [4, 2 if lock_consonant == -1 else lock_consonant]
    
    if word.endswith('e'):
        long_vowel = True
        word = word[:-1]
    if lock_consonant == -1:
        if word[-2:] in cons_map:
            consonant_type = cons_map[word[-2:]]
        elif word[-1:] in cons_map:
            consonant_type = cons_map[word[-1:]]
        elif word[-1] == 'c' and long_vowel:
            consonant_type = cons_map['s']
        elif word[-1] == 'g' and long_vowel:
            consonant_type = cons_map['j']
    else:
        consonant_type = lock_consonant
    
    lock_r = False
    if not word[-1] in SOMETIMES_VOWELS:
        while not word[-1] in SOMETIMES_VOWELS:
            if word.endswith('igh'):
                return [9, consonant_type]
            if word[-1] == 'r':
                lock_r = True
            elif lock_r:
                lock_r = False
            word = word[:-1]
            if word == '':
                return [8, lock_consonant]
    if word[-2:] in vowel_map:
        vowel_type = vowel_map[word[-2:]]
    elif word[-1:] in vowel_map:
        vowel_type = vowel_map[word[-1:]]
    
    vowel_type = getVowel(vowel_type, long_vowel, consonant_type == 0 or lock_r)
    return [vowel_type, consonant_type]
def pretty_rhyme(rhyme):
    v_map = ['bat', 'bet', 'bit', 'bot', 'but', 'pout', 'boil', 'bait', 'beat', 'bite', 'boat', 'boot', 'bar', 'sir']
    c_map = ['R', 'L', 'N/M/NG', 'P/B', 'T/D', 'F/V', 'S/SH/Z/ZH/TH', 'K/G', 'CH/J']
    return "Rhyme is " +\
        (v_map[rhyme[0]] if rhyme[0] != -1 else '--') + ' ' + (c_map[rhyme[1]] if rhyme[1] != -1 else 'ø')


def getMeter(line):
    if line is None:
        return 0
    res = 0
    nl = NEWLINE.lower()[1:-1]
    tl = TITLE.lower()[1:-1]
    for i in range(len(line)):
        word = line[i]
        if word == nl or word == tl or word is None:
            continue
        if word in DEFINED_METERS:
            res += DEFINED_METERS[word]
            continue
        if word == '=ed' and i > 0:
            if line[i-1].endswith('t') or line[i-1].endswith('d') or line[i-1].endswith('te') or line[i-1].endswith('de'):
                res += 1
            continue
        if word == '=s' and i > 0:
            if line[i-1].endswith('s') or line[i-1].endswith('z') or line[i-1].endswith('ch') or line[i-1].endswith('sh') or line[i-1].endswith('x'):
                res += 1
            continue
        if word.endswith('le') and len(word) >= 3 and not word[-3] in VOWELS:
            res += 1 # to account for the dropped e
        removed_e = False
        if word.endswith('e'):
            word = word[:-1]
            removed_e = True
        if word.endswith('y') and len(word) > 2 and not word[-2] in VOWELS:
            word = word[:-1]+'i'
        word = word.replace('ea','i').replace('ee','i')
        word = word.replace('ai','i').replace('au','o')
        word = word.replace('eu','u')
        word = word.replace('ei','i').replace('ie','i')
        word = word.replace('oa','o').replace('ou','o')
        word = word.replace('oi','o').replace('oo','u')
        this_count = 0
        for vowel in VOWELS:
            this_count += word.count(vowel)
        if removed_e and this_count == 0:
            this_count = 1
        res += this_count
    return res

def lastLine(tokens, endl, nl, vocab=None):
    res = []
    i = endl-1
    while len(res) < 1 and i >= 0:
        if tokens[i] == nl:
            line = tokens[i+1:endl]
            if vocab is not None:
                line = [vocab.index(x) for x in line]
            res.append(line)
            endl = i
        i -= 1
    if len(res) == 0:
        res.append(tokens[:endl])
    res = res[::-1]
    return res
def processRhymeMeter(split):
    in_title = False
    meter = []
    rhymes = []
    meter_stack = np.zeros(METER_STACK_SIZE, np.short)
    rhyme_stack = np.zeros((RHYME_STACK_SIZE, 2), np.short) - 1
    tl = TITLE.lower()[1:-1]
    nl = NEWLINE.lower()[1:-1]
    for i in range(len(split)):
        if split[i] == tl:
            in_title = True
            meter_stack = np.zeros(METER_STACK_SIZE, np.short)
            rhyme_stack = np.zeros((RHYME_STACK_SIZE, 2), np.short) - 1
            meter.append(np.zeros(METER_STACK_SIZE, np.short))
            rhymes.append(np.zeros((RHYME_STACK_SIZE, 2), np.short) - 1)
            continue
        elif in_title and split[i] == nl:
            in_title = False
            meter.append(np.zeros(METER_STACK_SIZE, np.short))
            rhymes.append(np.zeros((RHYME_STACK_SIZE, 2), np.short) - 1)
            continue
        if not in_title and split[i] == nl:
            line = lastLine(split, 1, i, nl)[0]
            rhymes.append(rhyme_stack.copy())
            meter.append(meter_stack.copy())
            if split[i-1] != nl:
                rhyme_stack = np.roll(rhyme_stack, -1, axis=0)
                rhyme_stack[-1] = np.array(getRhyme(line), np.short)
                meter_stack = np.roll(meter_stack, -1, axis=0)
                meter_stack[-1] = getMeter(line)
        else:
            line = lastLine(split, 1, i, nl)[0]
            meter_stack[-1] = getMeter(line)
            rhymes.append(rhyme_stack.copy())
            meter.append(meter_stack.copy())
    return [meter, rhymes]
def rhymeMeterFromTokens(tokens, endl, tl, vocab=None):
    # used as input for model
    res = []
    start = endl
    while start >= 0 and tokens[start] != tl:
        start -= 1
    lines = tokens[start:endl]
    while len(lines) < TRANSFORMER_N:
        lines.append(None)
    input_lines = lines if vocab is None else [vocab.index(x) for x in lines]
    meter, rhymes = processRhymeMeter(input_lines)
    rhymes = rhymes[-TRANSFORMER_N:] # context x RHYME_STACK_SIZE x 2
    meter = meter[-TRANSFORMER_N:] # context x METER_STACK_SIZE
    rhymes = np.array(rhymes)
    meter = np.array(meter)
    rhymes = np.reshape(rhymes, (rhymes.shape[0], -1)) # context x (RHYME_STACK_SIZE*2)
    res = np.concatenate((rhymes, meter), axis=1) # context x (RHYME_STACK_SIZE*2 + METER_STACK_SIZE)
    return res

if __name__ == '__main__':
    N = NGRAM_N if MODEL_TYPE == 'n' else TRANSFORMER_N+1
    for i in range(N-1):
        tokens.append(None)
    words.remove('<unk>')
    print({word: counts[word] for word in words[:VOCAB_SIZE]})
    title_token = words.index(TITLE.lower()[1:-1])
    newline_token = words.index(NEWLINE.lower()[1:-1])

    print("Splitting poems with masked dividers")
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

    if MODEL_TYPE == 'b':
        print("Computing rhyme and meter information")
        split_token_marks = []
        split_size = len(tokens)//N_THREADS
        for i in range(N_THREADS+1):
            split_token_marks.append(split_size*i)
        for i in range(1, N_THREADS):
            while tokens[split_token_marks[i]] != TITLE.lower()[1:-1]:
                split_token_marks[i] += 1
                if split_token_marks[i] >= len(tokens):
                    break
        meter_data = []
        rhymes_data = []
        split_token_marks[-1] = len(tokens)
        split_tokens = [tokens[split_token_marks[i]:split_token_marks[i+1]] for i in range(N_THREADS)]
        rhyme_meter_res = [None] * N_THREADS
        threads = []
        def rhymeMeterThread(thread_index, split):
            rhyme_meter_res[thread_index] = processRhymeMeter(split)
        for i in range(N_THREADS):
            t = Thread(target=rhymeMeterThread, args=(i, split_tokens[i]))
            threads.append(t)
            t.start()
        for i in range(N_THREADS):
            threads[i].join()
            meter_data += rhyme_meter_res[i][0]
            rhymes_data += rhyme_meter_res[i][1]
        
        print("Converting rhyme and meter information")
        meter_data = np.asarray(meter_data)
        rhymes_data = np.asarray(rhymes_data)
        rhymes_data = np.reshape(rhymes_data, (rhymes_data.shape[0], -1)) # flatten vowel/consonant axes into one
        rhyme_meter_data = np.concatenate([meter_data, rhymes_data], axis=1)
        print(rhyme_meter_data.shape)

    print("Masking unknown tokens")
    tokens = [(words.index(x) if x in vocab else -1) for x in tokens]

    print("Creating sets of ngrams")
    ngrams = []
    rm_ngrams = []
    for i in range(0, len(tokens)-N, TOKEN_SKIP):
        ngrams.append(tokens[i:i+N])
        if MODEL_TYPE == 'b':
            rm_ngrams.append(rhyme_meter_data[i:i+N-1,:])
    train_x = []
    train_y = []
    train_rm = []
    for i in range(len(ngrams)):
        sample = ngrams[i][:N]
        train_x.append(sample[:N-1])
        if MODEL_TYPE == 'b':
            sample_rm = rm_ngrams[i]
            train_rm.append(sample_rm)
        if MODEL_TYPE != 'n':
            train_y.append(sample[1:])
        else:
            train_y.append(sample[N-1])
    print("Converting arrays")
    train_x = np.asarray(train_x)
    train_y = np.asarray(train_y)
    if MODEL_TYPE == 'b':
        train_rm = np.asarray(train_rm, np.short)
    if MODEL_TYPE != 'n':
        train_x += 1 # x in [0, VOCAB_SIZE] since 0 is for <unk>
                     # y in [-1, VOCAB_SIZE-1] with VOCAB_SIZE tokens, one for each vocabulary item, and -1 for <unk>
    
    print("Saving data")
    fname = {'n': 'data/ngram_train.npz',
        't': 'data/transformer_train.npz',
        'b': 'data/bard_train.npz'
    }[MODEL_TYPE]
    if MODEL_TYPE != 'b':
        np.savez_compressed(fname, x=train_x, y=train_y)
    else:
        np.savez_compressed(fname, x=train_x, rm=train_rm, y=train_y)
    np.save('lemmas/lemmas.npy', words[:VOCAB_SIZE])
