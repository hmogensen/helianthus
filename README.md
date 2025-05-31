# timelapse

- `timelapse.py` Gateway function to create timelapse images using network cameras
- `camera_manager.py` Used to store and retrieve credentials for cameras
- `download_remote_files.py` Utility function to download images from remote device (e.g. raspberry pi connected to network camera)
- `make_video.py` Utility function to create videos from selected images, with options like frames-per-second, cropping, image rotation etc (TBD)
- `cameras.toml` Example file for specifying camera properties like IP address, RTSP stream path etc
- `video-settings.txt` Example file that is used to generate timelapse videos. Will be replaced by TOML in future update

Documentation in docs folder:
- `setup.md` General setup for linux devices streaming from network cameras, with auto restart if system is rebooted
- `poe-injector-local-network.md` Specific information on how to create a local network with a PoE injector, useful for cameras without internet access
- `systemd` folder: example service files for running jobs in Linux
