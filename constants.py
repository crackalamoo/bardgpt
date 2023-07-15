VOCAB_SIZE = 4096
NGRAM_N = 4
TRANSFORMER_N = 32
MODEL_TYPE = 'b' # n: ngram, t: transformer, b: bard
KAGGLE = False
TOKEN_SKIP = 1 if MODEL_TYPE == 'n' else (17 if KAGGLE else 3)

TITLE = " <TITLE> "
NEWLINE = " <NEWLINE> "

BRITISH_OUR = ['neighbor','color','flavor','splendor','labor','favor','fervor','savior','vapor','endeavor','parlor',
                     'clamor','harbor','splendor','behavior','rumor','humor','savor','valor','armor','honor','odor']

est_set = set(['for','t','n','liv','b','di','j','r','p','v','w','b','gu',
                            'l','eld','pr','inter','sever','hug','earn','smil',
                            'qu','ch','bl','conqu','pri'])
ed_set = set(['he','you','they','we','will','mov','w','wretch','fe','wav','gre',
                    'till','far','fell','de','b','f','l','re','hopp','ne','br',
                    'mann','bann','bl','pleas','mark','m','sh','se','spe','ble',
                    'lov','ste','rous','arm','bar','di','unmov','asham','cre'])
d_set = set(['be', 'she','we','see','re','fe','rowe','fee','le','seale','dee','ne',
                'reveale','traine','warme','coole','saile','sweate','mowe','cooke',
                'gree','warne','aire','seate','ree','temp','doome','helpe','feare',
                'neare','designe','adde','parte','repeate','gaine','parke','mourne',
                'backe','cleane','raine','charme','climbe','wee','fle','barbe','roote',
                'waite','fixe','hee','ende','wounde','pointe','earne','cree','matte',
                'kisse','haire','marke','neede','summe','farme','poure','owne','showe',
                'crowne','entere','evene','turne','crouche','laye','jade','recorde',
                'flowe','looke','nee','calle','learne','spe','ble','fille','washe',
                'boxe','talke','returne','sacre','dreame','pulle','seeme','calle',
                'prie','forme','ruine','lighte','appeare','adorne','aske','locke',
                'crosse','misse','arme','towe','shoute','heade','burne','faile','bowe',
                'rolle','walke','heape','obtaine'])
c_ed_set = set(['ad','cares','jag','pis','kis','mat','er','mis','cal','pas','fil'])
y_ed_set = set(['drapery','city','weary'])
s_set = set(['','a','i','it','his','her',"'",'their','one','will','your','our','down','pant','wa',
                    'god','well','other','saw','good','new','ye','leave','right','wood',
                    'ha','thi','hi','jesu','riche','specie','alway','ala','grasse','glorie',
                    'goe','doe','mas','pis','mi','pi','selve','wherea','prie','masse',
                    'beautie','jame','misse','san','la','lo','politic','u','ga','bu','tos',
                    'len'])
st_set = set(['be','we','ne','re','tempe','le','mode', 'fore','le','que','riche','cre','pe',
                'harde','sweete','cleane','je','te','che','highe','earne','deepe','meane','prie',
                'olde'])
c_est_set = set(['ful','smal'])
er_set = set(['with','she','h','quak','curr','hopp','minist','eth','thund','whisp','whit',
            'fev','rememb','inn','rend','de','beak','wand','port','heath','clos','should',
            'wrapp','cap','cow','lett','moth','chart','prop','danc','dinn','slumb','tend',
            'sever','ladd','falt','eld','aft','hind','flatt','murd','show','flow','sob',
            'pray','s','numb','pond','ev','und','wint','shiv','ang','fin','hov','teach',
            'clov','ov','oth','riv','barb','post','nev','discov','wat','draw','wait',
            'suff','deliv','quiv','silv','cov','shelt','los','m','slipp','batt','plast',
            'bitt','p','be','pe','ti','pi','ve','se','us','ton','min','sew','lit','tig',
            'lat','inn','out','off','ent','low','pow','less','wond','mann','care','lov',
            'rath','form','summ','bett','found','quart','tap','pap','record','shudd',
            'shatt','tatt','rid','butt','mis','bould','bord','glimm','answ','wav','walk',
            'glitt','gath','stick','care','temp','fish','corn','flick','dress','feath','met',
            'broth','both','lock','tow','conqu','che','encount','head','alt','mutt','san'])
