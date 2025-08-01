# timelapse
![Sprouting sunflowers](https://github.com/hmogensen/timelapse-gallery/raw/main/sprouting-sunflowers.gif)
## Gateway scripts
### Capture images and manage network cameras (on remote device)
- `timelapse.py` Create timelapse images using network cameras
- `camera_manager.py` Store and retrieve credentials for cameras
- `web_systemd_manager.py` Web interface for remote camera control
### Download images and customize timelapse videos (on local computer)
- `download_remote_files.py` Download images from remote device
- `make_video.py` Render videos from downloaded images

## Documentation
- `setup.md` General setup for remote Linux devices, with auto restart if system is rebooted
- `poe-injector-local-network.md` How to create a local network with a PoE injector, useful for cameras without internet access
- `running-systemd-manager.md` How to run applications that require root access as a systemd service

## Sample files
- `cameras.toml` Sample file with camera properties
- `video-settings.yaml` Sample file with video properties
- `systemd` folder: Sample service files for running jobs in Linux
