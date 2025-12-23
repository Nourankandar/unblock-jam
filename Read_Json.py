import json
import os
from Board import Board
from Board_GUI import GameGUI
import tkinter as tk
def load_data(file_path):

    if not os.path.exists(file_path):
        print(f" خطأ: لم يتم العثور على الملف في المسار المحدد: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data_map = json.load(f)
            
        return data_map

    except json.JSONDecodeError as e:
        print(f" خطأ في فك ترميز ملف JSON (تأكد من سلامة التنسيق): {e}")
        return None
    except Exception as e:
        print(f" حدث خطأ غير متوقع أثناء القراءة: {e}")
        return None

file_path="output_input2.json"
data=load_data(file_path)

if data is not None:
    game_board = Board(data)
    game_board.display_grid()
    root = tk.Tk()
    app = GameGUI(root, game_board)
    root.mainloop()
    
else:
    print(" فشل تحميل البيانات، لن يتم بناء اللوحة.")