import eng_to_ipa as ipa

def shelley():
    file = open("data/shelley-raw.txt", "r")
    raw = file.read().replace('\n', " NEWLINE\n")
    file.close()
    print(raw)

shelley()