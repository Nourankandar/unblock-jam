import json
import os
from Board import Board 
from Board_GUI import GameGUI
import tkinter as tk

#____هاد الملف لتحويل ملف جسون من للشكل الموجود عندي وهو من gemini مو انا عملته 

# خريطة الألوان
COLOR_MAP = {
    1: "yellow", 2: "red", 3: "blue", 4: "orange",
    5: "green", 6: "purple", 7: "cyan"
}

def shift_coord(r, c, rows_old, cols_old):
    """يعيد الإحداثي (r, c) كما هو للحفاظ على أبعاد 11x8."""
    return [r, c]

def clean_convert_level(field_data):
    """يقوم بتحويل هيكلية البيانات (11x8) مع الاحتفاظ بالأبعاد."""
    
    rows_new = field_data.get("rows", 11)  # 11
    cols_new = field_data.get("cols", 8)   # 8
    
    output_data = {
        "level_name": "New_Converted_Level_11x8",
        "board_settings": {"rows": rows_new, "cols": cols_new, "exit_gates": []},
        "static_elements": [],
        "blocks": []
    }
    
    # 1. معالجة الكتل المتحركة (shapes -> blocks)
    block_id_counter = 1
    for shape in field_data.get("shapes", []):
        color_name = COLOR_MAP.get(shape["colors"], "unknown")
        shifted_coords = [shift_coord(r, c, rows_new, cols_new) for r, c in shape["coordinates"]]
        
        min_row = min(r for r, c in shifted_coords)
        min_col = min(c for r, c in shifted_coords)
        shape_coords = [[r - min_row, c - min_col] for r, c in shifted_coords]
        
        block_entry = {
            "id": f"B{block_id_counter}", "color": color_name, "is_target": False,
            "start_row": min_row, "start_col": min_col, "shape_coords": shape_coords
        }
        if "direction" in shape:
             block_entry["direction"] = shape["direction"]

        output_data["blocks"].append(block_entry)
        block_id_counter += 1

    # 2. معالجة بوابات الخروج الملونة (exists -> exit_gates, is_wall: False)
    exit_id_counter = 1
    for exit_info in field_data.get("exists", []):
        color_name = COLOR_MAP.get(exit_info["color"], "unknown")
        shifted_coords = [shift_coord(r, c, rows_new, cols_new) for r, c in exit_info["coordinates"]]
        
        side = "Unknown"
        if all(r == 0 for r, c in shifted_coords): side = "Top"
        elif all(r == rows_new - 1 for r, c in shifted_coords): side = "Bottom"
        elif all(c == 0 for r, c in shifted_coords): side = "Left"
        elif all(c == cols_new - 1 for r, c in shifted_coords): side = "Right"
        
        output_data["board_settings"]["exit_gates"].append({
            "id": f"E{exit_id_counter}", "side": side, "contact_coords": shifted_coords,
            "is_wall": False, "required_color": color_name, "required_length": len(shifted_coords)
        })
        exit_id_counter += 1
        
    # 3. معالجة الكتل الثابتة (blocks -> static_elements & Walls)
    all_blocks_old = field_data.get("blocks", [])
    shifted_blocks = [shift_coord(r, c, rows_new, cols_new) for r, c in all_blocks_old]
    
    internal_blocks = []
    boundary_map = {"Top": [], "Bottom": [], "Left": [], "Right": []}
    
    for r, c in shifted_blocks:
        is_boundary = (r == 0 or r == rows_new - 1 or c == 0 or c == cols_new - 1)
        
        if not is_boundary:
            internal_blocks.append([r, c])
        else:
            if r == 0: boundary_map["Top"].append([r, c])
            if r == rows_new - 1: boundary_map["Bottom"].append([r, c])
            if c == 0 and r not in [0, rows_new - 1]: boundary_map["Left"].append([r, c])
            if c == cols_new - 1 and r not in [0, rows_new - 1]: boundary_map["Right"].append([r, c])

    if internal_blocks:
        output_data["static_elements"].append({"occupying_coords": internal_blocks})
        
    # تجميع الجدران المتجاورة
    grouped_walls = []
    for side, coords in boundary_map.items():
        if not coords: continue
        
        axis_index = 1 if side in ["Top", "Bottom"] else 0
        coords.sort(key=lambda x: x[axis_index])
        
        current_group = []
        for coord in coords:
            if not current_group or coord[axis_index] == current_group[-1][axis_index] + 1:
                current_group.append(coord)
            else:
                grouped_walls.append({"side": side, "coords": current_group})
                current_group = [coord]
        if current_group:
            grouped_walls.append({"side": side, "coords": current_group})

    wall_id_counter = 1
    SIDE_ORDER = {"Top": 0, "Left": 1, "Bottom": 2, "Right": 3}
    grouped_walls.sort(key=lambda w: SIDE_ORDER[w['side']])
    
    for wall in grouped_walls:
        output_data["board_settings"]["exit_gates"].append({
            "id": f"W{wall_id_counter}", "side": wall["side"], "contact_coords": wall["coords"],
            "is_wall": True, "required_color": "black", "required_length": len(wall["coords"])
        })
        wall_id_counter += 1
        
    return output_data

