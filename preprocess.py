import re
TITLE = " <TITLE> "
NEWLINE = " <NEWLINE> "

def getContents(fname):
    file = open(fname, "r")
    text = file.read()
    file.close()
    return text
def removeBrackets(text):
    while text.find('[') != -1:
        begin = text.find('[')
        end = text.find(']', begin+1)
        if end == -1:
            break
        else:
            text = text[:begin] + text[end+1:]
    return text
def isNumeral(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
def isRomanNumeral(s):
    return s != '' and bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", s))

def dickinson():
    text = getContents("data/dickinson-raw.txt")
    text = removeBrackets(text)
    index = getContents("data/dickinson-index.txt").split('\n')
    out = open("data/dickinson.txt", "w+")
    for i in range(len(index)):
        this = text.find(index[i])
        next = text.find('\n'*6, this+1)
        if this == -1 or next == -1:
            continue
        prev = text.rfind('\n', 0, this-3)
        prev2 = text.find('\n', prev+1)
        title = text[prev+1:prev2-1]
        if isRomanNumeral(title):
            title = ''
        poem = text[this:next]
        poem = poem.replace('\n', NEWLINE)
        poem = poem.replace("  ", "").replace('_','')
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.lower()
        out.write(poem)
        print(poem)
    out.close()
def frost():
    text = getContents("data/frost-raw.txt")
    text = removeBrackets(text)
    index = getContents("data/frost-index.txt").split('\n')
    print(index)
    out = open("data/frost.txt", "w+")
    skipindex = text.find("CONTENTS")
    skipindex = text.find("SELECTED POEMS", skipindex+1)
    for i in range(len(index)):
        this = text.find(index[i], skipindex)
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        title = text[this:this+len(index[i])]
        poem = text[text.find('\n\n',this)+2:next]
        poem = poem.replace('\n', NEWLINE).replace('_','')
        poem = TITLE + title + poem + NEWLINE
        poem = poem.lower()
        out.write(poem)
        print(poem)
    out.close()
def keats():
    text = getContents("data/keats-raw.txt")
    text = removeBrackets(text)
    index = getContents("data/keats-index.txt").split('\n')
    print(index)
    out = open("data/keats.txt", "w+")
    for heading in index:
        this = text.find(heading+".")
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        title = text[this:this+len(heading)]
        endtitle = this+len(heading+".")
        while text[endtitle] == '\n':
            endtitle += 1
        poem = text[endtitle:next]
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(" "):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if isRomanNumeral(poem[i][:-1]):
                if i+1 < len(poem) and poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            else:
                skipText = poem[i].rfind("     ")
                if skipText == -1:
                    skipText = 0
                if isNumeral(poem[i][skipText:]):
                    poem[i] = poem[i][:skipText]
                    if i > 0 and poem[i-1] == '':
                        poem.pop(i+1)
                    if poem[i] == '':
                        poem.pop(i)
            poem[i] = poem[i].replace("    ","").replace("   ","").replace("  ", "")
            if poem[i].endswith("10"):
                poem[i] = poem[i][:-2]
        if poem[0] == '':
            poem.pop(0)
        while poem[len(poem)-1] == '' or poem[len(poem)-1] == ' ':
            poem.pop()
        poem = '\n'.join(poem)
        if heading == "BOOK I" and poem.find("BOOK II") != -1:
            poem = poem[:poem.find("BOOK II")]
            while poem.endswith('\n'):
                poem = poem[:-1]
        elif heading == "BOOK II" and poem.find("BOOK III") != -1:
            poem = poem[:poem.find("BOOK III")]
            while poem.endswith('\n'):
                poem = poem[:-1]
        elif heading == "PART I" and poem.find("PART II") != -1:
            poem = poem[:poem.find("PART II")]
            while poem.endswith('\n'):
                poem = poem[:-1]
        elif heading == "BOOK III" and poem.find(" *****") != -1:
            poem = poem[:poem.find(" *****")]
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.replace('\n', NEWLINE)
        poem = poem.lower()
        if poem.rfind("footnotes:") != -1:
            poem = poem[:poem.rfind("footnotes:")]
        out.write(poem)
        print(title)
        #print(poem)
    out.close()
def poe():
    text = getContents("data/poe-raw.txt")
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[Illustration:', '[Illustration:')
    text = text.replace('\n[Illustration:', '[Illustration:')
    text = removeBrackets(text)
    text = text.replace("TAMERLANE", "_TAMERLANE_")
    index = getContents("data/poe-index.txt").upper().split('\n')
    print(index)
    out = open("data/poe.txt", "w+")
    for i in range(len(index)):
        this = text.find(index[i])
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        title = text[this+1:this+len(index[i])-1]
        endtitle = this+len(index[i])
        while text[endtitle] == '\n':
            endtitle += 1
        poem = text[endtitle:next]
        poem = poem.replace("    ", "").replace('_', '')
        poem = poem.split('\n')
        if i == 0:
            print(poem)
        j = len(poem)-1
        while j >= 0:
            while poem[j].startswith(" "):
                poem[j] = poem[j][1:]
            if isRomanNumeral(poem[j][:-1]) or isNumeral(poem[j]):
                if j+1 < len(poem) and poem[j+1] == '':
                    poem.pop(j+1)
                poem.pop(j)
                if j-1 >= 0 and poem[j-1] == '':
                    poem.pop(j-1)
                    j -= 1
                if j-2 >= 0 and poem[j-2] == '':
                    poem.pop(j-2)
                    j -= 1
                j -= 1
                continue
            if poem[j] == 'PART I.' or poem[j] == 'PART II.':
                poem.pop(j)
                if j+1 < len(poem) and poem[j+1] == '':
                    poem.pop(j+1)
            j -= 1
        while poem[0] == '\n':
            poem.pop(0)
        poem = '\n'.join(poem)
        if title == "THE RAVEN":
            poem = poem.replace('\ncraven',' craven').replace(',\nfearing', ', fearing')
            poem = poem.replace('flown\nbefore','flown before').replace('and\ndoor','and door')
            poem = poem.replace('hath\nsent','hath sent').replace('bird or\ndevil','bird or devil')
            poem = poem.replace(',\nupstarting',', upstarting')
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.replace('\n', NEWLINE)
        poem = poem.lower()
        out.write(poem)
        print(poem)
    out.close()
def shelley():
    text = getContents("data/shelley-raw.txt")
    text = removeBrackets(text)
    index = getContents("data/shelley-index.txt").split('\n')
    print(index)
    out = open("data/shelley.txt", "w+")
    for heading in index:
        this = text.find(heading)
        this = text.find(heading,this+1)
        next = text.find('\n***\n\n', this+1)
        if this == -1 or next == -1:
            continue
        title = text[this:this+len(heading)]
        endtitle = this+len(heading+".")
        while text[endtitle] == '\n':
            endtitle += 1
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(" "):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if isRomanNumeral(poem[i][:-1]):
                if i+1 < len(poem) and poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            else:
                skipText = poem[i].rfind("     ")
                if skipText == -1:
                    skipText = 0
                if isNumeral(poem[i][skipText:]) or isNumeral(poem[i][:-4]):
                    if isNumeral(poem[i][:-4]):
                        skipText = -4
                    elif isNumeral(poem[i][:-3]):
                        skipText = -3
                    elif isNumeral(poem[i][:-2]):
                        skipText = -2
                    poem[i] = poem[i][:skipText]
                    if i > 0 and poem[i-1] == '':
                        poem.pop(i+1)
                    if poem[i] == '':
                        poem.pop(i)
            poem[i] = poem[i].replace("    ","").replace("   ","").replace("  ", "")
        if poem[0] == '':
            poem.pop(0)
        while poem[len(poem)-1] == '' or poem[len(poem)-1] == ' ':
            poem.pop()
        poem = '\n'.join(poem)
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.replace('\n', NEWLINE)
        poem = poem.lower()
        if poem.rfind("notes;") != -1:
            poem = poem[:poem.rfind("notes;")]
        if poem.rfind("notes:") != -1:
            poem = poem[:poem.rfind("notes:")]
        if poem.rfind("\nnote:") != -1:
            poem = poem[:poem.rfind("\nnote:")]
        out.write(poem)
        print(title)
        #print(poem)
    out.close()
def byron():
    text = getContents("data/byron-raw.txt")
    text = text.replace(' [', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = removeBrackets(text)
    index = getContents("data/byron-index.txt").upper().split('\n')
    print(index)
    out = open("data/byron.txt", "w+")
    for heading in index:
        this = text.find(heading+'.')
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        title = text[this:this+len(heading)]
        endtitle = this+len(heading+'.')
        while text[endtitle] == '\n' or text[endtitle] == ' ':
            endtitle += 1
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(" "):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if (isNumeral(poem[i]) or isNumeral(poem[i][:-1]) or isRomanNumeral(poem[i][:-1]))\
                    and not poem[i].startswith('1.') and not poem[i].startswith('i.')\
                    and not poem[i] == '':
                if i+1 < len(poem) and poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            poem[i] = poem[i].replace("    ","").replace("   ","").replace("  ", "")
        while poem[0] == '' or poem[0] == ' ':
            poem.pop(0)
        poem.pop()
        poem.pop()
        while poem[len(poem)-1] == '' or poem[len(poem)-1] == ' ' or poem[len(poem)-1].endswith(']'):
            poem.pop()
        poem = '\n'.join(poem)
        if poem.find('1.\n') != -1:
            poem = poem[poem.find('1.\n')+3:]
        elif poem.find('i.\n') != -1:
            poem = poem[poem.find('i.\n')+3:]
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.replace('\n\n\n','\n\n')
        poem = poem.replace('\n', NEWLINE)
        poem = poem.replace("'d", "ed")
        poem = poem.lower()
        if poem.rfind("notes;") != -1:
            poem = poem[:poem.rfind("notes;")]
        if poem.rfind("notes:") != -1:
            poem = poem[:poem.rfind("notes:")]
        if poem.rfind("\nnote:") != -1:
            poem = poem[:poem.rfind("\nnote:")]
        out.write(poem)
        print(title)
        #print(poem)
    out.close()
def join():
    text = ''
    for author in ['dickinson', 'frost', 'keats', 'poe', 'shelley', 'byron']:
        text += getContents("data/"+author+".txt")
    text = text.replace("o'er","over").replace("e'er","ever").replace("thro'","through").replace("e'en","even")
    text = text.replace(" th'", " the").replace("i 'm", "i'm").replace("'t is", "it is")
    text = text.replace("'tis", "it is").replace("'twould", "it would").replace("it 's", "it's")
    text = text.replace("'twas", "it was").replace("'twere", "it were").replace("'twould","it would")
    text = text.replace(" twas "," it was ").replace(" twere "," it were ").replace(" twould "," it would ").replace(" twill "," it will ")
    text = text.replace("—-", "--")
    text = text.replace(" .",".").replace(" ,",",").replace("."," .").replace(","," ,")
    text = text.replace(" :",":").replace(" ;",";").replace(":"," :").replace(";"," ;")
    text = text.replace(" !","!").replace(" ?","?").replace("!"," !").replace("?"," ?")
    text = text.replace(NEWLINE+NEWLINE, NEWLINE+" "+NEWLINE)
    text = text.replace("><", "> <")
    text = text.replace("  ", " ")
    text = text.replace(" -","-").replace("- ","-").replace("-"," - ")
    text = text.replace(' "','"').replace('" ','"').replace('"',' " ')
    text = text.replace(" i'd "," ID ").replace(" we'd "," WED ").replace(" he'd "," HED ").replace(" she'd "," SHED ")
    text = text.replace("don't", "DONT").replace("wouldn't","WOULDNT").replace("isn't", "ISNT").replace("aren't","ARENT")
    text = text.replace("doesn't","DOESNT").replace("won't","WONT").replace("shouldn't","SHOULDNT").replace("couldn't","COULDNT")
    text = text.replace("can't","CANT").replace("shan't","SHANT").replace("didn't","DIDNT")
    text = text.replace("'s", " S").replace("'m"," M").replace("'ve"," VE").replace("'re"," RE")
    text = text.replace("'d", "ed")
    text = text.replace(" '","'").replace("' ","'").replace("'"," ' ")
    text = text.replace("ID","i 'd").replace("WED","we 'd").replace("HED","he 'd").replace("SHED","she 'd")
    text = text.replace("DONT","do n't").replace("WOULDNT", "would n't").replace("ISNT", "is n't").replace("ARENT", "are n't")
    text = text.replace("DOESNT","does n't").replace("WONT","wo n't").replace("SHOULDNT","should n't").replace("COULDNT","could n't")
    text = text.replace("CANT","can n't").replace("SHANT","sha n't").replace("DIDNT","did n't")
    text = text.replace("S", "'s").replace("M","'m").replace("VE","'ve").replace("RE","'re")
    text = text.replace("(","").replace(")","")
    text = text.replace("coming", "come ing").replace("living","live ing").replace("dying","die ing")
    text = text.replace("trembling","tremble ing").replace("sitting","sit ing").replace("getting","get ing")
    text = text.replace("breathing","breathe ing").replace("making","make ing").replace("leaving","leave ing")
    for root in ["go", "be", "burn", "pass", "look", "dream", "sleep", "wander", "think", "part", "say"]:
        text = text.replace(root+"ing",root+" ing")
    text = text.replace("dropped","drop ed")
    for root in ["pass", "seem", "look", "turn", "call", "ask", "touch", "wander", "roll", "depart", "stay", "perish", "fail", "want"]:
        text = text.replace(" "+root+"ed "," "+root+" ed ")
    for root in ["use", "die", "love", "live", "breathe", "smile",  "move", "cease", "save"]:
        text = text.replace(" "+root+"d "," "+root+" ed ")
    text = text.replace(" skies "," sky s ").replace(" memories "," memory s ").replace(" mysteries "," mystery s ")
    text = text.replace(" ings "," ing s ")
    for root in ["eye","flower","bell","thing","star","day","hour","tree","word","year","wing","angel","come","hand",
                 "bird","dream","hill","cloud","finger","sound","seem","make","lie","mountain","wave","look","time",
                 "heart","field","friend","say","know","water","sigh","sea","soul","arm","think","smile","shadow",
                 "thought","door","hope","head","forest","window","wall","stone","creature","lock","street","fear",
                 "float","rock","want","cheek","rock","stand","region","lover","voice","gale","pleasure","lamp",
                 "need","hall","pearl","horse","see","son","grief","bear","robin","nest","call","lead",
                 "like","love","night","heaven","light","way","tell","die","sun","sleep","air","own","live",
                 "spirit","summer","face","back","morning","take","hear","wind","turn","find","name",
                 "home","mine","place","put","pain","get","breast","keep","house","rest","fire","nothing",
                 "ask","mind","feel","bed","save","side","rose","right","breathe","art","breath","drop","joy",
                 "noon","ear","grave","snow","form","slow","sit","woe","forget","speak","morn","power","song",
                 "room","sorrow","bee","wander","fall","meet","part","land","storm","care","brain","warm",
                 "give","throne","spring","sight","truth","passion","play","shore","set","burn","delight",
                 "chamber","move","father","read","town","bring","close","bosom","shade","grace","cease",
                 "open","lake","work","break","shut","mortal","roll","river","weep","thousand","ring","kind",
                 "boy","calm","garden","brook","step","tongue","sing","glow","despair","use","brow","road",
                 "seek","view","run","moment","free","shape","please","tomb","prayer","tone","thunder",
                 "spread","stir","wait","king","doubt","fail","brother","eve"]:
        text = text.replace(" "+root+"s "," "+root+" s ")
    out = open("data/join.txt", "w+")
    out.write(text)
    out.close()

dickinson()
frost()
keats()
poe()
shelley()
byron()

join()