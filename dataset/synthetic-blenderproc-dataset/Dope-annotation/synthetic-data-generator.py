import blenderproc as bproc  # BlenderProc must be imported first
import subprocess
import argparse

# Argument parsing to pass camera, scene, and output directory paths
parser = argparse.ArgumentParser()
parser.add_argument('camera', nargs='?', default="camera_positions", help="Path to the camera file")
parser.add_argument('scene', nargs='?', default="scene.blend", help="Path to the scene.blend file")
parser.add_argument('output_dir', nargs='?', default="output", help="Path to where the final files will be saved")
args = parser.parse_args()

# First step: Generate .jpg images
print("Step 1: Generating .jpg images")
image_generation_command = [
    'python', 'image-generator.py', args.camera, args.scene, args.output_dir
]

result = subprocess.run(image_generation_command, capture_output=True, text=True)
if result.returncode != 0:
    print(f"Error in image generation: {result.stderr}")
else:
    print("Image generation completed successfully.")

# Second step: Generate .json files
print("Step 2: Generating .json files")
json_generation_command = [
    'python', 'json-generator.py', args.camera, args.scene, args.output_dir
]

result = subprocess.run(json_generation_command, capture_output=True, text=True)
if result.returncode != 0:
    print(f"Error in JSON generation: {result.stderr}")
else:
    print("JSON generation completed successfully.")

