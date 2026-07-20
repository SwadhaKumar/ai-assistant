import cv2
import base64
import sys
from groq import Groq
from dotenv import load_dotenv
from langchain_core.tools import tool
import camera_state

load_dotenv()


def _open_camera(index: int = 0):
    if sys.platform == "darwin":
        cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
        if cap is not None and cap.isOpened():
            return cap
        if cap is not None:
            cap.release()
    return cv2.VideoCapture(index)


def _read_frame_with_retries(cap, attempts: int = 5):
    for _ in range(attempts):
        ret, frame = cap.read()
        if ret and frame is not None and getattr(frame, "size", 0) > 0:
            return frame
    return None

def capture_image() -> str:
    """
    Grabs a fresh frame from the shared camera object (kept open by main.py).
    Falls back to opening the camera directly if the UI camera hasn't started.
    """
    cap = camera_state.camera
    if cap is not None and cap.isOpened():
        frame = _read_frame_with_retries(cap, attempts=5)
        if frame is not None:
            ret, buf = cv2.imencode('.jpg', frame)
            if ret:
                return base64.b64encode(buf).decode('utf-8')

    # Fallback: UI camera not started, open temporarily
    tmp = _open_camera(0)
    if tmp.isOpened():
        frame = _read_frame_with_retries(tmp, attempts=8)
        tmp.release()
        if frame is not None:
            ret, buf = cv2.imencode('.jpg', frame)
            if ret:
                return base64.b64encode(buf).decode('utf-8')

    raise RuntimeError("No camera frame available. Start the camera feed first.")

@tool
def analyze_image_with_query(query: str) -> str:
    """
    Expects a string with 'query'.
    Captures the image and sends the query and the image to
    to Groq's vision chat API and returns the analysis.
    """
    img_b64 = capture_image()
    model = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    if not query or not img_b64:
        return "Error: both 'query' and 'image' fields required."

    client = Groq()  
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}",
                    },
                },
            ],
        }]
    
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            tool_choice="none",
            temperature=0.7,
            max_tokens=1024
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"