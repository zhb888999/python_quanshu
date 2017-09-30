# -*- coding: UTF-8 -*-
import urllib
import re
import MySQLdb
class MySQL:
    def __init__(self,host = '127.0.0.1',user = 'mking',passwd = '507717',db = 'novel-quanshu',charset = 'utf8'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.charset = charset
        self.connect = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)

    def insert(self,table_name,**colu_vlue):
        cur = self.connect.cursor()
        v_str = ""
        vv_str = ""
        for i in colu_vlue:
            v_str = i + ',' + v_str
            vv_str = '"' + colu_vlue[i] + '"' + ',' + vv_str
        v_str = v_str[:-1]
        vv_str = vv_str[:-1]
        cur.execute('insert IGNORE into %s(%s) values(%s)' % (table_name, v_str, vv_str))
        self.connect.commit()
    def close(self):
        self.connect.close()
class Novel:
    def __init__(self,novel_name,novel_class,novel_author,novel_html):
        self.novel_name = novel_name
        self.novel_class = novel_class
        self.novel_author = novel_author
        self.novel_html = novel_html
    def putdb(self):
        connect = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)
        cur = connect.cursor()
        cur.execute('insert IGNORE into novel(novel_nam,novel_class,novel_author,novel_html) values("%s","%s","%s","%s")' % (self.novel_name, self.novel_class, self.novel_author,self.novel_html))
        connect.commit()
        connect.close()



def getClassList(html):
    html = urllib.urlopen(html).read().decode('gbk').encode('utf-8')
    reg = r'<ul class="channel-nav-list">(.*?)</ul>'
    html = re.findall(reg,html,re.S)
    reg = r'<li><a href="(.*?)">(.*?)</a></li>'
    html = re.findall(reg,"".join(html))
    reg = r' class="last">(.*?)</a><kbd>'
    connect = MySQLdb.connect(host='127.0.0.1', user='mking', passwd='507717', db='novel-quanshu', charset='utf8')
    cur = connect.cursor()
    for i in html:
        html1 = urllib.urlopen(i[0]).read().decode('gbk').encode('utf-8')
        class_page = re.findall(reg,html1)
        class_page = "".join(class_page)
        cur.execute('insert IGNORE into class(ClassName,ClassHtml,ClassPage) values("%s","%s",%s)' % (i[1], i[0], class_page))
    connect.commit()
    connect.close()
def getNovelList(novel_class,html):
    html = urllib.urlopen(html).read().decode('gbk').encode('utf-8')
    reg = r'<section class="section board-list board-list-collapse">(.*?) <script type="text/javascript">'
    html = re.findall(reg,html,re.S)
    reg = r'<li><a target="_blank" (.*?)class="readTo">'
    html = re.findall(reg,"".join(html),re.S)
    reg_novel_html = r'href="(.*?)" class="l mr10">'
    reg_novel_name = r'class="clearfix stitle">(.*?)</a>作者'
    reg_novel_author = r'</a>作者：<a href=".*?>(.*?)</a><em class="c999 clearfix">'
    connect = MySQLdb.connect(host='127.0.0.1', user='mking', passwd='507717', db='novel-quanshu', charset='utf8')
    cur = connect.cursor()
    for i in html:
        novel_name = re.findall(reg_novel_name, i, re.S)
        novel_author = re.findall(reg_novel_author, i, re.S)
        novel_html = re.findall(reg_novel_html, i, re.S)
        novel_class = "".join(novel_class)
        novel_name = "".join(novel_name)
        novel_author = "".join(novel_author)
        novel_html = "".join(novel_html)
        cur.execute('insert IGNORE into novel(novel_name,novel_class,novel_author,novel_html) values("%s","%s","%s","%s")' % (novel_name,novel_class,novel_author,novel_html))
    connect.commit()
    connect.close()


getClassList('http://www.quanshuwang.com/')
connect = MySQLdb.connect(host='127.0.0.1', user='mking', passwd='507717', db='novel-quanshu', charset='utf8')
cur = connect.cursor()
cur.execute("SELECT ClassName, ClassHtml, ClassPage FROM `novel-quanshu`.`class`")
results = cur.fetchall()
reg = '(.*?)_.*?'
for row in results:
    ClassName = row[0]
    ClassHtml = row[1]
    ClassPage = row[2]
    for i in range(1,ClassPage):
        url = "".join(ClassHtml)
        url = re.findall(reg, url)
        url = "".join(url)
        url =url+'_'+str(i)+'.html'
        print ClassName, url
        getNovelList(ClassName.encode('utf-8'),url)
cur.close()

