import ffmpeg

try:
    (
        ffmpeg
        .input("https://example.com/playlist.m3u8")
        .output("video.mp4", c="copy")
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
    print("Download complete")
except ffmpeg.Error as e:
    print("Error:", e.stderr.decode())