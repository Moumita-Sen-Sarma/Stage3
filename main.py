"""
Author: Samatha Ereshi Akkamahadevi
Email: samatha94@ksu.edu
Date: 08/27/2024
Project: Stage3: Parallelized Image Retrieval and Classification
File name: main.py
Description:
"""

import os
import shutil
import sys
import json
from keyword_extractor import extract_keywords
from pygoogle_image import image as pi
from image_classification import classify_images_for_solution
import model as md
from image_processor import process_and_classify_images

def main(neuron_index):
    
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    source_folder = config["source_folder"]
    destination_base_folder = config["destination_base_folder"]
    model_path = config["model_path"]
    base_output_path = config["base_output_path"]


    os.makedirs(destination_base_folder, exist_ok=True)
    print("Google_images folder is ready.")
  
    model, layer_outputs, layer_names, feature_map_model = md.load_and_analyze_model(model_path)
    
    file_name = f"neuron_{neuron_index}_results_ecii_V2.txt"
    # file_name = f"neuron_{neuron_index}_config_results_ecii_V2.txt"
    file_path = os.path.join(source_folder, file_name)
    solutions_keywords = extract_keywords(file_path)
    print(solutions_keywords)

    for solution, keywords in solutions_keywords.items():
        combined_keywords = "_and_".join(keywords)
        neuron_solution_folder = os.path.join(destination_base_folder, f'neuron_{neuron_index}', solution)
        os.makedirs(neuron_solution_folder, exist_ok=True)
        pi.download(keywords=combined_keywords, limit=100)
        downloaded_images_folder = os.path.join(os.getcwd(), 'images')
        if os.path.exists(downloaded_images_folder):
            for filename in os.listdir(downloaded_images_folder):
                shutil.move(os.path.join(downloaded_images_folder, filename), neuron_solution_folder)
        test_directory = neuron_solution_folder
        new_classes = [combined_keywords]
        process_and_classify_images(feature_map_model, test_directory, new_classes,neuron_index, solution,base_output_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <neuron_index>")
        sys.exit(1)
    neuron_index = sys.argv[1]
    main(neuron_index)

