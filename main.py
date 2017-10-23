import catcher as cer
import os
if __name__=="__main__":
    print("欢迎使用工口资源抓取器！\n")
    print("请选择抓取类型(1.视频,2.图片,3.小说):")
    namemap={
        1:"视频",
        2:"图片",
        3:"小说"
    }
    sele=int(input())
    dname=namemap[sele]
    #上面的dname留到后面输入路径后用
    print("请输入存储路径，当前路径请输入 . ：")
    path=input()
    os.chdir(path)
    #打开大类路径
    if not(dname in os.listdir(".")):
        os.mkdir(dname)
    #进入大类目录
    os.chdir(dname)
    #根据sele使用不同的类
    classmap={
        1:cer.SbmVideoCacher,
        2:cer.SbmPictureCatcher,
        3:cer.SbmArticleCatcher
    }
    # 创建抓取器对象
    ser=classmap[sele]()
    print("\n")
    print("请选择分类:")
    cn=input()
    ser.selectClass(cn)
    #选择起始页和页数 
    startpage=1
    print("请选择起始页(默认为1):")
    startpage=int(input())
    print("请输入抓取的页数:")
    pages=int(input())
    #多线程
    print("请选择是否使用多线程页面加载(0不使用，1使用 使用可能被防火墙拦截):")
    s=int(input())
    if s==0:
        ser.ismultithread=False
    else:
        ser.ismultithread=True
    
    # 开始
    print("开始抓取\n")
    ser.selectPage(startpage)
    
    ser.catch(pages)

    print("\n正在等待所有线程结束.......")