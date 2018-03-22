# -*- coding: utf-8 -*-
"""neural_net.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hkMrod2ncLR-9bVvddQDNvqxwf-19Cc4
"""

import tensorflow as tf
tf.test.gpu_device_name()


import pandas as pd
import math
import random
import numpy as np 
import scipy.misc
import matplotlib.pyplot as plt

URL = 'https://s3.us-east-2.amazonaws.com/kaggle551/'

train_x = pd.read_csv(URL + 'train_x_preproc.csv', header=None)
train_y = pd.read_csv(URL + 'train_y.csv', header=None)

train_x = np.array(train_x.as_matrix())
train_y = np.array(train_y[0])

test_x = pd.read_csv(URL + 'test_x_preproc.csv', header=None)
test_x = np.array(test_x.as_matrix())

print('data retrieved')

train_x[train_x < 235] = 0 
test_x[test_x < 235] = 0 

train_x /= 255.0
test_x /= 255.0

print(train_x.shape)
print(train_y.shape)
print(test_x.shape)

# sigmoid function
def sigmoid(x):
    return 1 / (1 + np.exp(-1 * x))

# derivative of our sigmoid function, in terms of the output (i.e. y)
def dsigmoid(x):
    return 1.0 - x**2

# Make a matrix 
def matrix(m, n, fill=0.0):
    return np.zeros(shape=(m,n)) + fill

# Make a random matrix
def rand_matrix(m, n, a=0, b=1):
	return np.random.rand(m, n) * (b - a) + a

# use logistic regression loss function 
def loss_fn(predict, truth):
    n = len(truth)
    loss = (- 1 / n) * np.sum(truth * np.log(predict) + (1 - truth) * (np.log(1 - predict)))
    loss = np.squeeze(loss)

    return loss

class NN:
    def __init__(self, ni, nh, no):
        # number of input, hidden, and output nodes
        self.ni = ni
        self.nh = nh
        self.no = no
        
        # bias vectors 
#         self.bh = np.zeros((1, self.nh))
#         self.bo = np.zeros((1, self.no))
        self.bh = np.ones(self.nh)
        self.bo = np.ones(self.no)
    

        # create weights
        # default to range (-0.5, 0.5)
        self.wh = rand_matrix(self.ni, self.nh, -0.5, 0.5)
        self.wo = rand_matrix(self.nh, self.no, -0.5, 0.5)
        
    
    # training feed forward, obtain output from weight matrices and bias vectors
    def propagate(self, inputs):
        self.ai = inputs

        # hidden layers activations
        #bh is bias of hidden layers
        self.ah = np.dot(self.ai, self.wh) + self.bh

        # hidden output 
        self.oh = np.tanh(self.ah)

        # output layers activations
        self.ao = np.dot(self.ah, self.wo) + self.bo
        
        #h output layers output 
        self.oo = sigmoid(self.ao)

    # training back propagation, updates neural network's weight matrices and bias vectors
    def backPropagate(self, x, y, eta):
        n = x.shape[0]
        self.dao = self.oo - y
        self.dwo = np.dot(self.oh.T, self.dao) / n
        self.dbo = np.sum(self.dao) / n
        
        self.dah = np.dot(self.dao, self.wo.T)*(1-np.tanh(self.ah))
        self.dwh = np.dot(x.T, self.dah) / n
        self.dbh = np.sum(self.dah) / n
        
        #update weights using gradient descent method. learning rate = eta
        self.wo = self.wo - eta * self.dwo
        self.wh = self.wh - eta * self.dwh
        self.bo = self.bo - eta * self.dbo
        self.bh = self.bh - eta * self.dbh
        
        
    
    def predict(self, x):
        ah = np.dot(x, self.wh) + self.bh

        # hidden output 
        oh = np.tanh(ah)

        # output layers activations
        ao = np.dot(ah, self.wo) + self.bo
        
        #h output layers output 
        oo = sigmoid(ao)
        return oo
      
    
    # takes in Y     
    def train(self, X, Y, iterations = 1000, eta=0.5):
        trend = []
        
        # create output matrix
        Y_m = np.zeros((X.shape[0], 10))
        for i in range(len(Y)):
          Y_m[i][int(Y[i])] = 1

        for i in range(iterations):
            output = self.propagate(X)
            self.backPropagate(X, Y_m, eta)

            pred = np.argmax(self.oo, axis=1)
            loss = loss_fn(self.oo, Y_m)
            diff = Y - pred
            acc = (diff == 0).sum() / len(Y)
            if( i % (iterations / 100) == 0): 
              trend.append([acc, loss])
              print("iteration ", i, " :    training acc: ", acc, "   training loss: ", loss)

        return trend

