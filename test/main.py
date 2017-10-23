from mxnet import ndarray as nd
from mxnet import autograd as ag
from mxnet import gluon
import numpy as np
import random
nn=gluon.nn


true_w=5
true_b=3
# y=wx+b
number_exp=1000
xs=nd.array(np.random.normal(loc=10,scale=3,size=(number_exp,)))
nosie=nd.array(np.random.normal(loc=1,scale=1.2,size=number_exp,))
ys=xs*true_w+true_b+0.1*nosie
w=nd.array([0])
b=nd.array([0])
#数据生成完毕 开始定义函数
def init():
    global w,b
    w = nd.array([0])
    b = nd.array([0])
    w.attach_grad()
    b.attach_grad()

def sq_loss(ey:nd.NDArray,y:nd.NDArray):
    ty=ey.reshape(shape=y.shape)
    loss=(ty-y)**2
    loss=loss.sum()/loss.size
    return loss

def SGD(pars:list,lr:float):
    for par in pars:
        par-=lr*par.grad

def data_iter(pochnum:int):
    idx=list(range(number_exp))
    random.shuffle(idx)
    for e in range(0,number_exp,pochnum):
        tid=nd.array(idx[e:min(e+pochnum,number_exp-e)])
        yield xs.take(tid),ys.take(tid)


def net(txs:nd.NDArray):
    return txs*w+b

def train(epochs:int,trainrate:float):
    for t in range(epochs):
        tloss=0
        for data,label in data_iter(50):
            with ag.record():
                output=net(data)
                loss=sq_loss(output,label)
            loss.backward()
            SGD([w,b],trainrate)
            p=loss.sum() #type:nd.NDArray
            tloss=p.asscalar()
        print("epoch %d,loss:%f"%(t,tloss))

# init()
# train(5,0.001)

for data,label in data_iter(50):
    print(data.dtype,label.dtype)
    print(data,label)