import tensorflow as tf
import numpy as np
from tensorflow.keras import Input
from tensorflow.keras import Model
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import UpSampling2D
from tensorflow.keras.layers import LeakyReLU
import tensorflow as tf
import csv
from .data_sequencer import DataSequencer

class NestmaticModel(tf.keras.Model):

    def __init__(self):
        super(NestmaticModel, self).__init__()

        self.conv1 = Conv2D(32, (4, 4), activation=LeakyReLU(), padding='same')
        self.conv1_2 = Conv2D(32, (4, 4), activation=LeakyReLU(), padding='same')
        self.conv2 = Conv2D(64, (3, 3), activation=LeakyReLU(), padding='same')
        self.conv2_2 = Conv2D(64, (3, 3), activation=LeakyReLU(), padding='same')
        self.conv3 = Conv2D(128, (3, 3), activation=LeakyReLU(), padding='same')
        self.conv3_2 = Conv2D(128, (3, 3), activation=LeakyReLU(), padding='same')
        self.conv4 = Conv2D(64, (3, 3), activation=LeakyReLU(), padding='same')
        self.conv4_2 = Conv2D(64, (3, 3), activation=LeakyReLU(), padding='same')
        self.conv5 = Conv2D(32, (3, 3), activation=LeakyReLU(), padding='same')
        self.conv6 = Conv2D(24, (3, 3), activation=LeakyReLU(), padding='same')

        
        self.dropout = Dropout(0.2)
        self.pool = MaxPooling2D((2, 2))

    def call(self, inputs, training=False):
        #Encoder
        conv1 = self.conv1(inputs)
        if training:
            conv1 = self.dropout(conv1)
        conv1_2 = self.conv1_2(conv1)
        if training:
            conv1_2 = self.dropout(conv1_2)
        pool1 = self.pool(conv1_2)

        conv2 = self.conv2(pool1)
        if training:
            conv2 = self.dropout(conv2)
        conv2_2 = self.conv2_2(conv2)
        if training:
            conv2_2 = self.dropout(conv2_2)
        pool2 = self.pool(conv2_2)

        conv3 = self.conv3(pool2)
        if training:
            conv3 = self.dropout(conv3)
        conv3_2 = self.conv3_2(conv3)
        if training:
            conv3_2 = self.dropout(conv3_2)
        
        #Decoder
        up1 = concatenate([UpSampling2D((2, 2))(conv3_2), conv2_2], axis=-1)
        conv4 = self.conv4(up1)
        if training:
            conv4 = self.dropout(conv4)
        conv4_2 = self.conv4_2(conv4)
        if training:
            conv4_2 = self.dropout(conv4_2)
        
        up2 = concatenate([UpSampling2D((2, 2))(conv4_2), conv1_2], axis=-1)
        conv5 = self.conv5(up2)
        if training:
            conv5 = self.dropout(conv5)
        conv6 = self.conv6(conv5)
        return conv6


def custom_loss_function(y_actual, y_predicted):
    """Custom loss function that takes into acount failing non zero values more. It is based on MSE.

    Args:
        y_actual (tensor): Tensor with true output value.
        y_predicted (tensor): Tensor with predicte output.

    Returns:
        tensor: Loss value
    """
    loss = tf.where(y_actual > 0, (y_actual-y_predicted)*3, (y_actual-y_predicted)) # It pennalises 3 times a missed ride.
    loss = tf.keras.backend.sum(tf.keras.backend.square(loss))
    return loss

