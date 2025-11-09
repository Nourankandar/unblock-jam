import tkinter as tk
from Board import Board 
class GameGUI:
    CELL_SIZE = 60 
    COLORS = {
        "green": "lightgreen",
        "yellow": "yellow",
        "red": "red",
        "orange": "orange",
        "W": "brown",  
        0: "gray"      
    }
    PAD = 50
    FRAME_PADDING = 50
    def __init__(self, master, Board_instance):
        self.master = master
        self.Board = Board_instance
        
        self.width = self.Board.cols * self.CELL_SIZE 
        self.height = self.Board.rows * self.CELL_SIZE
        
        master.title("Unblock jam") 
        master.geometry("+400+40")
        self.frame = tk.Canvas(master, bg="darkgray")
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, bg="lightgray")
        self.canvas.pack(fill=tk.BOTH, expand=True) 
        self.canvas.pack(padx=self.PAD, pady=self.PAD)
        self.frame.pack(expand=True, fill=tk.BOTH)
        
        self.draw_Board()

    def draw_Board(self):
        """ترسم الشبكة والكتل والعوائق بناءً على حالة اللوحة الحالية."""
        self.canvas.delete("all")
        self.frame.delete("gate_drawings") 
        
        rows = self.Board.rows
        cols = self.Board.cols
        OFFSET = 2
        for r in range(rows +1 ):
            # print(r)
            y = r * self.CELL_SIZE +OFFSET 
            self.canvas.create_line(OFFSET , y, self.CELL_SIZE*cols+OFFSET , y, fill="black", width=2)
            
        for c in range(cols +1 ):
            x = c * self.CELL_SIZE+OFFSET 
            self.canvas.create_line(x, OFFSET , x,self.CELL_SIZE*rows+OFFSET, fill="black", width=2)

        for r in range(rows):
            for c in range(cols):
                cell_content = self.Board.Grid[r][c]
                x1 = c * self.CELL_SIZE+OFFSET 
                y1 = r * self.CELL_SIZE+OFFSET 
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                fill_color = self.COLORS[0] 
                outline_color = "black"

                if cell_content != 0:
                    
                    if cell_content == 'W':
                        fill_color = self.COLORS['W']
                        
                    elif isinstance(cell_content, str): 
                        block_obj = self.Board.BlockObjects[cell_content]
                        fill_color = self.COLORS.get(block_obj.color, "gray")
                        if block_obj.is_target:
                            outline_color = "gold"
                            
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=3)
                    self.canvas.create_text(x1 + self.CELL_SIZE/2, y1 + self.CELL_SIZE/2, text=str(cell_content), fill="black")
        
        self.draw_edges1()
        
    def draw_edges(self):
        cell_size = self.CELL_SIZE
        rows = self.Board.rows
        cols = self.Board.cols
        OFFSET =2
        PAD = self.FRAME_PADDING
        for gate_id, gate in self.Board.ExitGates.items():
            fill_color = self.COLORS.get(gate.required_color, "gray")
            outline_color = "black"
            print(gate)
            for r_contact, c_contact in gate.contact_coords:
                x_start = c_contact * cell_size + OFFSET
                y_start = r_contact * cell_size + OFFSET
                if gate.side == "Top":
                    
                    x1 = x_start
                    y2 = OFFSET 
                    x2 = x_start + cell_size
                    y1 = y2 - cell_size/2 
                elif gate.side == "Bottom":
                    x1 = x_start
                    y1 = rows * cell_size + OFFSET 
                    x2 = x_start + cell_size
                    y2 = y1 + cell_size/2
                    
                elif gate.side == "Left":
                    y1 = y_start
                    x2 = OFFSET 
                    y2 = y_start + cell_size
                    x1 = x2 - cell_size /2
                    
                elif gate.side == "Right":
                    y1 = y_start
                    x1 = cols * cell_size + OFFSET 
                    y2 = y_start + cell_size
                    x2 = x1 + cell_size /2
                
                

                draw_x1 = x1 + PAD
                draw_y1 = y1 + PAD
                draw_x2 = x2 + PAD
                draw_y2 = y2 + PAD
                self.frame.create_rectangle(draw_x1, draw_y1, draw_x2, draw_y2, 
                                             fill=fill_color, 
                                             outline=outline_color, 
                                             width=3,
                                             tag="gate_drawings")
                
    def draw_edges1(self):
        """ترسم البوابات على أطراف اللوحة (على الـ frame)."""
        cell_size = self.CELL_SIZE
        rows = self.Board.rows
        cols = self.Board.cols
        
        OFFSET = 4 
        
        canvas_x_start = self.PAD
        canvas_y_start = self.PAD
        canvas_x_end = self.PAD + self.width
        canvas_y_end = self.PAD + self.height

        for gate in self.Board.ExitGates.values():
            
            x1, y1, x2, y2 = 0, 0, 0, 0
            required_color_name = gate.required_color.lower()
            if gate.is_wall:
                fill_color = "darkred" 
            else:
                fill_color = self.COLORS.get(required_color_name, "lightgray") 
            
            outline_color = "black"
            
            r_contact, c_contact = gate.contact_coords[0]
            if gate.side == "Top":
                y_start = canvas_y_start - cell_size / 2
                y_end = canvas_y_start
                x_start = canvas_x_start + c_contact * cell_size
                x_end = x_start + len(gate.contact_coords) * cell_size
                x1, y1, x2, y2 = x_start, y_start, x_end, y_end

            elif gate.side == "Bottom":
                y_start = canvas_y_end
                y_end = canvas_y_end + cell_size / 2
                x_start = canvas_x_start + c_contact * cell_size
                x_end = x_start + len(gate.contact_coords) * cell_size
                x1, y1, x2, y2 = x_start, y_start, x_end, y_end
                
            elif gate.side == "Left":
                x_start = canvas_x_start - cell_size / 2
                x_end = canvas_x_start
                y_start = canvas_y_start + r_contact * cell_size
                y_end = y_start + len(gate.contact_coords) * cell_size
                x1, y1, x2, y2 = x_start, y_start, x_end, y_end

            elif gate.side == "Right":
                x_start = canvas_x_end
                x_end = canvas_x_end + cell_size / 2
                y_start = canvas_y_start + r_contact * cell_size
                y_end = y_start + len(gate.contact_coords) * cell_size

                x1, y1, x2, y2 = x_start, y_start, x_end, y_end

            self.frame.create_rectangle(x1, y1, x2, y2, 
                                         fill=fill_color, 
                                         outline=outline_color, 
                                         width=3,
                                         tag="gate_drawings")
            
            symbol_text = f"{gate.required_color[0].upper()}/{gate.required_length}"
            self.frame.create_text(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2, 
                                    text=symbol_text, 
                                    fill="white", 
                                    font=('Arial', 8, 'bold'),
                                    tag="gate_drawings")

    
    def cell_to_coords(self, r, c):
        """تحويل إحداثيات الصف/العمود إلى إحداثيات بكسل على الـ canvas."""
        x = c * self.CELL_SIZE
        y = r * self.CELL_SIZE
        return x, y
                    