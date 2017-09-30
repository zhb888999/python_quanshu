# -*- coding: utf-8 -*-
import wx
import MySQLdb
import sys
from warnings import filterwarnings
reload(sys)
sys.setdefaultencoding('utf8')
filterwarnings('error', category = MySQLdb.Warning)
class search:
    def __init__(self):
        self.searchtext = ''
        self.novel_id = 1
        self.novel_chapter_number = 1
        self.novel_chapter_text = ''
        self.novel_name = ''
        self.novel_author = ''
    def get_text_chapter_id(self,searchtext):
        self.searchtext = searchtext
        try:
            connect = MySQLdb.connect(host='127.0.0.1', user='mking', passwd='507717', db='novel', charset='utf8')
            cur = connect.cursor()
            cur.execute("SELECT novel_id,novel_chapter_name,novel_chapter_text,novel_chapter_number,novel_name,novel_author FROM novel_quanshu_chapter WHERE novel_chapter_id ='%s'"% (self.searchtext))
            results = cur.fetchall()
        except:
            self.novel_chapter_text = 'Get chapter fail!'
            connect.close()
            return
        if not results:
            self.novel_chapter_text = 'Don\'t have this chapter!'
            connect.close()
            return
        self.novel_id = results[0][0]
        self.novel_chapter_number = results[0][3]
        self.novel_chapter_text = results[0][1]+'\n\n'+results[0][2]
        self.novel_chapter_text = self.novel_chapter_text.replace('&nbsp;',' ')
        self.novel_chapter_text = self.novel_chapter_text.replace('<br />','')
        self.novel_name = results[0][4]
        self.novel_author = results[0][5]
        connect.close()



def open(event):
    text.get_text_chapter_id(novel.GetValue())
    contents.SetValue(text.novel_chapter_text)
def next(event):
    text.novel_chapter_number = text.novel_chapter_number + 1
    search =str(text.novel_id) + '-' + str(text.novel_chapter_number)
    text.get_text_chapter_id(search)
    novel.SetValue(search)
    contents.SetValue(text.novel_chapter_text)
def up(event):
    if text.novel_chapter_number > 1:
        text.novel_chapter_number = text.novel_chapter_number - 1
    search =str(text.novel_id) + '-' + str(text.novel_chapter_number)
    text.get_text_chapter_id(search)
    novel.SetValue(search)
    contents.SetValue(text.novel_chapter_text)

app=wx.App()
win = wx.Frame(None,title="Novelreading",size = (410,335))
bkg = wx.Panel(win)

text = search()

openButton = wx.Button(bkg, label=u'打开')
openButton.Bind(wx.EVT_BUTTON,open)

nextButton = wx.Button(bkg, label=u'下一章')
nextButton.Bind(wx.EVT_BUTTON,next)
accelTb1 = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('N'), nextButton.GetId())])
nextButton.SetAcceleratorTable(accelTb1)

upButton = wx.Button(bkg, label=u'上一章')
upButton.Bind(wx.EVT_BUTTON,up)
accelTb2 = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('B'), upButton.GetId())])
upButton.SetAcceleratorTable(accelTb2)

novel = wx.TextCtrl(bkg)
contents = wx.TextCtrl(bkg, style = wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)

hbox1 = wx.BoxSizer()
hbox1.Add(novel, proportion =1,flag=wx.EXPAND)


hbox2 = wx.BoxSizer()
hbox2.Add(openButton, proportion=0,flag=wx.LEFT,border=5)
hbox2.Add(upButton,proportion=0, flag=wx.LEFT,border=5)
hbox2.Add(nextButton,proportion=0, flag=wx.LEFT,border=5)

vbox = wx.BoxSizer(wx.VERTICAL)
vbox.Add(hbox1, proportion=0, flag=wx.EXPAND | wx.ALL, border = 5)
vbox.Add(hbox2, proportion=0, flag=wx.EXPAND | wx.ALL, border = 5)
vbox.Add(contents, proportion=1,flag=wx.EXPAND|wx.LEFT|wx.BOTTOM|wx.RIGHT,border = 5)

bkg.SetSizer(vbox)
win.Show()

app.MainLoop()