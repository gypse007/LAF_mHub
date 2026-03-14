# RunPod Serverless GPU Worker

This directory contains the code to deploy the SDXL + ControlNet Depth model as a serverless API on [RunPod](https://runpod.io).

By moving the heavy diffusion workload to a cloud GPU (like an RTX 4090 or A100), mural generation drops from **~3.5 minutes on Mac MPS down to < 10 seconds**.

## Deployment Steps

1. **Build and push the Docker image** to Docker Hub or another container registry:
   ```bash
   docker build -t your-username/laf-mural-worker:v1 .
   docker push your-username/laf-mural-worker:v1
   ```
   *(Note: The build process downloads the 15GB SDXL weights into the image so cold starts are instant!)*

2. **Create a Serverless Endpoint on RunPod:**
   - Go to [RunPod Serverless](https://www.runpod.io/console/serverless)
   - Click "New Endpoint"
   - Select a GPU (e.g., 24GB VRAM like a 4090 or A5000)
   - Set the Container Image to `your-username/laf-mural-worker:v1`
   - Set the max workers and idle timeout

3. **Get your API credentials:**
   - Note the **Endpoint ID** from the endpoint you just created.
   - Go to RunPod Settings -> API Keys and create a **RunPod API Key**.

4. **Update your local environment:**
   In the main `backend/.env` file or your terminal, export the keys:
   ```bash
   export RUNPOD_API_KEY="your_api_key_here"
   export RUNPOD_ENDPOINT_ID="your_endpoint_id_here"
   ```

Restart your FastAPI server. The `AdvancedMuralPipeline` will automatically detect these keys and route all generations to your high-speed RunPod GPU instead of your local Mac!
