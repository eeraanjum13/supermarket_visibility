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

st.title("🛒 Shelf Visibility Analyzer (Multi-Image)")

files = st.file_uploader(
    "Upload several pictures of the same shelf",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)
if not files:
    st.info("Please upload at least one image.")
    st.stop()

if st.button("Analyze all at once"):
    with st.spinner("Sending batch to OpenAI…"):
        # 1) Build content sequence: start with prompt, then each image
        content = [{"type":"input_text", "text": SYSTEM_PROMPT}]
        for img in files:
            data = img.read()
            uri  = f"data:{img.type};base64,{base64.b64encode(data).decode()}"
            content.append({"type":"input_image", "image_url": uri})

        # 2) Single API call
        try:
            resp = client.responses.create(
                model="gpt-4o",    # vision-enabled
                input=[{"role":"user","content":content}]
            )
        except Exception as e:
            st.error(f"❌ OpenAI API error:\n{e}")
            st.stop()

    # 3) Extract & clean raw JSON
    raw = getattr(resp, "output_text", None) or resp.output or ""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$",             "", raw)

    # 4) Parse
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        st.error("Failed to parse JSON from model:")
        st.code(raw)
        st.stop()

    # 5) Display
    if isinstance(parsed, list) and parsed:
        st.subheader("Aggregated Shelf Visibility")
        st.table(parsed)
    else:
        st.warning("No products detected.")
