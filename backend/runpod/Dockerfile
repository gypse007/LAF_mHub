FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install --no-cache-dir \
    runpod \
    diffusers[torch] \
    transformers \
    accelerate \
    safetensors \
    Pillow

# Copy worker file
COPY worker.py /worker.py

# Download models during build so the container cold-starts instantly
RUN python -c "from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL; import torch; \
    ControlNetModel.from_pretrained('diffusers/controlnet-depth-sdxl-1.0', variant='fp16', use_safetensors=True, torch_dtype=torch.float16); \
    AutoencoderKL.from_pretrained('madebyollin/sdxl-vae-fp16-fix', torch_dtype=torch.float16); \
    StableDiffusionXLControlNetPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0', variant='fp16', use_safetensors=True, torch_dtype=torch.float16);"

CMD ["python", "-u", "/worker.py"]
