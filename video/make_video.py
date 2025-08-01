from .video_settings_parser import parse_video_settings


def make_video(video_tag: str, video_path: str, preview: bool):
    template = parse_video_settings(video_tag)
    template.render_video(video_path=video_path, preview=preview)
