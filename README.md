# Door Identification and Pose Estimation Dataset

This repository contains the dataset used for the paper **"Identification and Pose Estimation for Doors Under Occlusion Using Synthetic and Real Data"**.

## Overview

The dataset is designed for training and evaluating door detection and 6-DoF pose estimation models in indoor environments. The data includes both **synthetic** and **real-world images** of various door types in different configurations, lighting conditions, and levels of occlusion.

Our dataset can be used for a variety of tasks, including:

- Door detection
- Pose estimation (6-DoF)
- Training models for handling occluded doors
- Enhancing the generalization of models using synthetic data

## Contents

- **Real-Dataset**: 4,000 images (3,000 from a public dataset and 1,000 captured manually by our team).
- **Synthetic Dataset (NVSII)**: 50,000 automatically generated images using the NVSII method, with various occlusion and lighting conditions.
- **Our Synthetic Dataset**: 25,000 Full HD images automatically generated using the Isaac method and Blender for creating diverse 3D models and random occlusion scenarios.

Each dataset contains labeled data for both **door detection** and **keypoint annotations** to facilitate 6-DoF pose estimation.

## Directory Structure

```text
datasets/
├── real-dataset/
│   ├── images/              # Real-world RGB images
│   └── annotations/         # Corresponding keypoint annotations
├── synthetic-nvsii-dataset/
│   ├── images/              # Synthetic RGB images from NVSII
│   └── annotations/         # Keypoint annotations
├── synthetic-isaac-dataset/
│   ├── images/              # Synthetic RGB images from Isaac
│   └── annotations/         # Keypoint annotations
models/
├── yolov8/                  # YOLOv8 model configuration and weights
├── dope/                    # DOPE model configuration and weights
├── Gen6D/                   # Gen6D model configuration and tests
scripts/
├── train.py                 # Script for training the model
├── eval.py                  # Script for evaluating the model
└── dataset-prep.py          # Helper script for dataset preprocessing
