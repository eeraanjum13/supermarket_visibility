import os
import json
import re
import base64
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

# ─── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert in computer vision and retail analytics.
Given a shelf image, identify each unique product and estimate what
percentage of its front face is visible. Return *only* a JSON array, e.g.:

[
  {"product":"KitKat","visibility":60},
  {"product":"Oreo","visibility":85}
]
"""
# ────────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Shelf Visibility Analyzer", layout="centered")
st.title("🛒 Shelf Visibility Analyzer")

uploaded = st.file_uploader("Upload a shelf image", type=["jpg", "jpeg", "png"])
if not uploaded:
    st.info("Please upload an image to analyze.")
    st.stop()

st.image(uploaded, caption="Your shelf image", use_column_width=True)

if st.button("Analyze"):
    with st.spinner("Analyzing…"):
        data = uploaded.read()
        b64 = base64.b64encode(data).decode()
        data_uri = f"data:{uploaded.type};base64,{b64}"

        try:
            resp = client.responses.create(
                model="gpt-4o-mini",  # omni model with vision
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text",  "text": SYSTEM_PROMPT},
                        {"type": "input_image", "image_url":    data_uri}
                    ],
                }]
            )
        except Exception as e:
            st.error(f"❌ OpenAI API error:\n{e}")
            st.stop()

    # ─── 1) Get the raw output ─────────────────────────────────────────────────
    raw = getattr(resp, "output_text", None) or resp.output or ""
    
    # ─── 2) Strip Markdown code fences if present ──────────────────────────────
    #    e.g. ```json\n[ ... ]\n``` → [ ... ]
    raw = raw.strip()
    # remove leading ```json or ``` 
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    # remove trailing ```
    raw = re.sub(r"\s*```$", "", raw)

    # ─── 3) Parse only if it’s still a string ─────────────────────────────────
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            st.error("Failed to parse JSON from model:")
            st.code(raw)
            st.stop()
    else:
        parsed = raw

    # ─── 4) Unwrap {"products": [...]} if present ─────────────────────────────
    if isinstance(parsed, dict) and "products" in parsed:
        items = parsed["products"]
    else:
        items = parsed

    # ─── 5) Display ────────────────────────────────────────────────────────────
    if not isinstance(items, list) or not items:
        st.warning("No products detected.")
    else:
        st.subheader("Visibility Results")
        st.table(items)
