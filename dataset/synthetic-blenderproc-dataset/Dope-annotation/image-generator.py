import blenderproc as bproc
import argparse
import os
from PIL import Image  # Import the Python Imaging Library to save images

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('camera', nargs='?', default="camera_positions", help="Path to the camera file")
parser.add_argument('scene', nargs='?', default="scene.blend", help="Path to the scene.blend file")
parser.add_argument('output_dir', nargs='?', default="output", help="Path to where the final files will be saved ")
args = parser.parse_args()

bproc.init()

# Load objects into the scene
objs = bproc.loader.load_blend(args.scene)

# Set some category ids for loaded objects
for j, obj in enumerate(objs):
    obj.set_cp("category_id", j + 1)

# Define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

# Define the camera intrinsics
bproc.camera.set_resolution(512, 512)

# Read the camera positions file and convert into homogeneous camera-world transformation
with open(args.camera, "r") as f:
    for line in f.readlines():
        line = [float(x) for x in line.split()]
        position, euler_rotation = line[:3], line[3:6]
        matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)
        bproc.camera.add_camera_pose(matrix_world)

# Activate normal rendering and segmentation output
bproc.renderer.enable_normals_output()
bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])

# Render the whole pipeline
data = bproc.renderer.render()

# Write only the rendered images in JPEG format using PIL
for idx, color_img in enumerate(data['colors']):
    image = Image.fromarray(color_img)  # Convert the NumPy array to an image
    image_filename = os.path.join(args.output_dir, f"frame_{idx:06d}.jpg")
    image.save(image_filename, format="JPEG")  # Save the image in JPEG format

print("Rendering complete, only .jpg files are saved.")

