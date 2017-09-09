# coding=utf-8
import tensorflow as tf
import numpy as np

# 模拟生成100对数据对，对应的函数为y = x * 0.1 + 0.3
x_data = np.random.rand(100).astype("float32")
y_data = x_data * 0.1 + 0.3

# 制定w和b便利的取值范围
w = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
b = tf.Variable(tf.zeros([1]))

y = w * x_data + b

# 最小化均方误差
loss = tf.reduce_mean(tf.square(y - y_data))
optimizer = tf.train.GradientDescentOptimizer(0.5)
train = optimizer.minimize(loss)

# 初始化Tensorflow参数
init = tf.initialize_all_variables()

# 运行数据流图
sess = tf.Session()
sess.run(init)

# 观察多次迭代计算时，w和b的拟合值
for step in xrange(201):
    sess.run(train)
    if step % 20 == 0:
        print (step, sess.run(w), sess.run(b))
