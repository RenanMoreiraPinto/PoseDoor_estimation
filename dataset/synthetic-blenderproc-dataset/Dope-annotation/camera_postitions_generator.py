import numpy as np

# Define parameters for back and forth motion
camera_height = 4.1242  # Assuming the camera height remains constant (z-axis)
steps = 5  # 15 positions forward and backward on both axes
range_x = np.linspace(-10, 10, steps)
range_y = np.linspace(-10, 10, steps)

# Generate positions for back and forth motion on the X and Y axes, always pointing toward the origin
back_and_forth_positions = []
for x in range_x:
    for y in range_y:
        position = [x, y, camera_height]
        # Assume the camera orientation remains fixed at looking at the origin (no need for yaw/pitch)
        orientation = [0.0, 0.0]  # Placeholder for simplicity
        back_and_forth_positions.append(position + orientation)

# Convert the new positions to a string format
output_positions_back_and_forth = '\n'.join(' '.join(map(str, pos)) for pos in back_and_forth_positions)

# Save the back and forth camera positions to a file
output_file_back_and_forth_path = 'camera_positions_1'
with open(output_file_back_and_forth_path, 'w') as f:
    f.write(output_positions_back_and_forth)

print(f"Camera positions saved to {output_file_back_and_forth_path}")

