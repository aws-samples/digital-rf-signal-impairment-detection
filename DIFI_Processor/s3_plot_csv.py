#!/usr/bin/env python3
"""
Plot constellation diagrams and upload to S3
"""

import boto3
import tempfile
import os
from plot_random_csv import plot_random_csv_constellations

def plot_and_upload_s3(bucket, output_key, directory=".", every_nth=1, num_plots=20, aggregate=1):
    """Create constellation plots and upload to S3"""
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_base = os.path.join(tmp_dir, "constellation")
        output_files = plot_random_csv_constellations(directory, tmp_base + ".png", every_nth, num_plots, aggregate)
        
        s3 = boto3.client('s3')
        base_key = os.path.splitext(output_key)[0]
        
        uploaded_keys = []
        for output_file in output_files:
            filename = os.path.basename(output_file)
            s3_key = f"{base_key}_{filename}"
            s3.upload_file(output_file, bucket, s3_key)
            uploaded_keys.append(s3_key)
    
    print(f"Uploaded {len(uploaded_keys)} constellation plots to s3://{bucket}/")
    for key in uploaded_keys:
        print(f"  - {key}")
    return uploaded_keys

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot constellations and upload to S3')
    parser.add_argument('bucket', help='S3 bucket name')
    parser.add_argument('output_key', help='S3 key prefix for output PNGs')
    parser.add_argument('--directory', default='.', help='Directory with CSV files')
    parser.add_argument('--every-nth', type=int, default=1, help='Plot every nth sample')
    parser.add_argument('--num-plots', type=int, default=20, help='Number of plots')
    parser.add_argument('--aggregate', type=int, default=1, help='Files to aggregate per plot')
    
    args = parser.parse_args()
    
    plot_and_upload_s3(args.bucket, args.output_key, args.directory, 
                      args.every_nth, args.num_plots, args.aggregate)