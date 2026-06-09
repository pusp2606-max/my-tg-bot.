import subprocess
import os
import uuid
import random

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)
    
    # Случайная частота для кика (120-200 Гц)
    freq = random.randint(120, 200)
    
    # Команда синтезирует кик прямо во время обработки
    # -t 30 — ограничение времени, чтобы бот не уходил в бесконечный цикл
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi", "-i", f"sine=frequency={freq}:duration=0.15",
        "-i", input_file,
        "-filter_complex",
        f"[0:a]asade=1:0.05:0.05,volume=1.5[kick];"
        f"[1:a]atempo={round(random.uniform(1.3, 1.45), 2)},volume=0.6[music];"
        "[music][kick]amix=inputs=2:dropout_transition=0:duration=shortest[aout]",
        "-map", "[aout]",
        "-t", "30",
        "-b:a", "192k",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file
