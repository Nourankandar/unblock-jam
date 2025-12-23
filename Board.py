from itertools import count
# from numpy import block
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
    
    def fast_copy(self):
        # إنشاء كائن جديد بدون استدعاء __init__ بالكامل لتوفير الوقت
        new_board = Board.__new__(Board)
        new_board.rows = self.rows
        new_board.cols = self.cols
        # نسخ المصفوفة (الشبكة) بسرعة
        new_board.Grid = [row[:] for row in self.Grid]
        # نسخ الكتل - نقوم بنسخ القاموس ولكن الكتل نفسها يتم نسخها يدوياً
        new_board.BlockObjects = {k: copy.copy(v) for k, v in self.BlockObjects.items()}
        new_board.StaticElements = self.StaticElements # عادة لا تتغير
        new_board.ExitGates = self.ExitGates # عادة لا تتغير
        return new_board
    
    def initialize_board(self, data):
        settings = data['board_settings']
        self.rows = settings['rows']
        self.cols = settings['cols']
        #بيعمل المصفوفة صفيرة
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
            block = Block(block_data,settings['rows'],settings['cols'])
            self.BlockObjects[block.id] = block

            for r_abs, c_abs in block.get_absolute_coords():
                if block.direction == "horizontal":
                    marker = '--'
                elif block.direction == "vertical":
                    marker = '|'
                else:
                    marker = block.id 
                if 0 <= r_abs < self.rows and 0 <= c_abs < self.cols:
                    
                    if self.Grid[r_abs][c_abs] == 'W':
                        print(f" خطأ في التصميم الأولي: الكتلة {block.id} تتداخل مع عنصر ثابت في الموقع ({r_abs}, {c_abs})")
                    elif self.Grid[r_abs][c_abs] != 0:
                        print(f" خطأ في التصميم الأولي: الكتلة {block.id} تتداخل مع كتلة أخرى في الموقع ({r_abs}, {c_abs})")
                    self.Grid[r_abs][c_abs] = block.id
                else:
                    print(f" خطأ في التصميم الأولي: الكتلة {block.id} تبدأ خارج حدود اللوحة.")
    #هاد التابع جبتو من gemini
    def display_grid(self):
        print("-" * (self.cols * 4 + 1))
        for r in range(self.rows):
            row_str = "| "
            for c in range(self.cols):
                content = self.Grid[r][c]
                if content == 0:
                    row_str += "0 | "
                elif content == 'W':
                    row_str += "W | "
                elif content == 'E':
                    row_str += "E | "
                elif content == 'gate':
                    row_str += "G | "
                elif isinstance(content, str) and content in self.BlockObjects:
                    block = self.BlockObjects[content]
                    if block.direction == "horizontal":
                        row_str += "--| "
                    elif block.direction == "vertical":
                        row_str += "| | "
                    else:
                        row_str += f"{content:2}| " 
                else:
                    row_str += f"{content}| " 
            print(row_str)
            print("-" * (self.cols * 4 + 1))
    
    def get_hashable_key(self):
       
        state_parts = []
        # نفترض أن IDs الكتل مرتبة B1, B2, B3...
        for block_id in sorted(self.BlockObjects.keys()):
            block = self.BlockObjects[block_id]
            state_parts.append((block_id, block.start_row, block.start_col))
        
        return tuple(state_parts)
    
    def get_hashable_key1(self):
        # نجمع بيانات كل مكعب في قائمة نصية
        state_list = []
        
        sorted_ids = sorted(self.BlockObjects.keys())
        
        for b_id in sorted_ids:
            block = self.BlockObjects[b_id]
            block_str = f"{block.id}{block.start_row}{block.start_col}{block.moves_to_unlock}"
            state_list.append(block_str)
        
        return "-".join(state_list)
    
    def __repr__(self):
        grid_str = "\n".join([" ".join(map(str, row)) for row in self.Grid])
        summary = f"Board State (Rows: {self.rows}, Blocks: {len(self.BlockObjects)}):\n"
        return summary + grid_str
#------------------------------------------------------------------------------------------
#_________________________MOVES METHODS________________________________
# هي الدالة لتجيب كلشي بوابات حولين الكتلةة
#بالتوابع اللي جاية gemini كتبلي ال print ونسقلي الكود بعد ما عملتن بس اللوجيك انا عملتو
    def check_gate_arround(self,block_id,block_obj=None):
        if block_obj is None:
            if block_id not in self.BlockObjects:
                return set()
            block = self.BlockObjects[block_id]
        else:
            block = block_obj

        arroud_coords_set = set(block.get_border_coords())
        # print(arroud_coords_set) 
        gates_objects = set()
        
        for gate_obj in self.ExitGates.values():
            if block.color.lower() == gate_obj.required_color.lower():
                gate_contact_set = set(gate_obj.contact_coords) 
                if gate_contact_set.intersection(arroud_coords_set):
                    gates_objects.add(gate_obj)
                            
                            
        return gates_objects 
