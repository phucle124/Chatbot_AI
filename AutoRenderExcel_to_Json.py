import time
import pandas as pd
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

if __name__ == "__main__":
    excel_to_json()  # Chạy lần đầu
    event_handler = ExcelChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    print("Đang theo dõi thay đổi...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
