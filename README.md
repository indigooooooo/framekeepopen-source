#### FrameKeep - (C) 2025 Tanner Lucier

###### Licensed under GPLv3 - see LICENSE file for details

##### Simple, low power, low (but readable) resolution, non-invasive screen recorder for all the moments you wish you had saved.

#

### Minimum Requirements:
- Any Quad-core CPU (Intel i5-4xxx or newer, Ryzen 3 or better. Dual-cores 
  over 2.0 Ghz should work, don't expect perfection)
- 4GB Ram (App stays under 110MB)
- Any HDD or SSD (Disk Usage Stats are at the bottom of this file)
- Windows 10 / 11
- Python, Microsoft Visual C++ Runtime

#

### Instructions:

1. Open this repo, and download it's .zip file, Main Repo Screen > Code > Download Zip

2. Extract the .zip folder you just downloaded

3. Once you are in the extracted folder, the first thing you should do is open the   
   "dependencies.bat" file, which will obviously install the dependencies 
   needed for this recorder to work (you should also do this everytime you install an 
   update). I have a section below on all the dependencies functions. You have to download Python if you do not have it, I did not make this a dependecy, as some coders like to use older versions of Python

4. All there is to do now is launch the script, by right-clicking it, and opening it
    with Python (terminal options are below), and setting your directory for your recordings 
    (I recommend setting the FrameKeep repo folder where you want it, and just set your 
    recordings to the FrameKeep folder. It was just easier for me to keep files together 
    this way)

    4a. Opening with terminal is easy as right clicking the folder the script is in,
    clicking "Open in Terminal", and pasting this line of code;
    
    "python FrameKeepOSv2.1.0-stable.py"

    You can also open any terminal instance, type; 
    
    "cd c:\Users\you\yourfolder\framekeepos"

    Following with the same line earlier;

    "python FrameKeepOSv2.1.0-stable.py"

5. Click the arrow to the very left inside your icon tray (at the bottom right), 
    drag the FrameKeepOS icon down to the tray for effeciency, and right click to stop, start, or pause your recording of the past hour!

Remember, at 5FPS, videos will not be 60 minutes long. The past hour is still whats in your file

#

### Customization:
To start customizing how FrameKeep works, go to it's configuration directory;

C:\Users\you\AppData\Roaming\FrameKeepOS\config.json

Open the config.json file with Notepad++ (or whatever you use).

- To change the recording directory, replace the path parameter under "log_root". 
Make sure the quotation marks around the path are still there.
- To change what fps FrameKeep records at, change the "fps" parameter to whatever
FPS you desire, no quotations.
- To change how much FrameKeep downscales your recording to save size, change the
parameter under "downscale_factor" to whatever factor you desire, the default is 0.5
(This gives 1080p monitors a 540p recording, 1440p gets 720p, 2160p[4k] gets 1080p).
- To change which codec you'd like to record in, change the parameter under "codec" to "H264", or "MJPG"
- To change how long you want each file to record for, change the parameter under "chunk_minutes", to however many minutes you want FrameKeep to record for. No quotations around your minutes.
- To change whether you want H.264-based MP4 conversion, change the parameter under "convert_to_mp4" is set to true, or false. No quotations around your true or false.
- To turn CRF (Constant Rate Factor) on/off change the parameter under "use_crf" to true or false. To change the CRF value change the parameter under "crf_value" to what suits your needs, the default is 23, no quotations for either of these. 0 is lossless quality, 12-18 is near lossless, 19-22 is HQ, 23-27 is balanced, 28-32 is very low quality, storage focused. 33+ is not recommended

Codec Fallback Order: H.264 → MJPG

Make sure to save all changes, and restart the script!

#

Average Disk Usage Statistics - H.264 1080p downscaled 0.5x to 540p @ 5FPS w/ CRF(23) MP4 Conversion, 1 Monitor:
- Average Disk Usage/s ≈ 32.3 KB/s
- Average Disk Usage/hr ≈ 116.35 MB/hr
- Average Disk Usage/24hr ≈ 2.8 GB/24hr
- Average Disk Usage/week ≈ 19.55 GB/week
- Average Disk Usage/month ≈ 78.2 GB/month

Average Disk Usage Statistics - H.264 1080p downscaled 0.5x to 540p @ 5FPS, 1 Monitor:
- Average Disk Usage/s ≈ 45.5 KB/s
- Average Disk Usage/hr ≈ 164 MB/hr
- Average Disk Usage/24hr ≈ 3.93 GB/24hr
- Average Disk Usage/week ≈ 27.5 GB/week
- Average Disk Usage/month ≈ 110 GB/month

Average Disk Usage Statistics - H.264 1080p downscaled 0.5x to 540p @ 5FPS MP4 Conversion NO CRF, 1 Monitor:
- Average Disk Usage/s ≈ 52 KB/s
- Average Disk Usage/hr ≈ 186 MB/hr
- Average Disk Usage/24hr ≈ 4.5 GB/24hr
- Average Disk Usage/week ≈ 31.25 GB/week
- Average Disk Usage/month ≈ 126 GB/month

Average Disk Usage Statistics - MJPG 1080p downscaled 0.5x to 540p @ 5FPS, 1 Monitor:
- Average Disk Usage/s ≈ 0.25 MB/s
- Average Disk Usage/hr ≈ 905 MB/hr
- Average Disk Usage/24hr ≈ 21.7 GB/24hr
- Average Disk Usage/week ≈ 152 GB/week
- Average Disk Usage/month ≈ 652 GB/month

ALL ADUS ENTRIES ARE ON A SYSTEM USING THESE SYSTEM SPECIFICATIONS (FRAMEKEEP DOES NOT REQUIRE A GPU):
INTEL i5-12600K
32GB DDR5 6000MHz
NVME SSD

#

### FAQ

Q: Why has the .mkv → .mp4 conversion failed if I haven't changed anything?
A: Make sure all dependencies are installed, and ffmpeg.exe is trusted by your computer (if you double click it, it may say it is unknown program or try to flag it. If not check in your Windows Security settings), ffmpeg must be trusted in order for conversion to work. Also make sure in the configuration file that convert_to_mp4 is set to true. If neither of these work, post an issue on the Github page with any errors you get and I will *hopefully* help you.

# 

### Dependencies explained:
- Python. This is the language FrameKeepOS is written in. The open-source version of 
  FrameKeepOS needs Python the same way a Word document needs Microsoft Word. If you 
  are using the EXE version, Python is already included and you don’t need to install 
  anything.

- Screen Capture Library (mss). This takes very fast screenshots of your screen.
  FrameKeepOS works by saving frames over time. This is the tool that actually 
  “looks” at your screen. It does not record audio, send screenshots anywhere,
  or upload anything.

- Image & Math Libraries (opencv-python and numpy) help handle and organize image data 
  efficiently. Screenshots are just big piles of numbers. These tools make sure 
  FrameKeepOS can handle images quickly, use less CPU, and use less disk space.
  Without them, the program would be slow and very inefficient.

- Windows Integration (pywin32) lets the program interact properly with Windows.
  This is how FrameKeepOS can behave correctly on Windows, manage windows and 
  background behavior, handle console visibility properly. It does not control your 
  system or change settings.

- Tray Icon Support (pystray) creates the icon in the system tray (near the clock).
  This allows you to start and stop recording, and close the program cleanly.
  Without it, you’d have no easy way to control FrameKeepOS.

- Image Support (pillow) helps load and display icons and images. It is needed for 
  the tray icon, and other image format handling, it does nothing else.

- .NET Bridge (pythonnet) allows Python to talk to Windows’ built-in systems more 
  cleanly. This improves compatibility and stability on Windows and allows future 
  improvements without hacks.

- FFmpeg is used only after recording completes, and only if MP4 conversion is enabled in the configuration. When enabled, FrameKeepOS uses FFmpeg to convert recorded MKV files to MP4, encode using libx264, and optionally apply CRF-based compression. FFmpeg does not affect recording performance and is not required for MKV output.

- Cisco's OpenH264, FrameKeep uses OpenCV for screen capture and video encoding. When H.264 is selected, OpenCV relies on Cisco OpenH264 to provide the H.264 encoder backend. If the OpenH264 library is available, FrameKeepOS records H.264 video into MKV files directly through OpenCV.
If OpenH264 cannot be loaded, the recorder automatically falls back to MJPG encoding. OpenH264 is only used for live recording, not for file conversion.

#
### Third-Party Software

This project uses FFmpeg (GPLv3). FFmpeg is not part of this project’s code. 
See LICENSE_FFMPEG for details.

FFmpeg source code: https://github.com/GyanD/codexffmpeg/releases/tag/2025-12-24-git-abb1524138

Cisco's Open H.264 source code https://github.com/cisco/openh264
