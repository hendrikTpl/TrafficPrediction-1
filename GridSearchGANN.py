from SplitTrainTest import SplitTrainTest
from sklearn.grid_search import GridSearchCV
from initializer import *
from TrafficFeeder import TrafficFeeder
from GAEstimator import GAEstimator
param_dicts = {
    "cross_rate":np.arange(0.6,1.0,step=0.05),
    "pop_size":np.arange(30,300,step=5),
    "mutation_rate":np.arange(0.01,0.07,step=0.01)
}
n_sliding_window = 4
n_periodic = 1
n_input = n_sliding_window + n_periodic
neural_shape=[n_input,15,1]
dataFeeder = TrafficFeeder()
X,y = dataFeeder.fetch_traffic_training(n_sliding_window,n_periodic,(40,46))
estimator = GAEstimator()
cv = SplitTrainTest(X.shape[0])
fit_param = {'neural_shape':neural_shape}
# estimator.fit(X,y,**fit_param)
gs = GridSearchCV(estimator,param_grid=param_dicts,cv=cv,n_jobs=1,fit_params=fit_param,scoring='mean_squared_error')
gs.fit(X,y)
print gs.best_estimator_