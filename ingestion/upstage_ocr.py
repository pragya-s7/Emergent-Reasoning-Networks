import requests

def extract_text_from_file(filename: str, api_key: str) -> str:
    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"document": open(filename, "rb")}
    data = {"model": "ocr"}

    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json().get("text", "")
