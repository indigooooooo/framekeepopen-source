FrameKeep - (C) 2025 Tanner Lucier
Licensed under GPLv3 - see LICENSE file for details

v2.0.0 Changelog
- Fixed FrameKeep not being able to sometimes find openh264-1.8.0-win64.dll on startup
- Added ffmpeg.exe to handle automatic but safe .mkv → .mp4 conversions (you can download your own ffmpeg build, using a different build could cause script instability), this does add ~100MB to the final build. You can delete the .exe and/or turn this off in the configuration file if you wish.
- Added CRF (Constant Rate Factor) so .mkv → .mp4 conversions are not only safe, but will also save storage space. You can turn CRF off in the configuration .json file, you can also edit the CRF value in the config file, the default is 23 to maintain quality while getting smaller files. CRF is automatically ignored if .mkv → .mp4 conversions are turned off.
- Added the "chunk_minutes" option to the configuration file, this allows you to change how long you want each file to record for. The default has been left at 60 minutes
- Important actions added to the console. Also added color coding, and timestamps.
- Added folders for third-party software to clean the repo up.
- Fixed build version to match Semantic Versioning standards (hopefully), also started saving releases for older versions. FrameKeepOS, FFmpeg, and Cisco's Open H.264 licensing has been added to the repo.
- Adjusted H.264 ADUS to new averages done with personal testing (users are more than welcome to post their own results, they will be taken into account with ADUS numbers).

Future Plans
- FrameKeep only records the primary monitor, I hope to add configuration settings that let you choose all, or certain monitors.
- Plan on implementing a "frame-break" system that automatically detects when the same frame is being displayed (for say, 5 or 10 frames), and saves space by not saving that frame repeatedly. While CRF and H.264 are good at this on their own, a correct system could save even more storage space.
- H.265 and AV1 are in the plans, and will NOT be replacing the defaults, they will be optional bonuses to users that can computationally afford it.

v1.1.0 Changelog
- Switched MJPG from being the default recording codec, to H.264. MJPG is a fallback if for some reason H.264 doesn't work. This cuts recording file sizes by ~85%, with no loss in recording quality, while also using ~20% less RAM. You can also now customize which codec you want to use, in the FrameKeep config.json file.
- Updated MJPG Average Disk Usage Statistics (ADUS) after more testing. Also added H.264 ADUS