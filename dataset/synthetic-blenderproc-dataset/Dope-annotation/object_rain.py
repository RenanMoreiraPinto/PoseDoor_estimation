import blenderproc as bproc
import argparse
import os
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('scene', nargs='?', default="scene.blend", help="Path to the scene.blend file")
parser.add_argument('output_dir', nargs='?', default="output", help="Path to where the final files will be saved")
args = parser.parse_args()

bproc.init()

# Load the objects into the scene
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
bproc.camera.set_resolution(640, 480)  # Set to LINEMOD-like resolution (640x480)
K = bproc.camera.get_intrinsics_as_K_matrix()  # Get camera intrinsic matrix
fx, fy = K[0][0], K[1][1]
cx, cy = K[0][2], K[1][2]

# Enable segmentation output for generating masks
bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])

# Create output directories if they do not exist
rgb_dir = os.path.join(args.output_dir, 'rgb')
mask_dir = os.path.join(args.output_dir, 'masks')
label_dir = os.path.join(args.output_dir, 'labels')
coco_dir = os.path.join(args.output_dir, 'coco_data')
os.makedirs(rgb_dir, exist_ok=True)
os.makedirs(mask_dir, exist_ok=True)
os.makedirs(label_dir, exist_ok=True)
os.makedirs(coco_dir, exist_ok=True)

# Loop to rotate object and change camera position
for angle in np.linspace(0, 2 * np.pi, num=36):  # 36 rotations for a full 360-degree turn
    for obj in objs:
        # Apply rotation to the object around the Z-axis and Y-axis for variation
        obj.set_rotation_euler([angle / 2, angle, 0])

    # Randomize the camera position for each rotation
    camera_position = np.random.uniform([-10, -10, 8], [10, 10, 12])  # Random camera position
    rotation_matrix = bproc.camera.rotation_from_forward_vec([0, 0, 0] - camera_position, inplane_rot=np.random.uniform(-0.7854, 0.7854))
    cam2world_matrix = bproc.math.build_transformation_mat(camera_position, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)

    # Render the scene with the current object rotation
    data = bproc.renderer.render()

    # Save RGB images using PIL
    for i, color_img in enumerate(data["colors"]):
        img = Image.fromarray((color_img * 255).astype('uint8'))  # Convert to uint8 format
        img.save(os.path.join(rgb_dir, f"{str(i).zfill(6)}_angle_{int(np.degrees(angle))}.png"))

    # Save black and white segmentation masks
    for i, instance_map in enumerate(data["instance_segmaps"]):
        bw_mask = np.where(instance_map > 0, 255, 0).astype(np.uint8)  # Object pixels as 255, background as 0
        img = Image.fromarray(bw_mask)
        img.save(os.path.join(mask_dir, f"{str(i).zfill(6)}_angle_{int(np.degrees(angle))}.png"))

    # Write COCO-style annotations
    bproc.writer.write_coco_annotations(os.path.join(coco_dir, f'annotations_angle_{int(np.degrees(angle))}'),
                                        instance_segmaps=data["instance_segmaps"],
                                        instance_attribute_maps=data["instance_attribute_maps"],
                                        colors=data["colors"],
                                        color_file_format="PNG")

    # Generate .txt files for each rendered image
    for i, obj in enumerate(objs):
        keypoints_2d = bproc.camera.project_points(obj.get_bound_box())
        keypoints_2d_norm = [(kp[0] / 640, kp[1] / 480) for kp in keypoints_2d]

        # Compute bounding box
        x_min, y_min, x_max, y_max = min(kp[0] for kp in keypoints_2d_norm), min(kp[1] for kp in keypoints_2d_norm), max(kp[0] for kp in keypoints_2d_norm), max(kp[1] for kp in keypoints_2d_norm)

        category_id = obj.get_cp("category_id")
        with open(os.path.join(label_dir, f"{str(i).zfill(6)}_angle_{int(np.degrees(angle))}.txt"), 'w') as f:
            label_data = [category_id] + [coord for kp in keypoints_2d_norm for coord in kp]
            label_data += [fx, fy, 640, 480, cx, cy, 640, 480]
            f.write(' '.join(map(str, label_data)) + '\n')

print("Dataset generation with object rotation and camera variation complete.")

