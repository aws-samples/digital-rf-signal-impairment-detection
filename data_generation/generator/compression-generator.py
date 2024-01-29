import time
import numpy as np
import matplotlib.pyplot as plt

def shift_centroid(centroid, shift):
    x_shift, y_shift = shift

    # Check the quadrant of the centroid
    if centroid[0] >= 0 and centroid[1] >= 0:
        # Centroid is in the first quadrant, subtract the shifts from both X and Y
        centroid[0] -= x_shift
        centroid[1] -= y_shift
    elif centroid[0] < 0 and centroid[1] >= 0:
        # Centroid is in the second quadrant, add the shifts to X and subtract from Y
        centroid[0] += x_shift
        centroid[1] -= y_shift
    elif centroid[0] >= 0 and centroid[1] < 0:
        # Centroid is in the third quadrant, subtract from X and add the shifts to Y
        centroid[0] -= x_shift
        centroid[1] += y_shift
    else:
        # Centroid is in the fourth quadrant, add the shifts to both X and Y
        centroid[0] += x_shift
        centroid[1] += y_shift

def generate_points_between(start_x, start_y, end_x, end_y, num_points, scale_factor, deviation_factor):
    # Generate evenly spaced values between start and end points
    t = np.linspace(0, 1, num_points)
    
    # Add noise to the points
    noise = np.random.normal(0, scale_factor, (num_points, 2))
    
    # Calculate the deviation from the line
    deviation = np.random.uniform(-deviation_factor, deviation_factor, num_points)
    
    # Compute the interpolated points along the line
    x_values = start_x + (end_x - start_x) * t + deviation * (end_y - start_y)
    y_values = start_y + (end_y - start_y) * t - deviation * (end_x - start_x)
    
    # Add noise and deviation to the interpolated points
    points = np.column_stack((x_values, y_values)) + noise
    
    return points

# Generate points between start and end points with scale and deviation factors
num_points = 256
scale_factor = 0.01
deviation_factor = 0.1
centroid_shift = 0.2

# Define the original centroids
centroids = np.array([[1, 1], [-1, 1], [1, -1], [-1, -1]])

# Generate random uniform shifts
shifts = np.random.uniform(low=0, high=centroid_shift, size=centroids.shape)

# Apply shifts to centroids
shifted_centroids = centroids.copy().astype(float)
for i in range(centroids.shape[0]):
    shift_centroid(shifted_centroids[i], shifts[i])

start_point = centroids[0]
end_point = shifted_centroids[0]
points1 = generate_points_between(start_point[0], start_point[1], end_point[0], end_point[1], num_points, scale_factor, deviation_factor)

start_point = centroids[1]
end_point = shifted_centroids[1]
points2 = generate_points_between(start_point[0], start_point[1], end_point[0], end_point[1], num_points, scale_factor, deviation_factor)

start_point = centroids[2]
end_point = shifted_centroids[2]
points3 = generate_points_between(start_point[0], start_point[1], end_point[0], end_point[1], num_points, scale_factor, deviation_factor)

start_point = centroids[3]
end_point = shifted_centroids[3]
points4 = generate_points_between(start_point[0], start_point[1], end_point[0], end_point[1], num_points, scale_factor, deviation_factor)

points = np.append(points1, points2, axis=0)
points = np.append(points, points3, axis=0)
points = np.append(points, points4, axis=0)

X = points[:, 0] + 1j * points[:, 1]

np.save("./data/qpsk/compression/compression-%s.txt" % time.time(), X)

# np.savetxt("./data/compression-%s.txt" % time.time(), points)

# f = open("./data/compression-%s.txt" % time.time(), "x")
# f.write(String(X))
# f.close()


# Plot the original and shifted centroids
# plt.figure(figsize=(6, 6))
# plt.scatter(centroids[:, 0], centroids[:, 1], c='red', label='Original Centroids')
# plt.scatter(shifted_centroids[:, 0], shifted_centroids[:, 1], c='blue', label='Shifted Centroids')
# plt.scatter(points[:, 0], points[:, 1], c='blue', label='Interpolated Points')
# plt.axhline(0, color='black', linewidth=0.5)
# plt.axvline(0, color='black', linewidth=0.5)
# plt.xlabel('X')
# plt.ylabel('Y')
# plt.title('Centroids and Shifted Centroids')
# plt.legend()
# plt.grid(True)
# plt.show()
