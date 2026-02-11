"""
Author: Samatha Ereshi Akkamahadevi
Email: samatha94@ksu.edu
Date: 08/27/2024
Project: Stage3: Parallelized Image Retrieval and Classification
File name: keyword_extractor.py
Description:
"""

def extract_keywords(file_path):
    solutions_keywords = {'solution1': [], 'solution2': [], 'solution3': []}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'solution 1:' in line:
                keywords = extract_keywords_from_line(line)
                solutions_keywords['solution1'].extend(keywords)
            elif 'solution 2:' in line:
                keywords = extract_keywords_from_line(line)
                solutions_keywords['solution2'].extend(keywords)
            elif 'solution 3:' in line:
                keywords = extract_keywords_from_line(line)
                solutions_keywords['solution3'].extend(keywords)
    return solutions_keywords

def extract_keywords_from_line(line):
    keywords = []
    parts = line.split('.')
    if len(parts) > 1:
        sub_parts = parts[1].split(')')
        for part in sub_parts:
            if 'hcbdwsu' in part:
                keyword = part.split(':')[1].strip()
                keywords.append(keyword.replace('WN_', ''))  # Remove 'WN_' if present
    return keywords
