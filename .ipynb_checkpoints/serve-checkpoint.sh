CUDA_VISIBLE_DEVICES=0 vllm serve \
       	Qwen/Qwen2.5-7B-Instruct \
        --port 9002 \
        --dtype auto \
        --tensor-parallel-size 1 \
        --disable-log-requests
        