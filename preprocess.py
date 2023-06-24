import eng_to_ipa as ipa
import re
TITLE = "*** "
NEWLINE = " \n"

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
        poem = poem.lower()
        poem = poem.replace('\n', NEWLINE)
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
        poem = poem.lower()
        poem = poem.replace('\n', NEWLINE)
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
        poem = poem.lower()
        poem = poem.replace('\n', NEWLINE)
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
        poem = poem.lower()
        poem = poem.replace('\n\n\n','\n\n')
        poem = poem.replace('\n', NEWLINE)
        poem = poem.replace("'d", "ed")
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
    text = text.replace("o'er","over").replace("e'er","ever").replace("thro'","through")
    text = text.replace(" th'", " the").replace("i 'm", "i'm").replace("'t is", "it is")
    text = text.replace("'tis", "it is").replace("'twould", "it would").replace("it 's", "it's")
    text = text.replace("—-", "--")
    out = open("data/join.txt", "w+")
    out.write(text)
    out.close()
byron()
join()