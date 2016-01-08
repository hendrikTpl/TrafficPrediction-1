
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import sys
from pandas import HDFStore
import matplotlib.pyplot as pl
import lasagne as ls
from theano import tensor as T
from lasagne.layers import InputLayer, DenseLayer
from lasagne.updates import nesterov_momentum,sgd
from lasagne.nonlinearities import rectify
from nolearn.lasagne import NeuralNet
from DemoPyEvolve import PyEvolve
from ConfigParser import SafeConfigParser
from __init__ import *
store = HDFStore("storeTraffic.h5")
#"ita_public_tools/output/data.csv"
data = pd.Series.from_csv("10min_workload.csv",header=None,index_col=None)
def read_config():
    parser = SafeConfigParser()
    parser.read('configNeural.cfg')
    hidden_layer = int(parser.get("Neural","hidden_layer"))
    epochs = int(parser.get("Neural","epochs"))
    return hidden_layer, epochs
class LoadParam():
    def initNN(self):
        #Build layer for MLP
        hidden_layer, epochs = read_config()
        l_in = ls.layers.InputLayer(shape=(None,self.n_input+self.n_periodic),input_var=None)
        l_hidden = ls.layers.DenseLayer(l_in,num_units=hidden_layer,nonlinearity=ls.nonlinearities.rectify)
        network = l_out = ls.layers.DenseLayer(l_hidden,num_units=1)
        print "Neural network initialize"
        #Init Neural net
        net1 = NeuralNet(
            layers=network,
            # optimization method:
            update=nesterov_momentum,
            update_learning_rate=0.000001,
            update_momentum=0.9,
            regression=True,  # flag to indicate we're dealing with regression problem
            max_epochs=800,  # we want to train this many epochs
            eval_size = 0.4
#             verbose=1,
        )
        return net1
    def initGN(self,params=None):
        self.l_in = ls.layers.InputLayer(shape=(None,self.n_input+self.n_periodic),input_var=None,W=params.T)
        self.l_hidden = ls.layers.DenseLayer(self.l_in,num_units=15,nonlinearity=ls.nonlinearities.rectify)
        self.network = l_out = ls.layers.DenseLayer(self.l_hidden,num_units=1)
            #Init Neural net
        net1 = NeuralNet(
            layers=self.network,
            # optimization method:
            update=nesterov_momentum,
            update_learning_rate=0.000001,
            update_momentum=0.9,
            regression=True,  # flag to indicate we're dealing with regression problem
            max_epochs=800,  # we want to train this many epochs
#                 verbose=1,
            eval_size = 0.4
        )
        return net1
    def __init__(self,n_type,n_input,n_periodic=0):
        self.n_input = n_input
        self.n_periodic = n_periodic
        self.n_type = n_type
        if(n_periodic==0):
            self.net = self.initNN()
            if(n_type=="NN"):
                self.net.load_params_from('Params/saveNeuralNetwork_1e-05_%s.tdn'%n_input)
            elif(n_type=="GN"):
                self.net.load_params_from('GeneticParams/saveNeuralNetwork_1e-05_%s.tdn'%n_input)
        else:
            self.net = self.initNN()
            if(n_type=="NN"):
                self.net.load_params_from('ParamsPeriodic/saveNeuralNetwork_1e-05_%s.tdn'%n_input)
            elif(n_type=="GN"):
                self.net.load_params_from('GeneticParamsPeriodic/saveNeuralNetwork_1e-05_%s.tdn'%n_input)
    def normalize(self,dataCount,dataTest):
        dataNorm = pd.Series(np.zeros(dataCount.shape[0]),dtype=np.float64)
        dataNorm = (dataCount - dataTest.min())/(dataTest.max()-dataTest.min())
        return dataNorm
    def normalize(self,dataCount):
        dataNorm = pd.Series(np.zeros(dataCount.shape[0]),dtype=np.float64)
        dataNorm = (dataCount - dataCount.min())/(dataCount.max()-dataCount.min())
        return dataNorm
    def convert(self,data):
        max_val = self.workload.max()
        min_val = self.workload.min()
        return (data*(max_val-min_val)+min_val)
    def generate(self,range_training,range_test=1):
        # In[62]:
        print "Loading storage"
        print "generate data"
        self.workload = data[142*range_training[0]-self.n_input:142*range_training[1]]
        data_training = self.normalize(self.workload)
        X_training = self.getTraining(data_training)
