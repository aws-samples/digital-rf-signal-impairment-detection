import json
import os
import boto3
import subprocess
import tempfile

def handler(event, context):
    """Lambda handler for processing PCAP files from S3 events"""
    
    # Check if this is a test invocation
    if 'test' in event:
        return {
            'statusCode': 200,
            'body': json.dumps('Lambda function is working!')
        }
    
    # Process S3 event records
    if 'Records' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('No S3 records found in event')
        }
    
    results = []
    
    for record in event['Records']:
        # Extract S3 event details
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        print(f"Processing S3 event: {bucket}/{key}")
        
        result = process_pcap_file(bucket, key)
        results.append(result)
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {len(results)} files')
    }

def process_pcap_file(bucket, key):
    """Process a single PCAP file"""
    
    s3_client = boto3.client('s3')
    results_bucket = os.environ['RESULTS_BUCKET']
    
    print(f"Processing {key} from bucket {bucket}")
    
    try:
        # Download PCAP file to temp location
        with tempfile.NamedTemporaryFile(suffix='.pcap', delete=False) as tmp_file:
            s3_client.download_file(bucket, key, tmp_file.name)
            pcap_path = tmp_file.name
        
        # Process the PCAP file
        output_dir = tempfile.mkdtemp()
        
        # Step 1: Extract payload using local file
        max_packets = os.environ.get('MAX_PACKETS', '100')
        prefix = os.environ.get('OUTPUT_PREFIX', 'packet')
        
        extract_cmd = [
            'python', os.path.join(os.getcwd(), 'extract_payload.py'),
            pcap_path,
            '--prefix', prefix,
            '--max-packets', max_packets
        ]
        
        # Change to output directory and run extraction
        original_cwd = os.getcwd()
        os.chdir(output_dir)
        result = subprocess.run(extract_cmd, capture_output=True, text=True)
        os.chdir(original_cwd)
        
        print(f"Extract stdout: {result.stdout}")
        print(f"Extract stderr: {result.stderr}")
        
        if result.returncode != 0:
            print(f"Error extracting {key}: {result.stderr}")
            return f'Error extracting {key}: {result.stderr}'
        
        print(f"Successfully extracted payload from {key}")
        
        # Check if CSV files were created
        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
        print(f"Found CSV files: {csv_files}")
        
        if not csv_files:
            # Check if extraction found no DIFI packets
            if "No DIFI data packets found" in result.stdout:
                return f'No DIFI packets found in {key} - processing complete'
            else:
                return 'No CSV files generated from extraction'
        
        # Step 2: Generate constellation plots
        num_plots = os.environ.get('NUM_PLOTS', '20')
        every_nth = os.environ.get('EVERY_NTH', '1')
        aggregate = os.environ.get('AGGREGATE', '1')
        
        plot_cmd = [
            'python', 's3_plot_csv.py',
            results_bucket,
            f"results/{key.replace('.pcap', '')}/constellation.png",
            '--directory', output_dir,
            '--num-plots', num_plots,
            '--every-nth', every_nth,
            '--aggregate', aggregate
        ]
        
        result = subprocess.run(plot_cmd, capture_output=True, text=True)
        
        print(f"Plot stdout: {result.stdout}")
        print(f"Plot stderr: {result.stderr}")
        
        if result.returncode != 0:
            print(f"Error plotting {key}: {result.stderr}")
            return f'Error plotting {key}: {result.stderr}'
        
        print(f"Successfully generated plots for {key}")
        
        # Clean up temp files
        os.unlink(pcap_path)
        import shutil
        shutil.rmtree(output_dir)
        
        return f'Successfully processed {key}'
        
    except Exception as e:
        print(f"Exception processing {key}: {str(e)}")
        return f'Error processing {key}: {str(e)}'