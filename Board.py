from Block import Block
from ExitGate import ExitGate
# from Read_Json import load_data

class Board:
    def __init__(self, data_map):
        self.rows = 0
        self.cols = 0
        self.Grid = []  
        self.BlockObjects = {} 
        self.StaticElements = set() 
        self.ExitGates = {} 
        self.initialize_board(data_map)
    
    def initialize_board(self, data):
        """
        تقوم بتحويل بيانات JSON الخام إلى حالة اللعبة وكائنات تفاعلية.
        """
        settings = data['board_settings']
        self.rows = settings['rows']
        self.cols = settings['cols']
        self.Grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        print(f"✅ Board is created {self.rows}x{self.cols}")
        #لتخزين البوابات ومعلوماتها الموجودة في ال json 
        for gate_data in settings['exit_gates']:
            gate = ExitGate(gate_data)
            self.ExitGates[gate.id] = gate
        
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
                        print(f"🛑 خطأ في التصميم الأولي: الكتلة {block.id} تتداخل مع عنصر ثابت في الموقع ({r_abs}, {c_abs})")
                    elif self.Grid[r_abs][c_abs] != 0:
                        print(f"🛑 خطأ في التصميم الأولي: الكتلة {block.id} تتداخل مع كتلة أخرى في الموقع ({r_abs}, {c_abs})")
                    self.Grid[r_abs][c_abs] = block.id
                else:
                    print(f"🛑 خطأ في التصميم الأولي: الكتلة {block.id} تبدأ خارج حدود اللوحة.")
    
    def display_grid(self):
        print("\n--- حالة اللوحة الحالية (Grid) ---")
        for row in self.Grid:
            print("    |    ".join(map(str, row)))
        print("--------------------------------")