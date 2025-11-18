import json
import os
from Board import Board
from Board_GUI import GameGUI
import tkinter as tk

COLOR_MAP = {
    1: "yellow",
    2: "red",
    3: "blue",
    4: "orange",
    5: "green",
    6: "purple",
    7: "cyan"
}
def shift_coord(r, c, rows_old, cols_old):
    """
    يقوم بتحويل إحداثي (r, c) من الشبكة القديمة (11x8) إلى الشبكة الجديدة (9x6).
    """
    rows_new = rows_old - 2 
    cols_new = cols_old - 2 
    
    if r == 0:
        r_new = 0 
    elif r == rows_old - 1: 
        r_new = rows_new - 1 # ينتقل إلى الصف 8 (على الحدود الجديدة)
    else:
        r_new = r - 1 # الصفوف الداخلية (1-9) تطرح 1 (تصبح 0-8)

    # 2. Column shift
    if c == 0:
        c_new = 0 # العمود 0 يبقى 0
    elif c == cols_old - 1: # العمود 7
        c_new = cols_new - 1 # ينتقل إلى العمود 5
    else:
        c_new = c - 1 # الأعمدة الداخلية (1-6) تطرح 1 (تصبح 0-5)
        
    return [r_new, c_new]

def classify_and_group_blocks(blocks, rows, cols):
    """
    يفصل الكتل إلى داخلية (static_elements) وحدودية (exit_gates - walls).
    ويجمع الكتل الحدودية المتجاورة في مجموعات.
    """
    internal_blocks = []
    boundary_blocks_map = {"Top": [], "Bottom": [], "Left": [], "Right": []}
    
    for r, c in blocks:
        is_boundary = r == 0 or r == rows - 1 or c == 0 or c == cols - 1
        
        if not is_boundary:
            internal_blocks.append([r, c])
        else:
            # تصنيف الكتل الحدودية حسب الجانب
            if r == 0:
                boundary_blocks_map["Top"].append([r, c])
            if r == rows - 1:
                boundary_blocks_map["Bottom"].append([r, c])
            if c == 0:
                boundary_blocks_map["Left"].append([r, c])
            if c == cols - 1:
                boundary_blocks_map["Right"].append([r, c])
    
    grouped_walls = []
    
    for side in ["Top", "Bottom"]:
        if boundary_blocks_map[side]:
            boundary_blocks_map[side].sort(key=lambda x: x[1])
            current_group = []
            
            for r, c in boundary_blocks_map[side]:
                if not current_group:
                    current_group.append([r, c])
                else:
                    last_r, last_c = current_group[-1]
                    if abs(c - last_c) == 1 and r == last_r:
                        current_group.append([r, c])
                    else:
                        grouped_walls.append({"side": side, "coords": current_group})
                        current_group = [[r, c]]
            if current_group:
                 grouped_walls.append({"side": side, "coords": current_group})

    for side in ["Left", "Right"]:
        if boundary_blocks_map[side]:
            boundary_blocks_map[side].sort(key=lambda x: x[0])
            current_group = []
            
            for r, c in boundary_blocks_map[side]:
                if not current_group:
                    current_group.append([r, c])
                else:
                    last_r, last_c = current_group[-1]
                    # إذا كان تجاور في الصف (تجنب تكرار الكتل المائلة/الزاوية)
                    if abs(r - last_r) == 1 and c == last_c:
                        current_group.append([r, c])
                    else:
                        # بداية مقطع حائط جديد
                        grouped_walls.append({"side": side, "coords": current_group})
                        current_group = [[r, c]]
            if current_group:
                 grouped_walls.append({"side": side, "coords": current_group})

    return internal_blocks, grouped_walls

