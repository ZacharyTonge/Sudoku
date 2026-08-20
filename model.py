from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
from PIL import Image
import numpy as np
import os

def loadLocalDigits(directory):
    images = []
    labels = []

    for digit in range(1, 10):
        digit_directory = os.path.join(directory, str(digit))

        for filename in os.listdir(digit_directory):
            filepath = os.path.join(digit_directory, filename)

            image = Image.open(filepath).convert("L")
            image = image.resize((28, 28))

            image = np.array(image).astype("float32")

            images.append(image)
            labels.append(digit)

    images = np.array(images)
    labels = np.array(labels)

    images = images.reshape(images.shape[0], 28, 28, 1)
    images = images / 255.0

    return images, labels


# the MNIST data is split between train and test sets
(X_train, y_train), (X_test, y_test) = mnist.load_data()
X_my, y_my = loadLocalDigits("images/numbers")

# Reshape to be samples*pixels*width*height
X_train = X_train.reshape(X_train.shape[0], 28, 28, 1).astype('float32')
X_test = X_test.reshape(X_test.shape[0], 28, 28, 1).astype('float32')

# normalize to range [0, 1]
X_train = (X_train / 255.0)
X_test = (X_test / 255.0)

X_train = np.concatenate([X_train, X_my])
y_train = np.concatenate([y_train, y_my])

# DONT GET RID MASSIVE EFFECT
datagen = ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.15
)

datagen.fit(X_train)

early_stopping = EarlyStopping(monitor='val_loss', patience=3)

model = Sequential()
model.add(Conv2D(32, (3, 3), padding="same", activation='relu', kernel_initializer='he_uniform', input_shape=(28, 28, 1))) # Input layer (input_shape)
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), padding="same", activation='relu', kernel_initializer='he_uniform'))
model.add(Conv2D(64, (3, 3), padding="same", activation='relu', kernel_initializer='he_uniform'))
model.add(MaxPooling2D((2, 2))) # Makes the image effectivly less pixels (or more less neurons per section), so we go off general features rather than focus on details 
model.add(Dropout(0.5)) # Disables random neurons so the model doesn't get dependant on certain ones. I.e. a neuron recognises a section which always identifies a 9. By disabling it we are ensuring the network can still identify a 9 from other features rather than just one feature
model.add(Flatten()) # Converts all feature maps into one array 
model.add(Dense(10, activation='softmax')) # Output layer, softmax activation converts neuron activation in probability 
model.summary()

# compile model
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    X_train, y_train,
    batch_size=32,
    epochs=15,
    validation_data=(X_test, y_test),
    callbacks=[early_stopping]
)

model.save("model.keras")
print("Saved model to disk")
