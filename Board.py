from Block import Block
from ExitGate import ExitGate
import copy
import time
import datetime

class Board:
    def __init__(self, data_map):
        self.rows = 0
        self.cols = 0
        self.Grid = []  
        self.BlockObjects = {} 
        self.StaticElements = set() 
        self.ExitGates = {} 

        
        
        self.initialize_board(data_map)
    def deep_copy(self):
        return copy.deepcopy(self)
    
    def initialize_board(self, data):
        """
        تقوم بتحويل بيانات JSON الخام إلى حالة اللعبة وكائنات تفاعلية.
        """
        settings = data['board_settings']
        self.rows = settings['rows']
        self.cols = settings['cols']
        self.Grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        print(f" Board is created {self.rows}x{self.cols}")
        #لتخزين البوابات ومعلوماتها الموجودة في ال json 
        for gate_data in settings['exit_gates']:
            gate = ExitGate(gate_data)
            self.ExitGates[gate.id] = gate
            gate_id_marker = "gate" 
            for r, c in gate.contact_coords:
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    if self.Grid[r][c] == 0: 
                        self.Grid[r][c] = gate_id_marker

        
        #هون لحتى نخزن العناصر الثابتة
        for element in data['static_elements']:
            for r_abs, c_abs in element['occupying_coords']:
                self.StaticElements.add((r_abs, c_abs))
                if 0 <= r_abs < self.rows and 0 <= c_abs < self.cols:
                    self.Grid[r_abs][c_abs] = 'W' 

        #يقوم بتوزيع المعبات في الرقعة 
        for block_data in data['blocks']:
            block = Block(block_data)
            self.BlockObjects[block.id] = block
            for r_abs, c_abs in block.get_absolute_coords():
                if 0 <= r_abs < self.rows and 0 <= c_abs < self.cols:
                    if self.Grid[r_abs][c_abs] == 'W':
                        print(f" خطأ في التصميم الأولي: الكتلة {block.id} تتداخل مع عنصر ثابت في الموقع ({r_abs}, {c_abs})")
                    elif self.Grid[r_abs][c_abs] != 0:
                        print(f" خطأ في التصميم الأولي: الكتلة {block.id} تتداخل مع كتلة أخرى في الموقع ({r_abs}, {c_abs})")
                    self.Grid[r_abs][c_abs] = block.id
                else:
                    print(f" خطأ في التصميم الأولي: الكتلة {block.id} تبدأ خارج حدود اللوحة.")
    
    def display_grid(self):
        print("\n--- حالة اللوحة الحالية (Grid) ---")
        for row in self.Grid:
            print("    |    ".join(map(str, row)))
        print("--------------------------------")

