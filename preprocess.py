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
        if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", title)):
            title = ''
        poem = text[this:next]
        poem = poem.replace('\n', NEWLINE)
        poem = poem.replace("  ", "")
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
        poem = poem.replace('\n', NEWLINE)
        poem = TITLE + title + poem + NEWLINE
        poem = poem.lower()
        out.write(poem)
        print(poem)
    out.close()
def whitman():
    text = getContents("data/whitman-raw.txt")
    text = text.replace("’","'").replace('“','"').replace('”','"')
    text = removeBrackets(text)
    index = getContents("data/whitman-index.txt").replace("’","'").replace('“','"').replace('”','"').split('\n')
    print(index)
    out = open("data/whitman.txt", "w+")
    for i in range(len(index)):
        this = text.find(index[i])
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        title = text[this:this+len(index[i])]
        endtitle = this+len(index[i])
        while text[endtitle] == '\n':
            endtitle += 1
        poem = text[endtitle:next]
        poem = poem.replace('\n', NEWLINE).replace("    ","").replace("   ","").replace("  ", "")
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.lower()
        out.write(poem)
        print(poem)
    out.close()
def join():
    text = ''
    for author in ['dickinson', 'frost', 'whitman']:
        text += getContents("data/"+author+".txt")
    out = open("data/join.txt", "w+")
    out.write(text)
    out.close()

#whitman()
join()