import eng_to_ipa as ipa
import re
TITLE = "*** "
NEWLINE = " \n"

def dickinson():
    file = open("data/dickinson-raw.txt", "r")
    text = file.read()
    file.close()
    while text.find('[') != -1:
        begin = text.find('[')
        end = text.find(']', begin+1)
        if end == -1:
            break
        else:
            text = text[:begin] + text[end+1:]
    index = open("data/dickinson-index.txt", "r").read()
    index = index.split('\n')
    out = open("data/dickinson.txt", "w+")
    for i in range(len(index)-1):
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
        out.write(poem)
        print(poem)
    out.close()

dickinson()