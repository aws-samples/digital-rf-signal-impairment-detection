#!/usr/bin/env python3
"""
Plot constellation diagrams and upload to S3
"""

import boto3
import tempfile
import os
from plot_random_csv import plot_random_csv_constellations

def plot_and_upload_s3(bucket, output_key, directory=".", every_nth=1, num_plots=20, aggregate=1):
    """Create constellation plot and upload to S3"""
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        plot_random_csv_constellations(directory, tmp_file.name, every_nth, num_plots, aggregate)
        
        s3 = boto3.client('s3')
        s3.upload_file(tmp_file.name, bucket, output_key)
        os.unlink(tmp_file.name)
    
    print(f"Constellation plot uploaded to s3://{bucket}/{output_key}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot constellations and upload to S3')
    parser.add_argument('bucket', help='S3 bucket name')
    parser.add_argument('output_key', help='S3 key for output PNG')
    parser.add_argument('--directory', default='.', help='Directory with CSV files')
    parser.add_argument('--every-nth', type=int, default=1, help='Plot every nth sample')
    parser.add_argument('--num-plots', type=int, default=20, help='Number of plots')
    parser.add_argument('--aggregate', type=int, default=1, help='Files to aggregate per plot')
    
    args = parser.parse_args()
    
    plot_and_upload_s3(args.bucket, args.output_key, args.directory, 
                      args.every_nth, args.num_plots, args.aggregate)