c_er_set = set(['of','in','but','up','man','let','shut','sum','slip','din','flit',
            'mat','bat','bit','lad','ban','bet','ad','flat','pe','ful','smal','up',
            'pis','kis','slip','lat','cop','begin','shud','washe','shat','tat','lit',
            'glim','lay','lad','cal','glit','pas','fil','ham','sup','pep','rub','chat',
            'skip','alte','flut','mut','scat','dip','stag'])
r_set = set(['he',"'re",'rule','cottage','quake','cove','clove','warble','prime','lowe',
                'cape','tempe','late','e','rive','dee','eve','wave','me','rathe','meter',
                'anothe','mothe','mowe','sweate','saile','leade','hithe','warme','coole',
                'reaveale','traine','chee','manne','shee','uppe','withe','designe','neare',
                'barbe','darke','banne','pete','faste','soone','oute','rende','parke',
                'keepe','lee','rooste','cleane','sweete','bothe','harde','sleepe','poste',
                'loude','climbe','flowe','drawe','waite','highe','lathe','summe','fathe',
                'cove','farme','lose','showe','deepe','longe','hove','teache','pe','rule',
                'freeze','compute','consume','recorde','fille','washe','boxe','talke',
                'spide','meane','outside','inside','laye','lighte','reade','ladde',
                'eage','forme','coppe','answe','aske','dinne','wave','glitte','feve',
                'butte','gathe','pape','broke','matte','time','locke','olde','towe','inne',
                'shoute','heade','cunne','burne','singe','mutte','rolle','dippe','walke'])
ing_set = set(['','us','s','st','n','wan','din','k','heav','w','morn','cloth','br','wav',
                'even','cl','noth','charm','th','spr','bl','p','r','d','tempt','m','s','z',
                'ch','mean','exact','bless','train','lov','str','build','pleas','slid','light',
                'stock','feel','bo','gap'])
c_ing_set = set(['er','wed','ad','ear','begin','pis','kis','er','mis','cal','pas','fil'])
e_ing_set = set(['the','we','bee','bore','lute','ne','re','please','displease','tide','clothe','ke',
                    'neare','wounde','che','feare','doome','helpe','designe','evene','dye',
                    'adde','parte','repeate','gaine','parke','mourne','backe','cleane','charme',
                    'climbe','waite','fixe','raine','ende','wounde','pointe','earne','neede',
                    'summe','poure','owne','crowne','entere','turne','crouche','ble','laye',
                    'recorde','flowe','calle','morne','learne','fille','washe','boxe','talke',
                    'kisse','returne','dreame','pulle','seeme','matte','forme','meane','ruine',
                    'lighte','reade','appeare','adorne','stocke','aske','locke','calle','crosse',
                    'misse','towe','shoute','feele','heade','burne','singe','faile','bowe',
                    'rolle','walke','heape','obtaine'])
y_s_set = set(['ry'])
y_er_set = set(['by'])
y_est_set = set(['pry'])

BANNED_TOKENS = ['1','2','3','y','e','l','maud','olaf','lorenzo','de','oscar',
                 'r','d','f','p','agnes','eulalie','kate','niam','thel',
                 '+++++++++++++','c','j','h','4','5','6','7','8','9','10',
                 '11','12','*','x','b','/','k','g','ii','s','u','da','el',
                 'le','que','~','000','m','thu','thir','13','14','15','16','17',
                 '18','19','20','30','th','bu','ri','w','v','al','iv','wi',
                 'la','las','t','ma','ha','mee','ne','em','ry','di','st',
                 'yr','ful','iii','bo','faire','tos','ai','en','et','sug',
                 'ga','wel','hee','hon','n','wan','ut','te','ad','hym','na']
PUNCT = set(['.', ',', '!', '?', ':', ';', '-'])
VOWELS = set(['a','e','i','o','u'])
SOMETIMES_VOWELS = VOWELS.union(['y','w'])

