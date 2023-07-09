# https://www.kaggle.com/datasets/tgdivy/poetry-foundation-poems
import pandas as pd
from preprocess import NEWLINE, TITLE, stripTitle

df = pd.read_csv('kaggle/PoetryFoundationData.csv')

out = open("data/kaggle.txt", 'w+')
text = ""
for index, row in df.iterrows():
    title = row['Title'].replace('\x0d','')
    poem = row['Poem'].replace('\x0d','').replace('\u200a',' ')
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
    poem = TITLE + title + NEWLINE + poem + NEWLINE
    poem = poem.lower()
    #poem = poem.replace('\x0d\x0a','').replace('\x0a\x0d','')
    text += poem

text = text.replace('\x0d','').replace('\u2028','\n').replace('\u2029','\n\n')
text = text.replace('\u00a0',' ').replace('\u0009',' ').replace('\u2002',' ')
text = text.replace('\u2003',' ').replace('\u2006',' ').replace('\u200b',' ')
text = text.replace('\u2060',' ').replace('\ufeff',' ')
text = text.replace('_','').replace('\n',NEWLINE).replace(NEWLINE+'  ',NEWLINE).replace(NEWLINE+' ',NEWLINE)
text = text.replace('[','').replace(']','').replace('\xa0',' ').replace('\u200a',' ').replace('\u2009',' ')
text = text.replace('•','').replace('//','\n')
text = text.encode('utf-8').decode('utf-8-sig')
out.write(text)
out.close()