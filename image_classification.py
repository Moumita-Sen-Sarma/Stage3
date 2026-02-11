"""
Author: Samatha Ereshi Akkamahadevi
Email: samatha94@ksu.edu
Date: 08/27/2024
Project: Stage3: Parallelized Image Retrieval and Classification
File name: image_classification.py
Description:
"""

import os
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model  # Import load_model
import pandas as pd

def classify_images_for_solution(solution, neuron_solution_folder, model_path, new_classes,neuron_number):
    # Create an ImageDataGenerator for rescaling
    rescale_generator = image.ImageDataGenerator(rescale=1./255)

    # Load the test images for the new classes
    test_images = []
    filenames = []
    class_names = []

    for class_name in new_classes:
        class_directory = os.path.join(neuron_solution_folder, class_name)
        for image_name in os.listdir(class_directory):
            image_path = os.path.join(class_directory, image_name)
            try:
                #old code:
                # img = image.load_img(image_path, target_size=(224, 224))
                #new code:
                img = image.load_img(image_path, target_size=(299, 299))
                img = image.img_to_array(img)
                img = np.expand_dims(img, axis=0)
                img = rescale_generator.standardize(img)
                test_images.append(img)
                filenames.append(image_name)
                class_names.append(class_name)
            except:
                print("Corrupt image:", image_name)

    
                
    # Concatenate the test images into a single array
    if len(test_images) > 0:
        test_images = np.concatenate(test_images)

        # Perform predictions for the new test images
        model = load_model(model_path)  # Load your pre-trained model here
        predIdxs = model.predict(test_images)

        # Get classes by max element in predIdxs (as a list)
        classes = list(np.argmax(predIdxs, axis=1))

        # Create a dataframe with predIdxs, filenames, and classes
        df = pd.DataFrame(predIdxs)
        df['Class_names'] = class_names
        df['filenames'] = filenames
        df['Predicted_classes'] = classes

        # Modify the file name to include the neuron and solution names
        csv_file_name = 'neuron_{neuron_number}_solution_{solution}_predictions.csv'
        df.to_csv(os.path.join(neuron_solution_folder, csv_file_name), index=None, header=True)
    else:
        print("No valid images found for classification in this solution.")