def convert_field_to_input2(field_data):
    """
    يقوم بتحويل هيكلية بيانات لوحة اللعبة من field.json إلى الهيكلية المطلوبة (9x6).
    """
    
    rows_old = field_data["rows"] # 11
    cols_old = field_data["cols"] # 8
    rows_new = rows_old - 2      # 9
    cols_new = cols_old - 2      # 6
    
    output_data = {
        "level_name": "Converted_Level_9x6",
        "board_settings": {
            "rows": rows_new,
            "cols": cols_new,
            "exit_gates": []
        },
        "static_elements": [],
        "blocks": []
    }
    
    # 3. معالجة العناصر الثابتة (field_data["blocks"]) وتقسيمها إلى داخلية وحدودية
    internal_blocks = []
    boundary_blocks = [] # هذه ستصبح الجدران (Walls)
    
    for r, c in field_data.get("blocks", []):
        is_boundary = (r == 0 or r == rows_old - 1 or c == 0 or c == cols_old - 1)
        
        # يتم تحويل الإحداثي قبل تخزينه
        shifted_coord = shift_coord(r, c, rows_old, cols_old)
        
        if is_boundary:
            boundary_blocks.append(shifted_coord)
        else:
            internal_blocks.append(shifted_coord)

    # أ) إضافة الكتل الثابتة الداخلية إلى static_elements
    if internal_blocks:
        output_data["static_elements"].append({
            "occupying_coords": internal_blocks
        })

    # 4. معالجة الكتل المتحركة (field_data["shapes"] -> blocks)
    block_id_counter = 1
    for shape in field_data.get("shapes", []):
        color_num = shape["colors"]
        color_name = COLOR_MAP.get(color_num, "unknown")
        
        # تحويل جميع إحداثيات الكتل المتحركة
        shifted_coords = [shift_coord(r, c, rows_old, cols_old) for r, c in shape["coordinates"]]
        
        # تحديد الموقع الأولي وحساب الإزاحات بناءً على الإحداثيات المحولة
        min_row = min(r for r, c in shifted_coords)
        min_col = min(c for r, c in shifted_coords)
        
        shape_coords = [
            [r - min_row, c - min_col] 
            for r, c in shifted_coords
        ]
        
        block_entry = {
            "id": f"B{block_id_counter}",
            "color": color_name,
            "is_target": False,
            "start_row": min_row,
            "start_col": min_col,
            "shape_coords": shape_coords
        }
        
        if "direction" in shape:
             block_entry["direction"] = shape["direction"]

        output_data["blocks"].append(block_entry)
        block_id_counter += 1


    # 5. معالجة بوابات الخروج الملونة (field_data["exists"] -> exit_gates - is_wall: False)
    exit_id_counter = 1
    for exit_info in field_data.get("exists", []):
        color_num = exit_info["color"]
        color_name = COLOR_MAP.get(color_num, "unknown")
        
        # تحويل إحداثيات الاتصال
        shifted_coords = [shift_coord(r, c, rows_old, cols_old) for r, c in exit_info["coordinates"]]
        
        # استنتاج الجانب (Side) باستخدام الأبعاد الجديدة
        side = "Unknown"
        if all(r == 0 for r, c in shifted_coords):
            side = "Top"
        elif all(r == rows_new - 1 for r, c in shifted_coords):
            side = "Bottom"
        elif all(c == 0 for r, c in shifted_coords):
            side = "Left"
        elif all(c == cols_new - 1 for r, c in shifted_coords):
            side = "Right"
        
        length = len(shifted_coords)
        
        output_data["board_settings"]["exit_gates"].append({
            "id": f"E{exit_id_counter}",
            "side": side,
            "contact_coords": shifted_coords,
            "is_wall": False,
            "required_color": color_name,
            "required_length": length
        })
        exit_id_counter += 1
        
    # 6. إضافة الجدران الثابتة الحدودية (من field_data["blocks"])
    wall_id_counter = 1
    grouped_walls = []
    processed_coords = set()
    
    # تجميع الكتل المتجاورة بعد التحويل (boundary_blocks)
    for r, c in boundary_blocks:
        if (r, c) in processed_coords:
            continue
            
        current_group = [[r, c]]
        processed_coords.add((r, c))
        
        # تحديد الجانب
        side = "Unknown"
        if r == 0: side = "Top"
        elif r == rows_new - 1: side = "Bottom"
        elif c == 0: side = "Left"
        elif c == cols_new - 1: side = "Right"
        
        # البحث عن الكتل المجاورة (التجميع أفقيًا أو عموديًا)
        if side in ["Top", "Bottom"]:
            for neighbor_c in range(c + 1, cols_new):
                if [r, neighbor_c] in boundary_blocks and (r, neighbor_c) not in processed_coords:
                    current_group.append([r, neighbor_c])
                    processed_coords.add((r, neighbor_c))
                else:
                    break
        elif side in ["Left", "Right"]:
            for neighbor_r in range(r + 1, rows_new):
                if [neighbor_r, c] in boundary_blocks and (neighbor_r, c) not in processed_coords:
                    current_group.append([neighbor_r, c])
                    processed_coords.add((neighbor_r, c))
                else:
                    break
                    
        if current_group:
            grouped_walls.append({"side": side, "coords": current_group})

    for wall in grouped_walls:
        output_data["board_settings"]["exit_gates"].append({
            "id": f"W{wall_id_counter}",
            "side": wall["side"],
            "contact_coords": wall["coords"],
            "is_wall": True, 
            "required_color": "black", 
            "required_length": len(wall["coords"])
        })
        wall_id_counter += 1
        
    return output_data

