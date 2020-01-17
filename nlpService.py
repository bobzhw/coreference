#encoding=utf-8
import json
import requests
from py2neo import Graph,Node,Relationship


class nlpReulst:
    def __init__(self,d):
        self.__dict__=d

    def __lt__(self, other):  # override <操作符
        if len(self.types[0]) < len(other.types[0]):
            return True
        return False
def getNlpResult(sentence):
    # nlpService("三角形ABC的底边BC长为12cm，它的面积随BC边上的高度变化而变化")
    json_info={
        "type": 3,
        "stem": sentence,
        "subStems": [r""],
        "options": [],
        "solutions": []
    }

    user_info={"text_json": json.dumps(json_info),"chinese_type": "1"}
    r =requests.post("http://121.48.165.44:7776/nlp_api",data=user_info)
    s = json.dumps(r.json(),ensure_ascii=True)
    b = json.loads(s, object_hook=nlpReulst)
    return b

def get_graph(e1,e2,dic,words,index):
    graph = Graph('bolt://192.168.1.70:7687', username='neo4j', password='ad201')
    file = open('relation','r',encoding='utf-8')
    com1 = graph.run('match ({ChineseName:\"'+e1+'\"})-[{name:"有子类"}]-(n) return n')
    com2 = graph.run('match ({ChineseName:\"'+e2+'\"})-[{name:"有子类"}]-(n) return n')
    elst1 = [e1]
    elst2 = [e2]
    for i in com1:
        elst1.append(i[0]['ChineseName'])
    for i in com2:
        elst2.append(i[0]['ChineseNmae'])
    for e1 in elst1:
        for e2 in elst2:
            tripple = None
            for line in file.readlines():
                group = line.split(' ')
                if (e1 == group[0] and e2 == group[1]) or (e2 == group[0] and e1 == group[1]):
                    tripple=group
                    break
            command = 'match ({ChineseName:\''+e1+'\'})-[r]-({ChineseName:\''+e2+'\'}) return r'
            res = graph.run(command)
            for i in res:
                print(i)
                if i[0]['name']=='有子类':
                    continue
                if tripple is None:
                    return True
                else:
                    relation_keys = tripple[3].split('|')
                    words = words[index:]
                    for word in words:
                        for relation_key in relation_keys:
                            if word in dic.keys():
                                if relation_key in dic[word]:
                                    return True

    return False

if __name__ == '__main__':
    # get_graph(1,2)
    get_graph('等腰三角形','边',1,1,1)
