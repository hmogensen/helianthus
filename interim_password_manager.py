import toml

def _get_settings(tag:str):
    with open('credentials.toml', 'r') as f:
        settings = toml.load(f)[tag]
    return settings

def get_credentials(camera_id:str):
    settings = _get_settings(camera_id)
    return settings["username"], settings["password"]

def get_ssh_login(ssh_unit:str):
    settings = _get_settings(ssh_unit)
    return f'{settings["username"]}@{settings["ip"]}'
