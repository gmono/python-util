import requests as req
from selenium import webdriver as dri
import urllib as url
import os
from time import sleep
import json
from pyquery import PyQuery as pq
from threading import Thread as th
class Downloader:
    brwoser=None
    
    def __init__(self,usebrowser=False,storedir=None,btype="firefox"):
        """
        usebrowser:是否使用selenium进行动态抓取
        storedir存储目录
        btype 浏览器类型
        """
        if storedir==None or storedir=='.':
            storedir='.'
        elif not(storedir in os.listdir(".")):
            os.mkdir(storedir)
        
        ts={
            "firefox":dri.Firefox,
            "chrome":dri.Chrome,
            "edge":dri.Edge
        }
        if usebrowser and DataCatcher.brwoser==None:
            DataCatcher.brwoser=ts[btype]()
        self.storedir=storedir
    

    def download(link,index):
        """
        静态函数 用于下载
        """
        res=req.get(link)
        with open(index,"wb") as file:
            file.write(res.content)


    def downloadAll(self,li,indexs):
        """传入一个列表 下载列表中的所有链接
        li:列表
        indexs:文件名表
        """
        if len(li)<len(indexs):
            raise Exception("错误！长度不匹配")
        
        for link,index in zip(li,indexs):
            # 对每个图片的下载创建一个线程
            tempth=th(target=Downloader.download,args=(link,index))
            tempth.start()
        



    def downloadAllByIndex(self,li,ext):
        """
        直接下载所有文件，按顺序命名
        ext为扩展名
        li为链接表
        """
        indexs=["%s/%d%s"%(self.storedir,i,ext) for i in range(len(li))]
        self.downloadAll(li,indexs)


class DataCatcher(Downloader):
    level=None
    sleeptime=None
    def __init__(self,storedir=None,btype="firefox",catchLevel=5,sleeptime=1):
        super(Downloader,self).__init__(storedir,btype)
        cls=DataCatcher
        cls.level=catchLevel
        # DataCatcher.brwoser.get("http://www.huaban.com")
        cls.sleeptime=sleeptime
    
    def getImgFromHuaban(self,link):
        """
        从一个地址下载上面的所有图片
        link:地址
        """
        DataCatcher.brwoser.get(link)
        print("paging.....")
        for i in range(DataCatcher.level):
            DataCatcher.brwoser.execute_script("window.scrollBy(0,5000)")
            sleep(DataCatcher.sleeptime)
        #持续翻页
        print("loading......")
        # text=w.page_source
        # b=bs(text,"lxml")
        # tlist=b.select(".pin.wfc>a img") #此处不使用bs4解析 而直接使用selenium
        tlist=DataCatcher.brwoser.find_elements_by_css_selector(".pin.wfc>a img")
        srclist=[i.get_attribute("src") for i in tlist]
        self.downloadAllByIndex(srclist,".jpg")


    def getImage(self,desc:str):
        udesc=url.parse.quote(desc)
        link="http://huaban.com/search/?q="+udesc
        self.getImgFromHuaban(link)
    
    def getImageFromIndex(self):
        """
        从花瓣网主页提取图片
        """
        self.getImgFromHuaban("http://huaban.com")
    
    @classmethod
    def getImageByClass(cls,classdesc: str,folname=None):
        """
        静态方法 用于获取一类图片
        """
        if folname==None:
            folname=classdesc
        cls(classdesc).getImage(classdesc)

    
    @classmethod
    def getImagesByList(cls,lst):
        for i in lst:
            cls.getImageByClass(i)
    
    @classmethod
    def getImagesByJson(cls,lstpath,encoding="UTF-8"):
        obj=json.load(open(lstpath,encoding=encoding))
        cls.getImagesByList(obj)



# H网爬虫
# 合成规则 self.nowCatchURL+index%d.html 作为某一页面的地址
class SebimmCatcher(Downloader):
    def __init__(self,storedir=None,btype="firefox"):
        Downloader.__init__(self,usebrowser=False,storedir=storedir,btype=btype)

        # 网址
        self.baseurl=""
        # 初始化
        res=req.get(self.baseurl)
        res.encoding="cp936"
        text=res.text
        q=pq(text)
        # 解析
        ele=q(".first + dl")
        eles=ele.children("dd")
        # 创建分类
        self.topClass={}
        for e in eles:
            ep=pq(e)
            aele=pq(ep.children("a")[0])
            name=aele.text()
            href=aele.attr("href")
            self.topClass[name]=self.baseurl+href
        
        #这是当前正在抓取的URL
        self.nowCatchURL=""
        # 这是当前抓取目录页的地址
        self.nowPageURL=""
        self.nowpage=0
        #打印选择
        print("可选的分类，请先选择分类(调用selectClass函数):\n")
        self.showAllClass()

    def selectClass(self,classname):
        if not (classname in self.topClass):
            raise Exception("错误！没有则会个类型")
        
        self.nowCatchURL=self.topClass[classname]
        self.nowPageURL=self.nowCatchURL+"index.html"
        self.nowclass=classname


        #建立大类文件夹
        if not(classname in os.listdir(".")):
            os.mkdir(classname)
        
        #当前存储基目录
        self.basedir=str.format("./{}/",classname)
        #选择第一页
        self.selectPage(1)

    def showAllClass(self):
        for i in self.topClass:
            print(i+"\n")


    def selectPage(self,pageid):
        """
        选取一个页面 将当前URL切换到此页
        """
        if pageid<1:
            print("错误！页面号不能为%d"%pageid)
            return
        if pageid==1:
            self.nowPageURL=self.nowCatchURL+"index.html"
        else:
            self.nowPageURL=self.nowCatchURL+"index%d.html"%pageid
        self.nowpage=pageid
    

    def nextPage(self):
        self.selectPage(self.nowpage+1)

    def backPage(self):
        self.selectPage(self.nowpage-1)
    

    def catchPage(self,nowdir,link):
        """
        抓取一页的所有图片放到 nowdir中
        """
        text=req.get(link)
        text.encoding="cp936"
        text=text.text
        #解析
        page=pq(text)
        content=page(".main-content")
        imgs=content("img")
        srcs=[pq(img).attr("src") for img in imgs]
        #开始下载
        self.storedir=nowdir
        self.downloadAllByIndex(srcs,".jpg")

    def catchOne(self):
        """
        抓取一个页面
        """
        nowurl=self.nowPageURL
        text=req.get(nowurl)
        text.encoding="cp936"
        text=text.text
        # 解析
        p=pq(text)
        list20=p(".list20")
        dds=list20("a")
        names=dds("h2")
        names=[pq(e).text() for e in names]
        #转换为pq节点列表
        dds=[pq(i) for i in dds]
        burl=self.baseurl
        links=[burl+e.attr("href") for e in dds]
        for n,l in zip(names,links):
            #n为子目录名字
            #l为子页面链接
            print("抓取:%s\n"%n)
            if not(n in os.listdir(self.basedir)):
                os.mkdir(self.basedir+n)
            nowdir=str.format("{}{}/",self.basedir,n)
            #通过nowdir和l来抓取
            self.catchPage(nowdir,l)

    def catch(self,pagesum=1):
        """
        抓取多个页面
        """
        for i in range(pagesum):
            print("当前抓取第%d页\n"%self.nowpage)
            self.catchOne()
            self.nextPage()

