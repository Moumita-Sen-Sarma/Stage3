"""
Author: Samatha Ereshi Akkamahadevi
Email: samatha94@ksu.edu
Date: 08/27/2024
Project: Stage3: Parallelized Image Retrieval and Classification
File name: image_processor.py
Description:
"""

import os
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing import image
from sklearn.model_selection import train_test_split

def process_and_classify_images(feature_map_model, test_directory, new_classes, neuron_index, solution,base_output_path):
   
    eval_dir = os.path.join(base_output_path, 'evaluation')
    verif_dir = os.path.join(base_output_path, 'verification')

    # Create the evaluation and verification directories if they do not exist
    os.makedirs(eval_dir, exist_ok=True)
    os.makedirs(verif_dir, exist_ok=True)

    print(new_classes)
    rescale_generator = image.ImageDataGenerator(rescale=1./255)

    test_images = []
    filenames = []
    class_names = []

    print(new_classes)
    for class_name in new_classes:

        class_directory = os.path.join(test_directory, class_name)
        for image_name in os.listdir(class_directory):
            image_path = os.path.join(class_directory, image_name)
            try:
               #old code
               # img = image.load_img(image_path, target_size=(224, 224))
               #new code
               img = image.load_img(image_path, target_size=(299, 299))
               img = image.img_to_array(img)
               img = np.expand_dims(img, axis=0)
               img = rescale_generator.standardize(img)
               test_images.append(img)
               filenames.append(image_name)
               class_names.append(class_name)
            except Exception as e:
                # Log the problematic file and continue
                print(f"Failed to process image {image_path}: {e}")
                continue

    print(class_name)
    test_images = np.concatenate(test_images)
    print(class_names)

    train_images, val_images, train_filenames, val_filenames, train_class_names, val_class_names = train_test_split(
        test_images, filenames, class_names, test_size=0.2, random_state=42)

    train_predIdxs = feature_map_model.predict(train_images)
    train_classes = list(np.argmax(train_predIdxs, axis=1))

    val_predIdxs = feature_map_model.predict(val_images)
    val_classes = list(np.argmax(val_predIdxs, axis=1))

    train_df = pd.DataFrame(train_predIdxs)
    train_df['Class_names'] = train_class_names
    train_df['Filenames'] = train_filenames
    train_df['Predicted_classes'] = train_classes

    val_df = pd.DataFrame(val_predIdxs)
    val_df['Class_names'] = val_class_names
    val_df['Filenames'] = val_filenames
    val_df['Predicted_classes'] = val_classes

    # File paths for evaluation and verification CSVs
    eval_csv_path = os.path.join(eval_dir, f'neuron{neuron_index}_{solution}_evaluation_set.csv')
    verif_csv_path = os.path.join(verif_dir, f'neuron{neuron_index}_{solution}_verification_set.csv')

    # Save the dataframes to the new CSV file paths
    train_df.to_csv(eval_csv_path, index=False, header=True)
    val_df.to_csv(verif_csv_path, index=False, header=True)


