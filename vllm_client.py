import argparse
import asyncio
import aiohttp
import json
import traceback
import uuid

from transformers import AutoTokenizer
from tqdm import tqdm

class LLMClient:
    def __init__(self, flags: argparse.Namespace):
        self._tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct')
        self._flags = flags
        if not self._flags.url.startswith("http://"):
            self._flags.url = "http://" + self._flags.url
        self._flags.url += '/v1/completions'
        self._results = []  # Store results as a list of dictionaries
        self._loop = asyncio.get_event_loop()
        self._ccu = 0

    async def async_request_iterator(self, prompts, sampling_parameters):
        try:
            for i, prompt in enumerate(prompts):
                while self._ccu >= self._flags.concurrent_request:
                    await asyncio.sleep(0.05)

                prompt_id = str(uuid.uuid4())
                self._results.append({"prompt_id": prompt_id, "prompt": prompt, "response": ""})
                self._ccu += 1

                json_request = {
                    "prompt_id": prompt_id,
                    "prompt": prompt,
                    "sampling_parameters": sampling_parameters
                }
                
                yield json_request

        except Exception as error:
            print(f"Error in request iterator: {error}")
            traceback.print_exc()

    async def send_request(self, json_request):
        prompt = json_request["prompt"]
        prompt_id = json_request["prompt_id"]
        sampling_parameters = json_request["sampling_parameters"]
        try:
            conversation = [{'role': 'user', 'content': prompt}]
            prompt = self._tokenizer.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)

            vllm_request_dict = {
                "model": self._flags.model,
                "prompt": prompt,
                "max_tokens": sampling_parameters["max_tokens"],
                "temperature": sampling_parameters["temperature"],
                "ignore_eos": sampling_parameters["ignore_eos"],
                "stream": False,
                "seed": 42,
                "skip_special_tokens": True,
            }
            
            if not sampling_parameters['ignore_eos']:
                vllm_request_dict["stop"] = [
                    "<|end_of_text|>", "<|eot_id|>", 
                    "<|endoftext|>", "<|im_end|>", "<|eom_id|>"
                ]

            headers = {"Content-Type": "application/json"}
            session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=1200, sock_read=1200)
            async with aiohttp.ClientSession(headers=headers, timeout=session_timeout) as session:
                async with session.post(self._flags.url, data=json.dumps(vllm_request_dict)) as response:
                    response_json = await response.json()
                    for entry in self._results:
                        if entry["prompt_id"] == prompt_id:
                            if response_json and "choices" in response_json and len(response_json["choices"]) > 0:
                                entry["response"] = response_json["choices"][0]["text"]
                            else:
                                entry["response"] = ""
                            break

        except Exception as e:
            print(f"Error during request for prompt ID {prompt_id}: {e}")
            traceback.print_exc()

        finally:
            self._ccu -= 1

    async def run(self):
        sampling_parameters = {"max_tokens": 8192, "temperature": 0, "ignore_eos": False}
        input_file_name = self._flags.input_file

        if not input_file_name.endswith(".jsonl"):
            raise Exception("Only JSONL input files are supported.")

        prompts = []
        try:
            with open(input_file_name, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    if "prompt" not in data:
                        raise Exception("Each line in JSONL file must have a 'prompt' key")
                    prompts.append(data["prompt"])
        except FileNotFoundError:
            raise Exception(f"Input file not found: {input_file_name}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in {input_file_name}")

        total_requests = len(prompts)
        pbar = tqdm(total=total_requests, desc="Sending Requests")

        tasks = []
        async for request in self.async_request_iterator(prompts, sampling_parameters):
            task = self._loop.create_task(self.send_request(request))
            tasks.append(task)
            pbar.update(1)

        await asyncio.gather(*tasks)
        pbar.close()

        with open(self._flags.results_file, "w") as f:
            for entry in self._results:
                f.write(json.dumps(entry) + "\n")

    def run_async(self):
        self._loop.run_until_complete(self.run())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", type=str, required=False, default="llama2-7b-hf", help="Model name")
    parser.add_argument("-u", "--url", type=str, required=False, default="localhost:8001", help="Inference server URL")
    parser.add_argument("--input-file", type=str, required=False, default="prompts.jsonl", help="JSONL file with input prompts")
    parser.add_argument("--results-file", type=str, required=False, default="results.jsonl", help="Output file for results (JSONL)")
    parser.add_argument("-c", "--concurrent-request", type=int, required=False, default=10, help="Number of concurrent requests")
    FLAGS = parser.parse_args()

    client = LLMClient(FLAGS)
    client.run_async()