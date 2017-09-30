# -*- coding: UTF-8 -*-
import urllib2
import re
import MySQLdb
import multiprocessing
import time
import sys
from warnings import filterwarnings
reload(sys)
sys.setdefaultencoding('utf8')
filterwarnings('error', category = MySQLdb.Warning)

#novel_operate_state  1：No acquisition  2:In acquisition 3:success

# idnovel           #小说ID
# novel_name        #小说名称
# novel_class       #小说类型
# novel_author      #小说作者
# novel_state       #小说状态
# novel_chaptersurl #全部章节网址

#novel->novel_quanshuwang       #使用的数据库
#idnovel_quanshuwang            #表序列号
#novel_id                       #小说唯一ID识别号
#novel_name                     #小说名称
#novel_class                    #小说类型
#novel_author                   #小说作者
#novel_state                    #小说状态
#novel_chaptersurl              #小说章节列表地址
#novel_chapter_name             #小说章节名称
#novel_chapter_id               #小说章节唯一识别号
#novel_chapter_number           #小说章节号
#novel_chapter_url              #小说章节地址
#novel_chapter_text             #小说章节内容

def DownloadChapter(novel_id,novel_name,novel_class,novel_author,novel_state,novel_chapter_list_url):
    try:
        html = urllib2.urlopen(novel_chapter_list_url,timeout=5).read().decode('gbk').encode('utf-8')
    except:
        print "$ 打开小说列表网页错误",novel_id,novel_name,novel_chapter_list_url
        return 0
    reg_novel_chapter_url = r'<li><a href="([0-9]+.html)" title=".*?">(.*?)</a></li>'                                              #获取章节URL及章节名称的正则表达式
    html = re.findall(reg_novel_chapter_url,html,re.S)
    connect = MySQLdb.connect(host='127.0.0.1', user='mking', passwd='507717', db='novel', charset='utf8')
    print "$ 成功连接数据库"
    cur = connect.cursor()
    novel_chapter_number = 0
    reg_novel_chapter_text = r'<script type="text/javascript">style5()(.*?)<script type="text/javascript">style6()'             #获取章节内容的正则表达式
    for i in  html:
        novel_chapter_number = novel_chapter_number + 1
        novel_chapter_id = str(novel_id) + '-' + str(novel_chapter_number)
        novel_chapter_url = novel_chapter_list_url+'/'+i[0]
        novel_chapter_name = i[1]
        print "$ 获取章节 >> ",novel_chapter_url
        try:
            text = urllib2.urlopen(novel_chapter_url,timeout=5).read().decode('gbk').encode('utf-8')                                      #打开章节网址
            chaptertext = re.findall(reg_novel_chapter_text, text, re.S)
            novel_chapter_text = "".join(chaptertext[0])[12:]
        except:
            print "$ 错误:无法打开网址",novel_chapter_url,"稍后重试"
            novel_chapter_text = "GetError"
        try:
            cur.execute('INSERT IGNORE INTO novel_quanshu_chapter \
                    (novel_id,novel_name,novel_class,novel_author,novel_state,novel_chapter_list_url,\
                    novel_chapter_name,novel_chapter_id,novel_chapter_number,novel_chapter_url,novel_chapter_text) \
                    VALUES("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'% \
                       (novel_id,novel_name,novel_class,novel_author,novel_state,novel_chapter_list_url, \
                        novel_chapter_name,novel_chapter_id,novel_chapter_number, novel_chapter_url, novel_chapter_text))
            connect.commit()
            print "$ 成功写入数据"
        except MySQLdb.Warning, w:
            print "$ MySQL Warning:%s" % str(w)
        except MySQLdb.Error, e:
            print "$ MySQL Error:%s" % str(e)
    #
    # MySQLdb_connect_times = 3
    # while True:
    #     try:
    #         cur.execute("SELECT novel_chapter_id, novel_chapter_url FROM novel_quanshu_chapter WHERE novel_chapter_text = 'GetError'")
    #         results = cur.fetchall()
    #     except MySQLdb.Warning, w:
    #         print "$ MySQL Warning:%s" % str(w)
    #     except MySQLdb.Error, e:
    #         print "$ MySQL Error:%s" % str(e)
    #         MySQLdb_connect_times = MySQLdb_connect_times-1
    #         if not MySQLdb_connect_times:
    #             break
    #     if  not results:
    #         break
    #     for row in results:
    #         novel_chapter_id = row[0]
    #         novel_chapter_url = row[1]
    #         print "$ 重新获取章节 >> ", novel_chapter_url
    #         try:
    #             text = urllib2.urlopen(novel_chapter_url, timeout=5).read().decode('gbk').encode('utf-8')
    #             chaptertext = re.findall(reg_novel_chapter_text, text, re.S)
    #             novel_chapter_text = "".join(chaptertext[0])[12:]
    #             novel_chapter_id = str(novel_chapter_id)
    #         except:
    #             print "$ 重新打开出错，稍后重试"
    #             continue
    #         try:
    #             cur = connect.cursor()
    #             cur.execute("UPDATE novel_quanshu_chapter SET novel_chapter_text='%s' WHERE novel_chapter_id = '%s'"% (novel_chapter_text,novel_chapter_id))
    #             connect.commit()
    #             print "$ 成功重新写入",novel_chapter_id,"章节数据"
    #         except MySQLdb.Warning, w:
    #             print "$ MySQL Warning:%s" % str(w)
    #         except MySQLdb.Error, e:
    #             print "$ MySQL Error:%s" % str(e)
    # connect.close()
    # print "$ ",novel_id, novel_name,"成功爬取小说内容"
    # return 1

