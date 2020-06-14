import cv2
import dlib
import numpy as np
import requests
import tensorflow as tf
import tensorflow.keras.backend as K
import base64

from io import BytesIO
from PIL import Image
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import ZeroPadding2D, Convolution2D, MaxPooling2D
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.layers import (
    Dense,
    Dropout,
    Softmax,
    Flatten,
    Activation,
    BatchNormalization,
)

from .config import GENDER_REP

__all__ = (
    "get_vgg_face",
    "get_face_detector",
    "load_image",
    "process_image",
    "get_classifier_model",
)


def get_vgg_face():
    model = Sequential()
    model.add(ZeroPadding2D((1, 1), input_shape=(224, 224, 3)))
    model.add(Convolution2D(64, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(64, (3, 3), activation="relu"))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(128, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(128, (3, 3), activation="relu"))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(256, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(256, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(256, (3, 3), activation="relu"))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation="relu"))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation="relu"))
    model.add(ZeroPadding2D((1, 1)))
    model.add(Convolution2D(512, (3, 3), activation="relu"))
    model.add(MaxPooling2D((2, 2), strides=(2, 2)))
    model.add(Convolution2D(4096, (7, 7), activation="relu"))
    model.add(Dropout(0.5))
    model.add(Convolution2D(4096, (1, 1), activation="relu"))
    model.add(Dropout(0.5))
    model.add(Convolution2D(2622, (1, 1)))
    model.add(Flatten())
    model.add(Activation("softmax"))

    model.load_weights("./vgg_face_weights.h5")
    return Model(inputs=model.layers[0].input, outputs=model.layers[-2].output)


def get_face_detector():
    return dlib.cnn_face_detection_model_v1("./mmod_human_face_detector.dat")


def get_classifier_model():
    return tf.keras.models.load_model("./face_classifier_model.h5")


def process_image(img, face_detector, model, vgg_face, resizing_ratio: float = 1):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector(gray, 1)
    result = []

    for face in faces:
        left = face.rect.left()
        top = face.rect.top()
        right = face.rect.right()
        bottom = face.rect.bottom()
        width = right - left
        height = bottom - top
        img_crop = img[top: top + height, left: left + width]
        if img_crop.size == 0:
            continue

        img_crop = img[top: top + height, left: left + width]
        img_crop = cv2.resize(img_crop[..., ::-1], (224, 224))
        img_crop = np.expand_dims(img_crop, axis=0)
        img_crop = preprocess_input(img_crop)
        img_encode = vgg_face(img_crop)

        embed = K.eval(img_encode)
        gender = model.predict(embed)

        result.append(
            {
                "prediction": GENDER_REP[np.argmax(gender)],
                "accuracy": float(np.max(gender)),
                "cords": (
                    left // resizing_ratio,
                    top // resizing_ratio,
                    right // resizing_ratio,
                    bottom // resizing_ratio
                ),
            }
        )

    return result


def load_image(image_encoded: str = None, image_url: str = None):
    if image_url is not None:
        image = requests.get(image_url).content
    elif image_encoded is not None:
        image = base64.urlsafe_b64decode(image_encoded.encode('utf-8'))
    else:
        raise Exception("Image not specified")

    image = Image.open(BytesIO(image))
    width, _ = image.size
    image.thumbnail((1024, 1024), Image.ANTIALIAS)
    resizing_ratio = image.size[0] / width
    image = np.array(image)
    return image[:, :, ::-1].copy(), resizing_ratio
