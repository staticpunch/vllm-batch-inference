#!/bin/bash

# --- Configuration ---
# Model and server settings
MODEL="Llama-3.3-70B-Instruct"
SERVER_URL="0.0.0.0:9012"
CONCURRENT_REQUESTS=64

# Directory settings
INPUT_DIR="./question-prompts"
OUTPUT_DIR="./question-results"

# Loop parameters (similar to Python's range)
LOWER_BOUND=0
UPPER_BOUND=2
STEP=1

# --- Script Logic ---

# Get the name of the current script
SCRIPT_NAME=$(basename "$0")

# Get the current time in a suitable format (e.g., YYYYMMDD_HHMMSS)
CURRENT_TIME=$(date +"%Y%m%d_%H%M%S")

# Create a new script name with the current time appended
NEW_SCRIPT_NAME="${SCRIPT_NAME%.*}_${CURRENT_TIME}.${SCRIPT_NAME##*.}"

# Copy the script to the input directory with the new name
cp "$0" "$OUTPUT_DIR/$NEW_SCRIPT_NAME"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Loop through the input files using specified range
for i in $(seq "$LOWER_BOUND" "$STEP" "$UPPER_BOUND"); do
  # Use printf to format the index with leading zeros
  INDEX=$(printf "%03d" "$i")

  INPUT_FILE="$INPUT_DIR/input_$INDEX.jsonl"
  OUTPUT_FILE="$OUTPUT_DIR/output_$INDEX.jsonl"

  # Check if the input file exists
  if [ -f "$INPUT_FILE" ]; then
    echo "Processing input file: $INPUT_FILE"

    python vllm_client.py \
      -m "$MODEL" \
      -u "$SERVER_URL" \
      --input-file "$INPUT_FILE" \
      --results-file "$OUTPUT_FILE" \
      -c "$CONCURRENT_REQUESTS"

    echo "Results written to: $OUTPUT_FILE"
  else
    echo "Warning: Input file not found: $INPUT_FILE"
  fi
done

echo "Processing complete."
