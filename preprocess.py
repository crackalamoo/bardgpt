import re
import numpy as np
import os
from constants import *

if not os.path.exists("inputs"):
    os.mkdir("inputs")

AUTHOR_LIST = ['dickinson', 'frost', 'keats', 'poe', 'shelley', 'byron', 'ballads', 'tennyson', 'emerson', 'blake',
                   'longfellow', 'holmes', 'wilde', 'et_al', 'tagore']

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
def stripTitle(s):
    s = s.replace('_','')
    while s.endswith('\n') or s.endswith(' ') or s.endswith('.') or s.endswith(';'):
        s = s[:-1]
    return s

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
        poem = poem.replace(" they 'd "," they'd ").replace(" you 'd "," you'd ")
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.lower()
        poem = poem.replace(" i 'd "," i'd ").replace(" he 'd "," he'd ")
        poem = poem.replace(" who 'll "," who'll ").replace(" they 'll"," they'll ")
        out.write(poem)
        print("title:", title)
        # print(poem)
    out.close()
def frost():
    text = getContents("data/frost-raw.txt")
    text = removeBrackets(text)
    index = getContents("data/frost-index.txt").split('\n')
    # print(index)
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
        print("title:", title)
        # print(poem)
    out.close()
def keats():
    text = getContents("data/keats-raw.txt")
    text = removeBrackets(text)
    index = getContents("data/keats-index.txt").split('\n')
    # print(index)
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
        poem = poem.replace("faery","fairy")
        if poem.rfind("footnotes:") != -1:
            poem = poem[:poem.rfind("footnotes:")]
        out.write(poem)
        print("title: "+title.upper())
        # print(poem)
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
    # print(index)
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
        # print(poem)
    out.close()
def shelley():
    text = getContents("data/shelley-raw.txt")
    text = removeBrackets(text)
    text = text.replace('\x0a','\n').replace('\x0d','')
    index = getContents("data/shelley-index.txt").split('\n')
    # print(index)
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
        title = stripTitle(title)
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.replace('\n', NEWLINE)
        poem = poem.lower()
        if poem.rfind("notes;") != -1:
            poem = poem[:poem.rfind("notes;")]
        if poem.rfind("notes:") != -1:
            poem = poem[:poem.rfind("notes:")]
        if poem.rfind(NEWLINE.lower()+"note:") != -1:
            poem = poem[:poem.rfind(NEWLINE.lower()+"note:")]
        out.write(poem)
        print("title: "+title.upper())
        # print(poem)
    out.close()
