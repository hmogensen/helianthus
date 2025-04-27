from network_camera import NetworkCamera
import configparser
import argparse

default_flush_frames = 0
default_image_interval_s = 600

def record_timelapse(cam_id:str, location:str, flush_frames:int, image_interval_s:float, persistent:bool):
    
    config = configparser.ConfigParser()
    config.read('credentials.txt')
    
    if cam_id not in config:
        raise ValueError(f"Camera type '{cam_id}' not found in credentials.txt")
    
    cam_ip = config[cam_id]['ip']
    username = config[cam_id]['username']
    password = config[cam_id]['password']
    stream_path = config[cam_id]['stream_path']
    
    if "axis" in cam_id:
        rtsp_url = f"rtsp://{username}:{password}@{cam_ip}/{stream_path}"
    else:
        rtsp_url = f"rtsp://{username}:{password}@{cam_ip}:554/{stream_path}"
    
    cam = NetworkCamera(url=rtsp_url, location=location, flush_frames=flush_frames, image_interval_s=image_interval_s)
    cam.start_capture(persistent=persistent)
    
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
        cam_id=args.cam,
        location=args.loc,
        flush_frames=args.flush,
        image_interval_s=args.interval
        persistent=not args.restart_every_cycle
    )
