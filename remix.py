import subprocess
import os
import uuid

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)
    
    # 1. Ускоряем трек до 160 BPM (примерно 1.3x)
    # 2. Берем сэмпл бочки и зацикливаем его (aloop)
    # 3. Смешиваем (amix)
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-i", "kick.wav",  # Добавляем наш сэмпл бочки
        "-filter_complex", 
        "[1:a]aloop=loop=-1:size=2e9[kick];" # Зацикливаем бочку
        "[0:a]atempo=1.3,volume=0.8[music];"  # Ускоряем музыку
        "[music][kick]amix=inputs=2:duration=first[aout]", # Смешиваем
        "-map", "[aout]",
        "-b:a", "320k",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file
