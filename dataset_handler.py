import pandas as pd

# Load dataset
dataset = pd.read_excel('D:\\Python\\dataset.xlsx')

def search_answer(question_text):
    question_text = question_text.lower()
    
    for _, row in dataset.iterrows():
        course_name = str(row['Tên khóa học']).lower()
        language = str(row['Ngôn ngữ']).lower()
        description = str(row['Mô tả']).lower()
        
        # So khớp nếu từ khóa xuất hiện trong tên khóa học, ngôn ngữ hoặc mô tả
        if question_text in course_name or question_text in language or question_text in description:
            return f"Mô tả: {row['Mô tả']}\nỨng dụng: {row['Ứng dụng']}"
    
    return "Xin lỗi, tôi chưa có thông tin về câu hỏi này."