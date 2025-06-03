from video_toml import parse_video_settings


def make_video(video_tag:str, video_path:str, preview:bool):
    print("make_video")
    template = parse_video_settings(video_tag)
    writer = template.generate_writer(video_path=video_path)
    template.append_video(writer=writer, preview=preview)
    template.close_writer(writer, preview=preview)
