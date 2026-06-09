import subprocess
import os
import uuid

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)

    # Старый рабочий вариант без внешних сэмплов
    filter_complex = (
        "atempo=1.25,"
        "equalizer=f=80:width_type=h:width=50:g=8,"
        "bass=g=10:f=100,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter:a", filter_complex,
        "-b:a", "320k",
        "-ar", "44100",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file
