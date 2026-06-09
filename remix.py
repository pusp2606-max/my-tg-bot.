import subprocess
import os
import uuid

def make_remix(input_file):
    os.makedirs("output", exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_file = os.path.join("output", output_filename)

    # Пояснение фильтров для звука Mezzia:
    # 1. atempo=1.3: ускоряем ритм.
    # 2. bass=g=20: задираем бочку до предела.
    # 3. acrusher: создает "грязный", цифровой перегруз (дисторшн), характерный для хардтекка.
    # 4. compand: делает звук очень плотным, "сплющивает" его.
    
    filter_complex = (
        "atempo=1.3,"
        "bass=g=20:f=100,"
        "acrusher=bits=8:mode=log:samples=100,"
        "compand=attacks=0.001:decays=0.05:points=-80/-90|-40/-30|-10/-5|0/0:gain=2"
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

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обработке: {e.stderr}")
        raise Exception("Не удалось создать ремикс")
