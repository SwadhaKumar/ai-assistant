import os
import gradio as gr
from speech_to_text import record_audio, transcribe_with_groq
from ai_agent import ask_agent
from text_to_speech import text_to_speech_with_elevenlabs
from dotenv import load_dotenv

load_dotenv()

required_keys = ["GROQ_API_KEY", "ELEVENLABS_API_KEY"]
missing_keys = [key for key in required_keys if not os.environ.get(key)]
if missing_keys:
    raise EnvironmentError(f"Missing required API keys: {', '.join(missing_keys)}. Please set them in your .env file.")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
audio_filepath = "audio_question.mp3"

def process_single_interaction(chat_history):
    """Process one audio interaction and return updated chat history"""
    if chat_history is None:
        chat_history = []
    
    try:
        record_audio(file_path=audio_filepath, timeout=5)
        user_input = transcribe_with_groq(audio_filepath)
        
        if not user_input or user_input.strip() == "":
            return chat_history, "No speech detected. Please try again."
        
        response = ask_agent(user_query=user_input)
        text_to_speech_with_elevenlabs(input_text=response, output_filepath="final.mp3")
        
        # Append in correct Gradio format
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        return chat_history, f"✅ Response generated and spoken"
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return chat_history, error_msg
# Code for frontend
import cv2
import camera_state
# Global variables
camera = None
is_running = False
last_frame = None

def initialize_camera():
    """Initialize the camera with optimized settings"""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            # Optimize camera settings for better performance
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize lag
        camera_state.camera = camera  # share object so tools.py can grab fresh frames
    return camera is not None and camera.isOpened()

def start_webcam():
    """Start the webcam feed"""
    global is_running, last_frame
    is_running = True
    if not initialize_camera():
        return None
    
    ret, frame = camera.read()
    if ret and frame is not None:
        camera_state.last_frame = frame  # store BGR for tools.py
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_frame = frame
        return frame
    return last_frame

def stop_webcam():
    """Stop the webcam feed"""
    global is_running, camera
    is_running = False
    if camera is not None:
        camera.release()
        camera = None
    camera_state.camera = None
    return None

def get_webcam_frame():
    """Get current webcam frame with optimized performance"""
    global camera, is_running, last_frame
    
    if not is_running or camera is None:
        return last_frame
    
    # Skip frames if buffer is full to avoid lag
    if camera.get(cv2.CAP_PROP_BUFFERSIZE) > 1:
        for _ in range(int(camera.get(cv2.CAP_PROP_BUFFERSIZE)) - 1):
            camera.read()
    
    ret, frame = camera.read()
    if ret and frame is not None:
        camera_state.last_frame = frame  # store BGR for tools.py
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_frame = frame
        return frame
    return last_frame

# Setup UI

with gr.Blocks() as demo:
    gr.Markdown("<h1 style='color: orange; text-align: center;  font-size: 4em;'>Your Personal AI Assistant</h1>")

    with gr.Row():
        # Left column - Webcam
        with gr.Column(scale=1):
            gr.Markdown("## Webcam Feed")
            
            with gr.Row():
                start_btn = gr.Button("Start Camera", variant="primary")
                stop_btn = gr.Button("Stop Camera", variant="secondary")
            
            webcam_output = gr.Image(
                label="Live Feed",
                # streaming=True,
                show_label=False,
                width=640,
                height=480
            )
            
            # Faster refresh rate for smoother video
            webcam_timer = gr.Timer(0.1)  # ~30 FPS (1/30 ≈ 0.033 seconds)
        
        # Right column - Chat
        with gr.Column(scale=1):
            gr.Markdown("## Chat Interface")
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400,
                show_label=False
            )
            
            status_text = gr.Textbox(
                label="Status",
                interactive=False,
                value="Ready to listen"
            )
            
            with gr.Row():
                record_btn = gr.Button("🎤 Record & Ask", variant="primary", size="lg")
                clear_btn = gr.Button("Clear Chat", variant="secondary")
    
    # Event handlers
    start_btn.click(
        fn=start_webcam,
        outputs=webcam_output
    )
    
    stop_btn.click(
        fn=stop_webcam,
        outputs=webcam_output
    )
    
    webcam_timer.tick(
        fn=get_webcam_frame,
        outputs=webcam_output,
        show_progress=False  
    )
    
    record_btn.click(
        fn=process_single_interaction,
        inputs=chatbot,
        outputs=[chatbot, status_text]
    )
    
    clear_btn.click(
        fn=lambda: ([], "Ready to listen"),
        outputs=[chatbot, status_text]
    )

## Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )
