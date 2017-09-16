import catcher as cer
import os
if __name__=="__main__":
    print("欢迎使用色图抓取器！\n")
    print("请输入存储路径，当前路径请输入 . ：")
    path=input()
    os.chdir(path)
    ser=cer.SebimmCatcher()
    print("\n")
    print("请选择分类:")
    cn=input()
    ser.selectClass(cn)

    startpage=1
    print("请选择起始页(默认为1):")
    startpage=int(input())
    print("请输入抓取的页数:")
    pages=int(input())
    # 开始
    print("开始抓取\n")
    ser.selectPage(startpage)
    
    ser.catch(pages)