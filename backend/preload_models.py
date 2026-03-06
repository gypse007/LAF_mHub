import logging
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

device = "mps" if torch.backends.mps.is_available() else "cpu"

def preload():
    logger.info("Initializing SAM download...")
    from transformers import pipeline
    generator = pipeline("mask-generation", model="facebook/sam-vit-base", device=device)
    logger.info("SAM downloaded successfully!")

    logger.info("Initializing MiDaS Depth Estimator download...")
    depth_estimator = pipeline(task="depth-estimation", model="Intel/dpt-large")
    logger.info("MiDaS downloaded successfully!")

    logger.info("Initializing SDXL ControlNet + Base Models download... This will take a while (15GB+).")
    from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL

    controlnet = ControlNetModel.from_pretrained(
        "diffusers/controlnet-depth-sdxl-1.0",
        torch_dtype=torch.float16 if device != "cpu" else torch.float32
    )
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)

    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        controlnet=controlnet,
        vae=vae,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        use_safetensors=True
    )
    logger.info("All SDXL models downloaded successfully!")

if __name__ == "__main__":
    preload()
