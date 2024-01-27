import pytube


def int2str(cur_int: int) -> str:
    """ Get  """
    n = str(cur_int)[::-1]
    return '\u00A0'.join(n[i:i+3] for i in range(0, len(n), 3))[::-1]


def on_progress(stream, total_size, byte_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - byte_remaining
    percent = (bytes_downloaded / total_size) * 100
    print("\r" + chr(9646)*int(percent) + chr(9647)*(100-int(percent)) + f" {int(percent)}% " +
                                        f"[{int2str(bytes_downloaded)} / {int2str(total_size)}]", end="")


video_link = "https://www.youtube.com/watch?v=J8liLOiKCyQ"
yt = pytube.YouTube(video_link, on_progress_callback=on_progress)

Path2SavedVideo = yt.streams.get_highest_resolution().download()

print("\n"+Path2SavedVideo)

print("OK")
