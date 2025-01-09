import json
import requests
import time
import argparse
import threading
import os
from tqdm import tqdm

def send_request(url, model, prompt, request_id, results, errors, semaphore, pbar):
    """Sends a single request to the vLLM server."""
    headers = {"Content-Type": "application/json"}
    pload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 0.8,
        "repetition_penalty": 1.05,
        "stream": False
    }

    try:
        semaphore.acquire()
        response = requests.post(url, headers=headers, json=pload, timeout=1200)
        response.raise_for_status()

        response_json = response.json()
        results[request_id] = {
            "request_id": request_id,
            "prompt": prompt,
            "response": response_json["choices"][0]["message"]["content"]
        }
    except requests.exceptions.RequestException as e:
        errors[request_id] = str(e)
        results[request_id] = {
            "request_id": request_id,
            "prompt": prompt,
            "response": None  # Indicate failed requests with response = None
        }
    finally:
        semaphore.release()
        pbar.update(1)

def main(args):
    """Reads prompts from a JSONL file and performs batch inference."""
    url = f"http://{args.url}/v1/chat/completions"
    prompts = []

    with open(args.input_file, "r") as f:
        for line in f:
            data = json.loads(line)
            prompts.append(data["prompt"])

    results = {}
    errors = {}
    start_time = time.time()

    semaphore = threading.Semaphore(args.concurrent_request)

    with tqdm(total=len(prompts), desc="Processing requests") as pbar:
        threads = []
        for i, prompt in enumerate(prompts):
            thread = threading.Thread(
                target=send_request, 
                args=(
                    url, 
                    args.model, 
                    prompt, i, 
                    results, 
                    errors, 
                    semaphore, 
                    pbar
                )
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Sort results by request_id
    sorted_results = [results[i] for i in sorted(results.keys())]

    # Write sorted results to output file
    with open(args.results_file, "w") as outfile:
        for result in sorted_results:
            json.dump(result, outfile)
            outfile.write('\n')

    # Prepare statistics
    successful_requests = sum(1 for res in results.values() if res["response"] is not None)
    total_requests = len(prompts)
    throughput = successful_requests / elapsed_time
    failed_request_ids = list(errors.keys())

    stats = {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": total_requests - successful_requests,
        "failed_request_ids": failed_request_ids,  # Store failed request IDs
        "elapsed_time": elapsed_time,
        "throughput": throughput,
    }

    # Write statistics to a file
    input_file_name = os.path.splitext(args.input_file)[0]
    stats_file_name = f"{input_file_name}_stats.json"

    with open(stats_file_name, "w") as f:
        json.dump(stats, f, indent=4)

    print(f"Statistics written to {stats_file_name}")

    # (Optional) Print errors to console
    if errors:
        print("=" * 20)
        print("Errors:")
        print("=" * 20)
        for request_id, error in errors.items():
            print(f"Request ID: {request_id}")
            print(f"Prompt: {prompts[request_id]}")
            print(f"Error: {error}")
            print("-" * 10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch inference script for vLLM server.")
    parser.add_argument("-m", "--model", type=str, required=False, default="llama2-7b-hf", help="Model name")
    parser.add_argument("-u", "--url", type=str, required=False, default="localhost:8001", help="Inference server URL")
    parser.add_argument("--input_file", type=str, required=False, default="prompts.jsonl", help="JSONL file with input prompts")
    parser.add_argument("--results_file", type=str, required=False, default="results.jsonl", help="Output file for results (JSONL)")
    parser.add_argument("-c", "--concurrent_request", type=int, required=False, default=10, help="Number of concurrent requests")
    args = parser.parse_args()

    main(args)
