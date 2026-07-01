import os
import sys
import json
import time
import base64
import requests

API_KEY = "6f51ce0a4b55f75991bf824a73ccf22f"
UPLOAD_URL = "https://kieai.redpandaai.co/api/file-base64-upload"
TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"
POLL_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

def upload_image(file_path):
    print(f"Uploading {file_path}...")
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "base64Data": f"data:image/png;base64,{data}",
        "uploadPath": "images",
        "fileName": os.path.basename(file_path)
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    resp = requests.post(UPLOAD_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    print(f"Upload result: {json.dumps(result, indent=2)}")
    # The URL should be in the response
    data = result.get("data", {})
    url = data.get("downloadUrl") or data.get("url") or data.get("fileUrl") or result.get("url") or result.get("fileUrl")
    if not url:
        url = data
        if isinstance(url, dict):
            url = url.get("downloadUrl") or url.get("url") or url.get("fileUrl") or url.get("file_url")
    return url

def create_task(prompt, image_urls, aspect_ratio="3:4"):
    print("Creating generation task...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": image_urls,
            "aspect_ratio": aspect_ratio,
            "resolution": "4K",
            "output_format": "jpg"
        }
    }
    print(f"Payload keys: {list(payload.keys())}")
    print(f"image_input URLs: {image_urls}")
    resp = requests.post(TASK_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    task_id = result.get("data", {}).get("taskId")
    print(f"Task created. ID: {task_id}")
    return task_id

def poll_task(task_id):
    print("Polling for completion...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    params = {"taskId": task_id}
    for i in range(120):
        time.sleep(5)
        resp = requests.get(POLL_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        state = data.get("state")
        print(f"Poll {i+1}: state = {state}")
        if state in ("success", "completed"):
            result_json = json.loads(data.get("resultJson", "{}"))
            urls = result_json.get("resultUrls", [])
            if urls:
                return urls[0]
            # Try alternative location
            urls = result_json.get("urls", [])
            if urls:
                return urls[0]
            print(f"No URLs found in resultJson. Dumping: {json.dumps(result_json, indent=2)}")
            return None
        elif state in ("failed", "error"):
            print(f"Task failed: {json.dumps(data, indent=2)}")
            return None
    print("Timeout waiting for task")
    return None

def download_image(url, output_path):
    print(f"Downloading from {url}...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"Saved to {output_path}")

def main():
    project_dir = "/Users/rajeshcsharma/Desktop/Claude projects/BRamdev LP"
    baba_path = os.path.join(project_dir, "Baba holding Image.png")
    bottle_path = os.path.join(project_dir, "Aarogya Night gold plus 576.png")
    output_path = os.path.join(project_dir, "baba_arogya_champ_final.jpg")
    
    # Step 1: Upload images
    baba_url = upload_image(baba_path)
    print(f"Baba image URL: {baba_url}")
    if not baba_url:
        print("Failed to get URL for baba image")
        sys.exit(1)
    
    bottle_url = upload_image(bottle_path)
    print(f"Bottle image URL: {bottle_url}")
    if not bottle_url:
        print("Failed to get URL for bottle image")
        sys.exit(1)
    
    # Step 2: Create task
    prompt = """Professional commercial product endorsement portrait photograph of a male Indian spiritual leader (Baba Ramdev) in a medium waist-up shot. He wears a vibrant orange-colored traditional robe (saffron kurta) with distinct draping and folds across his chest and shoulders. He has a calm, confident smile with direct eye contact toward the camera. His facial features include a natural brown skin tone, a thick black beard covering his jaw and chin, a full black mustache, and thick black hair tied back away from his face. He stands in a confident relaxed pose, shoulders squared slightly toward camera. In his left hand at chest level, he naturally and realistically holds a white plastic bottle with a white ribbed cap, with his fingers wrapping realistically around the bottle without covering the brand name or important label details. The bottle label features 'AAROGYA CHAMP' bold black typography on a yellow band with black borders, a horse illustration graphic, 'Aarogya India' branding text, and detailed printed packaging text in black and yellow design. The bottle label faces directly toward the camera, fully visible and readable. The bottle is positioned on the left side of the frame near his face level. Behind him is a clean light gray seamless studio background with a subtle soft gradient from lighter gray at center-left to slightly darker gray at edges. No other props, furniture, or objects visible. Professional commercial studio lighting setup: large softbox key light from above and slightly camera-right creating soft natural shadows on his face and robe, a soft fill light from camera-left reducing shadow contrast, and a gentle rim light from behind creating subtle edge separation. The lighting produces natural skin tones with realistic subsurface scattering, soft realistic shadows under his chin and around his nose, and a premium wellness advertising aesthetic. Shot with an 85mm portrait lens at f/5.6, ISO 100, producing extremely sharp facial details, photorealistic skin texture with visible pores and natural skin variation, high dynamic range preserving detail in both the bright orange robe and the white bottle, and crisp readable product label typography. 8K resolution commercial photography quality. The final image must look like a genuine authentic commercial endorsement photograph where the baba is naturally holding the exact Aarogya Champ bottle with no changes to the bottle's branding, design, colors, label, or proportions whatsoever. Do not alter or redesign any aspect of the bottle packaging."""
    
    negative_prompt = "no plastic skin, no airbrushed texture, no CGI, no cartoon, no illustration, no 3D render, no digital art, no stylized realism, no anime, no painting, no sketch, no deformed hands, no extra fingers, no missing fingers, no malformed hands, no mutated hands, no anatomy normalization, no body proportion averaging, no skin smoothing, no beautification filters, no makeup styling, no facial hair alteration, no outfit redesign, no bottle redesign, no brand modification, no logo modification, no packaging simplification, no label recreation, no typography change, no color shift, no plastic sheen, no glossy highlights on skin, no fashion editorial lighting, no retouching, no wide-angle distortion, no lens distortion, no double vision, no blurred face, no blurred bottle, no background objects, no text overlays, no watermark, no added graphics"
    
    # Use the Dense Narrative format passed as a flat JSON structure (old format)
    prompt_data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "image_input": [baba_url, bottle_url],
        "api_parameters": {
            "aspect_ratio": "3:4",
            "resolution": "4K",
            "output_format": "jpg"
        }
    }
    
    task_id = create_task(prompt, [baba_url, bottle_url], "3:4")
    if not task_id:
        print("Failed to create task")
        sys.exit(1)
    
    # Step 3: Poll and download
    result_url = poll_task(task_id)
    if result_url:
        download_image(result_url, output_path)
    else:
        print("Failed to get result")
        sys.exit(1)

if __name__ == "__main__":
    main()
