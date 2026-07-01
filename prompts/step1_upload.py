import os, sys, json, time, base64, requests

API_KEY = "6f51ce0a4b55f75991bf824a73ccf22f"
UPLOAD_URL = "https://kieai.redpandaai.co/api/file-base64-upload"
TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"

def upload(file_path):
    print(f"Uploading {os.path.basename(file_path)}...")
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    payload = {"base64Data": f"data:image/png;base64,{b64}", "uploadPath": "images", "fileName": os.path.basename(file_path)}
    resp = requests.post(UPLOAD_URL, headers={"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}, json=payload, timeout=60)
    resp.raise_for_status()
    url = resp.json().get("data",{}).get("downloadUrl")
    print(f"  -> {url}")
    return url

def create_task(prompt, image_urls):
    print("Creating task...")
    payload = {"model":"nano-banana-2","input":{"prompt":prompt,"image_input":image_urls,"aspect_ratio":"3:4","resolution":"4K","output_format":"jpg"}}
    resp = requests.post(TASK_URL, headers={"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}, json=payload, timeout=30)
    resp.raise_for_status()
    tid = resp.json().get("data",{}).get("taskId")
    print(f"  Task ID: {tid}")
    return tid

project = "/Users/rajeshcsharma/Desktop/Claude projects/BRamdev LP"
baba_url = upload(os.path.join(project, "Baba holding Image.png"))
bottle_url = upload(os.path.join(project, "Aarogya Night gold plus 576.png"))

print("\n--- URLs ---")
print(f"BABA:   {baba_url}")
print(f"BOTTLE: {bottle_url}")
print("------------\n")

# Save URLs for later use
with open(os.path.join(project, "prompts", "uploaded_urls.json"), "w") as f:
    json.dump({"baba": baba_url, "bottle": bottle_url}, f)
print("URLs saved to prompts/uploaded_urls.json")
