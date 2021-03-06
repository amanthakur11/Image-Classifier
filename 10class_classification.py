import cv2
import numpy as np
import os
import pandas as pd
from random import shuffle
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import tensorflow as tf
from sklearn.metrics import confusion_matrix,accuracy_score
import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

train_dir='/Kaggle_10_Class_Dataset/train'
test_dir='/Kaggle_10_Class_Dataset/test1'
labels=pd.read_csv("/home/amanthakur/Documents/codes/Image classification/trainLabels.csv").values
print(labels)
img_size=50
lr=0.001

model_name="10classclassifier-()-()-model".format(lr,"6conv-basic")
def label_image(img):
    label=img.split('.')
    word_label=labels[int(label[0])-1][1]
    print(word_label)
    if word_label=='airplane': return [1,0,0,0,0,0,0,0,0,0]
    elif word_label=='automobile': return [0,1,0,0,0,0,0,0,0,0]
    elif word_label=='bird': return [0,0,1,0,0,0,0,0,0,0]
    elif word_label=='cat': return [0,0,0,1,0,0,0,0,0,0]
    elif word_label=='deer': return [0,0,0,0,1,0,0,0,0,0]
    elif word_label=='dog': return [0,0,0,0,0,1,0,0,0,0]
    elif word_label=='frog': return [0,0,0,0,0,0,1,0,0,0]
    elif word_label=='horse': return [0,0,0,0,0,0,0,1,0,0]
    elif word_label=='ship': return [0,0,0,0,0,0,0,0,1,0]
    elif word_label=='truck': return [0,0,0,0,0,0,0,0,0,1]
    
def label_of_test_data(img):
    test_label=img.split('.')
    test_label=test_label[1]
    print(test_label)
    return test_label

def create_train_data():
    training_data=[]
    for img in os.listdir(train_dir):
        
        label=label_image(img)
        print(label)
        path=os.path.join(train_dir,img)
        
        #print(path)
        im=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
        img=cv2.resize(im,(img_size,img_size))
        #image = mpimg.imread(path)
        #plt.imshow(image)
        #plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
        #plt.show()
        training_data.append([np.array(img),np.array(label)])
    shuffle(training_data)
    np.save("training_data.npy",training_data)
    return training_data


def process_test_data():
    testing_data=[]
    #y_test=[]
    for img in os.listdir(test_dir):
        #test_label=label_of_test_data(img)
        path=os.path.join(test_dir,img)
        img_num=img.split('.')[0]
        img=cv2.resize(cv2.imread(path,cv2.IMREAD_GRAYSCALE),(img_size,img_size))
        testing_data.append([np.array(img),img_num])
        #y_test.append(test_label)
    print(testing_data)
    np.save("test_data.npy",(testing_data))
    return testing_data


def train_model(train_data):
    train=train_data[:-1000]
    test=train_data[-1000:]
    x=np.array([i[0] for i in train]).reshape(-1,img_size,img_size,1)
    y=[i[1] for i in train]
    
    test_x=np.array([i[0] for i in test]).reshape(-1,img_size,img_size,1)
    test_y=[i[1] for i in test]
    
    tf.reset_default_graph()

    convnet = input_data(shape=[None, img_size,img_size, 1], name='input')
    
    convnet = conv_2d(convnet, 32, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)
    
    convnet = conv_2d(convnet, 64, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)
    
    convnet = conv_2d(convnet, 32, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)
    
    convnet = conv_2d(convnet, 64, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)
    
    convnet = conv_2d(convnet, 32, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)
    
    convnet = conv_2d(convnet, 64, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)
    
    convnet = fully_connected(convnet, 1024, activation='relu')
    convnet = dropout(convnet, 0.8)
    
    convnet = fully_connected(convnet, 10, activation='softmax')
    convnet = regression(convnet, optimizer='adam', learning_rate=lr, loss='categorical_crossentropy', name='targets')
    
    model = tflearn.DNN(convnet,tensorboard_dir='log')
    model.fit({'input': x}, {'targets': y}, n_epoch=5, validation_set=({'input': test_x}, {'targets': test_y}), 
    snapshot_step=500, show_metric=True, run_id=model_name)
    
    model.save(model_name)
    
    if os.path.exists('{}.meta'.format(model_name)):
        model.load(model_name)
        print("model loaded!")
    
    return model

def test_model(model,test_data):
    fig=plt.figure()
    y_pred=[]
    for num,data in enumerate(test_data[:16]):
        #cat:[1,0]
        #dog:[0,1]
        img_num=data[1]
        img_data=data[0]
        y=fig.add_subplot(4,4,num+1)
        orig=img_data
        data=img_data.reshape(img_size,img_size,1)
        model_out=model.predict([data])[0]
        
        if np.argmax(model_out)==0:str_label='airplane'
        elif np.argmax(model_out)==1:str_label='automobile'
        elif np.argmax(model_out)==2:str_label='bird'
        elif np.argmax(model_out)==3:str_label='cat'
        elif np.argmax(model_out)==4:str_label='deer'
        elif np.argmax(model_out)==5:str_label='dog'
        elif np.argmax(model_out)==6:str_label='frog'
        elif np.argmax(model_out)==7:str_label='horse'
        elif np.argmax(model_out)==8:str_label='ship'
        elif np.argmax(model_out)==9:str_label='truck'
        
        y_pred.append(str_label)
        
        y.imshow(orig,cmap='gray')
        plt.title(str_label)
        y.axes.get_xaxis().set_visible(False)
        y.axes.get_yaxis().set_visible(False)
    plt.show()
    with open("submission.file.csv","w") as f:
        f.write("id,label\n")

    with open("submission.file.csv","a") as f:
        for data in test_data:
           img_num=data[1]
           img_data=data[0]
           orig=img_data
           data=img_data.reshape(img_size,img_size,1)
           model_out=model.predict([data])[0]    
           f.write("{},{}\n".format(img_num,model_out[1]))
    return y_pred
           
def confusion_metrics(y_test,y_pred):
    return confusion_matrix(y_test,y_pred)

def accuracy(y_test,y_pred):
    return accuracy_score(y_test, y_pred, normalize=True, sample_weight=None)

train_data=create_train_data()
#if you already have train data
#train_data=np.load("training_data.npy")
test_data=process_test_data()
#test_data=np.load("test_data.npy")
#y_test=y_test[:16]
model=train_model(train_data)

y_pred=test_model(model,test_data)


print(y_pred)
#print("\nconfusion matrix: \n",confusion_metrics(y_test,y_pred))
#print("\naccuracy: ",accuracy(y_test,y_pred))



    

        
    