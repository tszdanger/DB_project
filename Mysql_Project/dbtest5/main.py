# -*- coding: utf-8 -*-
"""
Created on Sat Jun 04 08:34:29 2016

@author: 马晶义
"""
import re
class MyList:
    def __init__(self,statement,LnextNode,RnextNode,content):
        self.statement = statement
        self.LnextNode = LnextNode
        self.RnextNode = RnextNode
        self.content = content
          

sql0 = "SELECT [ ENAME = 'Mary' & DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT )"
sql1 = "PROJECTION [ BDATE ] ( SELECT [ ENAME = 'John' & DNAME = ' Research' ] ( EMPLOYEE JOIN DEPARTMENT ) )"
sql2 = "SELECT [ ESSN = '01' ] (  PROJECTION [ ESSN, PNAME ] ( WORKS_ON JOIN PROJECT ) )"

sql_keys = ["SELECT","PROJECTION","JOIN"] 

Table_list = [["ESSN","ADDRESS","SALARY","SUPERSSN","ENAME","DNO"], #EMPLOYEE
	["DNO","DNAME","DNEMBER","MGRSSN","MGRSTARTDATE"],            #DEPARTMENT
	["PNAME","PNO","PLOCATION","DNO"],                            #PROJECT
	["HOURS","ESSN","PNO"]]                                       #WORKS_ON


''' 打印原始执行树'''
def printOriginTree(sql):
    mylist = MyList(None,None,None,None)
    currentNode = MyList(None,None,None,None)
    currentNode = mylist
    print "\t ****origin tree****\n"
    for i in range(len(sql)):
        if sql[i]=="SELECT" or sql[i] == "PROJECTION":
            currentNode.statement = sql[i]
            temp = sql[i]
            s = '' 
            j = i+1
            if sql[j]=='[':
                j=j+1
                while(j<len(sql) and sql[j]!=']'):
                    #print sql[j]
                    s = s + sql[j]
                    j=j+1
                print temp, s,"\n"
                i = j       
        elif sql[i] =='[' or sql[i] ==']' or sql[i]==')':
            pass
        elif sql[i] == '(':
            currentNode.LnextNode = MyList(None,None,None,None)
            currentNode =  currentNode.LnextNode
        elif sql[i]=="JOIN":
            print "\t" + sql[i]
            x = sql[i-1] + "\t" + sql[i+1] + "\n"
            s = []
            s.append(sql[i-1])
            s.append(sql[i+1])
            print x
            currentNode.statement = sql[i]
            currentNode.content = None
            currentNode.LnextNode = MyList(None,None,None,None)
            currentNode.LnextNode.content = sql[i-1]
            currentNode.RnextNode = MyList(None,None,None,None)
            currentNode.RnextNode.content = sql[i+1]
            i = i+1
        else:
            if currentNode.content == None:
                currentNode.content =''
            if sql[i+1] == "JOIN":
                continue
            currentNode.content = currentNode.content+sql[i]
    return mylist

''' 测试存储的树的正确性'''
def testTreePrint(sql_tree):
    print "test tree OK"
    current = sql_tree
    s = []
    while current !=None or len(s)!=0:
        while current!=None:
            if current.statement !=None:
                if current.statement != None and current.statement!="JOIN":
                    print current.statement, current.content
                elif current.statement == "JOIN":
                    print '\t',current.statement
                    print current.LnextNode.content,"\t",current.RnextNode.content
                else:
                    print current.statement
            
            s.append(current)
            current = current.RnextNode
        if len(s)!=0:
            current = s.pop()
            current = current.LnextNode
           
''' 查找属性所在表'''            
def search(s):
    table_list = []
    for i in range(4):
        if s in Table_list[i]:
            if i == 0:
                table_list.append("EMPLOYEE")
            elif i==1:
                table_list.append("DEPARTMENT")
            elif i==2:
                table_list.append("PROJECTION")
            elif i==3:
                table_list.append( "WORKS_ON")
    return table_list

    
