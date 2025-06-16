import os
import json
import re
import base64
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI

# ─── Configuration ─────────────────────────────────────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert in computer vision and retail analytics.
I’m uploading multiple images of the **same** shelf.
Identify each unique product across all images and estimate 
the **maximum** percentage of its front face that is visible 
in any image. Return *only* a JSON array, e.g.:

[
  {"product":"KitKat","visibility":80},
  {"product":"Oreo","visibility":90}
]
"""
# ────────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Shelf Visibility Batch Analyzer")


@app.post("/analyze", summary="Upload multiple images of the same shelf")
async def analyze_shelf(
    images: List[UploadFile] = File(
        ..., 
        description="One or more images (jpg/png) of the same shelf"
    )
):
    if not images:
        raise HTTPException(400, "No images uploaded.")

    # 1) Build one content list: prompt + all images
    content = [{"type": "input_text", "text": SYSTEM_PROMPT}]
    for img in images:
        data = await img.read()
        if not data:
            continue
        b64 = base64.b64encode(data).decode()
        uri = f"data:{img.content_type};base64,{b64}"
        content.append({"type": "input_image", "image_url": uri})

    if len(content) == 1:
        raise HTTPException(400, "All uploaded files were empty.")

    # 2) Single API call
    try:
        resp = client.responses.create(
            model="gpt-4o-mini", 
            input=[{"role": "user", "content": content}]
        )
    except Exception as e:
        raise HTTPException(502, f"OpenAI API error: {e}")

    # 3) Extract raw output
    raw = getattr(resp, "output_text", None) or resp.output or ""
    raw = raw.strip()
    # strip possible ```json fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    # 4) Parse JSON
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        raise HTTPException(502, f"Invalid JSON from model:\n{raw}")

    # 5) Unwrap if wrapped in {"products": [...]}
    if isinstance(parsed, dict) and "products" in parsed:
        items = parsed["products"]
    else:
        items = parsed

    if not isinstance(items, list):
        raise HTTPException(502, f"Unexpected format from model:\n{parsed}")

    # 6) Return as JSON array
    return JSONResponse(content=items)