def ProessDownloadChapter():
    connect = MySQLdb.connect(host='127.0.0.1', user='mking', passwd='507717', db='novel', charset='utf8')
    while True:
        cur = connect.cursor()
        cur.execute("SELECT novel_id,novel_name,novel_class,novel_author,novel_state,novel_chapter_list_url FROM `novel_quanshu_list` WHERE novel_operate_state = 'No acquisition' AND novel_id >= (SELECT floor(RAND() * (SELECT MAX(novel_id) FROM `novel_quanshu_list`))) ORDER BY novel_id LIMIT 1")
        results = cur.fetchall()
        if  not results:
            connect.close()
            break
        print results
        cur = connect.cursor()
        cur.execute("UPDATE novel_quanshu_list SET novel_operate_state='In acquisition' WHERE novel_id = '%s'" % (results[0][0]))
        connect.commit()
        print results[0][0],results[0][1],results[0][2],results[0][3],results[0][4],results[0][5]
        i = DownloadChapter(results[0][0],results[0][1],results[0][2],results[0][3],results[0][4],results[0][5])
        if i:
            cur = connect.cursor()
            cur.execute("UPDATE novel_quanshu_list SET novel_operate_state='%s' WHERE novel_id = '%s'" % ('Success', results[0][0]))
            connect.commit()
        else:
            cur = connect.cursor()
            cur.execute("UPDATE novel_quanshu_list SET novel_operate_state='%s' WHERE novel_id = '%s'" % ('No acquisition', results[0][0]))
            connect.commit()
