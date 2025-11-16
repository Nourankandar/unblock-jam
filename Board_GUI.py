from cProfile import label
import tkinter as tk
from tkinter import *
from Board import Board 
from tkinter import messagebox
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

        self.history_stack = [ ]
        self.initial_board_state = Board_instance.deep_copy()
        self.master = master
        self.Board = Board_instance
        
        self.width = self.Board.cols * self.CELL_SIZE 
        self.height = self.Board.rows * self.CELL_SIZE


        self.selected_block_id = None
        self.start_x = None
        self.start_y = None
        


        master.title("Unblock jam") 
        master.geometry("+400+40")
        label= Label( master,text="Un Block Jam ",font=('Times New Roman',25))
        label.pack()
        self.frame = tk.Canvas(master, bg="darkgray")
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, bg="lightgray")
        self.canvas.pack(fill=tk.BOTH, expand=True) 
        self.canvas.pack(padx=self.PAD, pady=self.PAD)
        self.frame.pack(expand=True, fill=tk.BOTH)


        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.add_button(self.frame,"Undo",self.handle_undo)
        self.add_button(self.frame,"Reset",self.handle_reset)
        
        self.draw_Board()
    def add_button(self,frame,text,command):
        button = Button(frame,text=text,font=('Times New Roman',20))
        button.config(command=command)
        button.pack(side="left")

    def draw_Board(self):
        """ترسم الشبكة والكتل والعوائق بناءً على حالة اللوحة الحالية."""
        self.canvas.delete("all")
        self.frame.delete("gate_drawings") 
        
        rows = self.Board.rows
        cols = self.Board.cols
        OFFSET = 2
        for r in range(rows +1 ):
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
                    text_to_draw = str(cell_content)
                    if cell_content == 'W':
                        fill_color = self.COLORS['W']
                        
                    elif isinstance(cell_content, str): 
                        if cell_content in self.Board.BlockObjects:
                            block_obj = self.Board.BlockObjects[cell_content]
                        # block_obj = self.Board.BlockObjects[cell_content]
                            fill_color = self.COLORS.get(block_obj.color, "gray")
                    else:
                        self.Board.Grid[r][c] = 0
                        continue
                        
                            
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
    #_____________________________________________________________________________
    #الحركة 
    # ملف: Board_GUI.py (دالة جديدة)

    def on_click(self, event):
        col = (event.x ) // self.CELL_SIZE
        row = (event.y ) // self.CELL_SIZE

        if 0 <= row < self.Board.rows and 0 <= col < self.Board.cols:
            block_id = self.Board.Grid[row][col]
            print(block_id)
            if block_id != 0:
                self.selected_block_id = block_id
                self.start_x = event.x
                self.start_y = event.y
            else:
                self.selected_block_id = None
        else:
            self.selected_block_id = None
    

    def on_release(self, event):
        if self.selected_block_id is None:
            return

        block_id = self.selected_block_id
        
        end_x = event.x
        end_y = event.y
        delta_x_pixel = end_x - self.start_x
        delta_y_pixel = end_y - self.start_y
        
        
        final_col_delta = round(delta_x_pixel / self.CELL_SIZE)
        final_row_delta = round(delta_y_pixel / self.CELL_SIZE)

        if abs(final_row_delta) > abs(final_col_delta):
            final_col_delta = 0
        elif abs(final_col_delta) > abs(final_row_delta):
            final_row_delta = 0
        else:
            if abs(final_row_delta) == 0 and abs(final_col_delta) == 0:
                 self.selected_block_id = None
                 return
        new_state = self.Board.make_move(block_id, final_row_delta, final_col_delta)
        if new_state:
            self.history_stack.append(self.Board.deep_copy())
            self.Board = new_state
            self.draw_Board()
        else:
             print("🛑 فشلت الحركة: الحركة غير صالحة أو مغلقة. (الحالة لم تتغير)")

        self.selected_block_id = None
        self.start_x = None
        self.start_y = None
        if self.Board.is_final_state():
            messagebox.showinfo("تهانينا!", "🎉 تم حل اللغز بنجاح وإفراغ الرقعة!")
            print("تهانينا! 🎉 تم حل اللغز وإفراغ الرقعة.")
    
    def handle_undo(self):
        if self.history_stack:
            self.Board = self.history_stack.pop()
            self.draw_Board()
            print("↩️ تم التراجع خطوة واحدة.")
        else:
            print("⚠️ لا يوجد حركات سابقة للتراجع عنها.")
    
    def handle_reset(self):
        self.Board = self.initial_board_state.deep_copy()
        self.history_stack = []
        self.draw_Board()
        print("🔄 تمت إعادة ضبط اللعبة إلى الحالة البدائية.")