# -----------------------------------------------------------------------------

def load_data(file_path):
    """
    يقوم بتحميل بيانات JSON من مسار ملف محدد.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ خطأ: لم يتم العثور على الملف '{file_path}'.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في تنسيق JSON في الملف '{file_path}': {e}")
        return None
    except Exception as e:
        print(f"🚫 خطأ غير متوقع أثناء القراءة: {e}")
        return None

def process_files(input_filename="field.json", output_filename="output_input3.json"):
    """
    التابع الرئيسي: يقرأ field.json، يحوّل البيانات، ويكتبها overwrite على output_input3.json.
    """
    
    # 1. القراءة من ملف الإدخال (الآن تقرأ الملف الفعلي)
    field_data = None
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            field_data = json.load(f)
        print(f"✅ 1. تم قراءة بيانات المصدر المحدّثة بنجاح من: {input_filename}")
    except FileNotFoundError:
        print(f"❌ خطأ: ملف الإدخال '{input_filename}' غير موجود. تأكد من وضعه في نفس مجلد الكود.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ خطأ: تنسيق JSON غير صحيح في الملف '{input_filename}': {e}")
        return None
    
    # 2. التحويل
    transformed_data = clean_convert_level(field_data)
    
    # 3. الكتابة إلى ملف الإخراج (Overwriting)
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
             json.dump(transformed_data, f, indent=4)
        print(f"✅ 2. تم تحويل وكتابة البيانات بنجاح، وتحديث (Overwrite) لـ {output_filename}")
        print("-" * 30)
        return transformed_data
    except Exception as e:
        print(f"❌ خطأ أثناء الكتابة على {output_filename}: {e}")
        return None
        
# --- تنفيذ التابع ---
if __name__ == "__main__":
    
    # الخطوة 1: تشغيل عملية التحويل لإنشاء/تحديث output_input3.json (Read field.json -> Write output_input3.json)
    print("--- بدء عملية التحويل ---")
    transformed_data = process_files(input_filename="field.json", output_filename="output_input3.json")
    
    # الخطوة 2: تحميل البيانات من الملف الناتج وتشغيل اللوحة (Read output_input3.json)
    if transformed_data is not None:
        file_path = "output_input3.json"
        
        # print(f"--- اختبار قراءة الملف الجديد: {file_path} ---")
        
        # القراءة الفعلية للملف المكتوب حديثًا (للتأكد من سلامة الملف)
        data = load_data(file_path)

        if data is not None:
            print(f"✅ 3. تم تحميل بيانات اللوحة بنجاح من: {file_path}. جاري محاولة بناء اللوحة...")

            # المنطق المطلوب من المستخدم (يجب إزالة التعليق عنه ليعمل محلياً):
            game_board = Board(data)
            game_board.display_grid()
            root = tk.Tk()
            app = GameGUI(root, game_board)
            root.mainloop()
            
            # عرض البيانات (للتأكد من التحديث)
            # print("\n--- بيانات الإخراج المُحوَّلة والمُعاد قراءتها ---")
            # print(json.dumps(data, indent=4)) 
            # print("-------------------------------------------------")
            
        else:
            print("❌ فشل تحميل البيانات من الملف المكتوب، لن يتم بناء اللوحة. (تحقق من سلامة ملف output_input3.json)")