#هي الدالة لتتحقق اذا الكتلة بتخرج من البوابة او لا 
    def check_ifCanBolckGetOutThisGate(self,block_id,gates_objects,final_coords=None):
        if block_id not in self.BlockObjects:
            return False
        block = self.BlockObjects[block_id]

        
        if final_coords is not None:
            # print("hello final coords")
            source_coords = final_coords
        else:
            source_coords = block.get_absolute_coords()

        block_coords = set(source_coords)
        # print("hello block")
        # print(gates_objects)
        for gate in gates_objects:
            # print("hello ")
            # if block.color.lower() == gate.required_color.lower():
                
            is_fully_within_gate_range = True
            if gate.side == "Top" or gate.side == "Bottom":
                all_c = [c for r, c in gate.contact_coords]
                small_c = min(all_c) 
                big_c = max(all_c)  
                # print(small_c,big_c,"this is gate col")
                for r_abs, c_abs in block_coords:
                    if not (small_c <= c_abs <= big_c):
                        # print(f" Validation failed: Part ({r_abs}, {c_abs}) is out of the column range {small_c}-{big_c}.")      
                        is_fully_within_gate_range = False
                        break
                
            elif gate.side == "Left" or gate.side == "Right":
                all_r = [r for r, c in gate.contact_coords]
                small_r = min(all_r) 
                big_r = max(all_r) 
                # print(small_r,big_r,"this is gate row")  
                for r_abs, c_abs in block_coords:
                    if not (small_r <= r_abs <= big_r):
                        # print(f" Validation failed: Part ({r_abs}, {c_abs}) is out of the row range {small_r}-{big_r}.")
                        is_fully_within_gate_range = False
                        break
            if is_fully_within_gate_range:
                # print(f" can move out{gate.id}.")
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
        # print("cooooo",new_coords,"cooooo")
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
    #هاد تابع القطع المجمدة 
    def decrement_moves_to_unlock(self):
        for block_id, block in self.BlockObjects.items():
            if block.moves_to_unlock > 0:
                block.moves_to_unlock -= 1
                # print(f"📉 the move to unlock {block_id}. updated: {block.moves_to_unlock}")

    def make_move(self, block_id, row_delta, col_delta):
        
        if block_id not in self.BlockObjects:
            return None
        
        old_block = self.BlockObjects[block_id]
        new_start_row = old_block.start_row + row_delta
        new_start_col = old_block.start_col + col_delta
        new_coords = self.calculate_coords(old_block, new_start_row, new_start_col)
        # print(col_delta,row_delta)
        if old_block.direction == 'horizontal' and col_delta == 0:
            print(f" Move for {block_id} is invalid. Direction is restricted horizontally (Horizontal).")
            print(col_delta)
            return None

        if old_block.direction == 'vertical' and row_delta == 0:
            print(f" Move for {block_id} is invalid. Direction is restricted vertically (Vertical).")
            return None

        if not self.is_valid_position(block_id, new_coords):
            print(f" Move failed: Internal collision or illegal exit for block {block_id}.")
            return None

        if old_block.moves_to_unlock > 0:
            print(f" Block {block_id} is locked. It needs {old_block.moves_to_unlock} more removal operations to unlock.")
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
            # new_board.get_possible_moves_for_one_block(block_id)
            return new_board,True
        else:
            for r_abs, c_abs in new_coords:
                if 0 <= r_abs < new_board.rows and 0 <= c_abs < new_board.cols:
                    new_board.Grid[r_abs][c_abs] = block_id 
            # new_board.get_possible_moves_for_one_block(block_id)
            return new_board,False
    
    def make_move_for_search(self, block_id, row_delta, col_delta):
        
        if block_id not in self.BlockObjects:
            return None
        
        old_block = self.BlockObjects[block_id]
        new_start_row = old_block.start_row + row_delta
        new_start_col = old_block.start_col + col_delta
        new_coords = self.calculate_coords(old_block, new_start_row, new_start_col)
        if old_block.direction == 'horizontal' and col_delta == 0:
            print(f" Move for {block_id} is invalid. Direction is restricted horizontally (Horizontal).")
            print(col_delta)
            return None

        if old_block.direction == 'vertical' and row_delta == 0:
            print(f" Move for {block_id} is invalid. Direction is restricted vertically (Vertical).")
            return None

        if not self.is_valid_position(block_id, new_coords):
            print(f" Move failed: Internal collision or illegal exit for block {block_id}.")
            return None

        if old_block.moves_to_unlock > 0:
            print(f" Block {block_id} is locked. It needs {old_block.moves_to_unlock} more removal operations to unlock.")
            return None
                
        new_board = self.fast_copy()
        for r_abs, c_abs in old_block.get_absolute_coords():
            if 0 <= r_abs < new_board.rows and 0 <= c_abs < new_board.cols:
                if new_board.Grid[r_abs][c_abs] == block_id:
                    new_board.Grid[r_abs][c_abs] = 0

        
        new_block = new_board.BlockObjects[block_id]
        new_block.start_row = new_start_row
        new_block.start_col = new_start_col
        # print(f"block{new_block.id} moved ")
        gates_arround = self.check_gate_arround(block_id,new_block) 
        is_exit = self.check_ifCanBolckGetOutThisGate(block_id,gates_arround, new_coords)
        
        
        if(is_exit):
            if block_id in new_board.BlockObjects:
                del new_board.BlockObjects[block_id]
                new_board.decrement_moves_to_unlock()
                # print(f"✅ the {block_id} is exited successfully.")
            return new_board,True
        else:
            for r_abs, c_abs in new_coords:
                if 0 <= r_abs < new_board.rows and 0 <= c_abs < new_board.cols:
                    new_board.Grid[r_abs][c_abs] = block_id 
            return new_board,False
    
    def is_final_state(self):
        return len(self.BlockObjects) == 0
        
    def is_cell_valid(self,r_abs, c_abs):
        if not (0 <= r_abs < self.rows and 0 <= c_abs < self.cols):
            return False
        cell_content = self.Grid[r_abs][c_abs]
        if cell_content!=0:
            return False 
        if cell_content == 'W':
            return False
        return True
    

    def count_valid_moves(self,block_id,border_coords):
        block=self.BlockObjects[block_id]
        boards_child=[]
        top_count, bottom_count, left_count, right_count = 0, 0, 0, 0
        is_top_clear, is_bottom_clear, is_left_clear, is_right_clear = True, True, True, True
        if block.moves_to_unlock > 0:
            top_count, bottom_count,left_count,right_count=0,0,0,0
            return 0,boards_child
        else:
            top_coords_set = border_coords.get("Top", set())
            bottom_coords_set = border_coords.get("bottom", set())
            left_coords_set = border_coords.get("left", set())
            right_coords_set = border_coords.get("right", set())

            if block.direction in ['vertical', 'both']:
                for r_abs, c_abs in top_coords_set:
                    is_cell_valid=self.is_cell_valid(r_abs,c_abs)
                    if not is_cell_valid:
                        is_top_clear = False
                if is_top_clear:
                    top_count=1
                    r_delta, c_delta = -1, 0
                    move_result=self.make_move_for_search(block_id,r_delta,c_delta)
                    if move_result is not None:
                        new_board, is_exit = move_result
                        if new_board:
                            move_details = (block_id, r_delta, c_delta)
                            boards_child.append((new_board, move_details))
                # print(block.id ,"can move top ",top_count)

                for r_abs, c_abs in bottom_coords_set:
                    is_cell_valid=self.is_cell_valid(r_abs,c_abs)
                    if not is_cell_valid:
                        is_bottom_clear = False
                if is_bottom_clear:
                    bottom_count=1
                    r_delta, c_delta = 1, 0
                    move_result=self.make_move_for_search(block_id,r_delta,c_delta)
                    if move_result is not None:
                        new_board, is_exit = move_result
                        if new_board:
                            move_details = (block_id, r_delta, c_delta)
                            boards_child.append((new_board, move_details))
                # print(block.id ,"can move bottom ",bottom_count)
            if block.direction in ['horizontal', 'both']:
                for r_abs, c_abs in left_coords_set:
                    is_cell_valid=self.is_cell_valid(r_abs,c_abs)
                    if not is_cell_valid:
                        is_left_clear = False
                if is_left_clear:
                    left_count=1
                    r_delta, c_delta = 0, -1
                    move_result=self.make_move_for_search(block_id,r_delta,c_delta)
                    if move_result is not None:
                        new_board, is_exit = move_result
                        if new_board:
                            move_details = (block_id, r_delta, c_delta)
                            boards_child.append((new_board, move_details))
                # print(block.id ,"can move left ",left_count)
                for r_abs, c_abs in right_coords_set:
                    is_cell_valid=self.is_cell_valid(r_abs,c_abs)
                    if not is_cell_valid:
                        is_right_clear = False
                if is_right_clear:
                    right_count=1
                    r_delta, c_delta = 0, 1
                    move_result=self.make_move_for_search(block_id,r_delta,c_delta)
                    if move_result is not None:
                        new_board, is_exit = move_result
                        if new_board:
                            move_details = (block_id, r_delta, c_delta)
                            boards_child.append((new_board, move_details))
                # print(block.id ,"can move right ",right_count)
        
        count_moves=top_count+ bottom_count+left_count+right_count
        # print(f"possible moves for {block.id} is {count_moves}")
        return count_moves,boards_child
    
    def get_possible_moves_for_one_block(self, block_id):
        
        if block_id not in self.BlockObjects:
            return {}
        block = self.BlockObjects[block_id]
        
        # absolute_coords= block.get_absolute_coords()
        border_coords= block.get_directional_border_coords()
        # print("get_absolute_coords",absolute_coords)
        # print("get_border_coords",border_coords)
        count_moves,boards_child=self.count_valid_moves(block_id,border_coords)
        return count_moves,boards_child
    
    def get_possible_moves_for_board(self):
        count_possible_moves =0
        all_child_boards = []
        for block_id in self.BlockObjects:
            count_moves,boards_child=self.get_possible_moves_for_one_block(block_id)
            count_possible_moves+=count_moves
            all_child_boards.extend(boards_child)
        # print("------------\n","count possible moves for all board ",count_possible_moves)
        return count_possible_moves,all_child_boards
        