#         data_validation = data[142*range_training[1]-self.n_input:142*(range_training+range_test)]
        data_test = self.normalize(data[142*range_training[0]:142*range_training[1]])
        return np.asarray(X_training),np.asarray(data_test)
    def getTraining(self,data_training):
        raw_data = store["raw_data_conn"]
        n_row = data_training.shape[0]
        print "Generate X_traing, y_traing"
        print "X_training loading..."
    #     X_training = np.asarray([[data.iloc[t-i-1] for i in range(0,n_input)]
    #                  for t in np.arange(n_input,n_row)])
        X_training = []
        for t in range(self.n_input,n_row):
            temp = []
            for i in range(0,self.n_input):
                temp.append(data_training.iloc[t-i-1])
            for j in range(1,self.n_periodic+1):
                start_idx = data_training.index[t]
                temp.append(raw_data[start_idx-142*j])
            X_training.append(temp)
        return X_training
    def predict(self,X_test):
#         dataTest= pd.read_sql("SELECT count FROM workload where time >= 895096802-%d and time < 895096802+86400"%(n_input),conn)["count"]
        return self.net.predict(X_test)
    def score(self,X_test,y_actual):
        return self.net.score(X_test,y_actual)
#     def plot_loss(self):
#         """
#         Plot the training loss and validation loss versus epoch iterations with respect to 
#         a trained neural network.
#         """
#         net = self.net
#         train_loss = np.array([i["train_loss"] for i in net.train_history_])
#         valid_loss = np.array([i["valid_loss"] for i in net.train_history_])
#         pl.plot(train_loss, linewidth = 3, label = "train")
#         pl.plot(valid_loss, linewidth = 3, label = "valid")
#         pl.grid()
#         pl.legend()
#         pl.xlabel("epoch")
#         pl.ylabel("loss")
#         #pyplot.ylim(1e-3, 1e-2)
#         pl.yscale("log")
#         pl.show()
    def plot_loss(self,train_loss,valid_loss):
        """
        Plot the training loss and validation loss versus epoch iterations with respect to 
        a trained neural network.
        """
        pl.plot(train_loss, linewidth = 2, label = "train")
        pl.plot(valid_loss, linewidth = 2, label = "valid")

        pl.legend()
        pl.xlabel("epoch")
        pl.ylabel("loss")
        #pyplot.ylim(1e-3, 1e-2)
#         pl.yscale("log")
        pl.show()
    def fitTraining(self,X_training,y_training):
        if(self.n_type=="GN"):
            geneticEngine = PyEvolve(n_input)
            geneticEngine.fit()
            nnParams = geneticEngine.getParam()
            self.net = self.initGN(nnParams)
        else:
            self.net = self.initNN()
        self.net.fit(X_training,y_training)


# In[7]:

n_input = 13
print n_input
nn = LoadParam("NN",n_input,1)
gn = LoadParam("GN",n_input,1)
#     print "With input"
#     for i in np.arange(1,data[0:142*30].shape[0],1):
i = 3
skip_list = 2
print "%d-%d"%(i,i+skip_list)
# X_training,y_training = nn.generate((i,i+skip_list))
X_test,y_test = nn.generate((i,i+skip_list))

# Xp_training,yp_training = nnp.generate((i,i+skip_list))
# Xp_test,yp_test = nnp.generate((i+skip_list+1,i+skip_list+2))
# nn.fitTraining(X_training,y_training)
# nnp.fitTraining(Xp_training,yp_training)
# dataX = data[142*3:142*5]
print "NN score = %f"%nn.score(X_test,y_test)
print "GN score = %f"%gn.score(X_test,y_test)


# In[ ]:

# train_loss = np.array([i["train_loss"] for i in nn.net.train_history_])
# valid_loss = np.array([i["train_loss"] for i in nnp.net.train_history_])


# In[ ]:

# ax = pl.subplot()
# # ax.plot(train_loss,label="train loss nn")
# ax.plot(valid_loss,label="train_loss gn")
# ax.legend()
# pl.show()


# In[6]:

workload = nn.workload
gn_pred = nn.convert(gn.predict(X_test))
nn_pred = nn.convert(nn.predict(X_test))
y_actual = nn.convert(y_test)
ax = pl.subplot()
ax.set_color_cycle(['red','blue','green'])
ax.plot(gn_pred,label="Genetic Neural Network")
# ax.plot(nn_pred,label="Neural Network")
ax.set_title("Genetic Neural Network")
ax.plot(y_actual,'--',label="Actual")
ax.plot()
ax.legend()
# ax1.plot(GN.y_training)
# ax1.legend(["Predict","Actual"])
# # ax1.set_color_cycle(['blue','red'])
# ax2.plot(nn_pred,label="Neural Network")
# ax2.plot(NN.y_training)
# ax2.set_title("Neural Network")
# ax2.set_color_cycle(['blue','red'])
pl.show()


# In[ ]:



