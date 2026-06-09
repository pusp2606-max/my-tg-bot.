import subprocess
import os
import uuid
import random

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)
    
    # Генерируем случайные параметры для синтеза бочки
    # freq - начальная частота, decay - скорость затухания
    freq = random.randint(100, 250)
    decay = random.uniform(0.1, 0.3)
    
    # ffmpeg генерирует "синтетический" кик прямо в процессе обработки
    # Это создает эффект Hardtekk без использования внешних файлов
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi", "-i", f"sine=frequency={freq}:duration=0.2",
        "-i", input_file,
        "-filter_complex",
        f"[0:a]asade=1:0.1:0.1[kick];"
        f"[1:a]atempo={round(random.uniform(1.3, 1.5), 2)},volume=0.7[music];"
        "[music][kick]amix=inputs=2:dropout_transition=0:duration=shortest[aout]",
        "-map", "[aout]",
        "-b:a", "320k",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file
