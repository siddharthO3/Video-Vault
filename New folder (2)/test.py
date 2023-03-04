from moviepy.editor import *
from PIL import Image
import os
from pathlib import Path

def generate_all_thumbnails(folder):
    vidPaths = sum([[str(Path(f"{folder}/{f}")) for f in os.listdir(folder) if f.endswith(ext)] for ext in ['mp4', 'mkv', 'mov']], [])
    thumbPaths = sum([[f"{str(Path(os.getcwd()+'/thumbs/'+f))}"[:-4]+".jpg" for f in os.listdir(folder) if f.endswith(ext)] for ext in ['mp4', 'mkv', 'mov']],[])
    d = {}

    if not os.path.exists(Path(os.getcwd()+'/thumbs')):
        os.mkdir(Path(os.getcwd()+'/thumbs'))

    for i in range(len(thumbPaths)):
        if not os.path.exists(thumbPaths[i]):
            clips = VideoFileClip(vidPaths[i])
            duration = clips.duration # seconds
            max_duration = int(duration)+1
            t = max_duration//2  # Get the thumbnail in middle of the video

            frame = clips.get_frame(t)

            new_img = Image.fromarray(frame)
            new_img.save(thumbPaths[i])
            clips.close()
        d[vidPaths[i]] = thumbPaths[i]
    return d