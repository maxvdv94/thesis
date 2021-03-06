# -*- coding: utf-8 -*-
"""Kopie20 van GANomaly_3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12dgp_lFC2hekisbddhDY9kbEAzwifJDA
"""

#mounting drive 
from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
## packages
import matplotlib

matplotlib.use('Agg')

from keras.datasets import mnist
from keras.layers import Input, Dense, Reshape, Flatten, Dropout
from keras.layers import BatchNormalization, Activation, ZeroPadding2D
from keras.layers import MaxPooling2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.models import Sequential, Model
from keras.optimizers import Adam

from sklearn.metrics import roc_auc_score
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
# %matplotlib inline
import numpy as np
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

## Loading the data
X_train = np.load('/content/drive/My Drive/Thesis_code/thesis_data/training_test_sets/X_train.npy')
Y_train = np.load('/content/drive/My Drive/Thesis_code/thesis_data/training_test_sets/Y_train.npy')
X_test = np.load('/content/drive/My Drive/Thesis_code/thesis_data/training_test_sets/X_test.npy')
Y_test = np.load('/content/drive/My Drive/Thesis_code/thesis_data/training_test_sets/Y_test.npy')

print(X_train.shape)
print(Y_train.shape)
print(X_test.shape)
print(Y_test.shape)

np.unique(Y_test, return_counts=True)

print(type(X_test[0]))

print(np.min(X_train[1001]), np.max(X_train[1001]))
print(np.min(X_test[100]), np.max(X_test[100]))

X_train = X_train*255
X_test = X_test*255

print(np.min(X_train), np.max(X_train))
print(np.min(X_test), np.max(X_test))

## Scaling the data between -1 & 1
X_train = (X_train.astype(np.float32) -127.5)/127.5
X_test = (X_test.astype(np.float32) -127.5)/127.5

print(np.min(X_train[10]), np.max(X_train[10]))
print(np.min(X_train), np.max(X_train))

print(np.min(X_test[1000]), np.max(X_test[1000]))
print(np.min(X_test), np.max(X_test))

print(np.max(X_train[80] * 127.5 +127.5))

plt.imshow((X_train[80] * 127.5 +127.5).astype(int))

plt.imshow((X_test[30] * 127.5 +127.5).astype(int))

latent_dim = 150
input_shape = (128, 128, 3)


def make_encoder():
  modelE = Sequential()
  modelE.add(Conv2D(64, kernel_size=(4, 4), padding="same", input_shape=input_shape))
  modelE.add(BatchNormalization(momentum=0.8))
  modelE.add(Activation("relu"))
  modelE.add(MaxPooling2D(pool_size=(2, 2)))
  modelE.add(Conv2D(128, kernel_size=(4, 4),  padding="same"))
  modelE.add(BatchNormalization(momentum=0.8))
  modelE.add(Activation("relu"))
  modelE.add(MaxPooling2D(pool_size=(2, 2)))
  modelE.add(Conv2D(128, kernel_size=(4, 4),  padding="same"))
  modelE.add(BatchNormalization(momentum=0.8))
  modelE.add(Activation("relu"))
  modelE.add(MaxPooling2D(pool_size=(2, 2)))
  modelE.add(Conv2D(256, kernel_size=(4, 4), padding="same"))
  modelE.add(BatchNormalization(momentum=0.8))
  modelE.add(Activation("relu"))
  modelE.add(MaxPooling2D(pool_size=(2, 2)))
  modelE.add(Conv2D(512, kernel_size=(4, 4), padding="same"))
  modelE.add(BatchNormalization(momentum=0.8))
  modelE.add(Activation("relu"))
  modelE.add(MaxPooling2D(pool_size=(2, 2)))
  modelE.add(Conv2D(512, kernel_size=(4, 4), padding="same"))
  modelE.add(Activation("relu"))
  modelE.add(Conv2D(512, kernel_size=(4, 4), padding="same"))
  modelE.add(Activation("relu"))
  return modelE

