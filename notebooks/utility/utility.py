import numpy as np
from matplotlib.patches import Ellipse
from matplotlib.path import Path

def confidence_ellipse(x, y, n_std=3.0):
    if x.size != y.size:
        raise ValueError("x and y must be the same size")
    covariance = np.cov(x, y)
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    center = (mean_x, mean_y)    
    
     # Calculate eigenvectors and eigenvalues of covariance matrix
    eigenvalues, eigenvectors = np.linalg.eig(covariance)

    # Sort eigenvectors by decreasing eigenvalues
    order = eigenvalues.argsort()[::-1]
    eigenvectors = eigenvectors[:, order]   
    
    
    # Calculate major and minor axes lengths
    major_length = np.sqrt(eigenvalues[order[0]]) * n_std
    minor_length = np.sqrt(eigenvalues[order[1]]) * n_std

    # Calculate major and minor axes angles
    angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1]))

    # Plot data and ellipse
    ellipse = Ellipse(center, width=major_length*2,
                  height=minor_length*2, angle=angle, fill=False)  
    
    major_axis = eigenvectors[:, 0] * major_length
    minor_axis = eigenvectors[:, 1] * minor_length

    distance_major = np.sqrt(mean_x**2 * np.sin(angle)**2 + mean_y**2 * np.cos(angle)**2)
    distance_minor = np.sqrt(mean_x**2 * np.cos(angle)**2 + mean_y**2 * np.sin(angle)**2)

    # Count the number of points within the Ellipse
    path = Path(ellipse.get_verts())
    points = np.column_stack((x, y))
    num_inside = 0
    for point in points:
        if path.contains_point(point):
            num_inside += 1

    # Compute point density
    area = np.pi * major_length * minor_length
    density = num_inside / area
    
    return {"ellipse": ellipse, "major_axis": major_axis, "minor_axis": minor_axis, "center": center, "density": density, "ratio": (major_length/minor_length), "axis": (distance_major < distance_minor)}

# Check which line is closer to a given point
def line_distance(l1, l2, p):
    # Define the points
    P1 = p
    pa = l1[0]
    pb = l1[1]
    pc = l2[0]
    pd = l2[1]

    # Calculate the distances to the infinite lines
    dist_L1 = abs((pb[1]-pa[1])*P1[0] - (pb[0]-pa[0])*P1[1] + pb[0]*pa[1] - pb[1]*pa[0]) / ((pb[1]-pa[1])**2 + (pb[0]-pa[0])**2)**0.5
    dist_L2 = abs((pd[1]-pc[1])*P1[0] - (pd[0]-pc[0])*P1[1] + pd[0]*pc[1] - pd[1]*pc[0]) / ((pd[1]-pc[1])**2 + (pd[0]-pc[0])**2)**0.5
    
    # Extend the lines infinitely
    x = np.linspace(-10, 10, 100)
    y1 = (pb[1]-pa[1])/(pb[0]-pa[0])*(x-pa[0])+pa[1]
    y2 = (pd[1]-pc[1])/(pd[0]-pc[0])*(x-pc[0])+pc[1]

    return dist_L1 > dist_L2