# Shared camera state — updated by main.py, read by tools.py
last_frame = None   # numpy BGR frame (kept for fallback)
camera = None       # live cv2.VideoCapture object; tools.py grabs fresh frames from this
