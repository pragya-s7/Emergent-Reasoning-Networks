import requests
import os
import dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
dotenv.load_dotenv()

def extract_text_from_file(filename: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract text from a document file using Upstage OCR API.
    
    Args:
        filename: Path to the document file
        api_key: Upstage API key (optional, will use environment variable if not provided)
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    
    # Use provided API key or get from environment
    api_key = api_key or os.environ.get("UPSTAGE_API_KEY")
    
    if not api_key:
        raise ValueError("Upstage API key not provided and not found in environment variables")
        
    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with open(filename, "rb") as f:
        files = {"document": f}
        data = {"model": "ocr"}
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()  # Raise exception for HTTP errors
            result = response.json()
            
            # Extract useful information
            return {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "pages": result.get("pages", []),
                "metadata": result.get("metadata", {}),
                "model_version": result.get("modelVersion", "")
            }
        except requests.RequestException as e:
            raise Exception(f"Error calling Upstage API: {str(e)}")
