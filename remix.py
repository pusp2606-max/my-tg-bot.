import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize

class HardtekkProcessor:
    """
    Профессиональный процессор для Hardtekk сэмплов.
    Реализует жесткий клиппинг и нормализацию.
    """
    def __init__(self, file_path: str):
        self.audio = AudioSegment.from_file(file_path)

    def apply_hard_distortion(self, threshold_db: float = -3.0):
        """Создает характерный перегруженный звук (клиппинг)."""
        # Превращаем в массив для математической обработки
        samples = np.array(self.audio.get_array_of_samples())
        
        # Хардкорный клиппинг
        max_val = np.iinfo(samples.dtype).max
        threshold = max_val * (10 ** (threshold_db / 20))
        
        samples = np.clip(samples, -threshold, threshold)
        
        self.audio = self.audio._spawn(samples.tobytes())
        return self

    def boost_punch(self, gain_db: float = 6.0):
        """Усиление транзиентов (панча)."""
        self.audio = self.audio + gain_db
        return self

    def export(self, output_path: str):
        """Сохранение результата в WAV (стандарт для диджеев)."""
        self.audio = normalize(self.audio)
        self.audio.export(output_path, format="wav")
        print(f"Готово: {output_path}")

def main():
    # Пример использования для обработки бочки (kick)
    processor = HardtekkProcessor("kick_raw.wav")
    
    (processor
     .boost_punch(gain_db=5.0)
     .apply_hard_distortion(threshold_db=-2.0)
     .export("kick_tekk_final.wav"))

if __name__ == "__main__":
    main()
