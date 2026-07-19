**🚀 AI YouTube Shorts Automator**
An advanced, fully automated Python pipeline designed to transform a simple CSV spreadsheet of text scripts into high-retention, ready-to-upload faceless vertical videos tailored for YouTube Shorts, TikTok, and Instagram Reels. By executing local Machine Learning models directly on your hardware, this tool bypasses the need for costly cloud API subscriptions. It autonomously orchestrates the entire video production lifecycle: synthesizing zero-shot AI voiceovers, mixing background gameplay and looping music, applying algorithmic zoom jump-cuts, and rendering dynamic, mathematically synced subtitles. What normally requires hours of manual video editing is reduced to minutes, allowing creators to batch-generate an entire month of content from a single text file.

**✨ Features**
**Local Voice Cloning**: Uses Coqui XTTSv2 to generate audio natively—zero cloud API costs.

**Smart Editing**: moviepy automatically mixes voice, background media, and music into a 9:16 format.

**High Retention**: Features snappy 6-word dynamic subtitles and 15% zoom jump cuts every 4 seconds.

**Resilient Architecture & Runtime Patching**: Ensures out-of-the-box stability via custom monkey patches. It bypasses PyTorch 2.6 security blocks to load XTTSv2 weights and routes torchaudio through soundfile to prevent Windows FFmpeg crashes, eliminating complex manual setups.

**🛠️ Quick Start**
**Prerequisites**: Install Python 3.10+, eSpeak-NG (must be in C:\Program Files\eSpeak NG), and ImageMagick.

**Workspace Setup**: Add your raw media to backgrounds/ and music/. Populate scripts.csv (Title, Script) and provide a 10s voice sample named my_voice.wav.

**Install & Run**:
\'''pip install TTS moviepy pandas soundfile torchcodec'''
'''python bot.py'''


**⚖️ License**
The code is licensed under the **MIT License**.
Disclaimer: The XTTSv2 voice model is subject to the Coqui Public Model License (CPML) for non-commercial use.