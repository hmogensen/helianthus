from camera_manager import camera_settings, get_credentials
from network_camera import NetworkCamera
import argparse
import tomllib

default_flush_frames = 0
default_image_interval_s = 600
    
def record_timelapse(cam_stream:str, 
                     location:str, 
                     flush_frames:int, 
                     image_interval_s:float, 
                     persistent:bool):
    
    with open(camera_settings, 'rb') as f:
        config = tomllib.load(f)
    
    if '.' in cam_stream:
        camera_type, stream_type = cam_stream.split('.', 1)
    else:
        camera_type = cam_stream
        stream_type = None
        
    if camera_type not in config:
        raise ValueError(f"Camera type '{camera_type}' not found in {camera_settings}")
        
    cam_ip = config[camera_type]['ip']
    if stream_type and stream_type in config[camera_type]:
        stream_path = config[camera_type][stream_type]['stream_path']
    elif 'stream_path' in config[camera_type]:
        stream_path = config[camera_type]['stream_path']
    else:
        raise ValueError(f"Stream '{stream_type}' not found for camera '{camera_type}'")
    
    username, password = get_credentials(camera_type)
    if not username or not password:
        raise ValueError(f"No credentials found for camera '{camera_type}'. Use: python camera_manager.py save {camera_type}")

    if 'port' in config[camera_type]:
        port = config[camera_type]['port']
        rtsp_url = f"rtsp://{username}:{password}@{cam_ip}:{port}/{stream_path}"
    else:
        rtsp_url = f"rtsp://{username}:{password}@{cam_ip}/{stream_path}"
    
    cam = NetworkCamera(url=rtsp_url, location=location, flush_frames=flush_frames, image_interval_s=image_interval_s)
    cam.start_capture(continuous_capture=persistent)
    
    return cam

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Time lapse recording with network cameras')
    parser.add_argument('cam', help='Camera id')
    parser.add_argument('loc', type=str, help='Location (e.g. "garden") or portrayed object (e.g. "sprouting plant")')
    parser.add_argument('--flush', '-f', type=int, default=default_flush_frames, 
                        help=f'Number of frames to flush. Default: {default_flush_frames}')
    parser.add_argument('--interval', '-i', type=int, default=default_image_interval_s, 
                        help=f'Interval between image captures in seconds. Default: {default_image_interval_s}')
    parser.add_argument('--restart-every-cycle', '-r', action='store_true',
                    help='Restart the camera connection on every capture cycle')
    
    args = parser.parse_args()
    
    record_timelapse(
        cam_stream=args.cam,
        location=args.loc,
        flush_frames=args.flush,
        image_interval_s=args.interval,
        persistent=not args.restart_every_cycle
    )
