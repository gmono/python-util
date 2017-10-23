"""
此程序用于挑选出每个分类中的下载错误的图片放到一个对应的错误目录中
"""

from matplotlib import pyplot as plt
import os
import shutil
import re
print("请输入图片文件总目录:")
path=input()

# path=r"C:\Users\gaozi\MLFile\hhhh\图片"

os.chdir(path)

#此时获取所有分类
classes=[i for i in os.listdir() if os.path.isdir(i)]
#建立对应错误目录
os.mkdir("错误文件保存")
errdir=os.path.join(".","错误文件保存")
#建立对应类型的目录
for c in classes:
    os.mkdir(os.path.join(errdir,c))
#此时预先工作准备完成

def CopyTo(clss,dirn,fn):
    """把类型A的B目录复制到对应的错误目录"""
    erd=os.path.join(errdir,clss,dirn)
    if not os.path.exists(erd):
        os.mkdir(erd)
    erfn=os.path.join(erd,fn)
    trfn=os.path.join(".",clss,dirn,fn)
    shutil.copy(trfn,erfn)
    os.remove(trfn)
    print(f"Cut file from {trfn} to {erfn}")


def selectError(paths):
    """处理一个目录里的所有文件返回错误文件列表"""
    #得到给定路径的所有文件
    files=os.listdir(paths)
    #过滤得到图片文件
    files=[os.path.join(paths,f) for f in files if not (re.search(".*\.jpg",f) is None)]
    errlist=[]
    for f in files:
        try:
            plt.imread(f)
            plt.close("all") #释放资源
        except:
            errlist.append(f)
    
    return errlist



def selectClass(clss):
    """处理一个类别 得到一个字典数组 dirname:目录名,filenames:文件名列表"""
    #获得一个类别的所有目录
    #所有类型目录都在.目录下
    dirs=os.listdir(clss)
    dirlist=[]
    esum=0
    for d in dirs:
        #合成路径
        errlist=selectError(os.path.join(".",clss,d))
        item={"dirname":d,"filenames":errlist}
        dirlist.append(item)
        print(f"扫描一个目录完成，将处理{len(errlist)}个文件")
        esum+=len(errlist)
        if len(errlist)!=0:
            print(f"本类别:{clss} 当前扫描到损坏文件{esum}个")
    
    return dirlist


def selectAll():
    """处理所有类型的所有错误文件 分类存放"""
    for c in classes:
        arr=selectClass(c)
        for a in arr:
            #这里的a为一个item 字典 dirname为目录名 filenames为文件名列表
            dirname=a["dirname"]
            filenames=a["filenames"]
            for f in filenames:
                CopyTo(c,dirname,f)


#开始进行处理

selectAll()
