import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder

from utility import confidence_ellipse

class ConstellationProcessor:
    # Mapping of modulation types to number of clusters
    MOD_CLUSTERS = {
        'qpsk': 4,
        '8psk': 8,
        '16apsk': 16,
        '32apsk': 32
    }
    def __init__(self, modcod, std_dev=2.5):
        """
        Initialize constellation processor
        
        Args:
            modcod (str): Modulation and coding scheme
            n_clusters (int): Number of clusters for analysis
            std_dev (float): Standard deviation for confidence ellipse
        """        
        self.modcod = modcod.lower()  # Convert to lowercase for consistency
        if self.modcod not in self.MOD_CLUSTERS:
            raise ValueError(f"Unsupported modulation type. Must be one of: {list(self.MOD_CLUSTERS.keys())}")
        
        self.n_clusters = self.MOD_CLUSTERS[self.modcod]
        self.std_dev = std_dev
        self.kmeans = KMeans(n_clusters=self.n_clusters, n_init=10)
        self.blob_encoder = OneHotEncoder(sparse_output=False)
        self.blob_encoder.fit(np.array([4, 8, 16, 32]).reshape(-1, 1))                    
        
    def load_csv_data(self, file_path):
        """
        Load IQ constellation data from CSV files with headers
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            tuple: (i_values, q_values, metadata)
        """
        df = pd.read_csv(file_path)
        i_values = df['I'].values
        q_values = df['Q'].values

        return i_values, q_values
    
    def encode_blobs(self, n_blobs):
        """
        One-hot encode the number of blobs
        
        Args:
            n_blobs (int): Number of blobs/clusters
            
        Returns:
            np.array: One-hot encoded array
        """
        return self.blob_encoder.transform([[n_blobs]])[0]


    def extract_cluster_features(self, i_data, q_data):
        """
        Extract cluster-based features from constellation
        
        Args:
            i_data (np.array): I component values
            q_data (np.array): Q component values
            
        Returns:
            tuple: (clusters, cluster_metrics)
        """
        X = np.column_stack((i_data, q_data))
        y_pred = self.kmeans.fit_predict(X)
        
        # Build clusters
        clusters = [[] for _ in range(self.n_clusters)]
        for idx, point in enumerate(X):
            clusters[y_pred[idx]].append(point)
        clusters = np.array([np.array(cluster) for cluster in clusters], dtype=object)
        
        return clusters, y_pred

    def is_radially_aligned(self, center: tuple, angle: float, threshold_degrees: float = 10.0) -> bool:
        """
        Determines if an ellipse is radially aligned by comparing its major axis angle
        with the angle to the origin.
        
        Args:
            center: Tuple (x,y) representing ellipse center
            angle: The angle of the major axis in degrees
            threshold_degrees: Maximum allowed deviation from radial alignment
            
        Returns:
            bool: True if the ellipse is radially aligned
        """
        # Calculate angle between center point and origin (radial direction)
        radial_angle = np.degrees(np.arctan2(center[1], center[0]))
        
        # Normalize angles to [-180, 180]
        angle = angle % 360
        if angle > 180:
            angle -= 360
        
        # Calculate absolute angular difference
        angle_diff = abs(angle - radial_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # Check if the angle difference is within threshold
        return angle_diff <= threshold_degrees or abs(180 - angle_diff) <= threshold_degrees

    def calculate_ellipse_metrics(self, clusters):
        """
        Calculate metrics based on confidence ellipses
        
        Args:
            clusters (list): List of cluster points
                
        Returns:
            dict: Ellipse metrics including radial alignment information
        """
        metrics = {
            'density': [],
            'ratio': [],
            'major_axis': [],
            'minor_axis': [],
            'radially_aligned': 0,
            'ellipses': []
        }
        
        for cluster in clusters:
            ellipse = confidence_ellipse(cluster[:,0], cluster[:,1], n_std=self.std_dev)
            
            # Check radial alignment using angle information
            if self.is_radially_aligned(ellipse['center'], ellipse['angle']):
                metrics['radially_aligned'] += 1
                
            # Store other metrics
            maj_axis = ([ellipse['center'][0], ellipse['center'][0]+ellipse['major_axis'][0]], 
                    [ellipse['center'][1], ellipse['center'][1]+ellipse['major_axis'][1]])
            min_axis = ([ellipse['center'][0], ellipse['center'][0]+ellipse['minor_axis'][0]], 
                    [ellipse['center'][1], ellipse['center'][1]+ellipse['minor_axis'][1]])
            
            metrics['major_axis'].append(maj_axis)
            metrics['minor_axis'].append(min_axis)
            metrics['density'].append(ellipse['density'])
            metrics['ratio'].append(ellipse['ratio'])
            metrics['ellipses'].append(ellipse)
        
        # Calculate base radial alignment
        base_radial = metrics['radially_aligned'] / self.n_clusters

        # Convert to numpy arrays and calculate final metrics
        metrics.update({
            'density': np.array(metrics['density']),
            'ratio': np.array(metrics['ratio']),
            'major_axis': np.array(metrics['major_axis']),
            'minor_axis': np.array(metrics['minor_axis']),
            'radially_aligned': metrics['radially_aligned'] / self.n_clusters
        })
        
        metrics.update({
            'radial_low': 1 if base_radial < 0.33 else 0,
            'radial_mid': 1 if 0.33 <= base_radial < 0.66 else 0,
            'radial_high': 1 if base_radial >= 0.66 else 0
        })

        return metrics


    def process_constellation(self, i_data, q_data, data_type):
        """
        Process constellation data and extract features
        
        Args:
            i_data (np.array): I component values
            q_data (np.array): Q component values
            data_type (str): Type of data being processed
            
        Returns:
            dict: Processed results including metrics
        """
        # Extract cluster features
        clusters, cluster_labels = self.extract_cluster_features(i_data, q_data)
        
        # Calculate ellipse metrics
        ellipse_metrics = self.calculate_ellipse_metrics(clusters)
        
        # Get one-hot encoded blob features
        blob_features = self.encode_blobs(self.n_clusters)
        
        # Combine all metrics
        results = {
            'density_avg': np.mean(ellipse_metrics['density']),
            'density_std': np.std(ellipse_metrics['density']),
            'ratio_avg': np.mean(ellipse_metrics['ratio']),
            'ratio_std': np.std(ellipse_metrics['ratio']),
            # 'radially_aligned': ellipse_metrics['radially_aligned'],
            'blobs_4': blob_features[0],
            'blobs_8': blob_features[1],
            'blobs_16': blob_features[2],
            'blobs_32': blob_features[3],
            'class': data_type,
            'std_i': np.std(i_data),
            'std_q': np.std(q_data),
            'radial_low': ellipse_metrics['radial_low'],
            'radial_mid': ellipse_metrics['radial_mid'],
            'radial_high': ellipse_metrics['radial_high'],            
        }
        
        return results, clusters, cluster_labels, ellipse_metrics
    
    def plot_constellation(self, i_data, q_data, clusters, cluster_labels, ellipse_metrics, data_type):
        """
        Generate constellation plots
        
        Args:
            i_data, q_data: IQ data
            clusters: Cluster data
            cluster_labels: Cluster assignments
            ellipse_metrics: Ellipse metrics
            data_type: Type of data
        """
        plt.figure(figsize=(15, 5))
        
        # Original constellation plot
        plt.subplot(1, 3, 1)
        plt.scatter(i_data, q_data, alpha=0.5)
        plt.grid(True)
        plt.title(f'Original Constellation - {data_type}')
        plt.xlabel('I')
        plt.ylabel('Q')
        plt.axis('equal')
        
        # Clustered constellation plot
        plt.subplot(1, 3, 2)
        plt.scatter(i_data, q_data, c=cluster_labels, alpha=0.5)
        plt.grid(True)
        plt.title(f'Clustered Constellation - {data_type}')
        plt.xlabel('I')
        plt.ylabel('Q')
        plt.axis('equal')
        
        # Ellipse plot
        plt.subplot(1, 3, 3)
        for cluster in clusters:
            plt.scatter(cluster[:,0], cluster[:,1], alpha=0.5)
            
        # Add ellipses and axes
        for idx, cluster in enumerate(clusters):
            ellipse = confidence_ellipse(cluster[:,0], cluster[:,1], n_std=self.std_dev)
            plt.gca().add_patch(ellipse['ellipse'])
            
        plt.grid(True)
        plt.title(f'Confidence Ellipses - {data_type}')
        plt.xlabel('I')
        plt.ylabel('Q')
        plt.axis('equal')
        
        plt.tight_layout()
        plt.show()
    
    def process_file(self, file_path, data_type, plot=False):
        """
        Process a single constellation file
        
        Args:
            file_path (str): Path to the CSV file
            data_type (str): Type of data being processed
            plot (bool): Whether to generate plots
            
        Returns:
            dict: Processed results
        """
        try:
            i_data, q_data = self.load_csv_data(file_path)
            results, clusters, cluster_labels, ellipse_metrics = self.process_constellation(i_data, q_data, data_type)
            
            if plot:
                self.plot_constellation(i_data, q_data, clusters, cluster_labels, ellipse_metrics, data_type)
                
            return results
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return None
