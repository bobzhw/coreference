import os
import hobbs
from nltk import Tree
from nltk.parse.stanford import StanfordParser
import re
import jieba

os.environ['STANFORD_PARSER'] = 'data/stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'data/stanford-parser-3.9.2-models.jar'


mathcharRegex=r'([a-zA-Z]|[0-9]|[(]|[)]|[|]|{|}|,|[.]|%|[*]|[+]|-|/|=|_|:|\'|\"|<|>|≥|≤|$|#)+'
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
    jieba.add_word(g[0].strip())
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
    s = jieba.cut(sentence)
    sentence=''
    for c in s:
        sentence=sentence+c+' '
    sentences = sentence.split(" ")
    sentences.remove("")
    s = len(sentences)-1
    i=0
    flag = False
    while i<s:
        if re.match(mathcharRegex,sentences[i+1]):
            if sentences[i] in entity_table or flag is True:
                sentences[i]=sentences[i]+sentences[i+1]
                del sentences[i+1]
                s=s-1
            flag = True
        else:
            i = i + 1
            flag = False
    sentence=''
    for i in range(len(sentences)):
        sentence=sentence+sentences[i]+' '
    dic,sentence = replaceFruitChar(sentence,0)
    print(sentence)
    return dic,sentence
def replaceFruitChar(sentence,count):
    dic = dict()
    group = sentence.split(' ')
    sentence = ''
    for word in group:
        if word in entity_table:
            sentence = sentence+fruit_table[count]+' '
            dic[word]=entity_table[count]
            count=count+1
        else:
            sentence=sentence+word+' '
    return dic,sentence

if __name__ == '__main__':
    sentence='二次函数$y={{x}^{2}}+bx+c$中，若b+c=0，则它的图象一定过点_____.'
    # sentence='1+2*3是'
    dic,sentence=segWord(sentence)
    print(sentence)
    sentences = re.split('，|。|？|！',sentence)
    trees=[]
    for sent in sentences:
        tree = createTree(sent)
        modifyTree(tree)
        trees.append(tree)
        # tree.draw()
    line, pos = hobbs.hobbs(trees, (1,0,0,0))
    if line is None and pos is None:
        print("没有指代")
    else:
        print("Proposed antecedent for '它':", line[pos], '\n')