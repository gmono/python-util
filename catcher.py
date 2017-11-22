import requests as req
from selenium import webdriver as dri
import urllib as url
import os
from time import sleep
import json
from pyquery import PyQuery as pq
from threading import Thread as th
from abc import abstractmethod,ABCMeta

class EndException(Exception):
    def __init__(self):
        pass
    def __repr__(self):
        return "处理已结束"

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
        try:
            res=req.get(link)
            with open(index,"wb") as file:
                file.write(res.content)
        except:
            print("下载错误!")
        


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
        



    def downloadAllByIndex(self,li,ext,storedir=None):
        """
        直接下载所有文件，按顺序命名
        ext为扩展名
        li为链接表
        如果storedir不给值则采用self.storedir 这样就非线程安全
        否则为线程安全
        """
        if storedir==None:
            storedir=self.storedir
        indexs=["%s/%d%s"%(storedir,i,ext) for i in range(len(li))]
        self.downloadAll(li,indexs)


class DataCatcher(Downloader):
    level=None
    sleeptime=None
    def __init__(self,storedir=None,btype="firefox",catchLevel=5,sleeptime=1,isautoopen=True):
        Downloader.__init__(self,storedir,btype)
        cls=DataCatcher
        cls.level=catchLevel
        if isautoopen:
            DataCatcher.brwoser.get("http://www.huaban.com")
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
        cls(folname,isautoopen=False).getImage(classdesc)

    
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
    __metaclass__=ABCMeta
    #必须要clsid参数 指明以哪个大菜单为准
    #目前所知 0为视频 1为图片 3为小说 2 不明
    def __init__(self,clsid,storedir=None,btype="firefox",update_mod=False):
        Downloader.__init__(self,usebrowser=False,storedir=storedir,btype=btype)
        self.update_mod=update_mod
        # 网址
        self.baseurl="http://sebimeimei123.com"
        # 初始化
        res=req.get(self.baseurl)
        res.encoding="cp936"
        text=res.text
        q=pq(text)
        # 解析
        # 得到大类dl组
        tcls=q("#menu>.wrap>dl")
        #得到大类菜单dl
        # print(tcls)
        ele=pq(tcls[clsid])
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
        #参数 是否使用多线程进行页面加载
        self.ismultithread=False

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
    

    # 由于目录页为通用结构 只需要重写此函数即可实现其他类型页面的抓取
    #对于每个具体的内容页 到此函数时 存储用的目录已经被创建好了 只需要按需填充内容
    # 注意由于使用了多线程 此函数中只能写关于内容抓取的逻辑 而且不能使用成员变量
    @abstractmethod
    def catchContent(self,nowdir,text):
        """
        nowdir 内容存储的目录
        text 内容页的文本
        """
        pass

    
    def catchPage(self,nowdir,link):
        """
        抓取一页的所有图片放到 nowdir中
        """
        text=req.get(link)
        text.encoding="cp936"
        text=text.text
        self.catchContent(nowdir,text)

    #若每一页列表结构有所不同则重写此函数
    #返回names和Links
    #此为默认列表分析函数
    def parseList(self,text):
        p=pq(text)
        list20=p(".list20")
        dds=list20("a")
        names=dds("h2")
        names=[pq(e).text() for e in names]
        #转换为pq节点列表
        dds=[pq(i) for i in dds]
        burl=self.baseurl
        links=[burl+e.attr("href") for e in dds]
        return (names,links)


    def catchOne(self):
        """
        抓取一个目录页面
        """
        nowurl=self.nowPageURL
        text=req.get(nowurl)
        text.encoding="cp936"
        text=text.text
        # 解析
        names,links=self.parseList()
        for n,l in zip(names,links):
            #n为子目录名字
            #l为子页面链接
            print("抓取:%s\n"%n)
            #遇到不存在的目录就创建 如果不是更新模式 就直接在已有的目录里放文件 即假设目录为空
            #如果是更新模式 则遇到已有的目录就认为更新已经结束 则直接抛出EndException
            if not(n in os.listdir(self.basedir)):
                os.mkdir(self.basedir+n)
            elif self.update_mod:
                #如果是更新模式 则遇到目录n已经存在的情况 就直接跳过
                # continue
                # 改变策略 如果是更新模式 就直接抛出“更新已经结束的exception 因为遇到已经存在的 表示更新已经到了末尾
                raise EndException()
            nowdir=str.format("{}{}/",self.basedir,n)
            #通过nowdir和l来抓取
            #如果一页内容直接加载错误 即在catchPage中出错 则在这里处理
            #如果是在catchContent里出错可能需要自己显示一些信息
            try:
                if not self.ismultithread:
                    #不使用
                    self.catchPage(nowdir,l)
                else:
                    #使用多线程 抓取每一内容页的内容
                    tempth=th(target=self.catchPage,args=(nowdir,l))
                    tempth.start()
                
            except:
                #因为有可能出现某一页不能加载 所以这里拦截
                print("一页加载错误!\n")

    def catch(self,pagesum=1):
        """
        抓取多个页面
        """
        for i in range(pagesum):
            print("当前抓取第%d页\n"%self.nowpage)
            try:
                self.catchOne()
            except EndException as e:
                print("更新已经结束!")
            except:
                print("一目录页出现错误，加载下一页\n")
            self.nextPage()
#图片抓取器
class SbmPictureCatcher(SebimmCatcher):
    def __init__(self,sdir=None,update=False):
        SebimmCatcher.__init__(self,clsid=1,storedir=sdir,update_mod=update)

    def catchContent(self,nowdir,text):
        #解析
        page=pq(text)
        content=page(".main-content")
        imgs=content("img")
        srcs=[pq(img).attr("src") for img in imgs]
        #开始下载
        #这里的下载 调用下载器的下载函数  其永远是多线程下载 即对图片本身的下载是多线程的
        self.downloadAllByIndex(srcs,".jpg",storedir=nowdir)

#文章抓取器  
class SbmArticleCatcher(SebimmCatcher):
    def __init__(self,storedir=None,btype="firefox",update=False):
        SebimmCatcher.__init__(self,clsid=3,storedir=storedir,btype=btype,update_mod=update)
    

    #重写catchContent
    def catchContent(self,nowdir,text):
        page=pq(text)
        content=page(".main-content")
        ftext=content.text()
        #nowdir后方带/ 因此这里不加/
        with open("%scontent.txt"%nowdir,"wb") as f:
            f.write(ftext.encode())

#当前未实现 可能需要其他实现
class SbmVideoCacher(SebimmCatcher):
    def __init__(self,storedir=None,btype="firefox",update=False):
        SebimmCatcher.__init__(self,clsid=0,storedir=storedir,btype=btype,update_mod=update)
    