def byron():
    text = getContents("data/byron-raw.txt")
    text += getContents("data/byron-raw-harold.txt")
    don_juan = getContents("data/byron-raw-juan.txt")
    don_juan = don_juan.replace("CANTO THE FIRST","DON JUAN CANTO THE FIRST")
    don_juan = don_juan.replace("CANTO THE SECOND","DON JUAN CANTO THE SECOND")
    don_juan = don_juan.replace("CANTO THE THIRD","DON JUAN CANTO THE THIRD")
    text += don_juan
    text = text.replace('\x0a','\n').replace('\x0d','')
    text = text.replace(' [', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = text.replace('\n[', '[')
    text = removeBrackets(text)
    index = getContents("data/byron-index.txt").upper().split('\n')
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
        if endtitle >= next:
            next = text.find('\n'*4, endtitle+1)
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
        title = stripTitle(title)
        poem = TITLE + title + NEWLINE + poem + NEWLINE
        poem = poem.replace('\n\n\n','\n\n')
        poem = poem.replace('\n', NEWLINE)
        poem = poem.lower()
        if poem.rfind("notes;") != -1:
            poem = poem[:poem.rfind("notes;")]
        if poem.rfind("notes:") != -1:
            poem = poem[:poem.rfind("notes:")]
        if poem.rfind("\nnote:") != -1:
            poem = poem[:poem.rfind("\nnote:")]
        poem = poem.replace("childe", "child")
        out.write(poem)
        print("title:",title)
        # print(poem)
    out.close()
def ballads():
    text = getContents("data/ballads-raw.txt")
    text = text.replace('\x0a','\n').replace('\x0d','')
    index = getContents("data/ballads-index.txt").replace('  ','').split('\n')
    out = open("data/ballads.txt", "w+")
    titles = {"a conversational poem": "the nightingale",
              "the tables turned; an evening scene, on the same subject": "the tables turned",
              "old man travelling": "old man travelling",
              "lines written a few miles above tintern abbey": "on revisiting the banks",
              "lines written at a small distance from my house, and sent": "",
              "lines written near richmond, upon the thames, at evening": "upon the thames at evening",
              "lines written in early spring": "early spring",
              "lines left upon a seat in a yew-tree which stands near the lake": "a yew tree",
              "the rime of the ancyent marinere": "the rhyme of the ancient mariner",
              "simon lee, the old huntsman": "the old huntsman",
              "anecdote for fathers": "anecdote for fathers",
              "don juan canto the first": "canto the first",
              "don juan canto the second": "canto the second",
              "don juan canto the third": "canto the third"}
    for heading in index:
        this = text.find(heading.upper())
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        endtitle = text.find('\n\n',this+1)
        while text[endtitle] == '\n' or text[endtitle] == '.':
            endtitle += 1
        if heading.lower() in titles:
            title = titles[heading.lower()]
        else:
            title = text[this:endtitle]
        title = stripTitle(title)
        if heading == 'the thorn':
            next = text.find('THE LAST OF THE FLOCK', this+1)
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(' '):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if isRomanNumeral(poem[i][:-1]) and poem[i][-1] == '.':
                if poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            elif isNumeral(poem[i]):
                poem.pop(i)
        if heading.lower() == "the rime of the ancyent marinere":
            poem.pop(0)
            poem.pop(0)
        poem = '\n'.join(poem)
        poem = poem.lower()
        poem = poem.replace('contrée','country').replace('countrée','country')
        poem = poem.replace('\n\n\n','\n\n')
        if heading.lower() == "the rime of the ancyent marinere":
            poem = poem[poem.find("i."):]
            poem = poem.replace('ancyent','ancient').replace('marinere','mariner')
            poem = poem[3:]
        if heading.lower() == "the complaint of a forsaken indian woman":
            poem = removeBrackets(poem)
        else:
            notes = poem.count('[')
            for i in range(notes//2):
                poem = poem[:poem.rfind('[')]
            poem = removeBrackets(poem)
        while poem.startswith('\n'):
            poem = poem[1:]
        while poem.endswith('\n') or poem.endswith(' '):
            poem = poem[:-1]
        print("title: " + title.upper())
        # print("poem: "+poem)
        poem = poem.replace('\n',NEWLINE)
        poem = TITLE + title + NEWLINE + poem
        poem = poem.lower()
        out.write(poem)
    out.close()
def tennyson():
    text = getContents("data/tennyson-raw.txt")
    text = text.replace('\x0a','\n').replace('\x0d','')
    index = getContents("data/tennyson-index.txt").split('\n')
    out = open("data/tennyson.txt", "w+")
    titles = {"AN IDYL": "THE BROOK",
              "THE DUKE OF WELLINGTON": "ODE ON THE DEATH OF THE DUKE OF WELLINGTON",
              "WRITTEN AT EDINBURGH": "THE DAISY",
              "CHARGE OF THE LIGHT BRIGADE": "THE CHARGE OF THE LIGHT BRIGADE"}
    skipindex = text.find("BRIGADE")
    for heading in index:
        this = text.find(heading.upper(), skipindex)
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        endtitle = text.find('\n\n',this+1)
        while text[endtitle] == '\n' or text[endtitle] == '.':
            endtitle += 1
        if heading in titles:
            title = titles[heading]
        else:
            title = text[this:endtitle]
        title = stripTitle(title)
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(' '):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if isRomanNumeral(poem[i][:-1]) and poem[i][-1] == '.':
                if poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            elif isNumeral(poem[i][:-1]) and poem[i][-1] == '.':
                poem.pop(i)
        if heading == "TO THE REV. F. D. MAURICE":
            poem.pop()
            poem.pop()
        poem = '\n'.join(poem)
        poem = poem.lower()
        poem = poem.replace("' d", "'d")
        while poem.startswith('\n'):
            poem = poem[1:]
        while poem.endswith('\n') or poem.endswith(' '):
            poem = poem[:-1]
        print("title: " + title.upper())
        # print("poem: "+poem)
        poem = poem.replace('\n',NEWLINE)
        poem = poem.replace("vext","vexed").replace("perplext","perplexed")
        poem = TITLE + title + NEWLINE + poem
        poem = poem.lower()
        out.write(poem)
    out.close()
def emerson():
    text = getContents("data/emerson-raw.txt")
    text = text.replace('\x0a','\n').replace('\x0d','')
    index = getContents("data/emerson-index.txt").split('\n')
    index.append("\nBEAUTY\n")
    index.append("\nNATURE\nI")
    out = open("data/emerson.txt", "w+")
    skipindex = text.find("INDEX OF TITLES")
    titles = {"READ IN MUSIC HALL, JANUARY 1, 1863": "BOSTON HYMN",
              "SICUT PATRIBUS, SIT DEUS NOBIS": "BOSTON",
              "PORTO RICO, IN 1832": "THE LAST FAREWELL",
              "HER MARRIAGE TO MR. EMERSON": "",
              "BY ELLEN LOUISA TUCKER": "THE VIOLET",
              "CONCORD, 1838": "DIRGE",
              "MONUMENT, JULY 4, 1837": "CONCORD HYMN",
              "OF REV. CHANDLER ROBBINS": "HYMN",
              "\nBEAUTY\n": "BEAUTY",
              "\nNATURE\nI": "NATURE"}
    for heading in index:
        this = text.find(heading.upper(), skipindex)
        next = text.find('\n'*4, this+1)
        if this == -1 or next == -1:
            continue
        endtitle = text.find('\n\n',this+1)
        while text[endtitle] == '\n' or text[endtitle] == '.':
            endtitle += 1
        title = text[this:endtitle]
        title = stripTitle(title)
        if heading in titles:
            title = titles[heading]
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(' '):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if isRomanNumeral(poem[i][:-1]) and poem[i][-1] == '.':
                if poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            elif poem[i].endswith('.') and (isNumeral(poem[i][:-1]) or isNumeral(poem[i][-5:-1])):
                poem.pop(i)
            elif len(poem[i]) > 0:
                stars = poem[i].replace(" ","")
                if stars.count("*") == len(stars):
                    poem.pop(i)
        poem = '\n'.join(poem)
        poem = poem.lower()
        while poem.startswith('\n'):
            poem = poem[1:]
        while poem.endswith('\n') or poem.endswith(' '):
            poem = poem[:-1]
        print("title: " + title.upper())
        # print("poem: "+poem)
        poem = poem.replace('\n',NEWLINE)
        poem = poem.replace("reënter","reenter")
        poem = TITLE + title + NEWLINE + poem
        poem = poem.lower()
        out.write(poem)
    out.close()
def blake():
    text = getContents("data/blake-raw.txt")
    text = text.replace('\x0a','\n').replace('\x0d','')
    index = getContents("data/blake-index.txt").split('\n')
    index.append("THEL\n\n  I")
    out = open("data/blake.txt", "w+")
    for heading in index:
        this = text.find(heading)
        next = text.find('\n'*3, this+1)
        if heading == "THEL\n\n  I":
            next = text.find('\n'*5, this+1)
        if this == -1 or next == -1:
            continue
        endtitle = text.find('\n\n',this+1)
        while text[endtitle] == '\n' or text[endtitle] == '.':
            endtitle += 1
        title = text[this:endtitle]
        title = stripTitle(title)
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.lower()
        if heading == "THE VOICE OF THE ANCIENT BARD":
            poem = poem[:poem.rfind("appendix")]
        if heading == "THEL\n\nI":
            poem = poem.replace("II.\n","").replace("III.\n","")
        poem = poem.replace("  "," ").replace("\n    ","\n").replace("\n   ","\n").replace("\n  ","\n")
        while poem.startswith('\n') or poem.startswith(' '):
            poem = poem[1:]
        while poem.endswith('\n') or poem.endswith(' '):
            poem = poem[:-1]
        print("title: " + title.upper())
        # print("poem: "+poem)
        poem = poem.replace('\n',NEWLINE)
        poem = poem.replace('&', 'and').replace('ceasd','ceased').replace('smild','smiled')
        poem = TITLE + title + NEWLINE + poem
        poem = poem.lower()
        poem = poem.replace("tyger","tiger")
        out.write(poem)
    out.close()
def longfellow():
    text = getContents("data/longfellow-raw.txt")
    index = getContents("data/longfellow-index.txt").split('\n')
    text = text.replace('\x0a','\n').replace('\x0d','')
    index.append("INTERLUDE 2")
    index.append("INTERLUDE 3")
    index.append("INTERLUDE 4")
    index.append("INTERLUDE 5")
    index.append("INTERLUDE 6")
    out = open("data/longfellow.txt", "w+")
    skipindex = text.find("224\n")
    int_1 = text.find("INTERLUDE",skipindex)
    int_2 = text.find("INTERLUDE",int_1+1)
    int_3 = text.find("INTERLUDE",int_2+1)
    int_4 = text.find("INTERLUDE",int_3+1)
    int_5 = text.find("INTERLUDE",int_4+1)
    for heading in index:
        this = text.find(heading, skipindex)
        if heading == "INTERLUDE 2":
            this = text.find("INTERLUDE", int_1+1)
        elif heading == "INTERLUDE 3":
            this = text.find("INTERLUDE", int_2+1)
        elif heading == "INTERLUDE 4":
            this = text.find("INTERLUDE", int_3+1)
        elif heading == "INTERLUDE 5":
            this = text.find("INTERLUDE", int_4+1)
        elif heading == "INTERLUDE 6":
            this = text.find("INTERLUDE", int_5+1)
        if heading.startswith("INTERLUDE"):
            heading = "INTERLUDE"
        if heading == heading.upper():
            next = text.find('\n'*4, this+1)
        else:
            next = text.find('\n'*3, this+1)
        heading = heading.upper()
        if this == -1 or next == -1:
            continue
        endtitle = text.find('\n\n',this+1)
        while text[endtitle] == '\n' or text[endtitle] == '.':
            endtitle += 1
        title = heading
        title = stripTitle(title)
        poem = text[endtitle:next]
        if heading == "WEARINESS":
            poem = poem[:poem.rfind("THE END.")]
        if poem.endswith('.') and isNumeral(poem[-5:-1]):
            poem = poem[:-5]
        poem = poem.replace('_','')
        poem = poem.lower()
        poem = poem.replace("  "," ").replace("\n    ","\n").replace("\n   ","\n").replace("\n  ","\n").replace("\n ","\n")
        while poem.startswith('\n') or poem.startswith(' '):
            poem = poem[1:]
        while poem.endswith('\n') or poem.endswith(' '):
            poem = poem[:-1]
        print("title: " + title.upper())
        # print("poem: "+poem)
        poem = poem.replace('\n',NEWLINE)
        poem = TITLE + title + NEWLINE + poem
        poem = poem.replace("snow-flake","snowflake")
        poem = poem.lower()
        out.write(poem)
    out.close()
def holmes():
    text = getContents("data/holmes-raw.txt")
    text = text.replace('\x0a','\n').replace('\x0d','')
    text = removeBrackets(text)
    index = getContents("data/holmes-index.txt").split('\n')
    out = open("data/holmes.txt", "w+")
    text = text.replace("AT THE SATURDAY CLUB\nTHIS", "AT THE SATURDAY CLUB\n\nTHIS")
    text = text.replace("ALONE! no climber","Alone! no climber")
    text = text.replace("ALONE, beneath the","Alone, beneath the")
    skipindex = text.find("TO MY READERS")
    skipindex = text.find("TO MY READERS",skipindex+1)
    for heading in index:
        true_title = None
        if heading.find(" (") != -1:
            true_title = heading[heading.find(" (")+2:heading.find(")")]
            heading = heading[:heading.find(" (")]
        this = text.find(heading, skipindex)
        if text.find(heading,this+1) != -1:
            this = text.find(heading,this+1)
        next = text.find('\n'*3, this+1)
        if this == -1 or next == -1:
            continue
        endtitle = text.find('\n\n',this+1)
        while text[endtitle] == '\n' or text[endtitle] == '.':
            endtitle += 1
        title = text[this:endtitle]
        title = stripTitle(title)
        if true_title is not None:
            title = true_title
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(' '):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if isRomanNumeral(poem[i][:-1]) and poem[i][-1] == '.':
                if poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            elif poem[i].endswith('.') and (isNumeral(poem[i][:-1]) or isNumeral(poem[i][-5:-1])):
                poem.pop(i)
            elif len(poem[i]) > 0:
                stars = poem[i].replace(" ","")
                if stars.count("*") == len(stars) or stars.count(".") == len(stars):
                    poem.pop(i)
        poem = '\n'.join(poem)
        poem = poem.lower()
        while poem.startswith('\n'):
            poem = poem[1:]
        while poem.endswith('\n') or poem.endswith(' '):
            poem = poem[:-1]
        poem = poem.replace(" 'd ","'d ").replace(" 'll ","'ll ").replace(" 're ","'re ")
        poem = poem.replace(" n't","n't").replace("sha'n't","shan't")
        print("title: " + title.upper())
        # print("poem: "+poem)
        poem = poem.replace('\n',NEWLINE)
        poem = TITLE + title + NEWLINE + poem
        poem = poem.lower()
        out.write(poem)
    out.close()
def wilde():
    text = getContents("data/wilde-raw.txt")
    text = text.replace('\x0a','\n').replace('\x0d','')
    text = removeBrackets(text)
    index = getContents("data/wilde-index.txt").split('\n')
    out = open("data/wilde.txt", "w+")
    skipindex = text.find("HÉLAS!")-5
    index.append("THE BALLAD OF READING GAOL\n\n\n                                      I")
    titles = {"HÉLAS!": "GREECE!",
              "URBS SACRA ÆTERNA": "THE ETERNAL SACRED CITY",
              "E TENEBRIS": "OUT OF THE DARKNESS",
              "VITA NUOVA": "NEW LIFE",
              "IMPRESSION DU MATIN": "IMPRESSION OF THE MORNING",
              "CHANSON": "SONG",
              "LES SILHOUETTES": "THE SILHOUETTES",
              "LA FUITE DE LA LUNE": "THE FLIGHT OF THE MOON",
              "(NORMANDE)": "NORMAN",
              "(BRETON)": "THE DOLE OF THE KING’S DAUGHTER",
              "SILENTIUM AMORIS": "THE SILENCE OF LOVE",
              "ΓΛΥΚΥΠΙΚΡΟΣ ΕΡΩΣ": "FLOWER OF LOVE",
              "TRISTITÆ": "SADNESS",
              "ITALIA": "ITALY",
              "LE JARDIN": "THE GARDEN",
              "LA MER": "THE SEA",
              "LES BALLONS": "THE BALLOONS",
              "DÉSESPOIR": "DESPAIR",
              "THE BALLAD OF READING GAOL\n\n\n                                      I": "THE BALLAD OF READING JAIL",
    }
    for heading in index:
        this = text.find(heading, skipindex)
        next = text.find('\n'*3, this+1)
        if this == -1 or next == -1:
            continue
        endtitle = text.find('\n\n',this+1)
        while text[endtitle] == '\n' or text[endtitle] == '.' or text[endtitle] == ' ':
            endtitle += 1
        title = text[this:endtitle]
        title = stripTitle(title)
        if heading in titles:
            title = titles[heading]
        next = text.find('\n'*3, endtitle+1)
        poem = text[endtitle:next]
        poem = poem.replace('_','')
        poem = poem.split('\n')
        for i in reversed(range(len(poem))):
            while poem[i].startswith(' '):
                poem[i] = poem[i][1:]
            while poem[i].endswith(" "):
                poem[i] = poem[i][:-1]
            if (isRomanNumeral(poem[i][:-1]) and poem[i][-1] == '.') or isRomanNumeral(poem[i]) and poem[i]:
                if poem[i+1] == '':
                    poem.pop(i+1)
                poem.pop(i)
                continue
            elif poem[i].endswith('.') and (isNumeral(poem[i][:-1]) or isNumeral(poem[i][-5:-1])):
                poem.pop(i)
            elif len(poem[i]) > 0:
                stars = poem[i].replace(" ","")
                if stars.count("*") == len(stars) or stars.count(".") == len(stars):
                    poem.pop(i)
        poem = '\n'.join(poem)
        poem = poem.lower()
        while poem.startswith('\n'):
            poem = poem[1:]
        while poem.endswith('\n') or poem.endswith(' '):
            poem = poem[:-1]
        print("title: " + title.upper())
        # print("poem: "+poem)
        poem = poem.replace('\n',NEWLINE)
        poem = TITLE + title + NEWLINE + poem
        poem = poem.lower()
        out.write(poem)
    out.close()
def et_al():
    out = open("data/et_al.txt", "w+")
    def main_processing(text, index_file, skipindex=1, use_second=False, ending_newlines=3, remove_last=False):
        text = text.replace('\x0a','\n').replace('\x0d','')
        text = text.replace('\n\n[Illustration:','[')
        text = removeBrackets(text)
        index = getContents(index_file).split('\n')
        nonlocal out
        for heading in index:
            true_title = None
            if heading.find(" (") != -1:
                true_title = heading[heading.find(" (")+2:heading.find(")")]
                heading = heading[:heading.find(" (")]
            this = text.find(heading, skipindex)
            if use_second:
                this = text.find(heading,this+1)
            next = text.find('\n'*ending_newlines, this+1)
            if this == -1 or next == -1:
                continue
            endtitle = text.find('\n\n',this+1)
            while text[endtitle] == '\n' or text[endtitle] == '.':
                endtitle += 1
            title = text[this:endtitle]
            title = stripTitle(title)
            if true_title is not None:
                title = true_title
            poem = text[endtitle:next]
            poem = poem.replace('_','')
            poem = poem.split('\n')
            for i in reversed(range(len(poem))):
                while poem[i].startswith(' '):
                    poem[i] = poem[i][1:]
                while poem[i].endswith(" "):
                    poem[i] = poem[i][:-1]
                if isRomanNumeral(poem[i][:-1]) and poem[i][-1] == '.':
                    if poem[i+1] == '':
                        poem.pop(i+1)
                    poem.pop(i)
                    continue
                elif poem[i].endswith('.') and (isNumeral(poem[i][:-1]) or isNumeral(poem[i][-5:-1])):
                    poem.pop(i)
                elif len(poem[i]) > 0:
                    stars = poem[i].replace(" ","")
                    if stars.count("*") == len(stars) or stars.count(".") == len(stars):
                        poem.pop(i)
            poem = '\n'.join(poem)
            if heading == 'FIRST PART.' and poem.rfind("SECOND PART.") != -1:
                poem = poem[:poem.rfind("SECOND PART.")]
            elif heading == 'THIRD PART.' and poem.rfind("FOURTH PART.") != -1:
                poem = poem[:poem.rfind("FOURTH PART.")]
            if poem.rfind("FOOTNOTES:") != -1:
                poem = poem[:poem.rfind("FOOTNOTES:")]
            poem = poem.lower()
            while poem.startswith('\n'):
                poem = poem[1:]
            while poem.endswith('\n') or poem.endswith(' '):
                poem = poem[:-1]
            print("title: " + title.upper())
            # print("poem: "+poem)
            poem = TITLE + title + NEWLINE + poem
            if remove_last:
                poem = poem[:poem.rfind('\n')]
            poem = poem.replace('\n',NEWLINE)
            poem = poem.lower()
            poem = poem.replace("faery","fairy").replace("faeries","fairies")
            out.write(poem)
    
    vol4 = getContents("data/browning-raw-iv.txt")
    vol4 = vol4[vol4.find("A CHILD'S GRAVE AT FLORENCE."):]
    vol2 = getContents("data/browning-raw-ii.txt")
    vol2 = vol2[vol2.find("POEMS"):]
    browning = vol4 + vol2
    yeats = getContents("data/yeats-raw.txt")
    modern = getContents("data/modern-raw.txt")
    modern = modern[modern.find("LASCELLES ABERCROMBIE"):modern.rfind("INDEX")]
    bryant = getContents("data/bryant-raw.txt")
    bryant = bryant.replace('°','').replace('º','')
    bryant = bryant[bryant.find("THE AGES."):]
    whittier = getContents("data/whittier-raw.txt")
    whittier = whittier[whittier.find("NOTES"):]
    iliad = getContents("data/iliad-raw.txt")
    iliad_illustrations = getContents("data/iliad-illustrations.txt")
    for illustration in iliad_illustrations.split('\n'):
        iliad = iliad.replace(illustration+'\n','')

    main_processing(browning, "data/browning-index.txt", use_second=True)
    main_processing(yeats, "data/yeats-index.txt", use_second=True)
    main_processing(modern, "data/modern-index.txt", ending_newlines=4)
    main_processing(bryant, "data/bryant-index.txt", ending_newlines=4)
    main_processing(whittier, "data/whittier-index.txt", remove_last=True)
    main_processing(iliad, "data/iliad-index.txt", ending_newlines=4)
    out.close()
def tagore():
    gitanjali = getContents("data/tagore-raw-gitanjali.txt")
    gitanjali = gitanjali[gitanjali.find("1."):gitanjali.rfind("END OF THE PROJECT GUTENBERG EBOOK")]
    gardener = getContents("data/tagore-raw-gardener.txt")
    gardener = gardener[gardener.find("2\n\n"):gardener.rfind("END OF THE PROJECT GUTENBERG EBOOK")]
    gardener = gardener.replace("\n ","\n").replace("\n  "," ")
    out = open("data/tagore.txt", "w+")
    def writePoem(text, start, end):
        nonlocal out
        poem = text[start:end].replace('\n',NEWLINE).replace('_','').lower()
        out.write(poem)
    for i in range(2, 85):
        this = gardener.find(str(i)+"\n\n\n")
        endtitle = this+len(str(i)+"\n\n\n")
        next = gardener.find("\n\n\n", endtitle+1)
        writePoem(gardener, endtitle, next)
    for i in range(1, 104):
        this = gitanjali.find(str(i)+".\n\n\n")
        endtitle = this+len(str(i)+".\n\n\n")
        next = gitanjali.find("\n\n\n", endtitle+1)
        writePoem(gitanjali, endtitle, next)
    out.close()
def shakespeare():
    text = getContents("data/shakespeare-raw.txt")
    text = text[text.find("From fairest creatures"):text.rfind("water cools not love.")+21]
    text = text.split('\n')
    for i in reversed(range(len(text))):
        while text[i].startswith(' '):
            text[i] = text[i][1:]
        while text[i].endswith(" "):
            text[i] = text[i][:-1]
        if isRomanNumeral(text[i]):
            text[i] = TITLE
            text.pop(i+1)
    text = NEWLINE.join(text)
    text = TITLE + NEWLINE + text
    text = text.replace(NEWLINE+TITLE, TITLE)
    text = text.lower()
    text = text.replace("’gainst","against").replace("’fore","before").replace("bett’r","better")
    text = text.replace("’st ","est ")
    out = open("data/shakespeare.txt", "w+")
    out.write(text)
    out.close()

def join(kaggle=False):
    text = ''
    for author in (AUTHOR_LIST if not kaggle else AUTHOR_LIST + ['kaggle']):
        text += getContents("data/"+author+".txt")
    print("Processing punctuation and special tokens")
    text = text.lower()
    text = text.replace("’","'").replace("‘","'").replace('“','"').replace('”','"')
    text = text.replace("—-", "--").replace("–","-").replace("—","--")
    text = text.replace("…","...")
    text = text.replace(" .",".").replace(" ,",",").replace("."," . ").replace(","," , ")
    text = text.replace(" :",":").replace(" ;",";").replace(":"," : ").replace(";"," ; ")
    text = text.replace(" !","!").replace(" ?","?").replace("!"," ! ").replace("?"," ? ")
    text = text.replace(NEWLINE.lower()[:-1]+NEWLINE.lower()[1:], NEWLINE.lower())
    text = text.replace("><", "> <")
    text = text.replace('>','> ')
    text = text.replace("    ", " ").replace("  ", " ").replace("  ", " ")
    text = text.replace(" -","-").replace("- ","-").replace("-"," - ")
    text = text.replace(' "','"').replace('" ','"').replace('"',' " ')
    text = text.replace("&"," and ")
    PROCESS_MORPHEMES = True
    if PROCESS_MORPHEMES:
        print("Processing specific morphemes")
        text = text.replace("o'er","over").replace("e'er","ever").replace("thro'","through").replace("e'en","even")
        text = text.replace("ev'n","even").replace("fall'n","fallen").replace("heav'n","heaven")
        text = text.replace("deep'ning","deepening").replace("stol'n","stolen").replace("revery","reverie")
        text = text.replace(" tho' ", " though ").replace(" altho' "," although ").replace(" 'mid "," amid ")
        text = text.replace("ev'ry","every").replace("wond'rous","wonderous").replace("fev'rous","feverous")
        text = text.replace("whisp'ring","whispering").replace("thund'rous","thunderous").replace("minist'ring","ministering")
        text = text.replace("slumb'ring","slumbering").replace("rememb'ring","remembering").replace("flow'rs","flowers")
        text = text.replace(" flatt'r"," flatter").replace("wand'ring","wandering").replace("mould'ring","mouldering")
        text = text.replace("murm'ring","murmuring").replace(" ta'en "," taken ").replace(" wa'n't "," wasn't ")
        text = text.replace("orat'ries","oratories").replace("falt'ring","faltering").replace("imag'ries","imageries")
        text = text.replace(" practise"," practice").replace(" gaol "," jail ").replace(" dropt "," dropped ")
        text = text.replace("æ","ae").replace("œ","oe").replace("deathbed","death - bed")
        text = text.replace(" th'", " the").replace("i 'm", "i'm").replace("'t is", "it is")
        text = text.replace("'tis", "it is").replace("'twould", "it would").replace(" it 's ", " it's ")
        text = text.replace(" is't "," is it ").replace(" 'twill "," it will ")
        text = text.replace(" 'twas ", " it was ").replace(" 'twere ", " it were ").replace(" 'twould "," it would ")
        text = text.replace(" twas "," it was ").replace(" twere "," it were ").replace(" twould "," it would ").replace(" twill "," it will ")
        text = text.replace("èd ","ed ").replace("alarum","alarm")
        text = text.replace(" i'll "," i LL ").replace(" thou'lt "," thou LT ").replace(" we'll "," we LL ")
        text = text.replace(" he'll "," he LL ").replace(" she'll "," she LL ").replace(" it'll "," it LL ")
        text = text.replace(" they'll "," they LL ").replace(" you'll "," you LL ").replace(" who'll "," who LL ")
        text = text.replace("'ll "," LL ")
        text = text.replace(" i'd "," ID ").replace(" we'd "," WED ").replace(" he'd "," HED ").replace(" she'd "," SHED ").replace(" you'd "," YOUD ")
        text = text.replace("don't", "do NT").replace("wouldn't","would NT").replace("isn't", "is NT").replace("aren't","are NT")
        text = text.replace("doesn't","does NT").replace("won't","will NT").replace("shouldn't","should NT").replace("couldn't","could NT")
        text = text.replace("can't","can NT").replace("shan't","shall NT").replace(" didn't "," did NT ").replace("wasn't","was NT")
        text = text.replace("hasn't","has NT").replace("haven't","have NT").replace("weren't","were NT").replace("hadn't","had NT")
        text = text.replace("needn't","need NT").replace("mayn't","may NT").replace(" ain't "," ai NT ").replace(" musn't "," must NT ")
        text = text.replace("'s", " S").replace("'m "," M ").replace("'ve"," VE").replace("'re"," RE").replace("'rt", " art ")
        text = text.replace("'d ", "ed ")
        text = text.replace(" '","'").replace("' ","'").replace("'"," ' ")
        text = text.replace(" ID "," i 'd ").replace("WED","we 'd").replace("HED","he 'd").replace("SHED","she 'd").replace("YOUD","you 'd")
        text = text.replace("NT","=nt").replace("S", "'s").replace("M","'m").replace("VE","'ve").replace("RE","'re")
        text = text.replace(" LL "," 'll ").replace(" LT "," 'lt ")
        text = text.replace("(","").replace(")","")
        text = text.replace("dying","die =ing").replace(" lying"," lie =ing")
        text = text.replace(" ings "," =ing =s ").replace(" NT "," =nt ")
        words = text.split(' ')
        print("Counting words")
        counts = {}
        for word in words:
            if not word in counts:
                counts[word] = 0
            counts[word] += 1
        words = list(counts.keys())
        words.sort(key=lambda word: counts[word], reverse=True)
        print("Counted", len(words), "words")
        s_dict = {}
        ed_dict = {}
        er_dict = {}
        est_dict = {}
        ing_dict = {}
        text = text.replace(" hopper ", " hop =er ").replace(" dispelled "," dispel =ed ").replace(" hopped "," hop =ed ")
        text = text.replace(" conjectured "," conjecture =ed ").replace(' sophistries ',' sophistry =s ').replace(' beads ',' bead =s ')
        text = text.replace(" halves "," half =s ").replace(" dyeing "," dye =ing ").replace(" singeing "," singe =ing ")
        text = text.replace(" selves "," self =s ").replace(" wolves "," wolf =s").replace(" wives "," wife =s ")
        s_dict['half'] = 'halves'; s_dict['self'] = 'selves'; s_dict['wolf'] = 'wolves'; s_dict['wife'] = 'wives'
        s_dict['sophistry'] = 'sophistries'
        er_dict['hop'] = 'hopper'; ed_dict['hop'] = 'hopped'
        ed_dict['dispel'] = 'dispelled'
        ing_dict['die'] = 'dying'; ing_dict['lie'] = 'lying'
        ing_dict['dye'] = 'dyeing'; ing_dict['singe'] = 'singeing'
        print("Processing general morphemes")
        for word in words[:10000]:
            if word != '' and word+'est' in counts and not word in est_set:
                text = text.replace(" "+word+"est "," "+word+" =est ")
            elif word != '' and word+word[-1]+"ed" in counts and not word in c_ed_set:
                ed_dict[word] = word+word[-1]+"ed"
                text = text.replace(" "+word+word[-1]+"ed", " "+word+" =ed ")
            elif word != '' and word[-1] == 'e' and word+'d' in counts and not word in d_set:
                text = text.replace(" "+word+"d "," "+word+" =ed ")
            elif word.endswith('y') and word[:-1]+"ied" in counts and not word in y_ed_set:
                ed_dict[word] = word[:-1]+"ied"
                text = text.replace(" "+word[:-1]+"ied "," "+word+" =ed ")
            if word != '' and word+word[-1]+"est" in counts and not word in c_est_set:
                est_dict[word] = word+word[-1]+"est"
                text = text.replace(" "+word+word[-1]+"est", " "+word+" =est ")
            elif word.endswith('y') and word[:-1]+'iest' in counts and not word in y_est_set:
                est_dict[word] = word[:-1]+"iest"
                text = text.replace(" "+word[:-1]+"iest "," "+word+" =est ")
            elif word != '' and word[-1] == 'e' and word+'st' in counts and not word in st_set:
                text = text.replace(" "+word+"st "," "+word+" =est ")
            if word != '' and word+word[-1]+"er" in counts and not word in c_er_set:
                er_dict[word] = word+word[-1]+"er"
                text = text.replace(" "+word+word[-1]+"er "," "+word+" =er ")
            elif word.endswith('e') and word+"r" in counts and not word in r_set:
                er_dict[word] = word+"r"
                text = text.replace(" "+word+"r "," "+word+" =er ")
            elif word.endswith('y') and word[:-1]+'ier' in counts and not word in y_er_set:
                er_dict[word] = word[:-1]+"ier"
                text = text.replace(" "+word[:-1]+"ier "," "+word+" =er ")
            if word+'s' in counts and not word in s_set and not word.endswith('s'):
                text = text.replace(" "+word+"s "," "+word+" =s ")
            elif word.endswith('y') and word[:-1]+"ies" in counts and not word in y_s_set:
                s_dict[word] = word[:-1]+"ies"
                text = text.replace(" "+word[:-1]+"ies "," "+word+" =s ")
            elif (word.endswith('s') or word.endswith('sh') or word.endswith('x') or word.endswith('ch'))\
                    and word+'es' in counts and not word+'e' in s_set:
                text = text.replace(" "+word+"es "," "+word+" =s ")
            if word+'ing' in counts and not word in ing_set:
                text = text.replace(" "+word+"ing "," "+word+" =ing ")
            elif word != '' and word+word[-1]+"ing" in counts and not word in c_ing_set:
                ing_dict[word] = word+word[-1]+"ing"
                text = text.replace(" "+word+word[-1]+"ing "," "+word+" =ing ")
            elif word != '' and word.endswith('e') and word[:-1]+'ing' in counts and not word in e_ing_set:
                ing_dict[word] = word[:-1]+"ing"
                text = text.replace(" "+word[:-1]+"ing ", " "+word+" =ing ")
        print("Processing regular forms")
        for word in words[:10000]:
            if word != '' and word+"ed" in counts and not word in ed_set:
                text = text.replace(" "+word+"ed "," "+word+" =ed ")
            if word != '' and word+"er" in counts and not word in er_set:
                text = text.replace(" "+word+"er ", " "+word+" =er ")
        for root in ['echo','hero','go','do','potato','tomato']:
            if not word.endswith('s') and not word.endswith('sh') and not word.endswith('x') and not word.endswith('ch'):
                s_dict[root] = root+"es"
            text = text.replace(" "+root+"es "," "+root+" =s ")
        for root in ['mimic','panic']:
            ing_dict[root] = root+"king"
            text = text.replace(" "+root+"king ", " "+root+" =ing ")
            ed_dict[root] = root+"ked"
            text = text.replace(" "+root+"ked "," "+root+" =ed ")
        print("Processing spelling and final fixes")
        for word in BRITISH_OUR:
            text = text.replace(" "+word[:-2]+"our "," "+word+" ")
        text = text.replace(' grey ',' gray ').replace(' phrenzy ',' frenzy ').replace(' metre ',' meter ').replace(' metres ',' meters ')
        text = text.replace(" ' t was "," it was ").replace(" ' t were "," it were ").replace(" ' t would "," it would ").replace(" ' t will "," it will ")
        text = text.replace(" to - morrow "," tomorrow ").replace(" to - day "," today ").replace(" to - night ", " tonight ")
        text = text.replace(" ope "," open ").replace(" stopt "," stop =ed ").replace(" wrapt "," wrap =ed ")
        text = text.replace(NEWLINE.lower()+' '+TITLE.lower(), TITLE.lower())
        text = text.replace(TITLE.lower() + ' ' + NEWLINE.lower()+' '+NEWLINE.lower(), TITLE.lower()+' '+NEWLINE.lower())
        text = text.replace("   ", " ").replace("  ", " ")
        text = text.replace("   ", " ").replace("  ", " ")
        text = text.replace("= ="," =")
        print("Saving lemmas")
        np.save('lemmas/s.npy', s_dict)
        np.save('lemmas/ed.npy', ed_dict)
        np.save('lemmas/er.npy', er_dict)
        np.save('lemmas/est.npy', est_dict)
        np.save('lemmas/ing.npy', ing_dict)
    else:
        text = text.replace(" '","'").replace("' ","'").replace("'"," ' ")
    for numeral in ['ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
                    'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii',
                    'xix', 'xx', 'xxi', 'xxii', 'xlv']:
        text = text.replace(' book '+numeral+NEWLINE.lower(),'')
        text = text.replace(' part '+numeral+NEWLINE.lower(),'')
        text = text.replace(' '+numeral+' .'+NEWLINE.lower(),'')
        text = text.replace(' '+numeral+NEWLINE.lower(),'')
    text = text.replace("><", "> <")
    print("Saving text")
    out = open("inputs/join.txt" if not kaggle else "inputs/join-kaggle.txt", "w+")
    out.write(text)
    out.close()

if __name__ == '__main__':
    shakespeare()
    tagore()
    dickinson()
    frost()
    keats()
    poe()
    shelley()
    byron()
    ballads()
    tennyson()
    emerson()
    blake()
    longfellow()
    holmes()
    wilde()
    et_al()

    join(KAGGLE)
