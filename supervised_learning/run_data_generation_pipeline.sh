#!/bin/bash

# Exit on any error
set -e

echo "Starting data generation and processing pipeline..."

# Store the original directory
ORIGINAL_DIR=$PWD

# Step 1: Create folders
echo "Creating folders..."
cd data_generation/generator
./create_folders.sh

# Step 2: Run Docker container with GNU Radio
echo "Running GNU Radio container..."
cd ../..
docker run -it --rm -v $PWD/data_generation:/temp/data gnuradio-image bash -c "cd /temp/data/generator && python3 generator.py"

# Step 3: Process the data
echo "Processing data..."
cd data_generation/generator
python3 process.py

# Return to original directory
cd $ORIGINAL_DIR

echo "Pipeline completed successfully!"
