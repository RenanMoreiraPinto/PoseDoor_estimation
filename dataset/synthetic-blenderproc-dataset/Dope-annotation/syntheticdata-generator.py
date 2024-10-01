#!/usr/bin/env python3

import blenderproc as bproc
import argparse
import os
import numpy as np
from PIL import Image, ImageDraw
import cv2
import json
from scipy.spatial.transform import Rotation as R  # Import scipy for quaternion conversion

def get_cuboid_image_space(mesh, camera):
    """Project the 3D cuboid corners into 2D image space."""
    bbox = mesh.get_bound_box()
    centroid = np.mean(bbox, axis=0)

    cam_pose = np.linalg.inv(camera.get_camera_pose())  # world to camera transformation
    tvec = -cam_pose[0:3, 3]
    rvec = -cv2.Rodrigues(cam_pose[0:3, 0:3])[0]
    K = camera.get_intrinsics_as_K_matrix()

    # Reorder points to match the DOPE cuboid format
    dope_order = [6, 2, 1, 5, 7, 3, 0, 4]
    cuboid = [cv2.projectPoints(bbox[ii], rvec, tvec, K, np.array([]))[0][0][0] for ii in dope_order]
    cuboid.append(cv2.projectPoints(centroid, rvec, tvec, K, np.array([]))[0][0][0])  # Add centroid
    return np.array(cuboid, dtype=float).tolist()

def write_json(outf, args, camera, objects, objects_data, seg_map):
    cam_xform = camera.get_camera_pose()
    eye = (-cam_xform[0:3, 3]).tolist()  # Apply negation first, then convert to list
    at = (-cam_xform[0:3, 2]).tolist()  # Apply negation first, then convert to list
    up = cam_xform[0:3, 0].tolist()  # No negation needed, just convert to list

    K = camera.get_intrinsics_as_K_matrix()

    data = {
        "camera_data": {
            "width": args.width,
            "height": args.height,
            "camera_look_at": {
                "at": at,
                "eye": eye,
                "up": up
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

    # Object data
    for ii, obj in enumerate(objects):
        idx = ii + 1  # Object ID starts at 1
        num_pixels = int(np.sum((seg_map == idx)))

        if num_pixels < args.min_pixels:
            continue

        projected_keypoints = get_cuboid_image_space(obj, camera)

        # Get the rotation matrix and convert to quaternion using scipy
        rotation_matrix = obj.get_rotation_mat()
        quaternion = R.from_matrix(rotation_matrix).as_quat()  # Convert to quaternion

        data['objects'].append({
            'class': objects_data[ii]['class'],
            'name': objects_data[ii]['name'],
            'visibility': num_pixels,
            'projected_cuboid': projected_keypoints,  # Already converted to list in get_cuboid_image_space
            'location': obj.get_location().tolist(),  # Convert location (ndarray) to list
            'quaternion_xyzw': quaternion.tolist()  # Convert quaternion (ndarray) to list
        })

    with open(outf, "w") as write_file:
        json.dump(data, write_file, indent=4)

    return data

def draw_cuboid_markers(objects, camera, im):
    """Draw cuboid markers (keypoints) on the image."""
    colors = ['yellow', 'magenta', 'blue', 'red', 'green', 'orange', 'brown', 'cyan', 'white']
    R = 2  # Radius of the keypoint markers
    draw = ImageDraw.Draw(im)  # Prepare to draw on the image
    for obj in objects:
        projected_keypoints = get_cuboid_image_space(obj, camera)  # Project to 2D
        for idx, pp in enumerate(projected_keypoints):
            x, y = int(pp[0]), int(pp[1])
            draw.ellipse((x-R, y-R, x+R, y+R), fill=colors[idx % len(colors)])  # Draw colored markers
    return im

def add_random_lights():
    """Add random lights to the scene."""
    num_lights = np.random.randint(1, 4)  # Random number of lights (1 to 3)
    for _ in range(num_lights):
        # Random position for the light
        light_location = np.random.uniform([-10, -10, 5], [10, 10, 15])
        
        # Random intensity for the light
        light_intensity = np.random.uniform(300, 1500)  # Between 300 and 1500

        # Random color for the light
        light_color = np.random.uniform([0.8, 0.8, 0.8], [1, 1, 1])  # Slightly varying white

        # Add the light to the scene
        light = bproc.types.Light()
        light.set_type('POINT')
        light.set_location(light_location)
        light.set_energy(light_intensity)
        light.set_color(light_color)

def main(args):
    # Set up blenderproc
    bproc.init()

    # Load the scene and filter objects by name (only doors and frames)
    scene_objects = bproc.loader.load_blend(args.scene)
    target_objects = [obj for obj in scene_objects if obj.get_name().startswith(('door', 'frame'))]

    if len(target_objects) == 0:
        print("No doors or frames found in the scene.")
        return

    # Set the camera to be in front of the object
    cam_pose = bproc.math.build_transformation_mat([0, -25, 0], [np.pi / 2, 0, 0])
    bproc.camera.add_camera_pose(cam_pose)
    bproc.camera.set_resolution(args.width, args.height)

    # Enable rendering of segmentation maps
    bproc.renderer.enable_segmentation_output(map_by=["instance"])

    # Renderer setup
    bproc.renderer.set_output_format('PNG')
    bproc.renderer.set_render_devices(desired_gpu_ids=[0])

    # Prepare folder for JSON data
    for frame in range(args.nb_frames):
        # Add random lights to the scene
        add_random_lights()

        # Render the scene
        data = bproc.renderer.render()

        # Get segmentation map
        seg_map = data.get("instance_segmaps")[0]  # Segmentation map of the first frame

        # Prepare object data for JSON
        objects_data = []
        for obj in target_objects:
            objects_data.append({
                'class': "door" if "door" in obj.get_name().lower() else "frame",
                'name': obj.get_name(),
                'location': obj.get_location().tolist()  # Convert location to list
            })

        # Save JSON and images
        json_filename = os.path.join(args.outf, f"frame_{frame:06d}.json")
        write_json(json_filename, args, bproc.camera, target_objects, objects_data, seg_map)

        im = Image.fromarray(data['colors'][0])
        if args.debug:
            im = draw_cuboid_markers(target_objects, bproc.camera, im)

        image_filename = os.path.join(args.outf, f"frame_{frame:06d}.png")
        im.save(image_filename)

    print(f"Saved JSON and images to {args.outf}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--scene', default="scene11.blend", help="Path to the scene.blend file")
    parser.add_argument('--width', default=640, type=int, help='image output width')
    parser.add_argument('--height', default=480, type=int, help='image output height')
    parser.add_argument('--nb_frames', default=2, type=int, help="how many total frames to generate")
    parser.add_argument('--outf', default='output/', help="output folder for images and JSON data")
    parser.add_argument('--min_pixels', default=100, type=int, help="minimum number of pixels for visibility")
    parser.add_argument('--debug', action='store_true', help="Render cuboid markers for debugging purposes")

    opt = parser.parse_args()
    main(opt)

