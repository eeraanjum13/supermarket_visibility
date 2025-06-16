import os
import json
import base64
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

SYSTEM_PROMPT = """
You are an expert in computer vision and retail analytics.
Given a shelf image, identify each unique product and estimate what
percentage of its face is visible. Return a strict JSON array:
[{"product":"KitKat","visibility":60}, …] and nothing else.
"""

@app.post("/analyze")
async def analyze_shelf(image: UploadFile = File(...)):
    data = await image.read()
    if not data:
        raise HTTPException(400, "No image data received.")

    # Embed as Base64 data URI
    b64 = base64.b64encode(data).decode()
    data_uri = f"data:{image.content_type};base64,{b64}"

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",             # ← use the omni model
            messages=[
                {"role": "system",  "content": SYSTEM_PROMPT},
                {
                  "role": "user",
                  "content": [
                    {"type": "text",      "text": "Analyze this shelf image for product visibility:"},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                  ]
                }
            ],
            max_tokens=500,               # room for the JSON
            temperature=0,                # deterministic output
            response_format={"type": "json_object"}  # guarantee valid JSON
        )
    except Exception as e:
        raise HTTPException(500, f"OpenAI API error: {e}")

    # Parse the JSON directly
    result = resp.choices[0].message.content
    return JSONResponse(content=result)
