import runpod
import torch
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL
from PIL import Image
import base64
import io

pipe = None

def init_model():
    global pipe
    print("Loading SDXL + ControlNet on CUDA...")
    controlnet = ControlNetModel.from_pretrained(
        "diffusers/controlnet-depth-sdxl-1.0",
        variant="fp16",
        use_safetensors=True,
        torch_dtype=torch.float16,
    )
    vae = AutoencoderKL.from_pretrained(
        "madebyollin/sdxl-vae-fp16-fix",
        torch_dtype=torch.float16
    )
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        controlnet=controlnet,
        vae=vae,
        variant="fp16",
        use_safetensors=True,
        torch_dtype=torch.float16,
    )
    # Enable memory/speed optimizations for A100/H100
    pipe.enable_model_cpu_offload()
    print("Model loaded successfully.")

def handler(event):
    """
    RunPod Serverless Handler.
    Expects input:
    {
        "input": {
            "prompt": "...",
            "negative_prompt": "...",
            "depth_map_b64": "base64_encoded_depth_image",
            "num_inference_steps": 30,
            "controlnet_conditioning_scale": 0.85
        }
    }
    """
    global pipe
    if pipe is None:
        init_model()

    job_input = event.get("input", {})
    prompt = job_input.get("prompt")
    neg_prompt = job_input.get("negative_prompt", "flat, poor quality, bad lighting, cartoon, distorted room, mismatched perspective")
    depth_b64 = job_input.get("depth_map_b64")
    steps = job_input.get("num_inference_steps", 30)
    cond_scale = job_input.get("controlnet_conditioning_scale", 0.85)

    if not prompt or not depth_b64:
        return {"error": "Missing prompt or depth_map_b64"}

    try:
        # Decode depth map
        depth_bytes = base64.b64decode(depth_b64)
        depth_img = Image.open(io.BytesIO(depth_bytes)).convert("RGB")
        
        # Format the prompt using the 8-layer architectural structure for best output
        # (Assuming the main app already sent the fully structured prompt)

        print(f"Generating image with {steps} steps...")
        result_img = pipe(
            prompt=prompt,
            negative_prompt=neg_prompt,
            image=depth_img,
            controlnet_conditioning_scale=cond_scale,
            num_inference_steps=steps
        ).images[0]

        # Encode output to base64
        buffered = io.BytesIO()
        result_img.save(buffered, format="JPEG", quality=95)
        out_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return {"result_b64": out_b64}

    except Exception as e:
        print(f"Error during generation: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