if  __name__ == "__main__":

    lock = multiprocessing.Lock()
    p1 = multiprocessing.Process(target=ProessDownloadChapter)
    p2 = multiprocessing.Process(target=ProessDownloadChapter)
    p3 = multiprocessing.Process(target=ProessDownloadChapter)
    p4 = multiprocessing.Process(target=ProessDownloadChapter)
    p5 = multiprocessing.Process(target=ProessDownloadChapter)
    p6 = multiprocessing.Process(target=ProessDownloadChapter)
    p7 = multiprocessing.Process(target=ProessDownloadChapter)
    p8 = multiprocessing.Process(target=ProessDownloadChapter)
    # p9 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p10 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p11 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p12 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p13 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p14 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p15 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p16 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p17 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p18 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p19 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p20 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p21 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p22 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p23 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p24 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p25 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p26 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p27 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p28 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p29 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p30 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p31 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p32 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p33 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p34 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p35 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p36 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p37 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p38 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p39 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p40 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p41 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p42 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p43 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p44 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p45 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p46 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p47 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p48 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p49 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p50 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p51 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p52 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p53 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p54 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p55 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p56 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p57 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p58 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p59 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p60 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p61 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p62 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p63 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p64 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p65 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p66 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p67 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p68 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p69 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p70 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p71 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p72 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p73 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p74 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p75 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p76 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p77 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p78 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p79 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p80 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p81 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p82 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock, ))
    # p83 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p84 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p85 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p86 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p87 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p88 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p89 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p90 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p91 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p92 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p93 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p94 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p95 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p96 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p97 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p98 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p99 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))
    # p100 = multiprocessing.Process(target=ProessDownloadChapter, args=(lock,))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()
    # p9.start()
    # p10.start()
    # p11.start()
    # p12.start()
    # p13.start()
    # p14.start()
    # p15.start()
    # p16.start()
    # p17.start()
    # p18.start()
    # p19.start()
    # p20.start()
    # p21.start()
    # p22.start()
    # p23.start()
    # p24.start()
    # p25.start()
    # p26.start()
    # p27.start()
    # p28.start()
    # p29.start()
    # p30.start()
    # p31.start()
    # p32.start()
    # p33.start()
    # p34.start()
    # p35.start()
    # p36.start()
    # p37.start()
    # p38.start()
    # p39.start()
    # p40.start()
    # p41.start()
    # p42.start()
    # p43.start()
    # p44.start()
    # p45.start()
    # p46.start()
    # p47.start()
    # p48.start()
    # p49.start()
    # p50.start()
    # p51.start()
    # p52.start()
    # p53.start()
    # p54.start()
    # p55.start()
    # p56.start()
    # p57.start()
    # p58.start()
    # p59.start()
    # p60.start()
    # p61.start()
    # p62.start()
    # p63.start()
    # p64.start()
    # p65.start()
    # p66.start()
    # p67.start()
    # p68.start()
    # p69.start()
    # p70.start()
    # p71.start()
    # p72.start()
    # p73.start()
    # p74.start()
    # p75.start()
    # p76.start()
    # p77.start()
    # p78.start()
    # p79.start()
    # p80.start()
    # p81.start()
    # p82.start()
    # p83.start()
    # p84.start()
    # p85.start()
    # p86.start()
    # p87.start()
    # p88.start()
    # p89.start()
    # p90.start()
    # p91.start()
    # p92.start()
    # p93.start()
    # p94.start()
    # p95.start()
    # p96.start()
    # p97.start()
    # p98.start()
    # p99.start()
    # p100.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()
    # p9.join()
    # p10.join()
    # p11.join()
    # p12.join()
    # p13.join()
    # p14.join()
    # p15.join()
    # p16.join()
    # p17.join()
    # p18.join()
    # p19.join()
    # p20.join()
    # p21.join()
    # p22.join()
    # p23.join()
    # p24.join()
    # p25.join()
    # p26.join()
    # p27.join()
    # p28.join()
    # p29.join()
    # p30.join()
    # p31.join()
    # p32.join()
    # p33.join()
    # p34.join()
    # p35.join()
    # p36.join()
    # p37.join()
    # p38.join()
    # p39.join()
    # p40.join()
    # p41.join()
    # p42.join()
    # p43.join()
    # p44.join()
    # p45.join()
    # p46.join()
    # p47.join()
    # p48.join()
    # p49.join()
    # p50.join()
    # p51.join()
    # p52.join()
    # p53.join()
    # p54.join()
    # p55.join()
    # p56.join()
    # p57.join()
    # p58.join()
    # p59.join()
    # p60.join()
    # p61.join()
    # p62.join()
    # p63.join()
    # p64.join()
    # p65.join()
    # p66.join()
    # p67.join()
    # p68.join()
    # p69.join()
    # p70.join()
    # p71.join()
    # p72.join()
    # p73.join()
    # p74.join()
    # p75.join()
    # p76.join()
    # p77.join()
    # p78.join()
    # p79.join()
    # p80.join()
    # p81.join()
    # p82.join()
    # p83.join()
    # p84.join()
    # p85.join()
    # p86.join()
    # p87.join()
    # p88.join()
    # p89.join()
    # p90.join()
    # p91.join()
    # p92.join()
    # p93.join()
    # p94.join()
    # p95.join()
    # p96.join()
    # p97.join()
    # p98.join()
    # p99.join()
    # p100.join()

    print "Sub-process(es) done."

