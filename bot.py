import os
import random
import time
import sys
import torch
import torchaudio
import soundfile as sf
import pandas as pd

# --- PYTORCH 2.6 SECURITY MONKEY PATCH ---
# PyTorch 2.6 strictly blocks older AI models. This intercepts the core
# load function and forces it to accept the Coqui XTTSv2 weights.
_original_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load

# --- TORCHAUDIO 2.6 FFMPEG MONKEY PATCH ---
# Torchaudio 2.6 forces the use of torchcodec and FFmpeg, which crashes on Windows.
# This intercepts the audio loader and forces it to use the stable soundfile library.
_original_torchaudio_load = torchaudio.load
def _patched_torchaudio_load(filepath, *args, **kwargs):
    try:
        data, sr = sf.read(filepath, dtype='float32')
        if len(data.shape) == 1:
            tensor = torch.FloatTensor(data).unsqueeze(0)
        else:
            tensor = torch.FloatTensor(data).transpose(0, 1)
        return tensor, sr
    except Exception:
        # If soundfile fails, fallback to the original torchaudio method just in case
        return _original_torchaudio_load(filepath, *args, **kwargs)
torchaudio.load = _patched_torchaudio_load

# --- AUTO-AGREE TO XTTSv2 TERMS OF SERVICE ---
os.environ["COQUI_TOS_AGREED"] = "1"

# --- THE AGGRESSIVE ESPEAK BRIDGE ---
espeak_folder = r"C:\Program Files\eSpeak NG"
if not os.path.exists(espeak_folder):
    espeak_folder = r"C:\Program Files (x86)\eSpeak NG"

if not os.path.exists(espeak_folder):
    print("\nCRITICAL: Python cannot find eSpeak on your computer.")
    sys.exit(1)

os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = os.path.join(espeak_folder, "libespeak-ng.dll")
os.environ["PHONEMIZER_ESPEAK_PATH"] = os.path.join(espeak_folder, "espeak-ng.exe")
os.environ["PATH"] = espeak_folder + os.pathsep + os.environ.get("PATH", "")

# --- TTS & MOVIEPY IMPORTS ---
from TTS.api import TTS

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips
from moviepy.config import change_settings
from moviepy.audio.fx.all import audio_loop
import moviepy.video.fx.all as vfx

# Make sure ImageMagick is correct!
IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_random_file(folder_name, extensions):
    """Picks a random file from a given folder based on file extension."""
    folder_path = os.path.join(SCRIPT_DIR, folder_name)
    if not os.path.exists(folder_path):
        return None
    files = [f for f in os.listdir(folder_path) if f.endswith(extensions)]
    if not files:
        return None
    return os.path.join(folder_path, random.choice(files))

def generate_local_audio(tts_model, text, output_filename, reference_voice_path):
    """Uses XTTSv2 to clone your specific voice based on a 10-second reference file."""
    print("    -> Generating local AI audio (Cloning your voice!)...")
    
    tts_model.tts_to_file(
        text=text, 
        speaker_wav=reference_voice_path, 
        language="en", 
        file_path=output_filename
    )
    return []

