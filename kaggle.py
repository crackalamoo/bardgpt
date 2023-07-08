import pandas as pd
from preprocess import NEWLINE, TITLE, stripTitle

df = pd.read_csv('kaggle/PoetryFoundationData.csv')

out = open("data/kaggle.txt", 'w+')
text = ""
for index, row in df.iterrows():
    title = row['Title'].replace('\x0d','')
    poem = row['Poem'].replace('\x0d','')
    while title.startswith(' ') or title.startswith('\n'):
        title = title[1:]
    while title.endswith(' ') or title.endswith('\n'):
        title = title[:-1]
    title = stripTitle(title)
    while poem.startswith(' ') or poem.startswith('\n'):
        poem = poem[1:]
    while poem.endswith(' ') or poem.endswith('\n'):
        poem = poem[:-1]
    poem = poem.replace('\n',NEWLINE)
    poem = TITLE + title + NEWLINE + poem
    poem = poem.lower()
    #poem = poem.replace('\x0d\x0a','').replace('\x0a\x0d','')
    text += poem
text = text.replace('\x0d','').replace('_','').replace('\n',NEWLINE).replace(NEWLINE+'  ',NEWLINE).replace(NEWLINE+' ',NEWLINE)
out.write(text)
out.close()