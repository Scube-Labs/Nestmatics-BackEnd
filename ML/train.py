import numpy as np
import csv
from modelv2 import NestmaticModel, custom_loss_function
from data_sequencer_copy import DataSequencer
import datetime
import tensorflow as tf

# Initial code to train model "manually", for deployment purposes this will not be used, the function on the model.py will be used instead.


train = list(csv.reader(open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/3/train.csv')))
validate = list(csv.reader(open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/3/validation.csv')))


train_sequencer = DataSequencer(train, batch_size=256, blur=5, augmentation=True)
validation_sequencer = DataSequencer(validate, batch_size=256, blur=5)

model = NestmaticModel()
model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])


log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

model.predict(np.zeros((1,128,128,20)))
model.load_weights("/home/pedro/nestmatics/Nestmatics-BackEnd/ML/models/trainedModelv5-2.h5")

model.fit(train_sequencer, validation_data=validation_sequencer, callbacks=[tensorboard_callback], epochs=10, shuffle=True)

model.save_weights('models/trainedModelv5-2-3.h5')