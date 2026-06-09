import subprocess
import os
import uuid

def make_remix(input_file):
    # Создаем папку, если её нет
    os.makedirs("output", exist_ok=True)

    # Генерируем уникальное имя, чтобы запросы не конфликтовали
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)

    # Фильтры для Hardtekk: 
    # atempo=1.2 (ускорение)
    # bass=g=15 (мощный кик)
    # compand (сжатие для плотности звука)
    filter_complex = "atempo=1.2,bass=g=15:f=100,compand=attacks=0.01:points=-80/-900|-10/-10|0/0"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter:a", filter_complex,
        "-b:a", "320k",
        "-ar", "44100",
        output_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обработке: {e.stderr}")
        raise Exception("Не удалось создать ремикс")
