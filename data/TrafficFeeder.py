from __init__ import *
import pandas as pd
import numpy as np
#store = HDFStore("storeTraffic.h5")
data = pd.Series.from_csv("../data/10min_workload.csv", header=None, index_col=None)

"""
    Contains some functions to extract data from World Cup 1998.

"""
class TrafficFeeder():

    """
        Arg:
            n_input: Size of sliding window
            n_periodic: Number of past periodic
    """
    def __setup__(self, n_input, n_periodic=0):
        self.n_input = n_input
        self.n_periodic = n_periodic

    def normalize(self, dataCount):
        dataNorm = (dataCount - dataCount.min()) / (dataCount.max() - dataCount.min())
        return dataNorm

    def convert(self, data):
        max_val = self.workload.max()
        min_val = self.workload.min()
        return data * (max_val - min_val) + min_val

    def generate(self, range_training):
        # In[62]:

        self.workload = data[142 * range_training[0] - self.n_input:142 * range_training[1]]
        data_training = self.normalize(self.workload)
        X_training = self.getTraining(self.workload)
        data_test = self.normalize(data[142 * range_training[0]:142 * range_training[1]])
        return np.asarray(X_training), np.asarray(data_test)

    def generate_test(self, range_training):
        # In[62]:
        self.workload = data[142 * range_training[0] - self.n_input:142 * range_training[1]]
        X_training = self.getTraining(self.workload)
        data_test = data[142 * range_training[0]:142 * range_training[1]]
        return np.asarray(X_training), np.asarray(data_test)

    def getTraining(self, workload):
        raw_data = data
        data_training = self.normalize(workload)
        max_val = float(workload.max())
        min_val = float(workload.min())
        n_row = data_training.shape[0]
        X_training = []
        for t in range(self.n_input, n_row):
            temp = []
            for i in range(0, self.n_input):
                temp.append(data_training.iloc[t - i - 1])
            for j in range(1, self.n_periodic + 1):
                start_idx = data_training.index[t]
                norVal = (raw_data[start_idx - 142 * j] - min_val) / (max_val - min_val)
                temp.append(norVal)
            X_training.append(temp)
        return X_training

    """
        Arg:
            n_input: Size of sliding window
            n_periodic: Number of past periodic
            range_training: Day range in World Cup data. Ex range_training = (40,46) means that we get all connections from day 40 to 46
        Output:
            Return matrix data with size [142* day_range:(n_input+n_periodic]
    """
    def fetch_traffic_training(self,n_input,n_periodic,range_training):
        self.__setup__(n_input,n_periodic)
        return self.generate(range_training=range_training)

    def fetch_traffic_test(self,n_input,n_periodic,range_test):
        self.__setup__(n_input,n_periodic)
        return self.generate_test(range_training=range_test)

