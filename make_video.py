from video_toml import parse_video_settings


def make_video(videos:list[str], video_path:str, preview:bool):

    template = parse_video_settings(videos[0])
    writer = template.generate_writer(video_path=video_path)
    for video in videos:
        template = parse_video_settings(video)
        success = template.append_video(writer=writer, preview=preview)
        if not success:
            break
    template.close_writer(writer, preview=preview)
