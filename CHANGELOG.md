v1.1 Changelog
- Switched from MJPG as the default recording codec, to H.264. MJPG is a fallback if for some reason H.264 doesn't work. This cuts recording file sizes by ~75%, with no loss in recording quality, while also using ~23% less RAM. You can also now customize which codec you want to record in, in the FrameKeep config.json file.
- Updated MJPG Average Disk Usage Statistics (ADUS) after more testing. Also added H.264 ADUS

Future Plans
- Plan on adding H.265 (HEVC) and AV1 (AOMedia Video 1) for even more savings on storage, without losing any quality.