# Encoder 1
enc_model_1 = make_encoder()
img = Input(shape=input_shape)
z = enc_model_1(img)
encoder1 = Model(img, z)

enc_model_1.summary()

encoder1.summary()

# Generator
batch_size = 60

modelG = Sequential()
modelG.add(Conv2DTranspose(512, kernel_size=(4, 4), strides=2, padding="same", input_shape=(4, 4, 512)))
modelG.add(BatchNormalization(momentum=0.999))
modelG.add(LeakyReLU(alpha=0.2))
modelG.add(Conv2DTranspose(512, kernel_size=(4, 4), strides=2, padding="same"))
modelG.add(BatchNormalization(momentum=0.999))
modelG.add(LeakyReLU(alpha=0.2))
modelG.add(Conv2DTranspose(128, kernel_size=(4, 4), strides=2, padding="same"))
modelG.add(BatchNormalization(momentum=0.999))
modelG.add(LeakyReLU(alpha=0.2))
modelG.add(Conv2DTranspose(128, kernel_size=(4, 4), strides=2, padding="same"))
modelG.add(BatchNormalization(momentum=0.999))
modelG.add(LeakyReLU(alpha=0.2))
modelG.add(Conv2DTranspose(256, kernel_size=(4, 4), strides=2, padding="same"))
modelG.add(BatchNormalization(momentum=0.999))
modelG.add(LeakyReLU(alpha=0.2)) 
modelG.add(Conv2D(256, kernel_size=(4, 4),  padding="same"))
modelG.add(Activation("relu"))
modelG.add(Conv2DTranspose(3, kernel_size=(4, 4), strides=1, padding="same", activation='tanh'))

modelG.summary()

z = Input(shape=(4, 4, 512))
gen_img = modelG(z)
generator = Model(z, gen_img)

generator.summary()

# Encoder 2
enc_model_2 = make_encoder()
img = Input(shape=input_shape)
z = enc_model_2(img)
encoder2 = Model(img, z)

encoder2.summary()

# Discriminator
modelD = Sequential()
modelD.add(Conv2D(32, kernel_size=6, strides=2, input_shape=(128, 128, 3), padding="same"))
modelD.add(LeakyReLU(alpha=0.2))
modelD.add(Dropout(0.3))
modelD.add(Conv2D(64, kernel_size=6, strides=2, padding="same"))
modelD.add(ZeroPadding2D(padding=((0, 1), (0, 1))))
modelD.add(BatchNormalization(momentum=0.99))
modelD.add(LeakyReLU(alpha=0.2))
modelD.add(Dropout(0.3))
modelD.add(Conv2D(128, kernel_size=6, strides=2, padding="same"))
modelD.add(BatchNormalization(momentum=0.99))
modelD.add(LeakyReLU(alpha=0.2))
modelD.add(Dropout(0.3))
modelD.add(Conv2D(256, kernel_size=6, strides=1, padding="same"))
modelD.add(BatchNormalization(momentum=0.99))
modelD.add(LeakyReLU(alpha=0.2))
modelD.add(Dropout(0.3))
modelD.add(Flatten())
modelD.add(Dense(1, activation='sigmoid'))

discriminator = modelD
optimizer = Adam(0.00001, 0.5)

discriminator.summary()

# Build and compile the discriminator
discriminator.compile(loss=['binary_crossentropy'],
                          optimizer=optimizer,
                          metrics=['accuracy'])

discriminator.trainable = False

layer_name = 'conv2d_18'
get_features = Model(inputs=discriminator.input,
                                 outputs=discriminator.get_layer(layer_name).output)

batch_size = 60

# Adversarial ground truths
fake = np.zeros((batch_size, 1))
real = np.ones((batch_size, 1))

g_loss_list = []
d_loss_list = []

# First image encoding
img = Input(shape=input_shape)
z = encoder1(img)
f = get_features(img)

# Generate image from encoding
img_ = generator(z)
f_ = get_features(img_)

#second image encoding
z_ = encoder2(img_)
real = discriminator(img_)

