import numpy as np
from model import NestmaticModel, custom_loss_function
import tensorflow as tf
from PIL import Image
import imageio
   


# example = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/3/8-16-6-6.npz'

# loaded = np.load(example)
# x = np.array(loaded['x'])
# y = np.array(loaded['y'])


# model = NestmaticModel()
# model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])
# # model.build()
# model.predict(x.reshape((1,128,128,20)))
# print(model.evaluate(x.reshape((1,128,128,20)), y.reshape((1,128,128,24))))
# model.load_weights("/home/pedro/nestmatics/Nestmatics-BackEnd/ML/models/trainedModelv5-2-3.h5")
# print(model.evaluate(x.reshape((1,128,128,20)), y.reshape((1,128,128,24))))

# res = model.predict(x.reshape((1,128,128,20)))


def make_gif(arr, path="out.gif", threshold=0.0):
    images = []
    for i in range(0, 24):
        I = np.where(arr[:,:,i]>threshold, 1.0, 0.0)
        I[i:i+20,0:20] = 1.0
        I8 = (((I - I.min()) / (I.max() - I.min())) * 255).astype(np.uint8)
        images.append(I8)
    imageio.mimsave(path, images)

# def make_

# img = Image.fromarray(np.sum(x, axis=-1).astype(np.uint8)*255)
# img.save("file" + str(i) + ".bmp")

# print(np.max(res))