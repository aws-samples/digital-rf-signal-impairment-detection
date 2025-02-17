import numpy as np
import matplotlib.pyplot as plt
import os
import glob

def convert_complex_data(npy_path: str):
    """
    Convert a complex NPY file to both CSV and JPG files.
    
    Args:
        npy_path: Path to input NPY file
    """
    try:
        # Create output paths
        base_path = os.path.splitext(npy_path)[0]
        csv_path = base_path + '.csv'
        jpg_path = base_path + '.jpeg'
        
        # Load complex data
        complex_data = np.fromfile(npy_path, dtype=np.complex64)
        
        # Extract I/Q components
        i_data = np.real(complex_data)
        q_data = np.imag(complex_data)
        
        # Save CSV
        xy_coords = np.column_stack((i_data, q_data))
        np.savetxt(csv_path, xy_coords, delimiter=',', header='I,Q', comments='')
        
        # Create constellation plot
        plt.ioff()
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        
        # Create scatter plot
        ax.scatter(i_data, q_data, alpha=0.5, s=1)
        
        # Basic plot styling
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Set axis limits
        limit = max(abs(i_data).max(), abs(q_data).max()) * 1.1
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        
        # Save and clean up plot
        plt.savefig(jpg_path, bbox_inches='tight', dpi=300, pad_inches=0)
        plt.close(fig)
        
        # Remove the original NPY file
        os.remove(npy_path)
        
        # print(f"Processed {npy_path} -> {csv_path}, {jpg_path}")
        
    except Exception as e:
        print(f"Error processing {npy_path}: {e}")

def process_directory(root_dir: str):
    """
    Recursively process all NPY files in the directory and convert to both CSV and JPG files.
    
    Args:
        root_dir: Root directory to start the search
    """
    # Find all .npy files in directory and subdirectories
    npy_files = glob.glob(os.path.join(root_dir, '**/*.npy'), recursive=True)
    total_files = len(npy_files)
    
    print(f"Found {total_files} NPY files to process")
    
    for idx, npy_file in enumerate(npy_files, 1):
        # print(f"Processing file {idx}/{total_files}: {npy_file}")
        convert_complex_data(npy_file)
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    root_directory = '/Users/eparsell/digital-rf-signal-impairment-detection/data_generation/generator/data'
    process_directory(root_directory)
