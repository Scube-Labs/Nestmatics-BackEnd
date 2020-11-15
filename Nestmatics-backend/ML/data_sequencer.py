from keras.utils import Sequence
import numpy as np
import math
import random
from feature_makers import make_temporal_features
from data_preprocessor import blur

class DataSequencer(Sequence):
   
    def __init__(self, x_set, batch_size, augmentation=False, blur=0):
        
        self.x = x_set
        self.batch_size = batch_size
        self.augmentation = augmentation
        self.blur = blur

    def __len__(self):
        return math.ceil((len(self.x)/self.batch_size))


    def __getitem__(self, idx):

        batch = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]

        batch_x = []
        batch_y = []

        for example in batch:
            loaded = np.load(example[0])
            x = loaded['x']
            y = loaded['y']
            
            for layer in range(0, y.shape[2]):
                y[:,:,layer] = blur(y[:,:,layer], iteration=self.blur)
           
            
            if self.augmentation:
                if random.randint(0, 1) == 1: # 50% chance of flip 
                    x = np.flipud(x)
                    y = np.flipud(y)
                if random.randint(0, 1) == 1: # 50% chance of rotate (90)
                    x = np.rot90(x)
                    y = np.rot90(y)
                    if random.randint(0, 1) == 1: # 50% chance of rotate (180)    
                        x = np.rot90(x)
                        y = np.rot90(y)
                        if random.randint(0, 1) == 1: # 50% chance of rotate (270)        
                            x = np.rot90(x)
                            y = np.rot90(y)
            
            batch_x.append(x)
            batch_y.append(y)

         
        return np.array(batch_x), np.array(batch_y)



    