#///////////////////////////////////////////////////////////////////////////
#هاد مشان يروح لاقصى خطوى مش وحدة وحدة 
# --------------------- دوال التحويل بين التنسيقات ---------------------
    def count_valid_moves1(self, block_id, border_coords):
        block = self.BlockObjects[block_id]
        boards_child = []
        total_moves_count = 0
        
        # إذا كانت الكتلة مقفلة، لا يمكنها التحرك نهائياً
        if block.moves_to_unlock > 0:
            return 0, boards_child

        # تحديد الاتجاهات المسموحة بناءً على نوع الكتلة (أفقي أو عمودي)
        possible_directions = []
        if block.direction in ['vertical', 'both']:
            possible_directions.append((-1, 0, "Top"))    # للأعلى
            possible_directions.append((1, 0, "bottom"))  # للأسفل
        if block.direction in ['horizontal', 'both']:
            possible_directions.append((0, -1, "left"))   # لليسار
            possible_directions.append((0, 1, "right"))   # لليمين

        for r_delta, c_delta, side_name in possible_directions:
            step = 1
            # نستمر في زيادة المسافة طالما الطريق فارغ
            while True:
                current_r_delta = r_delta * step
                current_c_delta = c_delta * step
                
                # نفحص الحواف (border) في هذا الاتجاه عند هذه المسافة
                is_path_clear = True
                current_side_coords = border_coords.get(side_name, set())
                
                for r_abs, c_abs in current_side_coords:
                    # نحسب الخلية المجاورة بناءً على المسافة الحالية
                    # الخلية الجديدة = الخلية الأصلية + (الاتجاه * المسافة)
                    target_r = r_abs + (r_delta * (step - 1))
                    target_c = c_abs + (c_delta * (step - 1))
                    
                    if not self.is_cell_valid(target_r, target_c):
                        is_path_clear = False
                        break
                
                if is_path_clear:
                    # إذا كان الطريق فارغاً، نولّد لوحة جديدة لهذه الحركة
                    move_result = self.make_move_for_search(block_id, current_r_delta, current_c_delta)
                    
                    if move_result is not None:
                        new_board, is_exit = move_result
                        total_moves_count += 1
                        boards_child.append((new_board, (block_id, current_r_delta, current_c_delta)))
                        
                        # إذا أدت هذه الحركة لخروج الكتلة، نتوقف عن البحث في هذا الاتجاه
                        if is_exit:
                            break
                    else:
                        # فشلت الحركة برمجياً (تصادم غير متوقع)
                        break
                else:
                    # اصطدمنا بكتلة أخرى أو جدار، نتوقف عن زيادة المسافة
                    break
                    
                step += 1 # ننتقل للخطوة التالية (مربع أبعد)

        return total_moves_count, boards_child