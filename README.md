Door Identification and Pose Estimation Dataset
This repository contains the dataset used for the paper "Identification and Pose Estimation for Doors Under Occlusion Using Synthetic and Real Data", presented by Renan Moreira, Thiago Segreto, Juliano D. Negri, João C. V. Soares, Marcelo Becker, and Vivian S. Medeiros.

Overview
The dataset is designed for training and evaluating door detection and 6-DoF pose estimation models in indoor environments. The data includes both synthetic and real-world images of various door types in different configurations, lighting conditions, and levels of occlusion.

Our dataset can be used for a variety of tasks, including:

Door detection
Pose estimation (6-DoF)
Training models for handling occluded doors
Enhancing the generalization of models using synthetic data
Contents
Real-Dataset: 4,000 images (3,000 from a public dataset and 1,000 captured manually by our team).
Synthetic Dataset (NVSII): 50,000 automatically generated images using the NVSII method, with various occlusion and lighting conditions.
Our Synthetic Dataset: 25,000 Full HD images automatically generated using the Isaac method and Blender for creating diverse 3D models and random occlusion scenarios.
Each dataset contains labeled data for both door detection and keypoint annotations to facilitate 6-DoF pose estimation.

Data Description
The dataset includes:

RGB images of doors from different angles and occlusion levels.
Point cloud data for some images (useful for refining pose estimation).
Bounding box annotations for door detection.
Keypoint annotations for 6-DoF pose estimation (corners and handles of the doors).
Methods
The models used in our experiments were trained with a combination of real and synthetic data, leveraging advanced deep learning techniques, including:

YOLOv8 for keypoint detection: Detects door features such as corners and handles.
DOPE (Deep Object Pose Estimation): For precise 3D pose estimation.
Usage
You can use this dataset for training or testing machine learning models aimed at detecting and estimating the pose of doors. It is particularly suitable for applications in autonomous navigation, robotic manipulation, and SLAM systems where door interaction is required.

Citation
If you use this dataset in your research, please cite our paper:

bibtex
Copiar código
@article{Moreira2024DoorDetection,
  title={Identification and Pose Estimation for Doors Under Occlusion Using Synthetic and Real Data},
  author={Renan Moreira, Thiago Segreto, Juliano D. Negri, João C. V. Soares, Marcelo Becker, and Vivian S. Medeiros},
  journal={To be published},
  year={2024}
}
Contact
For questions or further information, feel free to reach out to Renan Moreira at renanmoreira@usp.br.

