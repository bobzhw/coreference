#encoding=utf-8
from py2neo import Graph,Node,Relationship
graph = Graph('bolt://192.168.1.70:7687',username='neo4j',password='ad201')

list = graph.run('MATCH (n:entity) RETURN n').data()
for d in list:
    print(d)
    print(d['n']['ChineseName'])
pass