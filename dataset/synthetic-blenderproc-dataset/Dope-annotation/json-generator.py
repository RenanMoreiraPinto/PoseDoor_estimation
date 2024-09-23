import blenderproc as bproc
import argparse
import os
import numpy as np
import json
from PIL import Image

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('camera', nargs='?', default="camera_positions", help="Path to the camera file")
parser.add_argument('scene', nargs='?', default="scene.blend", help="Path to the scene.blend file")
parser.add_argument('output_dir', nargs='?', default="output", help="Path to where the final files will be saved")
args = parser.parse_args()

bproc.init()

# Load objects into the scene
objs = bproc.loader.load_blend(args.scene)

# Set category ids for loaded objects
for j, obj in enumerate(objs):
    obj.set_cp("category_id", j + 1)

# Define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

# Set the camera resolution
bproc.camera.set_resolution(512, 512)

# Enable normal rendering and segmentation output
bproc.renderer.enable_normals_output()
bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])

# Function to save JSON data
def write_json(outf, camera, objects, objects_data, seg_map):
    cam_xform = camera.get_camera_pose()
    eye = -cam_xform[0:3, 3]
    at = -cam_xform[0:3, 2]
    up = cam_xform[0:3, 0]

    K = camera.get_intrinsics_as_K_matrix()

    data = {
        "camera_data": {
            "width": 512,
            "height": 512,
            "camera_look_at": {
                "at": [at[0], at[1], at[2]],
                "eye": [eye[0], eye[1], eye[2]],
                "up": [up[0], up[1], up[2]]
            },
            "intrinsics": {
                "fx": K[0][0],
                "fy": K[1][1],
                "cx": K[2][0],
                "cy": K[2][1]
            }
        },
        "objects": []
    }

    for ii, oo in enumerate(objects):
        idx = ii + 1
        num_pixels = int(np.sum((seg_map == idx)))

        data['objects'].append({
            'class': objects_data[ii]['class'],
            'name': objects_data[ii]['name'],
            'visibility': num_pixels,
            'location': objects_data[ii]['location'],
            'quaternion_xyzw': objects_data[ii]['quaternion_xyzw']
        })

    with open(outf, "w") as write_file:
        json.dump(data, write_file, indent=4)

def draw_cuboid_markers(objects, camera, im):
    colors = ['yellow', 'magenta', 'blue', 'red', 'green', 'orange', 'brown', 'cyan', 'white']
    R = 2 # radius
    # draw dots on image to label the cuiboid vertices
    draw = ImageDraw.Draw(im)
    for oo in objects:
        projected_keypoints = get_cuboid_image_space(oo, camera)
        for idx, pp in enumerate(projected_keypoints):
            x = int(pp[0])
            y = int(pp[1])
            draw.ellipse((x-R, y-R, x+R, y+R), fill=colors[idx])

    return im

# Create object data
objects_data = []
for j, obj in enumerate(objs):
    obj_data = {
        'class': "door",  
        'name': f"door_{j}",
        'location': list(obj.get_location()),
        'quaternion_xyzw': [0, 0, 0, 1]
    }
    objects_data.append(obj_data)

# Read the camera positions file
with open(args.camera, "r") as f:
    camera_positions = [line.split() for line in f.readlines()]

# Loop over each camera position
for idx, cam_pos in enumerate(camera_positions):
    try:
        # Parse the position and rotation
        position = np.array(list(map(float, cam_pos[:3])))
        euler_rotation = np.array(list(map(float, cam_pos[3:6])))

        # Print the camera position for debugging
        print(f"Processing camera position {idx}: Position={position}, Rotation={euler_rotation}")

        # Build the transformation matrix
        matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)

        # Apply the new camera pose
        bproc.camera.add_camera_pose(matrix_world)

        # Render the scene
        data = bproc.renderer.render()

   

        # Save the corresponding JSON data
        json_filename = os.path.join(args.output_dir, f"frame_{idx:06d}.json")
        seg_map = data["instance_segmaps"][0]
        write_json(json_filename, bproc.camera, objs, objects_data, seg_map)

    except Exception as e:
        print(f"Error processing camera position at index {idx}: {e}")

print("Rendering complete.")

