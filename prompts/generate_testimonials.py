import os, sys, json, time, requests

API_KEY = "6f51ce0a4b55f75991bf824a73ccf22f"
TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"
POLL_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

BOTTLE_URL = "https://tempfile.redpandaai.co/kieai/1063754/images/Aarogya%20Night%20gold%20plus%20576.png"

people = [
    {
        "file": "testimonial_1.jpg",
        "prompt": """Ultra-realistic waist-up portrait of a 35-year-old Indian man in a simple cheap white vest (banyan), unshaven, rough skin with visible pores and blemishes, tired eyes but genuine happy smile. He stands in a modest home with a blurred concrete wall and an old curtain behind him. Harsh overhead fluorescent tube light creating strong shadows, unflattering realistic lighting. No studio lighting, no professional photography. He holds a white plastic bottle with a white ribbed cap in his right hand at chest level, the bottle label faces the camera showing 'AAROGYA CHAMP' branding, yellow and black label with horse illustration, 'Aarogya India' text. His fingers wrap around the bottle naturally without covering the label. The bottle must look exactly like the reference image with no changes to its design, colors, typography, or packaging. Realistic Indian lower middle class home setting. Candid documentary style photograph. Visible sensor grain, compressed image quality, slightly soft focus. Do not beautify, do not edit skin, do not add makeup, do not alter the bottle packaging in any way.""",
        "negative": "no plastic skin, no airbrushed texture, no CGI, no cartoon, no illustration, no 3D render, no digital art, no stylized realism, no skin smoothing, no beautification filters, no makeup, no studio lighting, no fashion lighting, no professional photography look, no blurred bottle, no bottle redesign, no brand modification, no logo change, no typography change, no color shift, no retouching, no watermark"
    },
    {
        "file": "testimonial_2.jpg",
        "prompt": """Ultra-realistic chest-up portrait of a 28-year-old Indian man in a cheap faded blue shirt, messy hair, stubble, visible acne scars and uneven skin tone, genuine happy smile. He stands in a small room with a painted concrete wall behind him, a steel almirah visible in background. Mixed natural daylight and warm incandescent bulb lighting creating realistic shadows on his face. He proudly holds a white plastic bottle with a white ribbed cap in his left hand near his shoulder, the bottle label faces directly toward the camera showing 'AAROGYA CHAMP' branding, yellow and black label with horse illustration, 'Aarogya India' text. His thumb rests on the side of the bottle, fingers wrapping around without covering the brand name or important label details. The bottle must be an exact match to the reference image with no changes to its branding, design, colors, typography, or packaging. Indian lower middle class home environment. Documentary candid photography style. Unretouched skin, visible imperfections. Do not beautify, do not smooth skin, do not alter facial features, do not modify the bottle packaging in any way.""",
        "negative": "no plastic skin, no airbrushed texture, no CGI, no cartoon, no illustration, no 3D render, no digital art, no stylized realism, no skin smoothing, no beautification filters, no makeup, no studio lighting, no fashion lighting, no professional photography look, no blurred bottle, no bottle redesign, no brand modification, no logo change, no typography change, no color shift, no retouching, no watermark"
    },
    {
        "file": "testimonial_3.jpg",
        "prompt": """Ultra-realistic waist-up portrait of a 48-year-old Indian man with a salt-and-pepper beard, wrinkled skin, visible dark circles under eyes, wearing a simple cheap checkered shirt, genuine warm smile showing teeth. He stands next to a wooden door frame in a modest home with peeling paint on the wall behind him. Soft window light from one side creating natural modeling on his face, uneven realistic home lighting. He holds a white plastic bottle with a white ribbed cap in both hands at chest level, presenting it toward the camera. The bottle label faces directly forward showing 'AAROGYA CHAMP' branding, yellow and black label with horse illustration, 'Aarogya India' text completely visible and readable. His fingers wrap around the bottle naturally without covering the brand name or important label text. The bottle packaging must be an exact unchanged match to the reference image. Indian lower middle class home background. Documentary candid photography. Unretouched skin with wrinkles, pores, and age spots. Do not beautify, do not smooth skin, do not remove wrinkles, do not alter facial features, do not modify the bottle packaging in any way.""",
        "negative": "no plastic skin, no airbrushed texture, no CGI, no cartoon, no illustration, no 3D render, no digital art, no stylized realism, no skin smoothing, no beautification filters, no makeup, no studio lighting, no fashion lighting, no professional photography look, no blurred bottle, no bottle redesign, no brand modification, no logo change, no typography change, no color shift, no retouching, no watermark, no age reduction"
    }
]

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
project = "/Users/rajeshcsharma/Desktop/Claude projects/BRamdev LP"

# Create all tasks first
tasks = []
for p in people:
    print(f"Creating task for {p['file']}...")
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": p["prompt"],
            "negative_prompt": p["negative"],
            "image_input": [BOTTLE_URL],
            "aspect_ratio": "3:4",
            "resolution": "4K",
            "output_format": "jpg"
        }
    }
    resp = requests.post(TASK_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    tid = resp.json().get("data", {}).get("taskId")
    tasks.append({"id": tid, "file": p["file"]})
    print(f"  Task ID: {tid}")

print(f"\nAll {len(tasks)} tasks created. Polling...\n")

pending = list(tasks)
completed = []
attempt = 0

while pending and attempt < 120:
    time.sleep(6)
    attempt += 1
    still_pending = []
    for t in pending:
        resp = requests.get(POLL_URL, headers=headers, params={"taskId": t["id"]}, timeout=15)
        data = resp.json().get("data", {})
        state = data.get("state")
        print(f"  [{attempt}] {t['file']}: {state}")
        if state in ("success", "completed"):
            result_json = json.loads(data.get("resultJson", "{}"))
            urls = result_json.get("resultUrls", [])
            if urls:
                out = os.path.join(project, t["file"])
                img = requests.get(urls[0], timeout=60)
                with open(out, "wb") as f:
                    f.write(img.content)
                print(f"  -> Saved {out} ({len(img.content)} bytes)")
                completed.append(t)
            else:
                print(f"  -> No URLs in result")
                still_pending.append(t)
        elif state in ("failed", "error"):
            print(f"  -> FAILED")
            still_pending.append(t)
        else:
            still_pending.append(t)
    pending = still_pending

print(f"\nDone. {len(completed)}/{len(tasks)} images generated.")
for t in completed:
    print(f"  {t['file']}")
