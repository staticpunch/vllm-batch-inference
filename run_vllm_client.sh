#!/bin/bash

# Set default values for the parameters
MODEL="Qwen/Qwen2.5-7B-Instruct"  # Replace with your actual model name
SERVER_URL="0.0.0.0:9002"
INPUT_FILE="prompts.jsonl"
RESULTS_FILE="results.jsonl"
CONCURRENT_REQUESTS=64

python vllm_client.py \
  -m "$MODEL" \
  -u "$SERVER_URL" \
  --input-file "$INPUT_FILE" \
  --results-file "$RESULTS_FILE" \
  -c "$CONCURRENT_REQUESTS"