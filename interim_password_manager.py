import toml

def get_credentials(camera_id:str):
    print(f"camera_id: {camera_id}")
    with open('credentials.toml', 'r') as f:
        settings = toml.load(f)[camera_id]
    return settings["username"], settings["password"]