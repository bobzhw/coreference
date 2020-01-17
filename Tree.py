import os
import hobbs
from nltk import Tree
from nltk.parse.stanford import StanfordParser
import re
import jieba
import nltk
import queue
os.environ['STANFORD_PARSER'] = 'data/stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'data/stanford-parser-3.9.2-models.jar'


daici=['它','其']
daici2 =['该','这个','此','那个']
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
    for dc in daici2:
        entity_table.append(dc+g[0].strip())
file = open("segmentation",'r',encoding='utf-8')
word = []
for line in file.readlines():
    word.append(line.strip())
word.sort(key=lambda i: len(i), reverse=True)

jieba.load_userdict('segmentation')
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

def adjustSegment(s):
    news=[]
    for c in s:
        flag = False
        for i in range(len(word)):
            w = word[i]
            if w in c:
                index = c.find(w)
                if index==0 and c!=w:
                    continue
                news.append(c[0:index])
                news.append(c[index:])
                flag = True
                break
        if flag==False:
            news.append(c)
    while '' in news:
        news.remove('')
    for i in range(len(news)-2):
        if news[i] in daici2:
            news[i]=news[i]+news[i+1]
            news.pop(i+1)
            daici.append(news[i])
    return news
def segWord(sentence):
    # jieba.suggest_freq(('长','为'),True)
    s = jieba.lcut(sentence)
    s = adjustSegment(s)
    sentence=''
    for c in s:
        if c!='':
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
        elif sentences[i] in entity_table:
            isEntity[i]=1
            i=i+1
            last=False
        else:
            i = i + 1
            last = False
        for k in range(len(daici)):
            if daici[k] in sentences[i]:
                daici[k]=sentences[i]
    sentence=''
    for i in range(len(sentences)):
        sentence=sentence+sentences[i]+' '
    dic,newsentence = replaceFruitChar(sentence.strip(),0,isEntity)
    print(newsentence)
    return dic,sentence,newsentence
    # return sentence
def replaceFruitChar(sentence,count,isEntity):
    dic = dict()
    group = sentence.split(' ')
    sentence = ''
    for i in range(len(group)):
        if isEntity[i]==1 :
            flag = False
            for dc in daici2:
                if dc in group[i]:
                    flag = True
                    break
            if flag == True:
                sentence=sentence+group[i]+' '
                continue
            sentence = sentence+fruit_table[count]+' '
            dic[fruit_table[count]]=group[i]
            count=count+1
        else:
            sentence=sentence+group[i]+' '
    return dic,sentence

def dfs(tree,pos):
    if isinstance(tree,str):
        if tree in daici:
            return True
        else:
            return False
    if isinstance(tree,nltk.Tree):
        for i in range(len(tree)):
            pos.append(i)
            if dfs(tree[i],pos):
                return True
            pos.pop()
    return False
def findPos(trees):
    tree=trees[len(trees)-1]
    pos=[]
    dfs(tree,pos)
    print(tree[pos])
    return pos


if __name__ == '__main__':
    # sentence=' 设$P$为椭圆$c$上异于其顶点$F$的一点$D$'
    # sentence='已知双曲线$C$的离心率为$D$，且其右焦点为$F$'
    # sentence='设$F$是双曲线$C$的一个焦点，若$C$上存在点$P$，使线段$PF$的中点恰为其虚轴的一个端点'
    # sentence='设$P(3,1)$为函数$f(x)=a{{x}^{2}}-2ax+b$的图象与其反函数$y={{f}^{-1}}(x)$的图象的一个交点'
    sentence='在等腰三角形中，一腰上的中线把周长分成$15cm$和$6cm$两部分，求这个三角形各边的长.'
    # # sentence='苹果的香蕉是橘子'
    # # sentence='1+2*3是'
    import nlpService
    print("正在请求nlp服务")
    dics = nlpService.getNlpResult(sentence)
    sentence = dics.fakeText
    dic,sentence,newsentence=segWord(sentence)
    print(sentence)
    print(newsentence)
    sentences = re.split('，|。|？|！',newsentence)
    trees = []
    for sent in sentences:
        tree = createTree(sent)
        modifyTree(tree)
        trees.append(tree)
        # tree.draw()
    pos = findPos(trees)
    p = tuple(pos)
    line, pos = hobbs.hobbs(trees,p,sentence,newsentence,dic)

    if line is None and pos is None:
        print("没有指代")
    else:
        s = line[pos]
        while isinstance(s,nltk.Tree):
            s=s[0]
        print("Proposed antecedent for '它':", dic[s], '\n')
    # s = segWord(sentence)