def create_short(video_path, audio_path, music_path, output_path, subs, text_content, title_text):
    print("    -> Assembling Video, Music, and Graphics...")
    
    # 1. Load Audio and Video - Boosted voice volume to 4.0!
    audio = AudioFileClip(audio_path).volumex(4.0)
    duration = audio.duration 
    video = VideoFileClip(video_path)
    
    # Loop the background video if the audio is longer
    if duration > video.duration:
        video = video.fx(vfx.loop, duration=duration)
    
    # 2. Add Background Music (if available)
    if music_path:
        print(f"    -> Mixing in background music: {os.path.basename(music_path)}")
        music = AudioFileClip(music_path).volumex(0.15) 
        if music.duration < duration:
            music = audio_loop(music, duration=duration)
        else:
            music = music.subclip(0, duration)
        final_audio = CompositeAudioClip([audio, music])
    else:
        print("    -> WARNING: No music found! Check your 'music' folder.")
        final_audio = audio

    # 3. Crop Video to Vertical (9:16)
    max_start = max(0, video.duration - duration)
    start_time = random.uniform(0, max_start)
    video = video.subclip(start_time, start_time + duration).set_audio(final_audio)
    
    w, h = video.size
    target_w = int(h * (9 / 16))
    crop_x1 = (w - target_w) // 2
    video_vertical = video.crop(x1=crop_x1, y1=0, x2=crop_x1 + target_w, y2=h).resize((1080, 1920))
    
    # 4. Apply Artificial Jump Cuts (Resets attention span every 4 seconds)
    clips = []
    for t_start in range(0, int(duration), 4):
        t_end = min(t_start + 4, duration)
        sub_clip = video_vertical.subclip(t_start, t_end)
        if (t_start // 4) % 2 != 0:
            sub_clip = sub_clip.resize(1.15).set_position(('center', 'center'))
        clips.append(sub_clip)
    
    video_with_cuts = concatenate_videoclips(clips, method="compose")

    # 5. Build The Graphics Layer (Title Banner & Subtitles)
    graphic_clips = []
    
    # THE TITLE BANNER
    title_clip = TextClip(title_text.upper(), fontsize=90, color='black', bg_color='yellow', 
                          font='Arial-Bold', size=(1080, 180), method='caption')
    title_clip = title_clip.set_position(('center', 150)).set_duration(duration)
    graphic_clips.append(title_clip)
    
    # THE MATHEMATICAL ESTIMATOR 
    if len(subs) == 0:
        words = text_content.split()
        time_per_word = duration / len(words)
        for i, word in enumerate(words):
            subs.append({"text": word, "start": i * time_per_word, "end": (i + 1) * time_per_word})
    
    # DYNAMIC SUBTITLES (Grouped by 6 words)
    current_group = []
    group_start = 0
    
    for i, sub in enumerate(subs):
        if not current_group:
            group_start = sub["start"]
        current_group.append(sub["text"])
        
        if len(current_group) >= 6 or i == len(subs) - 1:
            group_end = subs[i+1]["start"] if i + 1 < len(subs) else duration
            
            txt_clip = TextClip(
                " ".join(current_group), 
                fontsize=75, 
                color='white', 
                stroke_color='black',
                stroke_width=3,
                font='Arial-Bold', 
                method='caption', 
                size=(900, None)
            ).set_position(('center', 1200)).set_start(group_start).set_end(group_end)
            
            graphic_clips.append(txt_clip)
            current_group = []
    
    # 6. Final Export
    final_clip = CompositeVideoClip([video_with_cuts] + graphic_clips)
    print("    -> Rendering Final MP4... (This may take a minute)")
    final_clip.write_videofile(output_path, fps=60, codec="libx264", audio_codec="aac", audio_bitrate="320k", audio_fps=48000, logger=None)
    
    video.close()
    audio.close()
    final_clip.close()
    print("    -> ✅ Video Complete!")

def main():
    print("==================================================")
    print("   🚀 STARTING YOUTUBE AUTOMATION PIPELINE 🚀   ")
    print("==================================================")

    # 1. Verify the Voice Clone File Exists BEFORE loading the AI
    clone_voice_path = os.path.join(SCRIPT_DIR, 'my_voice.wav')
    if not os.path.exists(clone_voice_path):
        print(f"\nCRITICAL ERROR: Cannot find '{clone_voice_path}'!")
        print("Please record a 10-15 second clip of your voice talking clearly.")
        print("Save it as 'my_voice.wav' in the same folder as this script and run again.")
        return

    # 2. Load the heavy Voice Cloning AI model (XTTSv2)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n[1/3] Warming up Voice Cloning AI Model (XTTSv2) on {device.upper()}...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # 3. Check for the scripts file
    csv_path = os.path.join(SCRIPT_DIR, 'scripts.csv')
    if not os.path.exists(csv_path):
        print(f"\nCRITICAL ERROR: Cannot find {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    output_folder = os.path.join(SCRIPT_DIR, 'output')
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"\n[2/3] Found {len(df)} scripts in CSV. Starting generation...")

    # 4. Process every row in the CSV
    for index, row in df.iterrows():
        title = str(row['Title'])
        script_text = str(row['Script'])
        
        audio_file = os.path.join(SCRIPT_DIR, f"temp_audio_{index}.wav")
        output_file = os.path.join(output_folder, f"Short_{index + 1}.mp4")
        
        # Smart Selectors
        bg_video = get_random_file("backgrounds", (".mp4", ".mov"))
        bg_music = get_random_file("music", (".mp3", ".wav"))
        
        print(f"\n--- Processing Video {index + 1}: {title} ---")
        
        if not bg_video:
            print("ERROR: No videos found in 'backgrounds' folder!")
            continue

        # Pipeline (Passing your voice file into the generator)
        timing_data = generate_local_audio(tts, script_text, audio_file, clone_voice_path)
        create_short(bg_video, audio_file, bg_music, output_file, timing_data, script_text, title)
        
        # Clean up temp audio
        if os.path.exists(audio_file):
            os.remove(audio_file)

    print("\n[3/3] PIPELINE FINISHED! Check your 'output' folder.")

if __name__ == "__main__":
    main()