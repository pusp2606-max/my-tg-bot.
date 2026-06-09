import subprocess
import os
import uuid
import random

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)
    
    # Бот ищет все .wav файлы в папке /kicks
    kick_files = [os.path.join("kicks", f) for f in os.listdir("kicks") if f.endswith(".wav")]
    
    # Если бот нашел файлы, он берет один случайный
    if kick_files:
        selected_kick = random.choice(kick_files)
    else:
        return None # Или верни путь к стандартному файлу, если нет сэмплов
    
    # Случайная скорость для уникальности каждого трека
    random_tempo = round(random.uniform(1.2, 1.45), 2)
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-stream_loop", "-1", "-i", selected_kick, 
        "-filter_complex", 
        f"[0:a]atempo={random_tempo},volume=0.6[music];" 
        "[1:a]volume=1.2[kick];"             
        "[music][kick]amix=inputs=2:duration=shortest[aout]", 
        "-map", "[aout]",
        "-b:a", "320k",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file
