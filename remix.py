import subprocess
import os
import uuid

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)
    
    # Теперь бот будет брать твой kick.wav и накладывать его на трек
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-stream_loop", "-1", "-i", "kick.wav", 
        "-filter_complex", 
        "[0:a]atempo=1.3,volume=0.5[music];" 
        "[1:a]volume=1.2[kick];"             
        "[music][kick]amix=inputs=2:duration=shortest[aout]", 
        "-map", "[aout]",
        "-b:a", "320k",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file
