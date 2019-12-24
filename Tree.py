import os
import hobbs
from nltk import Tree
from nltk.parse.stanford import StanfordParser
import re
import jieba

os.environ['STANFORD_PARSER'] = 'data/stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'data/stanford-parser-3.9.2-models.jar'


mathcharRegex=r'([a-zA-Z]|[0-9]|[(]|[)]|[|]|{|}|,|[.]|%|[*]|[+]|-|/|=|_|:|\'|\"|<|>|≥|≤|[$]|#|\^)+'
parser = StanfordParser(model_path="data/stanford-parser-3.9.2-models/edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz")
fruit_table=[]
file = open('fruit','r',encoding='utf-8')
for line in file.readlines():
    fruit_table.append(line.strip())
entity_table=[]
file = open('entity','r',encoding='utf-8')
for line in file.readlines():
    g = line.split("\t")
    entity_table.append(g[0].strip())
jieba.load_userdict('entity')
def modifyTree(tree):
    if tree.__len__() == 1 and tree[0].__len__() == 1:
        if isinstance(tree[0],type("str")) == False:
            tree[0].set_label(tree.label())
            tree.set_label("")
        else:
            return
    print(tree.__len__())
    for i in range(tree.__len__()):
        modifyTree(tree[i])


def createTree(sentence):
    data = parser.parse(sentence.split(" "))
    for t in data:
        for tree in t:
            return tree

def segWord(sentence):
    jieba.suggest_freq(('长','为'),True)
    s = jieba.lcut(sentence)
    sentence=''
    for c in s:
        sentence=sentence+c+' '
    sentences = sentence.split(" ")
    sentences.remove("")
    s = len(sentences)-1
    i=0
    last = False
    isEntity = [0]*len(sentences)
    while i<s:
        if re.match(mathcharRegex,sentences[i+1]):
            if sentences[i] in entity_table or last is True:
                sentences[i]=sentences[i]+sentences[i+1]
                isEntity[i]=1
                del sentences[i+1]
                s=s-1
                last = True
            else:
                last=True
                i=i+1
        else:
            i = i + 1
            last = False
    sentence=''
    for i in range(len(sentences)):
        sentence=sentence+sentences[i]+' '
    dic,sentence = replaceFruitChar(sentence.strip(),0,isEntity)
    print(sentence)
    return dic,sentence
def replaceFruitChar(sentence,count,isEntity):
    dic = dict()
    group = sentence.split(' ')
    sentence = ''
    for i in range(len(group)):
        if isEntity[i]==1:
            sentence = sentence+fruit_table[count]+' '
            dic[group[i]]=entity_table[count]
            count=count+1
        else:
            sentence=sentence+group[i]+' '
    return dic,sentence

if __name__ == '__main__':
    sentence='△ABC的底边BC长为12cm，它的面积随BC边上的高度变化而变化'
    # sentence='1+2*3是'
    dic,sentence=segWord(sentence)
    print(sentence)
    sentences = re.split('，|。|？|！',sentence)
    trees=[]
    for sent in sentences:
        tree = createTree(sent)
        # modifyTree(tree)
        trees.append(tree)
        tree.draw()
    line, pos = hobbs.hobbs(trees, (0,0,0,0))
    if line is None and pos is None:
        print("没有指代")
    else:
        print("Proposed antecedent for '它':", line[pos], '\n')