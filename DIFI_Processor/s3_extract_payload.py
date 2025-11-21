#!/usr/bin/env python3
"""
Extract signal payload from DIFI packets with S3 support
"""

import boto3
import tempfile
import os
from extract_payload import extract_payload_from_pcap

def extract_from_s3(bucket, pcap_key, output_prefix="packet", max_packets=None):
    """Download PCAP from S3, extract payload, return count"""
    s3 = boto3.client('s3')
    
    try:
        print(f"Checking if s3://{bucket}/{pcap_key} exists...")
        s3.head_object(Bucket=bucket, Key=pcap_key)
        print("File found, downloading...")
    except Exception as e:
        print(f"Error accessing s3://{bucket}/{pcap_key}: {e}")
        return 0
    
    with tempfile.NamedTemporaryFile(suffix='.pcap', delete=False) as tmp_file:
        s3.download_file(bucket, pcap_key, tmp_file.name)
        count = extract_payload_from_pcap(tmp_file.name, output_prefix, max_packets)
        os.unlink(tmp_file.name)
    
    return count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract DIFI payload from S3 PCAP')
    parser.add_argument('bucket', help='S3 bucket name')
    parser.add_argument('pcap_key', help='S3 key for PCAP file')
    parser.add_argument('--prefix', default='packet', help='Output file prefix')
    parser.add_argument('--max-packets', type=int, help='Maximum packets to process')
    
    args = parser.parse_args()
    
    count = extract_from_s3(args.bucket, args.pcap_key, args.prefix, args.max_packets)
    print(f"Extracted {count} packets from s3://{args.bucket}/{args.pcap_key}")