# Set up and compile the combined model
# Trains generator to fool the discriminator
# and decrease loss between (img, _img) and (z, z_)
bigan_generator = Model(img, [real, img_, z_])
bigan_generator.compile(loss=['binary_crossentropy', 'mean_absolute_error',
                                  'mean_squared_error'], optimizer=optimizer, loss_weights=[1, 1, 1])

bigan_generator.summary()

idx = np.random.randint(0, X_train.shape[0], batch_size)
imgs = X_train[idx]
z = encoder1.predict(imgs)
imgs_ = generator.predict(z)
real = discriminator.predict(imgs_)
f = get_features.predict(imgs_)



g_loss = bigan_generator.train_on_batch(imgs, [real, imgs, z])

print(g_loss)

print(real.shape)
print(fake.shape)
print(X_train.shape)
print(X_test.shape)
print(Y_train.shape)
print(Y_test.shape)

np.unique(Y_test, return_counts=True)

print(real.dtype)
print(fake.dtype)
print(X_train.dtype)
print(X_test.dtype)
print(Y_train.dtype)
print(Y_test.dtype)

## loading the weights to return training
generator.load_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_gen_weights_kopie20_ganomaly.h5')
encoder1.load_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_enc1_weights_kopie20_ganomaly.h5')
encoder2.load_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_enc2_weights_kopie20_ganomaly.h5')
discriminator.load_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_dis_weights_kopie20_ganomaly.h5')

idx = np.random.randint(0, X_train.shape[0], batch_size)
imgs = X_train[idx]
z = encoder1.predict(imgs)
imgs_ = generator.predict(z)

predicted_images_10 = (imgs_ *127.5 + 127.5).astype(int)

plt.imshow(predicted_images_10[5])

epochs = 110
steps_per_epoch = 200

for epoch in range(epochs):
  for steps in range(steps_per_epoch):

    # ---------------------
    #  Train Discriminator
    # ---------------------
    # Select a random batch of images and encode/decode/encode
    idx = np.random.randint(0, X_train.shape[0], batch_size)
    imgs = X_train[idx]
    z = encoder1.predict(imgs)
    imgs_ = generator.predict(z)
    f = get_features.predict(imgs)
    #if steps % 5 == 0:

      # Train the discriminator (imgs are real, imgs_ are fake)
    d_loss_real = discriminator.train_on_batch(imgs, real)
    d_loss_fake = discriminator.train_on_batch(imgs_, fake)
    d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

    # ---------------------
    #  Train Generator
    # ---------------------
  
    # Train the generator (z -> img is valid and img -> z is is invalid)
    ## Intermediate outputs and adversarial loss calculation
  
    g_loss = bigan_generator.train_on_batch(imgs, [real, imgs, z])

    g_loss_list.append(g_loss)
    d_loss_list.append(d_loss)

  ## saving the predicted and real images at some points during the training
  if epoch % 10 == 0 and epoch > 0:
    encoded_images = encoder1.predict(imgs)
    predicted_temp = generator.predict(encoded_images)
    np.save('/content/drive/My Drive/Thesis_code/thesis_data/predicted_images_20/real' + str(epoch), imgs)
    np.save('/content/drive/My Drive/Thesis_code/thesis_data/predicted_images_20/' + str(epoch), predicted_temp)


    ## saving the model weights
  if epoch % 2 == 0 and epoch > 0:
    generator.save_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_gen_weights_kopie20_ganomaly.h5')
    encoder1.save_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_enc1_weights_kopie20_ganomaly.h5')
    encoder2.save_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_enc2_weights_kopie20_ganomaly.h5')
    discriminator.save_weights('/content/drive/My Drive/Thesis_code/thesis_data/models/d_dis_weights_kopie20_ganomaly.h5')

  ## 
  # Plot the progress
  print("%d [D loss: %f, acc: %.2f%%] [G loss: %f]" %
        (epoch, d_loss[0], 100 * d_loss[1], g_loss[0]))

print(len(d_loss_list))

print(d_loss_fake)
print(d_loss_real)

