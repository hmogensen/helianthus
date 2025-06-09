# timelapse

## Sprouting sunflowers
![Sprouting sunflowers](https://github.com/hmogensen/timelapse-gallery/raw/main/sprouting-sunflowers.gif)

## Gateway scripts
- `timelapse.py` Create timelapse images using network cameras
- `camera_manager.py` Store and retrieve credentials for cameras
- `download_remote_files.py` Utility function to download images from remote device (e.g. raspberry pi connected to network camera)
- `make_video.py` Utility function to create videos from selected images, with options like frames-per-second, cropping, image rotation etc (work in progress)
- `cameras.toml` Example file for specifying camera properties like IP address, RTSP stream path etc
- `video-settings.toml` Example file that is used to generate timelapse videos.

## Documentation in docs folder:
- `setup.md` General setup for linux devices streaming from network cameras, with auto restart if system is rebooted
- `poe-injector-local-network.md` Specific information on how to create a local network with a PoE injector, useful for cameras without internet access
- `running-systemd-manager.md` Info on how to run applications that require root access as a systemd service
- `systemd` folder: example service files for running jobs in Linux
