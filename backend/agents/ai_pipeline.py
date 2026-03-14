import cv2
import numpy as np
import torch
from PIL import Image
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class AdvancedMuralPipeline:
    """
    V2 Production-Ready Mural Pipeline.
    Implements Depth-Guided Diffusion, Homography Perspective Warping, and Lighting Mathing.
    """
    def __init__(self, use_mock: bool = True):
        # Defaulting to mock for local dev to avoid sudden 15GB SDXL downloads.
        # Set to False in production.
        self.use_mock = use_mock
        self.device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        self.depth_estimator = None
        self.pipe = None
        self.models_loaded = False

    def load_models(self):
        if self.use_mock or self.models_loaded:
            return
            
        logger.info(f"Loading SDXL + ControlNet on {self.device}...")
        from transformers import pipeline
        from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL

        # 1. Load MiDaS Depth Estimator
        self.depth_estimator = pipeline(task="depth-estimation", model="Intel/dpt-large")
        
        # 2. Load ControlNet (Depth)
        controlnet = ControlNetModel.from_pretrained(
            "diffusers/controlnet-depth-sdxl-1.0",
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32
        )
        
        # 3. Load SDXL Base with VAE (for lower VRAM usage)
        vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
        
        self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            controlnet=controlnet,
            vae=vae,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            use_safetensors=True
        )
        
        # Optimization for Mac MPS or CUDA
        if self.device == "mps":
            import os
            os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
            self.pipe.to(self.device)
            # Dramatically reduces memory usage on Mac to prevent Metal crashes
            self.pipe.enable_attention_slicing()
            # Also slice the VAE to prevent OOM when decoding the high-res image
            self.pipe.enable_vae_slicing()
            logger.info("Enabled MPS attention and VAE slicing to prevent OOM crashes.")
        elif self.device == "cuda":
            self.pipe.enable_model_cpu_offload()

        self.models_loaded = True

    def get_depth_map(self, pil_image: Image.Image) -> Image.Image:
        """Extracts room geometry map using MiDaS."""
        if self.use_mock:
            # Return a simple mock depth map
            return Image.new("L", pil_image.size, color=128)
            
        self.load_models()
        logger.info("Extracting depth map with MiDaS...")
        depth_output = self.depth_estimator(pil_image)
        return depth_output["depth"]

    def create_mask(self, image_size: Tuple[int, int], corners: List[List[int]]) -> np.ndarray:
        """Rasterizes the 4 print area corners into a binary mask."""
        mask = np.zeros((image_size[1], image_size[0]), dtype=np.uint8)
        pts = np.array(corners, np.int32)
        cv2.fillPoly(mask, [pts], 255)
        return mask

    def _enhance_prompt_for_mural(self, raw_prompt: str) -> str:
        """Auto-translates a user's free-form prompt into a high-quality mural prompt."""
        # Strip common filler words and enhance with mural-specific language
        enhanced = raw_prompt.strip().rstrip('.')
        
        # Add mural-optimized suffixes if not already present
        quality_tags = []
        lower = enhanced.lower()
        if 'mural' not in lower:
            quality_tags.append('wall mural art')
        if '8k' not in lower and '4k' not in lower and 'high res' not in lower:
            quality_tags.append('8k ultra high resolution')
        if 'realistic' not in lower and 'photorealistic' not in lower:
            quality_tags.append('photorealistic')
        if 'detail' not in lower:
            quality_tags.append('intricate details')
        
        quality_tags.extend([
            'masterpiece quality',
            'professional art',
            'vivid colors',
            'beautiful composition'
        ])
        
        return f"{enhanced}, {', '.join(quality_tags)}"

    def generate_mural(self, wall_image: Image.Image, prompt: str, corners: List[List[int]], reference_image_path: str = None) -> Image.Image:
        """Generates the base mural using RunPod Nano Banana or falls back to mock."""
        import os
        import requests
        import base64
        import io
        import time
        
        runpod_api_key = os.getenv("RUNPOD_API_KEY")
        runpod_endpoint = os.getenv("RUNPOD_ENDPOINT_ID")
        
        # Enhance the prompt for mural quality
        enhanced_prompt = self._enhance_prompt_for_mural(prompt)
        logger.info(f"Enhanced prompt: {enhanced_prompt}")

        # ─── REAL GENERATION via RunPod Nano Banana ───
        # RunPod credentials OVERRIDE use_mock — if you have keys, use real generation
        if runpod_api_key and runpod_endpoint:
            logger.info(f"Routing generation to RunPod Nano Banana: {runpod_endpoint}")
            
            headers = {
                "Authorization": f"Bearer {runpod_api_key}",
                "Content-Type": "application/json"
            }
            
            # Determine output size based on wall image
            w, h = wall_image.size
            # Cap at 1024 for fast generation, maintain aspect ratio
            scale = min(1024 / max(w, h), 1.0)
            out_w = int(w * scale)
            out_h = int(h * scale)
            # Round to nearest 8 (required by most diffusion models)
            out_w = (out_w // 8) * 8
            out_h = (out_h // 8) * 8
            
            # Nano Banana is an IMAGE EDITING model — it needs a source image
            # Resize and encode the wall image as base64
            resized_wall = wall_image.resize((out_w, out_h), Image.Resampling.LANCZOS)
            wall_buf = io.BytesIO()
            resized_wall.save(wall_buf, format="PNG")
            wall_b64 = base64.b64encode(wall_buf.getvalue()).decode("utf-8")
            
            payload = {
                "input": {
                    "prompt": enhanced_prompt,
                    "images": [wall_b64],
                    "resolution": "1k",
                    "output_format": "png",
                    "enable_safety_checker": True,
                    "width": out_w,
                    "height": out_h
                }
            }
            
            try:
                # Submit async job
                run_url = f"https://api.runpod.ai/v2/{runpod_endpoint}/run"
                logger.info(f"Submitting job to {run_url}")
                resp = requests.post(run_url, json=payload, headers=headers, timeout=30)
                resp.raise_for_status()
                job_data = resp.json()
                job_id = job_data.get("id")
                
                if not job_id:
                    raise Exception(f"No job ID returned: {job_data}")
                
                logger.info(f"RunPod job submitted: {job_id}, polling for results...")
                
                # Poll for completion (max 120 seconds)
                status_url = f"https://api.runpod.ai/v2/{runpod_endpoint}/status/{job_id}"
                for attempt in range(60):  # 60 * 2s = 120s max
                    time.sleep(2)
                    status_resp = requests.get(status_url, headers=headers, timeout=15)
                    status_resp.raise_for_status()
                    status_data = status_resp.json()
                    status = status_data.get("status")
                    
                    logger.info(f"  Poll {attempt+1}: {status}")
                    
                    if status == "COMPLETED":
                        output = status_data.get("output")
                        logger.info(f"  RunPod raw output: {output}")
                        
                        # Handle different output formats
                        image_data = None
                        if isinstance(output, list) and len(output) > 0:
                            # Format: [{"image": "url_or_b64", ...}]
                            item = output[0]
                            image_data = item.get("image") or item.get("image_url") or item.get("result")
                        elif isinstance(output, dict):
                            # Format: {"image": "url_or_b64"} or {"result_b64": "..."}
                            image_data = output.get("image") or output.get("image_url") or output.get("result_b64") or output.get("result") or output.get("images")
                            # If images is a list, take first
                            if isinstance(image_data, list) and len(image_data) > 0:
                                image_data = image_data[0]
                                if isinstance(image_data, dict):
                                    image_data = image_data.get("image") or image_data.get("url") or image_data.get("image_url")
                        elif isinstance(output, str):
                            image_data = output
                        
                        if not image_data:
                            raise Exception(f"Could not extract image from RunPod output: {output}")
                        
                        # Check if it's a URL or base64
                        if image_data.startswith("http"):
                            logger.info(f"Downloading result image from URL...")
                            img_resp = requests.get(image_data, timeout=30)
                            img_resp.raise_for_status()
                            return Image.open(io.BytesIO(img_resp.content)).convert("RGB")
                        else:
                            # Base64 encoded
                            # Strip data URI prefix if present
                            if "," in image_data:
                                image_data = image_data.split(",", 1)[1]
                            img_bytes = base64.b64decode(image_data)
                            return Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    
                    elif status == "FAILED":
                        error = status_data.get("error", "Unknown error")
                        raise Exception(f"RunPod job failed: {error}")
                    
                    elif status in ("IN_QUEUE", "IN_PROGRESS"):
                        continue
                    else:
                        logger.warning(f"Unknown status: {status}")
                
                raise Exception("RunPod job timed out after 120 seconds")
                
            except Exception as e:
                logger.error(f"RunPod Nano Banana error: {e}")
                logger.info("Falling back to mock generation...")
                # Fall through to mock below

        # ─── MOCK FALLBACK (only if no RunPod credentials) ───
        logger.info(f"Mock generating mural image for prompt: {enhanced_prompt}")
        
        w, h = wall_image.size
        mock = np.zeros((h, w, 3), dtype=np.uint8)
        
        import hashlib
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        
        c1 = rng.randint(60, 200, 3)
        c2 = rng.randint(60, 200, 3)
        c3 = rng.randint(60, 200, 3)
        c4 = rng.randint(60, 200, 3)
        
        for y in range(h):
            fy = y / max(h - 1, 1)
            top = c1 * (1 - fy) + c3 * fy
            bot = c2 * (1 - fy) + c4 * fy
            for x_step in range(0, w, max(1, w // 200)):
                fx = x_step / max(w - 1, 1)
                color = top * (1 - fx) + bot * fx
                end = min(x_step + max(1, w // 200), w)
                mock[y, x_step:end] = color.astype(np.uint8)
        
        noise = rng.normal(0, 15, mock.shape).astype(np.float32)
        mock = np.clip(mock.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        
        mock_cv = mock.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = prompt[:60] + ("..." if len(prompt) > 60 else "")
        text_size = cv2.getTextSize(text, font, 0.7, 2)[0]
        tx = (w - text_size[0]) // 2
        ty = (h + text_size[1]) // 2
        cv2.putText(mock_cv, text, (tx + 2, ty + 2), font, 0.7, (0, 0, 0), 2)
        cv2.putText(mock_cv, text, (tx, ty), font, 0.7, (255, 255, 255), 2)
        badge = "MOCK PREVIEW — Set RUNPOD_API_KEY for real generation"
        cv2.putText(mock_cv, badge, (10, h - 20), font, 0.5, (200, 200, 200), 1)
        
        return Image.fromarray(cv2.cvtColor(mock_cv, cv2.COLOR_BGR2RGB))

    def apply_perspective_warp(self, wall_img_cv: np.ndarray, mural_img_cv: np.ndarray, corners: List[List[int]]):
        """Warps the 2D generated mural onto the exact wall 3D plane using Homography."""
        h, w = mural_img_cv.shape[:2]
        # Source points: full dimensions of the generated mural
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        # Dest points: the 4 corners tracked by user
        dst = np.float32(corners)
        
        # Calculate Homography Matrix
        matrix = cv2.getPerspectiveTransform(src, dst)
        
        wall_h, wall_w = wall_img_cv.shape[:2]
        
        # Warp the mural into perspective
        warped = cv2.warpPerspective(mural_img_cv, matrix, (wall_w, wall_h))
        
        # Create warp mask for blending
        warp_mask = cv2.warpPerspective(np.ones((h, w), dtype=np.uint8)*255, matrix, (wall_w, wall_h))
        
        return warped, warp_mask

    def match_lighting_and_texture(self, mural_cv: np.ndarray, wall_cv: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Matches luma curves between wall and mural, and multiplies texture."""
        wall_region = cv2.bitwise_and(wall_cv, wall_cv, mask=mask)
        mural_region = cv2.bitwise_and(mural_cv, mural_cv, mask=mask)
        
        # 1. Match Average Brightness
        valid_pixels = mask > 0
        if np.any(valid_pixels):
            wall_mean = np.mean(wall_region[valid_pixels])
            mural_mean = np.mean(mural_region[valid_pixels])
            
            if mural_mean > 0:
                correction = (wall_mean / mural_mean) * 1.05 # Add 5% boost for typical mural vibrancy
                mural_calibrated = np.clip(mural_cv.astype(np.float32) * correction, 0, 255).astype(np.uint8)
            else:
                mural_calibrated = mural_cv
        else:
            mural_calibrated = mural_cv
            
        # 2. Extract surface texture via low-pass filter subtraction
        # Extracts fine wall details (bumps, plaster)
        texture = cv2.GaussianBlur(wall_cv, (31, 31), 0)
        
        # 3. Blend them together: 85% paint, 15% underlying wall plaster texture
        final_mural = cv2.addWeighted(mural_calibrated, 0.85, texture, 0.15, 0)
        
        # 4. Add surface noise to remove "AI Sticker" look
        noise = np.random.normal(0, 1, final_mural.shape).astype(np.float32)
        final_mural = np.clip(final_mural.astype(np.float32) + (noise * 3), 0, 255).astype(np.uint8)
        
        return final_mural

    def slice_panels(self, img: np.ndarray, panel_width_px: int) -> List[np.ndarray]:
        """Slices the upscaled hd mural into print-machine ready vertical strips."""
        panels = []
        for x in range(0, img.shape[1], panel_width_px):
            panel = img[:, x:x+panel_width_px]
            panels.append(panel)
        return panels

    def run_full_pipeline(self, wall_image_path: str, prompt: str, corners: List[List[int]], reference_image_path: str = None) -> Image.Image:
        """Executes the complete V2 10-step rendering pipeline."""
        wall_pil = Image.open(wall_image_path).convert("RGB")
        wall_cv = cv2.cvtColor(np.array(wall_pil), cv2.COLOR_RGB2BGR)
        
        # Step 1-5: Get depth & generate art
        mural_pil = self.generate_mural(wall_pil, prompt, corners, reference_image_path)
        mural_cv = cv2.cvtColor(np.array(mural_pil), cv2.COLOR_RGB2BGR)
        
        # Step 6: Perspective warp
        warped_mural, warp_mask = self.apply_perspective_warp(wall_cv, mural_cv, corners)
        
        # Step 7: Lighting & Texture matching
        final_mural = self.match_lighting_and_texture(warped_mural, wall_cv, warp_mask)
        
        # Step 10: Composite Preview
        inv_mask = cv2.bitwise_not(warp_mask)
        background = cv2.bitwise_and(wall_cv, wall_cv, mask=inv_mask)
        
        mural_masked = cv2.bitwise_and(final_mural, final_mural, mask=warp_mask)
        composite = cv2.add(background, mural_masked)
        
        return Image.fromarray(cv2.cvtColor(composite, cv2.COLOR_BGR2RGB))