DEFINED_RHYMES = {
    "'ll": [4,1], "=er": [13,0], "the": [4,-1], 'a': [4,-1], 'we': [8,-1], 'ye': [8,-1], 'e': [8,-1],
    'zimbabwe': [7,-1], 'one': [4,2], 'two': [11,-1], 'oh': [10,-1], 'ah': [12,-1], 'i': [9,-1],
    'you': [11,-1], 'own': [10,2], 'know': [10,-1], 'do': [11,-1], 'upon': [3,2], 'whereon': [3,2],
    'world': [13,4], 'learn': [13,2], 'earn': [13,2], 'yearn': [13,2], 'of': [4,5], 'service': [4,6],
    'practice': [4,6], 'police': [8,6], 'through': [11,-1], 'tough': [4,5], 'enough': [4,5],
    'thorough': [10,-1], 'dough': [10,-1], 'rough': [4,5], 'cough': [3,5], 'snow': [10,-1],
    'w': [11,-1], 'walk': [3,7], 'talk': [3,7], 'son':[4,2], 'iron': [13,2], 'anon': [3,2],
    'full': [11,1], 'pull': [11,1], 'bull': [11,1], 'put': [11,1], 'push': [11,6], 'book': [11,7],
    'won': [4,2], 'what': [4,4], 'who': [11,-1], 'whose': [11,6], 'where': [7,0], 'there': [7,0],
    'their': [7,0], 'theirs': [7,6], 'bear': [7,0], 'wear': [7,0], 'show': [10,-1], 'tow': [10,-1],
    'sow': [10,-1], 'brow': [5,-1], 'prow': [5,-1], 'allow': [5,-1], 'laugh': [0,5],
    'elbow': [10,-1], 'window': [10,-1], 'rainbow': [10,-1], 'shadow': [10,-1],
    'meant': [1,4], 'dreamt': [1,4], 'learnt': [13,4], 'hymn': [2,2], 'could': [11,4], 'should': [11,4],
    'to': [11,-1], 'was': [4,6], 'were': [13,0], 'love': [4,5], 'eye': [9,-1], 'bury': [8,-1],
    'your': [11,0], 'heart': [12,4], 'some': [4,2], 'come': [4,2], 'from': [4,2], 'become': [4,2],
    'would': [11,4], 'pour': [10,0],'figure': [13,0], 'author': [4,0], 'sure': [11,0], 'rhythm': [4,2],
    'every': [8,-1], 'very': [8,-1], 'many': [8,-1], 'any': [8,-1], 'busy': [8,-1], 'easy': [8,-1],
    'happy': [8,-1], 'live': [2,5], 'into': [11,-1], 'soul': [10,2], 'only': [8,-1], 'earth': [13,6],
    'though': [10,-1], 'thought': [3,4], 'bought': [3,4], 'brought': [3,4], 'ought': [3,4],
    'said': [1,4], 'dead': [1,4], 'word': [13,4], 'heard': [13,4], 'death': [1,6], 'head': [1,4],
    'once': [4,6], 'great': [7,4], 'young': [4,2], 'among': [4,2], 'yon': [3,2],
    'door': [10,0], 'find': [9,4], 'mind': [9,4], 'kind': [9,4], 'behind': [9,4], 'blind': [9,4],
    'wild': [9,4],'give': [2,5], 'beauty': [8,-1], 'duty': [8,-1], 'move': [11,5], 'above': [4,5],
    'prove': [11,5], 'have': [0,5], 'whom': [11,2], 'warm': [10,2], 'done': [4,2], 'gone': [3,2],
    'behind': [9,4], 'none': [4,2], 'most': [10,4], 'ghost': [10,4], 'host': [10,4], 'post': [10,4],
    'travel': [4,1], 'broad': [3,4],'veil': [7,1],'tread': [1,4], 'bread': [1,4], 'ocean': [4,2],
    'truth': [11,6], 'human': [4,2], 'woman': [4,2], 'unto': [11,-1], 'worm': [13,4],
}
for word in BRITISH_OUR:
    DEFINED_RHYMES[word] = [4,0]