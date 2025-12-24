Simple, low power, low (but readable) resolution, non-invasive screen recorder for all 
the moments you wish you had saved. 

This is the customizable, open-source release, please go to the link below if you
would like the "plug-n-play" .exe experience.

*the plug-n-play version is not out yet, still needs some minor things tweaked*

Minimum Requirements:
- Any Quad-core CPU (Intel i5-4xxx or newer, Ryzen 3 or better. Dual-cores 
  over 2.0 Ghz should work, don't expect perfection)
- 4GB Ram (App stays under 70MB)
- Any HDD or SSD (Disk Usage Stats are at the bottom of this file)
- Windows 10 / 11
- Python must be installed prior

Instructions:

1. Open this repo, and download it's .zip file, Main Repo Screen > Code > Download Zip

2. Extract the .zip folder you just downloaded

3. Once you are in the extracted folder, the first thing you should do is open the   
   "dependencies.bat" file, which will obviously install the dependencies 
   needed for this recorder to work (you should also do this everytime you install an 
   update). I have a section below on all the dependencies functions.

4. All there is to do now is launch the script, by right-clicking it, and opening it
    with Python (terminal options are below), and setting your directory for your recordings 
    (I recommend setting the FrameKeep repo folder where you want it, and just set your 
    recordings to the FrameKeep folder. It was just easier for me to keep files together 
    this way)

    4a. Opening with terminal is easy as right clicking the script the folder is in,
    clicking "Open in Terminal", and pasting this line of code;
    
    "python FrameKeepOSStable.py"

    You can also open any terminal instance, type; 
    
    "cd c:\Users\you\yourfolder\framekeepos"

    Following with the same line earlier;

    "python FrameKeepOSStable.py"

5. Click the arrow to the very left inside your icon tray (at the bottom right), 
    drag the FrameKeepOS icon down to the tray for effeciency, and right click to stop,start, 
    or pause your recording of the past hour!

Remember, at 5FPS, videos will be around 51 minutes long, not 60. The past hour is
still whats in your file

Intended Future Fixes:

I am currently working on some way to hide the console on the open-source and .exe
versions.

Customization:
To start customizing how FrameKeep works, go to it's configuration directory;

C:\Users\you\AppData\Roaming\FrameKeepOS\config.json

Open the config.json file with Notepad++ (or whatever you use).

- To change the recording directory, replace the path parameter under "log_root". 
  Make sure the quotation marks around the path are still there
- To change what fps FrameKeep records at, change the "fps" parameter to whatever
  FPS you desire
- To change how much FrameKeep downscales your recording to save size, change the
  parameter under "downscale_factor" to whatever factor you desire, the default is 0.5
  (This gives 1080p monitors a 540p recording, 1440p gets 720p, 2160p[4k] gets 1080p)

Make sure to save all changes!

Average Disk Usage Statistics - 1080p (downscaled 0.5x to 540p) @ 5FPS:
- Average Disk Usage/s ≈ 0.24 MB/s
- Average Disk Usage/hr ≈ 850 MB/hr
- Average Disk Usage/24hr ≈ 20.4 GB/24hr
- Average Disk Usage/week ≈ 143 GB/week
- Average Disk Usage/month ≈ 610 GB/month

Dependencies explained:
- Python. This is the language FrameKeepOS is written in. The open-source version of 
  FrameKeepOS needs Python the same way a Word document needs Microsoft Word. If you 
  are using the EXE version, Python is already included and you don’t need to install 
  anything.

- Screen Capture Library (mss). This takes very fast screenshots of your screen.
  FrameKeepOS works by saving frames over time. This is the tool that actually 
  “looks” at your screen. It does not; record audio, send screenshots anywhere,
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