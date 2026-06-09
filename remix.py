import subprocess
import os

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)

    output_file = "output/remix.mp3"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter:a",
        "asetrate=44100*1.25,aresample=44100,bass=g=8",
        "-b:a",
        "320k",
        output_file
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        raise Exception(result.stderr)

    return output_file
