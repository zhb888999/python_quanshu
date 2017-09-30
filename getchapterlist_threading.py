#-*- coding: UTF-8 -*-
import urllib2
import re
import MySQLdb
import multiprocessing
import threading
import time
import sys
from warnings import filterwarnings
reload(sys)
sys.setdefaultencoding('utf8')
filterwarnings('error', category = MySQLdb.Warning)
def GetChapterList():
    connect = MySQLdb.connect(host='127.0.0.1', user='mking', passwd='507717', db='novel', charset='utf8')
    reg_novel_state = r'<meta property="og:novel:status" content="(.*?)"/>'
    reg_novel_chapter_list_url = r'<div class="b-oper"><a href="(.*?)" class="reader" title='
    while True:
        cur = connect.cursor()
        cur.execute("SELECT novel_id,novel_url FROM novel_quanshu_list WHERE novel_chapter_list_url = ''AND \
                      novel_id >= (SELECT floor(RAND() * (SELECT MAX(novel_id) FROM `novel_quanshu_list`))) \
                       ORDER BY novel_id LIMIT 1")
        results = cur.fetchall()
        if not results:
            connect.close()
            break
        try:
            print "$ 获取章节列表 >> "+ results[0][1]
            request = urllib2.Request(results[0][1])
            request.add_header("user-agent", "Mozilla/5.0")  # 伪装成浏览器
            html = urllib2.urlopen(request).read().decode('gbk', 'ignore').encode('utf-8')
            novel_state = re.findall(reg_novel_state, html)
            novel_chapter_list_url = re.findall(reg_novel_chapter_list_url, html)
            cur = connect.cursor()
            cur.execute('UPDATE novel_quanshu_list SET novel_state = "%s", novel_chapter_list_url="%s"  WHERE novel_id = "%s"' % (novel_state[0], novel_chapter_list_url[0], results[0][0]))
            connect.commit()
            print "$ 成功获取章节列表地址"
        except:
            print "$ 获取章节列表地址失败,稍后重新获取"
            continue
    connect.close()
threads = []
t1 = threading.Thread(target=GetChapterList)
threads.append(t1)
t2 = threading.Thread(target=GetChapterList)
threads.append(t2)
t1 = threading.Thread(target=GetChapterList)
threads.append(t1)
t3 = threading.Thread(target=GetChapterList)
threads.append(t3)
t4 = threading.Thread(target=GetChapterList)
threads.append(t4)
t5 = threading.Thread(target=GetChapterList)
threads.append(t5)
t6 = threading.Thread(target=GetChapterList)
threads.append(t6)
t7 = threading.Thread(target=GetChapterList)
threads.append(t7)
t8 = threading.Thread(target=GetChapterList)
threads.append(t8)
t9 = threading.Thread(target=GetChapterList)
threads.append(t9)
t10 = threading.Thread(target=GetChapterList)
threads.append(t10)
t11 = threading.Thread(target=GetChapterList)
threads.append(t11)
t12 = threading.Thread(target=GetChapterList)
threads.append(t12)
if  __name__ == "__main__":
    for t in threads:
#       t.setDaemon(True)
        t.start()

