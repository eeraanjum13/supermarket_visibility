# Shelf Visibility Analyzer

A proof-of-concept tool for analyzing product visibility on supermarket shelves using OpenAI's vision-enabled models. This repository offers two interfaces:

1. **Single Image Upload** via FastAPI
2. **Multiple Image Upload** via Streamlit

---

## Table of Contents

* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)

  * [1. FastAPI Single Image Upload](#1-fastapi-single-image-upload)
  * [2. Streamlit Multiple Image Upload](#2-streamlit-multiple-image-upload)
* [Environment](#environment)
* [License](#license)

---

## Features

* **FastAPI endpoint** for uploading a single shelf image and receiving a JSON array of products with visibility percentages.
* **Streamlit app** for batch uploading multiple images of the same shelf and obtaining an aggregated visibility report.
* Uses OpenAI's `gpt-4o` vision model for analyzing images.

---

## Prerequisites

* Python 3.13+
* An OpenAI API key with vision model access
* Git for cloning this repository

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/shelf-visibility-analyzer.git
   cd shelf-visibility-analyzer
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .\.venv\\Scripts\\activate # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Add your OpenAI API key**

   Create a `.env` file in the project root:

   ```bash
   echo "OPENAI_API_KEY=sk-...your-key..." > .env
   ```

---

## Usage

### 1. FastAPI Single Image Upload

This endpoint accepts a single image and returns a JSON array of `{product, visibility}` objects.

1. **Start the FastAPI server**

   ```bash
   uvicorn app_fastapi:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Upload an image**

   * **cURL** example:

     ```bash
     curl -X POST "http://localhost:8000/analyze" \
       -F "images=@/path/to/shelf.jpg"
     ```

3. **Response**

   ```json
   [
     {"product":"KitKat","visibility":60},
     {"product":"Oreo","visibility":85},
     ...
   ]
   ```

---

### 2. Streamlit Multiple Image Upload

This app accepts multiple images of the same shelf in one batch and provides an aggregated visibility report.

1. **Run the Streamlit app**

   ```bash
   streamlit run app_streamlit.py
   ```

2. **Use the web UI**

   * Open your browser at `http://localhost:8501`
   * Upload two or more images of the same shelf
   * Click **Analyze all at once**

3. **Results**

   * Per-image visibility tables
   * Final aggregated visibility table

---

## Environment

Store any environment-specific settings in the `.env` file. Make sure to keep your API key secure and never commit it to source control.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