#------------------------------------------------------------------------------------------
#_________________________MOVES METHODS________________________________

    
    def check_gate_arround(self,block_id,block_obj=None):
        if block_obj is None:
            if block_id not in self.BlockObjects:
                return set()
            block = self.BlockObjects[block_id]
        else:
            block = block_obj

        arroud_coords_set = set(block.get_border_coords())
        print(arroud_coords_set) 
        gates_objects = set()
        
        for gate_obj in self.ExitGates.values():
            
            gate_contact_set = set(gate_obj.contact_coords) 
            if gate_contact_set.intersection(arroud_coords_set):
                gates_objects.add(gate_obj)
                            
                            
        return gates_objects 

    def check_ifCanBolckGetOutThisGate(self,block_id,gates_objects,final_coords=None):
        if block_id not in self.BlockObjects:
            return False
        block = self.BlockObjects[block_id]
        if final_coords is not None:
            print("hello final coords")
            source_coords = final_coords
        else:
            source_coords = block.get_absolute_coords()

        block_coords = set(source_coords)
        print("hello block")
        print(gates_objects)
        for gate in gates_objects:
            print("hello ")
            if block.color.lower() == gate.required_color.lower():
                
                is_fully_within_gate_range = True
                if gate.side == "Top" or gate.side == "Bottom":
                    all_c = [c for r, c in gate.contact_coords]
                    small_c = min(all_c) 
                    big_c = max(all_c)  
                    print(small_c,big_c,"this is gate col")
                    for r_abs, c_abs in block_coords:
                        if not (small_c <= c_abs <= big_c):
                            print(f"🛑 فشل التحقق: جزء ({r_abs}, {c_abs}) خارج نطاق الأعمدة {small_c}-{big_c}.")
                            is_fully_within_gate_range = False
                            break
                    
                elif gate.side == "Left" or gate.side == "Right":
                    all_r = [r for r, c in gate.contact_coords]
                    small_r = min(all_r) 
                    big_r = max(all_r) 
                    print(small_r,big_r,"this is gate row")  
                    for r_abs, c_abs in block_coords:
                        if not (small_r <= r_abs <= big_r):
                            print(f"🛑 فشل التحقق: جزء ({r_abs}, {c_abs}) خارج نطاق الصفوف {small_r}-{big_r}.")
                            is_fully_within_gate_range = False
                            break
                if is_fully_within_gate_range:
                    print(f"✅ تحقق الخروج بنجاح عبر البوابة {gate.id}.")
                    return True 

        return False
                
                    
    def calculate_coords(self, block, new_start_row, new_start_col):
        new_coords = []
        for r_rel, c_rel in block.shape_coords:
            r_abs = new_start_row + r_rel
            c_abs = new_start_col + c_rel
            new_coords.append((r_abs, c_abs))
        return new_coords
    

    def is_valid_position(self,block_id,new_coords):
        rows, cols = self.rows, self.cols

        for r_abs, c_abs in new_coords:
            if r_abs < 0 or r_abs >= rows or c_abs < 0 or c_abs >= cols:
                return False
            if (r_abs, c_abs) in self.StaticElements:
                return False
            cell_content = self.Grid[r_abs][c_abs]
            if cell_content == 'W':
                return False
            if cell_content !=0 and cell_content!= block_id:
                return False
                    
        return True
    
    def make_move(self, block_id, row_delta, col_delta):

        if block_id not in self.BlockObjects:
            return None
        
        old_block = self.BlockObjects[block_id]
        new_start_row = old_block.start_row + row_delta
        new_start_col = old_block.start_col + col_delta
        new_coords = self.calculate_coords(old_block, new_start_row, new_start_col)
        if old_block.direction == 'horizontal' and row_delta != 0:
            print(f"🛑 الحركة لـ {block_id} غير صالحة. الاتجاه مقيد أفقياً (Horizontal).")
            return None
            
        if old_block.direction == 'vertical' and col_delta != 0:
            print(f"🛑 الحركة لـ {block_id} غير صالحة. الاتجاه مقيد عمودياً (Vertical).")
            return None
        
        if not self.is_valid_position(block_id, new_coords):
            print(f"🛑 فشلت الحركة: اصطدام داخلي أو خروج غير مسموح به للكتلة {block_id}.")
            return None
    
        new_board = self.deep_copy()
        for r_abs, c_abs in old_block.get_absolute_coords():
            if 0 <= r_abs < new_board.rows and 0 <= c_abs < new_board.cols:
                if new_board.Grid[r_abs][c_abs] == block_id:
                    new_board.Grid[r_abs][c_abs] = 0

        
        new_block = new_board.BlockObjects[block_id]
        new_block.start_row = new_start_row
        new_block.start_col = new_start_col
        gates_arround = self.check_gate_arround(block_id,new_block) 
        is_exit = self.check_ifCanBolckGetOutThisGate(block_id,gates_arround, new_coords)
        
        
        if(is_exit):
            for r_abs, c_abs in new_coords:
                if 0 <= r_abs < new_board.rows and 0 <= c_abs < new_board.cols:
                    new_board.Grid[r_abs][c_abs] = block_id 
                
            return new_board,True
        else:
            for r_abs, c_abs in new_coords:
                if 0 <= r_abs < new_board.rows and 0 <= c_abs < new_board.cols:
                    new_board.Grid[r_abs][c_abs] = block_id 
                
            return new_board,False
    
    
    
    

    def is_final_state(self):
        return len(self.BlockObjects) == 0
        
    
    


    # توابع قديمة؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟؟
    #لاااااا اريدها الان
    #-------------------------------------------------------------------------

    def get_possible_moves(self, block_id):
        """
        يحدد جميع الحركات الصالحة الممكنة لكتلة معينة.
        (الكتل مسموح لها بالحركة في جميع الاتجاهات إذا كانت الشروط محققة).
        الناتج: قائمة من القفزات (final_row_delta, final_col_delta) الممكنة.
        """
        if block_id not in self.BlockObjects:
            return []
        
        block = self.BlockObjects[block_id]
        possible_moves = []
        
        # نحدد جميع الاتجاهات الأربعة الممكنة (خطوة واحدة في كل اتجاه)
        directions_to_check = [
            (0, 1),   # يمين
            (0, -1),  # يسار
            (1, 0),   # أسفل
            (-1, 0)   # أعلى
        ]
        
        for r_step, c_step in directions_to_check:
            
            # r_delta و c_delta هما مقدار الإزاحة الكلي عن موقع البداية
            r_delta, c_delta = r_step, c_step 
            
            # نبدأ من خطوة واحدة ونزيدها تدريجياً
            while True:
                new_start_row = block.start_row + r_delta
                new_start_col = block.start_col + c_delta
                new_coords = self.calculate_coords(block, new_start_row, new_start_col)

                # 1. فحص الاصطدام الداخلي
                if not self.is_valid_position(block_id, new_coords):
                    # فشلت الحركة بسبب اصطدام داخلي (كتلة أخرى/جدار ثابت)
                    break 

                # 2. فحص الحدود وتحديد المصير
                is_fully_inside = True
                
                # نتحقق مما إذا كانت أي إحداثية جديدة خارج حدود اللوحة
                for r_abs, c_abs in new_coords:
                    if not (0 <= r_abs < self.rows and 0 <= c_abs < self.cols):
                        is_fully_inside = False
                        break
                
                if is_fully_inside:
                    # الحركة صالحة وداخلية بالكامل، نضيفها ونفحص الخطوة التالية
                    possible_moves.append((r_delta, c_delta))
                    
                    # ننتقل للخطوة التالية في نفس الاتجاه
                    r_delta += r_step
                    c_delta += c_step
                
                else:
                    # محاولة خروج/تجاوز جزئي للحدود. يجب الآن تطبيق الشرط الصارم الذي اتفقنا عليه في apply_move
                    
                    # نتحقق مما إذا كانت هذه الحركة هي خروج كامل عبر بوابة مسموح بها.
                    if self.check_for_exit(block_id, new_coords):
                        # الخروج مسموح به، نضيفه وننهي
                        possible_moves.append((r_delta, c_delta))
                    
                    # في كلتا الحالتين (خروج ناجح أو محاولة تجاوز جزئي مرفوضة)، نتوقف عن الفحص
                    # لأن المنطق الذي وضعناه في apply_move يرفض أي تجاوز جزئي غير مصرح به للخروج.
                    break
                    
        return possible_moves
    
    def apply_move(self, block_id, final_row_delta, final_col_delta):
        """
        [مُحدِّث الحالة] يطبق الحركة النهائية على اللوحة بعد التأكد من صلاحيتها.
        المدخلات: مقدار التغير النهائي في الصفوف (final_row_delta) والأعمدة (final_col_delta).
        """
        if block_id not in self.BlockObjects:
            print(f"🛑 خطأ: لم يتم العثور على الكتلة بالمعرف {block_id}.")
            return False

        block = self.BlockObjects[block_id]
        
        new_start_row = block.start_row + final_row_delta
        new_start_col = block.start_col + final_col_delta
        new_coords = self.calculate_coords(block, new_start_row, new_start_col)

        if not self.is_valid_position(block_id, new_coords):
            print(f"🛑 فشلت الحركة: اصطدام داخلي (كتلة/جدار ثابت) للكتلة {block_id}.")
            return False
        
        is_touching_boundary = False
        is_fully_inside = True
        
        for r_abs, c_abs in new_coords:
            if r_abs < -1 or r_abs >= self.rows + 1 or c_abs < -1 or c_abs >= self.cols + 1:
                print(f"🛑 فشلت الحركة: الحركة مفرطة للكتلة {block_id}.")
                return False
            
            if not (0 <= r_abs < self.rows and 0 <= c_abs < self.cols):
                is_fully_inside = False

            if r_abs < 0 or r_abs >= self.rows or c_abs < 0 or c_abs >= self.cols:
                    is_touching_boundary = True
        old_coords = block.get_absolute_coords()
        
        if is_touching_boundary:
            if self.check_for_exit(block_id, new_coords):
                is_exit = True
                print(f"🎉 خرجت الكتلة {block_id} بنجاح من اللوحة!")
            else:
                print(f"🛑 فشلت الحركة: محاولة خروج غير مطابقة للشروط للكتلة {block_id}.")
                return False 
        else:
            is_exit = False
            print(f"✅ تحركت الكتلة {block_id} إلى ({new_start_row}, {new_start_col})")
        
        for r_abs, c_abs in old_coords:
            if 0 <= r_abs < self.rows and 0 <= c_abs < self.cols:
                if self.Grid[r_abs][c_abs] == block_id:
                     self.Grid[r_abs][c_abs] = 0
        if not is_exit:
            block.start_row = new_start_row
            block.start_col = new_start_col
            
            for r_abs, c_abs in new_coords:
                if 0 <= r_abs < self.rows and 0 <= c_abs < self.cols:
                    self.Grid[r_abs][c_abs] = block_id
        else:
            del self.BlockObjects[block_id]

        return True
    
    def check_proximity_to_gates(self, block_id):
        """
        يتحقق مما إذا كانت أي خلية من خلايا الكتلة تقع في الصفوف/الأعمدة المجاورة 
        للحدود مباشرة (على بعد خلية واحدة من البوابة) - منطق التقاطع.
        """
        if block_id not in self.BlockObjects:
            return False
            
        block = self.BlockObjects[block_id]
        block_coords = block.get_absolute_coords()
        rows = self.rows
        cols = self.cols
        proximal_rows = {1, rows - 2}
        proximal_cols = {1, cols - 2}
        
        for r_abs, c_abs in block_coords:
            
            if not (0 <= r_abs < rows and 0 <= c_abs < cols):
                continue
            if r_abs in proximal_rows:
                return True
            if c_abs in proximal_cols:
                return True
       
        return False    
    
    
