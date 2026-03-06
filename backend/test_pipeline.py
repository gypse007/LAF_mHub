import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api/wall"
TEST_IMG = "/Users/praharshinikhil/.gemini/antigravity/brain/635db3aa-522a-4979-896d-ec3753054f19/wall_mural_run_test_1772821467803.webp"

def run_test():
    print(f"Uploading image: {TEST_IMG}")
    with open(TEST_IMG, "rb") as f:
        upload_res = requests.post(
            f"{BASE_URL}/upload", 
            files={"file": ("test.webp", f, "image/webp")}
        )
    
    upload_res.raise_for_status()
    wall_id = upload_res.json()["wall_id"]
    print(f"Uploaded successfully. Wall ID: {wall_id}")
    
    print("\nDetecting walls (SAM)...")
    detect_res = requests.post(f"{BASE_URL}/{wall_id}/detect-walls")
    detect_res.raise_for_status()
    polygons = detect_res.json()["detected_walls"]
    print(f"Detected {len(polygons)} wall polygons.")
    
    if not polygons:
        print("No walls detected!")
        sys.exit(1)
        
    print(f"\nQueueing SDXL Generation...")
    # Choose the first polygon
    print_area = polygons[0]
    gen_res = requests.post(f"{BASE_URL}/generate", json={
        "wall_id": wall_id,
        "style": "modern_minimalist",
        "print_area": print_area,
        "wall_size": {"width": 10, "height": 8}
    })
    gen_res.raise_for_status()
    task_id = gen_res.json()["task_id"]
    print(f"Task queued. Task ID: {task_id}")
    
    print("\nPolling status...")
    while True:
        status_res = requests.get(f"{BASE_URL}/status/{task_id}")
        status_res.raise_for_status()
        data = status_res.json()
        status = data["status"]
        print(f"Status: {status}")
        
        if status == "completed":
            print("\nGeneration COMPLETE!")
            print(f"Result URL: {data['result']['image_url']}")
            print(f"Print Resolution: {data['result'].get('print_resolution')}")
            print(f"Print Panels generated: {len(data['result'].get('panels', []))}")
            break
        elif status == "failed":
            print(f"\nGeneration FAILED: {data.get('error')}")
            sys.exit(1)
            
        time.sleep(3)

if __name__ == "__main__":
    run_test()
