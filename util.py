import requests as req
from selenium import webdriver as dri
import urllib as url
import os
class DataCatcher:
    brwoser=None;
    def __init__(self,storedir=None,btype="firefox"):
        if storedir==None or storedir=='.':
            storedir='.'
        elif not(storedir in os.listdir(".")):
            os.mkdir(storedir)
        
        ts={
            "firefox":dri.Firefox,
            "chrome":dri.Chrome,
            "edge":dri.Edge
        }
        if DataCatcher.brwoser==None:
            DataCatcher.brwoser=ts[btype]()
        
        self.storedir=storedir


    def downloadAll(self,li,indexs):
        """传入一个列表 下载列表中的所有链接
        li:列表
        indexs:文件名表
        """
        if len(li)<len(indexs):
            raise Exception("错误！长度不匹配")

        for link,index in zip(li,indexs):
            res=req.get(link)
            with open(index,"wb") as file:
                file.write(res.content)


    def downloadAllByIndex(self,li,ext):
        """
        直接下载所有文件，按顺序命名
        ext为扩展名
        li为链接表
        """
        indexs=["%s/%d%s"%(self.storedir,i,ext) for i in range(len(li))]
        self.downloadAll(li,indexs)
    
    def getImgFromHuaban(self,link):
        """
        从一个地址下载上面的所有图片
        link:地址
        """
        DataCatcher.brwoser.get(link)
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
    
    def getImageByClass(classdesc: str,folname=None):
        """
        静态方法 用于获取一类图片
        """
        if folname==None:
            folname=classdesc
        DataCatcher(classdesc).getImage(classdesc)
    
    def getImagesByList(lst):
        for i in lst:
            DataCatcher.getImageByClass(i)
        
