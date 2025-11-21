#!/usr/bin/env python3
"""
Plot 20 random constellation diagrams from packet_*.csv files in directory
"""

import sys
import os
import glob
import random
import numpy as np
import matplotlib.pyplot as plt

def plot_random_csv_constellations(directory=".", output_file="random_constellations.png", every_nth=1, num_plots=20, aggregate=1):
    """Create subplot of random constellation diagrams from CSV files"""
    
    # Find all packet_*.csv files
    csv_pattern = os.path.join(directory, "packet_*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if len(csv_files) == 0:
        print(f"No packet_*.csv files found in {directory}")
        return
    
    # Sort files by packet number for sequential aggregation
    csv_files.sort(key=lambda x: int(os.path.basename(x).replace('packet_', '').replace('.csv', '')))
    
    # Select random starting points for aggregation
    max_start = len(csv_files) - aggregate + 1
    if max_start <= 0:
        print(f"Not enough files for aggregation of {aggregate}")
        return
    
    start_indices = random.sample(range(max_start), min(num_plots, max_start))
    
    # Create file groups with sequential aggregation
    file_groups = []
    for start_idx in start_indices:
        group = csv_files[start_idx:start_idx + aggregate]
        file_groups.append(group)
    
    num_plots = len(file_groups)
    
    print(f"Found {len(csv_files)} CSV files, plotting {num_plots} random ones")
    
    # Create subplot grid
    cols = 5
    rows = (num_plots + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 3*rows))
    
    # Handle single row case
    if rows == 1:
        axes = axes.reshape(1, -1)
    fig.suptitle(f'Random Constellation Diagrams from CSV Files', fontsize=16)
    
    for i, file_group in enumerate(file_groups):
        row = i // cols
        col = i % cols
        ax = axes[row, col]
        
        try:
            # Aggregate samples from multiple CSV files
            all_i_samples = []
            all_q_samples = []
            packet_nums = []
            
            for csv_file in file_group:
                data = np.loadtxt(csv_file, delimiter=',')
                i_samples = data[:, 0][::every_nth]
                q_samples = data[:, 1][::every_nth]
                all_i_samples.extend(i_samples)
                all_q_samples.extend(q_samples)
                
                # Extract packet number
                filename = os.path.basename(csv_file)
                packet_num = filename.replace('packet_', '').replace('.csv', '')
                packet_nums.append(packet_num)
            
            # Convert to numpy arrays
            all_i_samples = np.array(all_i_samples)
            all_q_samples = np.array(all_q_samples)
            
            # Limit samples for performance
            if len(all_i_samples) > 1000:
                indices = np.random.choice(len(all_i_samples), 1000, replace=False)
                all_i_samples = all_i_samples[indices]
                all_q_samples = all_q_samples[indices]
            
            # Plot constellation
            ax.scatter(all_i_samples, all_q_samples, alpha=0.6, s=0.5)
            
            # Create title showing aggregated packets
            if len(packet_nums) == 1:
                title = f'Packet {packet_nums[0]}'
            else:
                title = f'Packets {packet_nums[0]}-{packet_nums[-1]} ({len(packet_nums)} files)'
            ax.set_title(title, fontsize=8)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error loading\nfiles', 
                   ha='center', va='center', transform=ax.transAxes)
        
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
    
    # Hide empty subplots
    for i in range(num_plots, rows * cols):
        row = i // cols
        col = i % cols
        axes[row, col].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Random constellation overview saved to {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot random constellation diagrams from CSV files')
    parser.add_argument('directory', nargs='?', default='.', help='Directory containing packet_*.csv files')
    parser.add_argument('--output', default='random_constellations.png', help='Output file name')
    parser.add_argument('--every-nth', type=int, default=1, help='Plot every nth sample (e.g., 2 for every other)')
    parser.add_argument('--num-plots', type=int, default=20, help='Number of plots to create')
    parser.add_argument('--aggregate', type=int, default=1, help='Number of CSV files to aggregate per plot')
    
    args = parser.parse_args()
    
    plot_random_csv_constellations(args.directory, args.output, args.every_nth, args.num_plots, args.aggregate)