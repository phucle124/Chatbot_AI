import os
import time
import json
import pandas as pd
import whisper
import pyaudio
import wave
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import FastAPI, File, UploadFile

# ================== AUTO RENDER EXCEL TO JSON ===================
excel_file = 'dataset.xlsx'
json_file = 'dataset.json'

class ExcelChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(excel_file):
            print(f'{excel_file} đã thay đổi. Đang cập nhật {json_file}...')
            excel_to_json()

def excel_to_json():
    df = pd.read_excel(excel_file)
    json_data = []
    for _, row in df.iterrows():
        json_data.append({
            "language": str(row['Ngôn ngữ']),
            "course_name": str(row['Tên khóa học']),
            "application": str(row['Ứng dụng'])
        })
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f'Cập nhật {json_file} thành công!')

# ================== DATASET SEARCH FUNCTION ===================
def search_answer(user_text):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        return "Dataset chưa được tạo, vui lòng kiểm tra!"
    
    for entry in dataset:
        if entry['course_name'].lower() in user_text.lower():
            return f"Khóa học: {entry['course_name']}\nỨng dụng: {entry['application']}"
    return "Không tìm thấy khóa học phù hợp trong dataset!"

# ================== CHATBOT & VOICE ===================
app = FastAPI()
os.environ["PATH"] += r";D:\Python\ffmpeg-2025-03-10-git-87e5da9067-full_build\bin"

try:
    model = whisper.load_model("large")
    print("✅ Model Whisper đã tải xong!")
except Exception as e:
    print(f"Lỗi khi tải model: {e}")
    model = None

@app.get("/health")
def health_check():
    return {"status": "API is running"}

def record_audio(filename="D:\\Python\\record\\Uservoice.wav", duration=5, samplerate=16000):
    try:
        print("🎤 Đang ghi âm...")
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=samplerate, input=True, frames_per_buffer=1024)
        frames = [stream.read(1024) for _ in range(0, int(samplerate / 1024 * duration))]
        stream.stop_stream()
        stream.close()
        p.terminate()

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

@app.get("/listen")
def listen():
    if model is None:
        return {"error": "Model Whisper chưa sẵn sàng!"}

    file_path = record_audio()
    if file_path is None:
        return {"error": "Không thể ghi âm, vui lòng kiểm tra micro!"}

    print("📝 Đang nhận diện giọng nói...")
    result = model.transcribe(file_path, language="vi")
    recognized_text = result["text"].strip()

    if len(recognized_text) < 5:
        return {"error": "Âm thanh không rõ, vui lòng thử lại hoặc tải file lên!"}

    answer = search_answer(recognized_text)
    return {"recognized_text": recognized_text, "answer": answer}

# @app.post("/transcribe")
# def transcribe(file: UploadFile = File(...)):
#     if model is None:
#         return {"error": "Model Whisper chưa sẵn sàng!"}

#     try:
#         file_path = "D:\\Python\\record\\Uservoice.wav"
#         with open(file_path, "wb") as temp_audio:
#             temp_audio.write(file.file.read())

#         print(f"📂 File được tải lên: {file.filename}")
#         result = model.transcribe(file_path, language="vi")
#         return {"text": result["text"]}
#     except Exception as e:
#         return {"error": f"Lỗi xử lý file: {e}"}

# ... các hàm khác ...

def transcribe_audio(file_path):
    if model is None:
        print("❌ Model Whisper chưa sẵn sàng!")
        return None
    try:
        print("🎧 Đang nhận diện giọng nói từ file audio...")
        result = model.transcribe(file_path, language="vi")
        recognized_text = result["text"].strip()
        print(f"📝 Văn bản nhận diện: {recognized_text}")
        return recognized_text
    except Exception as e:
        print(f"❌ Lỗi transcribe: {e}")
        return None


# ================= ChatBot response ===============
def chatbot_response(user_input):
    with open('dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Tách từ khóa tìm kiếm trong user_input
    keywords = ["python", "java", "html", "javascript", "nodejs"]  # bổ sung thêm khóa học
    user_input_lower = user_input.lower()

    for keyword in keywords:
        if keyword in user_input_lower:
            for item in dataset:
                if keyword.lower() in item['course_name'].lower():
                    return f"💡 {item['application']}"
            return "❌ Xin lỗi, tôi không tìm thấy thông tin bạn cần!"
    return "❌ Xin lỗi, tôi không tìm thấy khóa học bạn nói đến!"


if __name__ == "__main__":
    excel_to_json()

    # Theo dõi dataset.xlsx
    event_handler = ExcelChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    print("🚀 Đang chạy hệ thống! Theo dõi dataset.xlsx...")

    # Đọc file âm thanh và xử lý
    audio_path = "D:\\Python\\record\\Uservoice.wav"
    user_text = transcribe_audio(audio_path)

    if user_text:
        response = chatbot_response(user_text)
        print(response)

    observer.stop()
    observer.join()


