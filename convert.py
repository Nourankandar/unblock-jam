import json
import os
# يجب أن تكون أصناف Board و GameGUI و tkinter متاحة محلياً لتشغيل الجزء السفلي من الكود
from Board import Board 
from Board_GUI import GameGUI
import tkinter as tk

# ____هاد الملف لتحويل ملف جسون من للشكل الموجود عندي وهو من gemini مو انا عملته 

# خريطة الألوان
COLOR_MAP = {
    1: "yellow", 2: "red", 3: "blue", 4: "orange",
    5: "green", 6: "purple", 7: "cyan"
}

def shift_coord(r, c, rows_old, cols_old):
    """يعيد الإحداثي (r, c) كما هو للحفاظ على أبعاد 11x8. (تابع مؤقت غير مُستخدم فعلياً هنا)."""
    return [r, c]
def clean_convert_level(field_data):
    """يقوم بتحويل هيكلية البيانات (11x8) من field.json إلى تنسيق output_input3.json."""
    
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
        shifted_coords = shape["coordinates"] 
        
        # تحديد الموضع الأولي (start_row, start_col)
        min_row = min(r for r, c in shifted_coords)
        min_col = min(c for r, c in shifted_coords)
        
        # حساب إحداثيات الشكل النسبية (shape_coords)
        shape_coords = [[r - min_row, c - min_col] for r, c in shifted_coords]
        
        block_entry = {
            "id": f"B{block_id_counter}", 
            "color": color_name, 
            "is_target": shape.get("is_target", False), 
            "start_row": min_row, 
            "start_col": min_col, 
            "shape_coords": shape_coords
        }
        
        # إضافة الخاصيات الإضافية (direction و move_lock) إن وجدت
        if "direction" in shape:
             block_entry["direction"] = shape["direction"]
        
        if "move_lock" in shape:
             block_entry["moves_to_unlock"] = shape["move_lock"] # ✅ تم التصحيح

        output_data["blocks"].append(block_entry)
        block_id_counter += 1

    # 2. معالجة بوابات الخروج الملونة (exists -> exit_gates)
    exit_id_counter = 1
    for exit_info in field_data.get("exists", []):
        color_name = COLOR_MAP.get(exit_info["color"], "unknown")
        contact_coords = exit_info["coordinates"]
        
        side = "Unknown"
        # تحديد الجانب (Side)
        if all(r == 0 for r, c in contact_coords): side = "Top"
        elif all(r == rows_new - 1 for r, c in contact_coords): side = "Bottom"
        elif all(c == 0 and r not in [0, rows_new - 1] for r, c in contact_coords): side = "Left"
        elif all(c == cols_new - 1 and r not in [0, rows_new - 1] for r, c in contact_coords): side = "Right"
        
        output_data["board_settings"]["exit_gates"].append({
            "id": f"E{exit_id_counter}", 
            "side": side, 
            "contact_coords": contact_coords,
            # ❌ تم حذف خاصية "is_wall" بناءً على طلبك
            "required_color": color_name, 
            "required_length": len(contact_coords)
        })
        exit_id_counter += 1
        
    # 3. معالجة الكتل الثابتة (blocks -> static_elements فقط)
    
    # ✅ التصحيح: يتم دمج جميع الإحداثيات الثابتة (الداخلية والمحيطية/الجدران) في قائمة واحدة
    all_static_coords = field_data.get("blocks", [])

    # إضافة العناصر الثابتة المدمجة (الجدران + الداخلية)
    if all_static_coords:
        output_data["static_elements"].append({"occupying_coords": all_static_coords})
        
    # 🚫 تم إلغاء منطق تجميع الجدران المحيطية في exit_gates

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

def process_files(input_filename, output_filename):
    """
    التابع الرئيسي: يقرأ field.json، يحوّل البيانات، ويكتبها overwrite على output_input3.json.
    """
    
    # 1. القراءة من ملف الإدخال 
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
    transformed_data = process_files(input_filename="field-1.1.json", output_filename="output_input3.json")
    
    # الخطوة 2: تحميل البيانات من الملف الناتج وتشغيل اللوحة (Read output_input3.json)
    if transformed_data is not None:
        file_path = "output_input3.json"
        
        # القراءة الفعلية للملف المكتوب حديثًا (للتأكد من سلامة الملف)
        data = load_data(file_path)

        if data is not None:
            print(f"✅ 3. تم تحميل بيانات اللوحة بنجاح من: {file_path}. جاري محاولة بناء اللوحة...")

            # المنطق المطلوب من المستخدم (يجب إزالة التعليق عنه ليعمل محلياً):
            # ملاحظة: يجب أن تكون أصناف Board و GameGUI متوفرة
            try:
                game_board = Board(data)
                game_board.display_grid()
                root = tk.Tk()
                app = GameGUI(root, game_board)
                root.mainloop()
            except NameError:
                 print("⚠️ تحذير: لم يتم العثور على أصناف Board أو GameGUI أو tk.Tk. (يجب توفيرها لتشغيل اللعبة).")
            
        else:
            print("❌ فشل تحميل البيانات من الملف المكتوب، لن يتم بناء اللوحة. (تحقق من سلامة ملف output_input3.json)")