def process_files(input_filename="field.json", output_filename="output_input2.json"):
    """
    التابع الرئيسي للقراءة والتحويل والكتابة.
    """
    
    # 1. القراءة من ملف الإدخال
    try:
        # قراءة محتوى field.json الذي تم تحميله
        with open(input_filename, 'r', encoding='utf-8') as f:
            field_data = json.load(f)
        print(f"✅ تم قراءة بيانات المصدر بنجاح من: {input_filename}")
    except FileNotFoundError:
        print(f"❌ خطأ: ملف الإدخال '{input_filename}' غير موجود.")
        return None
    except json.JSONDecodeError:
        print(f"❌ خطأ: تنسيق JSON غير صحيح في الملف '{input_filename}'.")
        return None
    
    # 2. التحويل
    print("⏳ جاري تحويل البيانات...")
    transformed_data = convert_field_to_input2(field_data)
    
    # 3. الكتابة إلى ملف الإخراج
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            # استخدام indent=4 لتنسيق ملف JSON وجعله مقروءاً
            json.dump(transformed_data, f, indent=4)
        print(f"✅ تم تحويل وكتابة البيانات بنجاح إلى: {output_filename}")
        print("-" * 30)
        return transformed_data
    except Exception as e:
        print(f"❌ حدث خطأ أثناء كتابة الملف: {e}")
        return None

def load_data(file_path):
    """
    يقوم بتحميل البيانات من ملف JSON للتأكد من صحتها.
    """

    if not os.path.exists(file_path):
        print(f"🛑 خطأ: لم يتم العثور على الملف في المسار المحدد: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data_map = json.load(f)
            
        return data_map

    except json.JSONDecodeError as e:
        print(f"❌ خطأ في فك ترميز ملف JSON (تأكد من سلامة التنسيق): {e}")
        return None
    except Exception as e:
        print(f"🚫 حدث خطأ غير متوقع أثناء القراءة: {e}")
        return None

# --- تنفيذ التابع ---
if __name__ == "__main__":
    
    # الخطوة 1: تشغيل عملية التحويل لإنشاء output_input2.json
    print("--- بدء عملية التحويل ---")
    transformed_data = process_files(input_filename="field.json", output_filename="output_input2.json")
    
    # الخطوة 2: تحميل البيانات من الملف الناتج وتشغيل اللوحة (المنطق المطلوب من المستخدم)
    if transformed_data is not None:
        file_path = "output_input2.json"
        
        print(f"--- اختبار قراءة الملف الجديد: {file_path} ---")
        data = load_data(file_path)

        if data is not None:
            # تم تحميل البيانات بنجاح. جاري محاولة تشغيل لوحة اللعبة.
            print(f"✅ تم تحميل بيانات اللوحة بنجاح من: {file_path}. جاري محاولة بناء اللوحة...")

            # المنطق المطلوب من المستخدم (يجب تفعيله محلياً):
            game_board = Board(data)
            game_board.display_grid()
            root = tk.Tk()
            app = GameGUI(root, game_board)
            root.mainloop()
            
        else:
            print("❌ فشل تحميل البيانات، لن يتم بناء اللوحة.")