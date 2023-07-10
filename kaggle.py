# https://www.kaggle.com/datasets/tgdivy/poetry-foundation-poems
import pandas as pd
from preprocess import NEWLINE, TITLE, stripTitle

df = pd.read_csv('kaggle/PoetryFoundationData.csv')

out = open("data/kaggle.txt", 'w+')
text = ""
remove_poets = set(['William Shakespeare', 'Emily Dickinson', 'Percy Bysshe Shelley',
            'William Blake', 'Edgar Allan Poe', 'John Keats', 'Ralph Waldo Emerson',
            'Alfred, Lord Tennyson', 'Lord Byron (George Gordon)', 'Henry Wadsworth Longfellow',
            'Oliver Wendell Holmes Sr.', 'Oscar Wilde', 'Elizabeth Barrett Browning',
            'William Butler Yeats', 'Rabindranath Tagore', 'Geoffrey Chaucer', 'William Langland',
            'John Lydgate'])

for index, row in df.iterrows():
    if 'John Gower' in row['Poet']:
        print(row['Poet'])
    if row['Poet'] in remove_poets:
        continue
    if row['Tags'] == row['Tags'] and 'sex' in row['Tags'].lower():
        continue
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
    if poem.count('\n') <= 2:
        continue
    poem = poem.replace('\n',NEWLINE)
    poem = TITLE + title + NEWLINE + poem + NEWLINE
    poem = poem.lower()
    text += poem

text = text.replace('\x0d','').replace('\u2028','\n').replace('\u2029','\n\n')
text = text.replace('\u00a0',' ').replace('\u0009',' ').replace('\u2002',' ')
text = text.replace('\u2003',' ').replace('\u2006',' ').replace('\u200b',' ')
text = text.replace('\u2060',' ').replace('\ufeff',' ').replace('\x0a','\n')
text = text.replace('\x0d\x0a','\n').replace('//','\n')
text = text.replace('_',' ').replace('\n',NEWLINE).replace(NEWLINE+'  ',NEWLINE).replace(NEWLINE+' ',NEWLINE)
text = text.replace('[','').replace(']','').replace('\xa0',' ').replace('\u200a',' ').replace('\u2009',' ')
text = text.replace('•','')
text = text.replace(' againe ',' again ').replace(' againe, ',' again, ').replace(' againe. ',' again. ')
text = text.replace('everie ','every ').replace(' sterne ',' stern ').replace(' soule ',' soul ')
text = text.replace('endles ','endless ').replace('beautie','beauty').replace(' obtaine ',' obtain ')
text = text.replace(' aire ',' air ').replace("pow'r","power").replace(' thru ',' through ').replace(' tho ',' though ')
text = text.replace('   ',' ').replace('  ',' ')
text = text.lower()
text = text.encode('utf-8').decode('utf-8-sig')
out.write(text)
out.close()