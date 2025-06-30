from glob import glob
import os
from pathlib import Path
import subprocess


def clear_remote_images(image_folder, remote_top_dir, remote_login):
    
    remote_dir = remote_top_dir / image_folder
    remote_pattern = str(remote_dir / "*.png")

    ssh_rm_png = f"ssh {remote_login} 'rm -f {remote_pattern}'"
    subprocess.run(ssh_rm_png, shell=True)

def download_remote_files(image_folder, filter, ignore_existing, local_top_dir, remote_top_dir, remote_login):

    local_dir = local_top_dir / image_folder
    remote_dir = remote_top_dir / image_folder
    local_pattern = str(local_dir / filter)
    remote_pattern = str(remote_dir / filter)
    
    old_file_list = set(glob(local_pattern))
    ssh_rsync = f"rsync -av {'--ignore-existing ' if ignore_existing else ''}{remote_login}:{remote_pattern} {local_dir}"
    subprocess.run(ssh_rsync, shell=True)
    os.sync()
    updated_file_list = set(glob(local_pattern))
    added_files = updated_file_list - old_file_list
    return len(added_files) > 0
