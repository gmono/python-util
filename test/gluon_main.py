from mxnet import gluon
from mxnet import  ndarray as nd
import  numpy as np
from mxnet import autograd as ag
nn=gluon.nn

true_w=10
true_b=2
# y=wx+b
number_exp=5000
xs=nd.array(np.random.normal(loc=10,scale=3,size=(number_exp,)))
nosie=nd.array(np.random.normal(loc=1,scale=1.2,size=number_exp,))
ys=xs*true_w+true_b+0.1*nosie
w=nd.array([0])
b=nd.array([0])
#数据生成完毕 开始定义函数

bsize=50
dataset=gluon.data.ArrayDataset(xs,ys)
data_iter=gluon.data.DataLoader(dataset=dataset,batch_size=bsize,shuffle=True)
net=nn.Sequential()
net.add(nn.Dense(1))
net.initialize()
sq_loss=gluon.loss.L2Loss()
trainer=gluon.Trainer(net.collect_params(),'sgd',{'learning_rate':0.01})

epochs=100
oloss=None
for e in range(epochs):
    tloss=0
    for data,label in data_iter:
        with ag.record():
            output=net(data)
            loss=sq_loss(output,label) #type: nd.NDArray
        loss.backward()
        trainer.step(bsize)
        tloss+=loss.sum().asscalar()/number_exp
    if oloss==None:
        oloss=tloss*1.5
    print("epoch %d,tloss:%f"%(e,tloss))
    if oloss-tloss>abs(oloss) or oloss-tloss<0:
        trainer.set_learning_rate(trainer.learning_rate/1.8)

    oloss=tloss
    print("now rate:%f"%trainer.learning_rate)

p=net[0] # type: nn.Dense
print(str.format("最终结果：weight:{} b:{}",p.weight.data(),p.bias.data()))

