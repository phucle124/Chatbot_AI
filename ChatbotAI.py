cách sử dụng trong code file ChatbotAI :
from fastapi import FastAPI, File, UploadFile
import whisper
import pyaudio
import wave
import os

app = FastAPI()

#"D:\Python\ffmpeg-2025-03-10-git-87e5da9067-full_build\bin" là đường dẫn local gốc để sử dụng ffmpeg cho việc định dạng dữ liệu chuyển đổi codec (audio)
os.environ["PATH"] += r";D:\Python\ffmpeg-2025-03-10-git-87e5da9067-full_build\bin"

# Load model Whisper chỉ một lần khi khởi động server
try:
    model = whisper.load_model("large")  # Có thể đổi thành "base" nếu cần
    print("Model Whisper đã tải xong!")
except Exception as e:
    print(f"Lỗi khi tải model: {e}")
    model = None  # Tránh lỗi khi truy cập model nếu chưa tải xong

# Kiểm tra API đang hoạt động
@app.get("/health")
def health_check():
    return {"status": "API is running"}

# Hàm ghi âm và lưu thành file cố định
def record_audio(filename="D:\\Python\\record\\Uservoice.wav", duration=5, samplerate=16000):
    try:
        print("🎤 Đang ghi âm... Hãy nói vào micro!")
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=samplerate, input=True, frames_per_buffer=1024)
        frames = []

        for _ in range(0, int(samplerate / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Lưu vào file Uservoice.wav (ghi đè)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(samplerate)
            wf.writeframes(b''.join(frames))

        print(f"✅ Ghi âm xong! File lưu tại: {filename}")
        return filename
    except Exception as e:
        print(f"Lỗi ghi âm: {e}")
        return None

# API Ghi Âm và Nhận Diện Văn Bản
@app.get("/listen")
def listen():
    if model is None:
        return {"error": "Model Whisper chưa tải xong. Vui lòng thử lại!"}

    file_path = record_audio()
    if file_path is None:
        return {"error": "Không thể ghi âm, vui lòng kiểm tra micro!"}

    print("📝 Đang nhận diện giọng nói...")
    result = model.transcribe(file_path, language="vi")  # Chỉ định tiếng Việt

    if len(result["text"].strip()) < 5:
        return {"error": "Âm thanh không rõ, vui lòng thử lại hoặc tải file lên!"}

    return {"text": result["text"]}

# API Upload File để nhận diện giọng nói
@app.post("/transcribe")
def transcribe(file: UploadFile = File(...)):
    if model is None:
        return {"error": "Model Whisper chưa tải xong. Vui lòng thử lại!"}

    try:
        file_path = "D:\\Python\\record\\Uservoice.wav"  # Ghi đè lên file cũ
        with open(file_path, "wb") as temp_audio:
            temp_audio.write(file.file.read())

        print(f"📂 File được tải lên: {file.filename}")
        result = model.transcribe(file_path, language="vi")  # Nhận diện tiếng Việt
        return {"text": result["text"]}

    except Exception as e:
        return {"error": f"Lỗi xử lý file: {e}"}

# Chạy ghi âm khi chạy script
if __name__ == "__main__":
    file_path = record_audio(duration=10)  # Ghi âm trong 10 giây
    if file_path:
        print("📝 Đang nhận diện giọng nói (Tiếng Việt)...")
        result = model.transcribe(file_path, language="vi")
        print(f"📜 Kết quả: {result['text']}")
    else:
        print("❌ Ghi âm thất bại!")