nn = NN(ni=4096, nh=6, no=10)

nn.propagate(train_x)
print("output: ", nn.ao)
print("output shape: ", nn.ao.shape)

cross_validation=5
valid_split = 0.05

# best_pred = [accuracy, nn, training trend]
best_pred = (0, 0, [])

for valid in range(cross_validation):
    print("\nCross Validation fold ", valid)
  
    # randomly split the dataset into validation and training sets 
    mask = np.random.rand(train_x.shape[0]) <= valid_split
    t_x = train_x[mask]
    t_y = train_y[mask]

    v_x = train_x[~mask]
    v_y = train_y[~mask]
    
    nn = NN(ni=4096, nh=6, no=10)
    
    res = nn.train(t_x, t_y, 2000)
    
    # validate with validation set after the training
    v_o = nn.predict(v_x)
    pred = np.argmax(v_o, axis=1)
    diff = v_y - pred
    acc = (diff == 0).sum() / len(v_y)
   
    
    if(acc > best_pred[0]): best_pred = (acc, nn, res)

best_nn = best_pred[1]

pred = best_nn.predict(test_x)
pred = np.argmax(v_o, axis=1)

arr = np.arange(len(pred))

np.savetxt('nn_prediction.csv', np.dstack((arr, pred))[0], "%d,%d", header = "Id,Label", comments='')

epoch = np.arange(len(res))

plt.figure(1)
plt.title('Neural Network Training Loss Trend')
plt.plot(epoch, res[:,1], 'r--')

plt.figure(2)
plt.title('Neural Network Training Accuracy Trend')
plt.plot(epoch, res[:,0], 'b')
plt.ylim(0, 1)

plt.show()

cross_validation=5
valid_split = np.arange(0.02, 0.3, 0.3)

# best_pred = [accuracy, nn, training trend]
best_pred = (0, 0, 0, [])

# best_split = [accuracy, split]

for split in valid_split:
  split_acc = 0
  for valid in range(cross_validation):
      print("\nCross Validation fold ", valid)

      # randomly split the dataset into validation and training sets 
      mask = np.random.rand(train_x.shape[0]) <= split
      t_x = train_x[mask]
      t_y = train_y[mask]

      v_x = train_x[~mask]
      v_y = train_y[~mask]

      nn = NN(ni=4096, nh=6, no=10)

      res = nn.train(t_x, t_y, 2000)

      # validate with validation set after the training
      v_o = nn.predict(v_x)
      pred = np.argmax(v_o, axis=1)
      diff = v_y - pred
      acc = (diff == 0).sum() / len(v_y)
      
      split_acc = acc / cross_validation
      
  if(split_acc > best_pred[0]): best_pred = (acc, split, nn, res)

best_pred

best_split = best_pred[1]

best_nn = best_pred[2]

pred = best_nn.predict(test_x)
pred = np.argmax(v_o, axis=1)

arr = np.arange(len(pred))

np.savetxt('nn_prediction_param_valid_split.csv', np.dstack((arr, pred))[0], "%d,%d", header = "Id,Label", comments='')



cross_validation=5
valid_split = 0.05

# best_pred = [accuracy, nn, training trend]
best_pred = (0, 0, [])

trends = []
layers = np.arange(1, 7)

for layer in layers:
  for valid in range(cross_validation):
      print("\nCross Validation fold ", valid)

      # randomly split the dataset into validation and training sets 
      mask = np.random.rand(train_x.shape[0]) <= valid_split
      t_x = train_x[mask]
      t_y = train_y[mask]

      v_x = train_x[~mask]
      v_y = train_y[~mask]

      nn = NN(ni=4096, nh=layer, no=10)

      res = nn.train(t_x, t_y, 2000)

      # validate with validation set after the training
      v_o = nn.predict(v_x)
      pred = np.argmax(v_o, axis=1)
      diff = v_y - pred
      acc = (diff == 0).sum() / len(v_y)


      if(acc > best_pred[0]): best_pred = (acc, nn, res) 
   
  trends.append(best_pred[2])

res = np.array(best_pred[2])
epoch = np.arange(len(res))

plt.figure(1)
plt.plot(epoch[1:], res[:,1][1:], 'r--')



plt.figure(2)
plt.plot(epoch, res[:,0], 'b')
plt.ylim(0, 0.5)

plt.show()



