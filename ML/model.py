import tensorflow as tf
from PIL import Image
import numpy as np
from tensorflow.keras import Input
from tensorflow.keras import Model
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import UpSampling2D
import skimage.measure

class NestmaticModel(tf.keras.Model):
    def __init__(self):
        super(NestmaticModel, self).__init__()

        self.input_height = 128
        self.input_width = 128
        self.input_depth = 15

        # self.inputs = Input(shape=(self.input_height, self.input_width , self.input_depth))

        self.conv1 = Conv2D(32, (4, 4), activation='relu', padding='same')
        self.conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')
        self.conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')
        self.conv4 = Conv2D(64, (3, 3), activation='relu', padding='same')
        self.conv5 = Conv2D(32, (3, 3), activation='relu', padding='same')
        self.conv6 = Conv2D(24, (3, 3), activation='relu', padding='same')

        
        self.dropout = Dropout(0.2)
        self.pool = MaxPooling2D((2, 2))

    def call(self, inputs, training=False):
        #Encoder
        print(inputs)
        conv1 = self.conv1(inputs)
        if training:
            conv1 = self.dropout(conv1)
        pool1 = self.pool(conv1)
        conv2 = self.conv2(pool1)
        if training:
            conv2 = self.dropout(conv2)
        pool2 = self.pool(conv2)
        conv3 = self.conv3(pool2)
        if training:
            conv3 = self.dropout(conv3)
        #Decoder
        up1 = concatenate([UpSampling2D((2, 2))(conv3), conv2], axis=-1)
        conv4 = self.conv4(up1)
        if training:
            conv4 = self.dropout(conv4)
        up2 = concatenate([UpSampling2D((2, 2))(conv4), conv1], axis=-1)
        conv5 = self.conv5(up2)
        if training:
            conv5 = self.dropout(conv5)
        conv6 = self.conv6(conv5)#TODO add emporal and weather stuff here
        return conv6


rides = np.load('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/2019-08-12.npy')
streets = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/street.bmp'))
buldings = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/buildings.bmp'))
education = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/Education.bmp'))
entertainment = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/Entertainment.bmp'))
healthcare = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/Healthcare.bmp'))
substance = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/Substenance.bmp'))
transportation = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/Transportation.bmp'))
other = np.asarray(Image.open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1/other.bmp'))

print(rides.shape) #1242, 1157, 24
print(streets.shape) #5785, 6210
ix = int(streets.shape[0]/2)
iy = int(streets.shape[1]/2)

x = np.dstack([
    np.full((128,128,7), 2).astype(np.float16),
    skimage.measure.block_reduce(streets[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16), 
    skimage.measure.block_reduce(buldings[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16), 
    skimage.measure.block_reduce(education[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16), 
    skimage.measure.block_reduce(entertainment[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16), 
    skimage.measure.block_reduce(healthcare[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16), 
    skimage.measure.block_reduce(substance[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16), 
    skimage.measure.block_reduce(transportation[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16), 
    skimage.measure.block_reduce(other[ix:ix+(128*5), iy:iy+(128*5)], (5,5), func=np.max).astype(np.float16)
    ])

y = rides[int(ix/5):int(ix/5)+128, int(iy/5):int(iy/5)+128]

x = np.array([x])
y = np.array([y])

model = NestmaticModel()
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(x, y,epochs=20, batch_size=1)
model.evaluate(x, y)
model.summary()
model.save_weights('my_model.h5')
