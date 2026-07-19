🚀 AI YouTube Shorts Automator

A fully automated Python pipeline that generates faceless YouTube Shorts using local Machine Learning models.

This project reads from a CSV of scripts, utilizes open-source zero-shot voice cloning to generate human-like narration, and dynamically edits the final vertical video with jump cuts, background music, and timed subtitles.

✨ Features

100% Local AI Voice: Uses Coqui TTS (XTTSv2) running locally to clone voices and generate audio without API costs.

Automated Video Editing: Uses moviepy to assemble vertical (9:16) videos.

Dynamic Jump Cuts: Automatically zooms in 15% every 4 seconds to reset viewer attention span.

Smart Subtitles: Calculates word timings mathematically and groups them into snappy, 6-word title blocks.

Monkey Patched Resiliency: Includes custom runtime patches for PyTorch 2.6 security blocks and Windows FFmpeg audio codec issues.

🛠️ Prerequisites (Windows)

Python 3.10+

eSpeak-NG: Required for the phonetic translation backend. Installed to C:\Program Files\eSpeak NG.

ImageMagick: Required by MoviePy to render the subtitle text graphics.

📁 Folder Structure

To run this project, ensure your directory looks like this (media folders are ignored by git):

├── backgrounds/      # Place your raw .mp4 gameplay/background clips here
├── music/            # Place your .mp3 background tracks here
├── output/           # The final Shorts will generate here
├── scripts.csv       # Must contain 'Title' and 'Script' columns
├── my_voice.wav      # A 10-15 second clear voice sample for cloning
└── bot.py            # Main automation script


🚀 Usage

Activate your virtual environment and run:

python bot.py
