import sounddevice as sd
import numpy as np
import wave
import requests

# Raspberry Pi Server URL
PI_SERVER_URL = "http://192.168.1.3:8000/transcribe"  # Đổi IP của Pi (VD: 192.168.1.100)

# Hàm ghi âm và lưu file
def record_audio(duration=5, samplerate=16000, filename="recorded.wav"):
    print("🎤 Đang ghi âm... Hãy nói vào micro!")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    print(f"File đã được lưu: {filename}")
    return filename

# Gửi file đến Raspberry Pi để nhận diện giọng nói
def send_audio_to_pi(filename):
    with open(filename, "rb") as audio_file:
        files = {"file": audio_file}
        response = requests.post(PI_SERVER_URL, files=files)

    if response.status_code == 200:
        print("Kết quả từ Raspberry Pi:", response.json())
    else:
        print("Lỗi khi gửi file:", response.text)

# Ghi âm và gửi file
if __name__ == "__main__":
    file_path = record_audio()
    send_audio_to_pi(file_path)
