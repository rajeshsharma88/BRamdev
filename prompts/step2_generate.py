import os, sys, json, time, requests

API_KEY = "6f51ce0a4b55f75991bf824a73ccf22f"
TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"
POLL_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

prompt = """Professional commercial product endorsement portrait photograph of a male Indian spiritual leader in a medium waist-up shot. He wears a vibrant orange-colored traditional robe (saffron kurta) with distinct draping and folds across his chest and shoulders. He has a calm, confident smile with direct eye contact toward the camera. His facial features include a natural brown skin tone, a thick black beard covering his jaw and chin, a full black mustache, and thick black hair tied back away from his face. He stands in a confident relaxed pose, shoulders squared slightly toward camera. In his left hand at chest level, he naturally and realistically holds a white plastic bottle with a white ribbed cap, with his fingers wrapping realistically around the bottle without covering the brand name or important label details. The bottle label features 'AAROGYA CHAMP' bold black typography on a yellow band with black borders, a horse illustration graphic, 'Aarogya India' branding text, and detailed printed packaging text in black and yellow design. The bottle label faces directly toward the camera, fully visible and readable. The bottle is positioned on the left side of the frame near his face level. Behind him is a clean light gray seamless studio background with a subtle soft gradient from lighter gray at center-left to slightly darker gray at edges. No other props, furniture, or objects visible. Professional commercial studio lighting setup: large softbox key light from above and slightly camera-right creating soft natural shadows on his face and robe, a soft fill light from camera-left reducing shadow contrast, and a gentle rim light from behind creating subtle edge separation. The lighting produces natural skin tones with realistic subsurface scattering, soft realistic shadows under his chin and around his nose, and a premium wellness advertising aesthetic. Shot with an 85mm portrait lens at f/5.6, ISO 100, producing extremely sharp facial details, photorealistic skin texture with visible pores and natural skin variation, high dynamic range preserving detail in both the bright orange robe and the white bottle, and crisp readable product label typography. 8K resolution commercial photography quality. The final image must look like a genuine authentic commercial endorsement photograph where the baba is naturally holding the exact Aarogya Champ bottle with no changes to the bottle's branding, design, colors, label, or proportions whatsoever. Do not alter or redesign any aspect of the bottle packaging."""

negative_prompt = "no plastic skin, no airbrushed texture, no CGI, no cartoon, no illustration, no 3D render, no digital art, no stylized realism, no anime, no painting, no sketch, no deformed hands, no extra fingers, no missing fingers, no malformed hands, no mutated hands, no anatomy normalization, no body proportion averaging, no skin smoothing, no beautification filters, no makeup styling, no facial hair alteration, no outfit redesign, no bottle redesign, no brand modification, no logo modification, no packaging simplification, no label recreation, no typography change, no color shift, no plastic sheen, no glossy highlights on skin, no fashion editorial lighting, no retouching, no wide-angle distortion, no lens distortion, no double vision, no blurred face, no blurred bottle, no background objects, no text overlays, no watermark, no added graphics"

project = "/Users/rajeshcsharma/Desktop/Claude projects/BRamdev LP"
with open(os.path.join(project, "prompts", "uploaded_urls.json")) as f:
    urls = json.load(f)

image_urls = [urls["baba"], urls["bottle"]]
print(f"Using {len(image_urls)} reference images")
print(f"BABA:   {image_urls[0]}")
print(f"BOTTLE: {image_urls[1]}")

print("\nCreating generation task...")
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
payload = {
    "model": "nano-banana-2",
    "input": {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "image_input": image_urls,
        "aspect_ratio": "3:4",
        "resolution": "4K",
        "output_format": "jpg"
    }
}
resp = requests.post(TASK_URL, headers=headers, json=payload, timeout=30)
resp.raise_for_status()
task_id = resp.json().get("data", {}).get("taskId")
print(f"Task ID: {task_id}")

if not task_id:
    print("ERROR: No task ID returned")
    print(resp.json())
    sys.exit(1)

print("\nPolling...")
for i in range(120):
    time.sleep(5)
    resp = requests.get(POLL_URL, headers=headers, params={"taskId": task_id}, timeout=15)
    data = resp.json().get("data", {})
    state = data.get("state")
    print(f"  [{i+1}] state = {state}")
    if state in ("success", "completed"):
        result_json = json.loads(data.get("resultJson", "{}"))
        result_urls = result_json.get("resultUrls", [])
        if result_urls:
            out_path = os.path.join(project, "baba_arogya_champ_final.jpg")
            print(f"\nDownloading from {result_urls[0]}...")
            img = requests.get(result_urls[0], timeout=60)
            with open(out_path, "wb") as f:
                f.write(img.content)
            print(f"Saved to {out_path}")
            sys.exit(0)
        else:
            print(f"No URLs in resultJson: {json.dumps(result_json, indent=2)}")
            sys.exit(1)
    elif state in ("failed", "error"):
        print(f"FAILED: {json.dumps(data, indent=2)}")
        sys.exit(1)

print("TIMEOUT")
sys.exit(1)