plt.plot(np.asarray(g_loss_list)[:, 0], label='G loss')
plt.plot(np.asarray(d_loss_list)[:, 0], label='D loss')
plt.plot(np.asarray(d_loss_list)[:, 1], label='D accuracy')
plt.legend(bbox_to_anchor=(1, 1))

loss_all = np.asarray([np.asarray(g_loss_list)[:, 0],
                        np.asarray(d_loss_list)[:, 0], np.asarray(d_loss_list)[:, 1]])

## Predicting on the test set
z1_gen_ema = encoder1.predict(X_test)
reconstruct_ema = generator.predict(z1_gen_ema)
z2_gen_ema = encoder2.predict(reconstruct_ema)

print(z1_gen_ema.shape)
print(reconstruct_ema.shape)
print(z2_gen_ema.shape)

print(np.min(reconstruct_ema[0]), np.max(reconstruct_ema[0]))

predicted_images = reconstruct_ema
predicted_images = (predicted_images *127.5 + 127.5).astype(int)
X_test_2 = (X_test *127.5 +127.5).astype(int)
type(predicted_images)

print(predicted_images.shape)

# saving the images
#np.save('/content/drive/My Drive/Thesis_code/thesis_data/predicted_images/predict_np_images', predicted_images)

print(np.min(predicted_images[0]), np.max(predicted_images[0]))

X_test_2 = (X_test *127.5 +127.5).astype(int)
print(np.min(X_test_2[0]), np.max(X_test_2[0]))

plt.imshow(predicted_images[308])
plt.show()

plt.imshow(X_test_2[308])

label = 1
num_remove = 1

val_list = []
for i in range(0, len(X_test)):
  val_list.append(np.mean(np.square(z1_gen_ema[i] - z2_gen_ema[i])))

anomaly_labels = np.zeros(len(val_list))
for i, label in enumerate(Y_test):
  if label == num_remove:
    anomaly_labels[i] = 1

np.unique(anomaly_labels, return_counts=True)

"""# Finding Anomaly Scores"""
roc_auc_scores = []
prauc_scores = []

val_arr = np.asarray(val_list)
val_probs = val_arr / max(val_arr)

roc_auc = roc_auc_score(anomaly_labels, val_probs)
prauc = average_precision_score(anomaly_labels, val_probs)
roc_auc_scores.append(roc_auc)
prauc_scores.append(prauc)

print("ROC AUC SCORE FOR %d: %f" % (num_remove, roc_auc))
print("PRAUC SCORE FOR %d: %f" % (num_remove, prauc))

# plt.scatter(np.arange(10), anom_score_avgs)
# plt.savefig("anom/anom_scores_%d.png" % num_remove)
# plt.close()

## precision under the recall curve
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc
from matplotlib import pyplot

print(np.mean(val_probs))
print(np.unique(anomaly_labels, return_counts=True))

print(val_probs.shape)

f1_y_hat = np.array([])
count_0 = 0
count_1 = 0

for i in val_probs:
  if i > 0.5:
    f1_y_hat = np.append(f1_y_hat, 0)
    count_0 += 1
  else:
    f1_y_hat = np.append(f1_y_hat, 1)
    count_1 += 1

print(count_0, count_1)

## precision under the recall curve
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc
from matplotlib import pyplot

## calculating precision, recall and area under the curve
precision_G, recall_G, thresholds = precision_recall_curve(Y_test, f1_y_hat)
f1 = f1_score(Y_test, f1_y_hat)

auc = auc(recall, precision)

print(precision)
print(thresholds)

print(precision, recall)

precision_E = [0.24878, 1]
recall_E = [1, 0]
precision_R = [0.25134, 1]
recall_R = [1, 0]

# plot the AUC
pyplot.plot(recall_G, precision_G, marker='.', label='GANomaly')
pyplot.plot(recall_E, precision_E, marker=',', label='EGBAD')
pyplot.plot(recall_R, precision_R, marker='v', label='ResNet')
# axis labels
pyplot.xlabel('Recall')
pyplot.ylabel('Precision')
# show the legend
pyplot.legend()
# show the plot
pyplot.show()

