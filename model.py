"""
Author: Samatha Ereshi Akkamahadevi
Email: samatha94@ksu.edu
Date: 08/27/2024
Project: Stage3: Parallelized Image Retrieval and Classification
File name: model.py
Description:
"""

from tensorflow.keras.applications import ResNet50V2
from tensorflow.keras.layers import Input, AveragePooling2D, Dropout, Flatten, Dense
from tensorflow.keras.models import Model, load_model

#-----------------------------------------------------------------------------------------------
#removed below code as create =_model is not called anywhere in stage3 code
#-----------------------------------------------------------------------------------------------

# def create_model(num_classes):
#     print("[INFO] preparing model...")
#     base_model = ResNet50V2(weights="imagenet", include_top=False, input_tensor=Input(shape=(224, 224, 3)))
#     print(len(base_model.layers))
    

#     head_model = base_model.output
#     head_model = AveragePooling2D(pool_size=(7, 7))(head_model)
#     head_model = Flatten(name="flatten")(head_model)
#     head_model = Dense(64, activation="relu")(head_model)
#     head_model = Dropout(0.5)(head_model)
#     head_model = Dense(num_classes, activation="softmax")(head_model)

#     model = Model(inputs=base_model.input, outputs=head_model)
#     for layer in base_model.layers:
#         layer.trainable = False
#     return model
#-----------------------------------------------------------------------------------------------

def load_and_analyze_model(model_path):
    model = load_model(model_path)
    # print(model.summary())

    # Extract outputs from the last three layers
    layer_outputs = [layer.output for layer in model.layers[-3:-2]]
    print(layer_outputs)
    layer_names = [layer.name for layer in model.layers[-3:-2]]
    print(layer_names)
    # Creating a feature map model
    feature_map_model = Model(inputs=model.input, outputs=layer_outputs)
    # print(feature_map_model.summary())

    return model, layer_outputs, layer_names, feature_map_model
