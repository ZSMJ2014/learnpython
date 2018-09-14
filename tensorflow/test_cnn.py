#
# -*-coding:utf-8 -*-
#
# @Author: zhaojianghua
# @Date  : 2018-09-11 15:06
#

"""

""" 

import cv2
from keras import backend as K
from keras.layers import Conv2D, MaxPooling2D, BatchNormalization, Activation, Dropout, Flatten, Dense, UpSampling2D, Input, add
from keras.models import Model, Sequential, load_model
import numpy as np

rs_img = cv2.imread('/home/zjh/FCN-RSI/data/train-set/seg_20180113_181_2006.jpg')

# 搭建整个网络，保存权值
def createmodel():
    model = Sequential()
    model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))#3 filters, kernel size is (3,3)
    model.add(MaxPooling2D(pool_size=(3,3)))
    model.add(Activation('relu'))#only values large than 0
    model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_2'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Activation('relu'))
    model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_3'))
    model.add(Activation('relu'))
    model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_4'))
    model.add(Activation('relu'))
    model.add(Flatten())
    model.add(Dense(8, activation='relu',name='zjhdens_1'))#fully connected layer, 8 classes

    model.save_weights('rs.h5',overwrite=True)

def visualize(img, file_name):
    girl_img = np.squeeze(img, axis=0)

    max_img = np.max(girl_img)
    min_img = np.min(girl_img)
    girl_img = girl_img-(min_img)
    girl_img = girl_img/(max_img-min_img)
    girl_img = girl_img*256
    cv2.imwrite(file_name, girl_img)


# example1: one convolution layer
createmodel()
model = Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
visualize(conv_girl,'/home/zjh/conv1_output.jpg')


# example2: one convolution layer and one maxpooling layer
createmodel()
model=Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.add(MaxPooling2D(pool_size=(3,3)))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
visualize(conv_girl,'/home/zjh/maxpool1_output.jpg')

# example3: one convolution layer and one maxpooling layer and an activation layer
createmodel()
model=Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.add(MaxPooling2D(pool_size=(3,3)))
model.add(Activation('relu'))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
visualize(conv_girl,'/home/zjh/activation1_output.jpg')

# example4: two convolution layer and one maxpooling layer and an activation layer
createmodel()
model=Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.add(MaxPooling2D(pool_size=(3,3)))
model.add(Activation('relu'))
model.add(Conv2D(3,(3,3), input_shape=rs_img.shape, name='zjhconv_2'))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
visualize(conv_girl,'/home/zjh/conv2_output.jpg')

# example5: two convolution layer and two maxpooling layer and an activation layer
createmodel()
model=Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.add(MaxPooling2D(pool_size=(3,3)))
model.add(Activation('relu'))
model.add(Conv2D(3,(3,3), input_shape=rs_img.shape, name='zjhconv_2'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
visualize(conv_girl,'/home/zjh/maxpool2_output.jpg')


model=Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.add(MaxPooling2D(pool_size=(3,3)))
model.add(Activation('relu'))
model.add(Conv2D(3,(3,3), input_shape=rs_img.shape, name='zjhconv_2'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Activation('relu'))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
girl_img = np.squeeze(conv_girl, axis=0)

max_img = np.max(girl_img)
min_img = np.min(girl_img)
girl_img = girl_img-(min_img)
girl_img = girl_img/(max_img-min_img)
girl_img = girl_img*256
cv2.imwrite('/home/zjh/activation2_output.jpg', girl_img)

model=Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.add(MaxPooling2D(pool_size=(3,3)))
model.add(Activation('sigmoid'))
model.add(Conv2D(3,(3,3), input_shape=rs_img.shape, name='zjhconv_2'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Activation('sigmoid'))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
girl_img = np.squeeze(conv_girl, axis=0)

max_img = np.max(girl_img)
min_img = np.min(girl_img)
girl_img = girl_img-(min_img)
girl_img = girl_img/(max_img-min_img)
girl_img = girl_img*256
cv2.imwrite('/home/zjh/sigmoid_output.jpg', girl_img)

model=Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))
model.add(MaxPooling2D(pool_size=(3,3)))
model.add(Activation('tanh'))
model.add(Conv2D(3,(3,3), input_shape=rs_img.shape, name='zjhconv_2'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Activation('tanh'))
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
girl_img = np.squeeze(conv_girl, axis=0)

max_img = np.max(girl_img)
min_img = np.min(girl_img)
girl_img = girl_img-(min_img)
girl_img = girl_img/(max_img-min_img)
girl_img = girl_img*256
cv2.imwrite('/home/zjh/tanh_output.jpg', girl_img)

model = Sequential()
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_1'))#3 filters, kernel size is (3,3)
model.add(MaxPooling2D(pool_size=(3,3)))
model.add(Activation('relu'))#only values large than 0
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_2'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Activation('relu'))
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_3'))
model.add(Activation('relu'))
model.add(Conv2D(3,(3,3),input_shape=rs_img.shape, name='zjhconv_4'))
model.add(Activation('relu'))
model.add(Flatten())
model.add(Dense(4, activation='relu',name='zjhdens_1'))#fully connected layer, 8 classes
model.load_weights('rs.h5', by_name=True)

girl_batch=np.expand_dims(rs_img, axis=0)# dims from (575,607,3) to (1,575,607,3)
conv_girl=model.predict(girl_batch)
girl_img = np.squeeze(conv_girl, axis=0)

max_img = np.max(girl_img)
min_img = np.min(girl_img)
girl_img = girl_img-(min_img)
girl_img = girl_img/(max_img-min_img)
girl_img = girl_img*256
cv2.imwrite('/home/zjh/dense4_output.jpg', girl_img)
