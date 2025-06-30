#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from interim_password_manager import get_ssh_login
from download_remote_files import download_remote_files, clear_remote_images
from make_video import make_video

def main(tags, make_movie, delete_remote):
    # tags = ["tradgard-torpet", "garden-lowres"]#"sunflowers-lowres", "scaffolding"]
    top_dir = Path(os.path.expanduser("~"))
    active_dir = top_dir / "repos/timelapse"
    data_dir = top_dir / "data"

    remote_login = get_ssh_login("rbpi5")

    for image_folder in tags:

        # download images from active directory
        download_remote_files(image_folder=image_folder, filter="*.png", ignore_existing=True,
                            local_top_dir=data_dir,
                            remote_top_dir=active_dir,
                            remote_login=remote_login)
        
        # download images from data directory
        download_remote_files(image_folder=image_folder, filter="*.png", ignore_existing=True,
                            local_top_dir=data_dir,
                            remote_top_dir=data_dir,
                            remote_login=remote_login)
        
        if delete_remote:
            clear_remote_images(image_folder=image_folder, remote_top_dir=active_dir, remote_login=remote_login)
            clear_remote_images(image_folder=image_folder, remote_top_dir=data_dir, remote_login=remote_login)
        
        # # download movies from remote active directory, and overwrite corresponding file in local data directory
        # download_remote_files(image_folder=image_folder, filter="*.mp4", ignore_existing=False,
        #                       local_top_dir=data_dir,
        #                       remote_top_dir=active_dir,
        #                       remote_login=remote_login)

    if make_movie:
        for tag in tags:
            make_video(tag, tag + ".mp4", preview=True)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('remote', nargs='*', help='List of remote values')
    parser.add_argument('--make-movie', action='store_true', default=False, 
                    help='Make movie (default: False)')
    parser.add_argument('--delete-remote', action='store_true', default=False,
                        help='Delete images on remote device after downloading them')

    args = parser.parse_args()

    main(tags=args.remote, make_movie=args.make_movie, delete_remote=args.delete_remote)