'''  优化后的查询执行树 '''    
def parseTree(sql_node,sql_arr): 
   print "\tparseTree"
   currentnode = MyList(None,None,None,None)
   if sql_node.statement == "SELECT":
       if '&' in sql_node.content:
           s= sql_node.content.split('&')
           #print s  
           table_s = []
           for i in range(len(s)):
               pro = re.split('=|>|<|!=',s[i])
               #print pro
               table_s.append(search(pro[0]))
               #print "SELECT"+' '+s[i]+'\n'+search(pro[0])
           #print table_s
           sel_list =[]
           sel_list.append(s[0])
           sel_list.append(table_s[0])
           currentnode.content  = sel_list
           currentnode.statement = "SELECT"
           for j in range(1,len(table_s)):
               newnode = MyList(None,None,None,None)
               topnode = MyList(None,None,None,None)
               sel_list =[]
               sel_list.append(s[j])
               sel_list.append(table_s[j])
               newnode.statement = "SELECT"
               newnode.content = sel_list
               topnode.statement = "JOIN"
               topnode.LnextNode = currentnode
               topnode.RnextNode = newnode
               currentnode = topnode
   elif sql_node.statement == "PROJECTION":
       topnode = MyList(None,None,None,None)
       topnode.statement = "PROJECTION"
       topnode.content = sql_node.content
       #currentnode = sql_node.LnextNode
       if sql_node.LnextNode.statement == "SELECT":
           if '&' in sql_node.LnextNode.content:
               s = sql_node.LnextNode.content.split('&')
               table_s = []
               for i in range(len(s)):
                   pro = re.split('=|>|<|!=',s[i])
                   table_s.append(search(pro[0]))
               sel_list =[]
               sel_list.append(s[0])
               sel_list.append(table_s[0])
               currentnode.content  = sel_list
               currentnode.statement = "SELECT"
               for j in range(1,len(table_s)):
                   newnode = MyList(None,None,None,None)
                   toplnode = MyList(None,None,None,None)
                   sel_list =[]
                   sel_list.append(s[j])
                   sel_list.append(table_s[j])
                   newnode.statement = "SELECT"
                   newnode.content = sel_list
                   toplnode.statement = "JOIN"
                   toplnode.LnextNode = currentnode
                   toplnode.RnextNode = newnode
                   currentnode = toplnode
       topnode.LnextNode = toplnode
       print topnode.statement
       currentnode = topnode
   else:
       tempnode = sql_node
       while(tempnode.LnextNode != None):
           tempnode = tempnode.LnextNode
           if tempnode.statement == "SELECT":
               if '&' in sql_node.content:
                   s= tempnode.content.split('&')
                   print s 
   return currentnode


''' 打印优化后的查询执行树'''
def printAfterParseTree(afterParseTree):
    print "\t****new tree****\n"
    print afterParseTree.statement
    print afterParseTree.content
    print afterParseTree.LnextNode.statement
    if afterParseTree.statement == None:
        print "tree None"
        return
    if afterParseTree.content == None:
        print '\t'+afterParseTree.statement
        lnode =  afterParseTree.LnextNode
        rnode = afterParseTree.RnextNode
        print lnode.statement,lnode.content[0],rnode.statement,rnode.content[0]
        print lnode.content[1],'\t\t',rnode.content[1]
    else:
        print afterParseTree.statement,afterParseTree.content
        
        
print "input 1 or 2 or 3 to select sql"
while(1):
    sel = raw_input()
    if sel == '1':
        sql_arr = sql0.split(" ")
        sql_node =  printOriginTree(sql_arr)
        testTreePrint(sql_node)
        #afterParseTree = parseTree(sql_node,sql_arr)
        #printAfterParseTree(afterParseTree)
    elif sel == '2':
        sql_arr = sql1.split(" ")
        sql_node =  printOriginTree(sql_arr)
        testTreePrint(sql_node)
        #afterParseTree = parseTree(sql_node,sql_arr)
        #printAfterParseTree(afterParseTree)
    elif sel == '3':
        sql_arr = sql2.split(" ")
        sql_node = printOriginTree(sql_arr)
        #afterParseTree = parseTree(sql_node,sql_arr)
        #printAfterParseTree(afterParseTree)
    else:
        print "over"
        break
        
