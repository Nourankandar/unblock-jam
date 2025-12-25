import tkinter as tk
from tkinter import *
from Board import Board 
from tkinter import messagebox
import time
import datetime
from algorithms import BFS_solver, UCS_solver, a_star_solver,dfs_solver, hill_climbing_solver,recursive_dfs_solver,hill_climbing_beam_solver
class GameGUI:
    CELL_SIZE = 50 
    COLORS = {
        "green": "lightgreen",
        "yellow": "yellow",
        "red": "red",
        "orange": "orange",
        "W": "brown",  
        0: "gray",
        "darkblue": "midnightblue",
        "purple": "mediumpurple",    
        "cyan": "cyan",
        "blue":"blue"

    }
    PAD = 50
    FRAME_PADDING = 50
    def __init__(self, master, Board_instance):

        self.history_stack = [ ]
        self.initial_board_state = Board_instance.deep_copy()
        self.master = master
        self.Board = Board_instance
        self.exited_blocks_count = 0
        self.width = self.Board.cols * self.CELL_SIZE 
        self.height = self.Board.rows * self.CELL_SIZE
        self.selected_block_id = None
        self.start_x = None
        self.start_y = None
        master.title("Unblock jam") 
        master.geometry("+400+10")
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
        self.add_button(self.frame,"get moves",self.handle_get_moves_button)
        self.add_button(self.frame,"Bfs",self.handle_get_moves_button11)
        self.add_button(self.frame,"Dfs",self.handle_get_moves_button12)
        self.add_button(self.frame,"Dfs R",self.handle_get_moves_button13)
        self.add_button(self.frame,"UCS",self.handle_get_moves_button14)
        self.add_button(self.frame,"Hill Climbing",self.handle_get_moves_button15)
        self.add_button(self.frame,"A Star",self.handle_get_moves_button16)
        self.draw_Board()

    def add_button(self,frame,text,command):
        button = Button(frame,text=text,font=('Times New Roman',20))
        button.config(command=command)
        button.pack(side="left")
    #استخدمت gemini لمساعدتي في رسم الرقعة وبعض التفاصيل هنا
    def draw_Board(self):
        self.canvas.delete("all")
        self.frame.delete("gate_drawings") 
        
        rows = self.Board.rows
        cols = self.Board.cols
        OFFSET = 2
        for r in range(rows +1 ):
            y = r * self.CELL_SIZE +OFFSET 
            self.canvas.create_line(OFFSET+self.CELL_SIZE , y, self.CELL_SIZE*cols+OFFSET , y, fill="white", width=2)
            
        for c in range(cols +1 ):
            x = c * self.CELL_SIZE+OFFSET 
            self.canvas.create_line(x, OFFSET , x,self.CELL_SIZE*rows+OFFSET, fill="white", width=2)
        
                
        gate_cells_info = {}
        for gate_id, gate_obj in self.Board.ExitGates.items():
            required_color_name = gate_obj.required_color.lower()
            fill_color = self.COLORS.get(required_color_name, "lightgray") 
            
            for r, c in gate_obj.contact_coords:
                if 0 <= r < rows and 0 <= c < cols:
                    gate_cells_info[(r, c)] = {
                        'fill': fill_color,
                        'text': f"{gate_obj.required_color[0].upper()}/{gate_obj.required_length}"
                    }
        #هون لتعبئة الرقعة بالبيانات
        for r in range(rows):
            for c in range(cols):
                cell_content = self.Board.Grid[r][c]
                x1 = c * self.CELL_SIZE+OFFSET 
                y1 = r * self.CELL_SIZE+OFFSET 
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                fill_color = self.COLORS[0] 
                if (r, c) in gate_cells_info:
                    info = gate_cells_info[(r, c)]
                    fill_color = info['fill']
                    text_to_draw = info['text']
                else:
                    fill_color = self.COLORS[0] 
                    text_to_draw = "" 
                
                outline_color="white"
                if cell_content != 0:
                    text_to_draw = str(cell_content)
                    if cell_content == 'W':
                        fill_color = self.COLORS['W']
                        
                    elif isinstance(cell_content, str): 
                        if cell_content in self.Board.BlockObjects:
                            block_obj = self.Board.BlockObjects[cell_content]
                            fill_color = self.COLORS.get(block_obj.color)
                            remaining_moves = block_obj.moves_to_unlock
                            text_to_draw  = block_obj.id
                            if block_obj.direction == "horizontal":
                                text_to_draw = "--"
                            if block_obj.direction == "vertical":
                                text_to_draw = "|"
                            if remaining_moves > 0:
                                text_to_draw  = str(remaining_moves)
                                fill_color = "white"
                                self.canvas.create_text(x1 + self.CELL_SIZE/2, y1 + self.CELL_SIZE/2, 
                                                        text=text_to_draw ,
                                                        fill="black", 
                                                        font=('Times New Roman', 14, 'bold'),
                                                        tag="lock_indicator")
                    else:
                        
                        self.Board.Grid[r][c] = 0
                        continue
                        
                            
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=3)
                
                if text_to_draw:
                     fill_text_color = "black" if fill_color != self.COLORS['W'] else "white"
                     self.canvas.create_text(x1 + self.CELL_SIZE/2, y1 + self.CELL_SIZE/2, 
                                             text=text_to_draw, 
                                             fill=fill_text_color)
   
    
    def cell_to_coords(self, r, c):
        x = c * self.CELL_SIZE
        y = r * self.CELL_SIZE
        return x, y
    #_____________________________________________________________________________
    #الحركة 
    # ملف: Board_GUI.py (دالة جديدة)
    def handle_get_moves_button(self):
        count_possible_moves,all_child_boards=self.Board.get_possible_moves_for_board()     
        print(all_child_boards)   
        print("--------------------------------------------------")

    def on_click(self, event):
        col = (event.x ) // self.CELL_SIZE
        row = (event.y ) // self.CELL_SIZE

        if 0 <= row < self.Board.rows and 0 <= col < self.Board.cols:
            block_id = self.Board.Grid[row][col]
            print(f"Clicked Coordinates: (Row={row}, Col={col})")
            
            if block_id != 0 and block_id != 'W'and block_id!='gate':
                
                block_to_exit = self.Board.BlockObjects[block_id]
                # nn= self.Board.check_gate_arround(block_id)
                # for n in nn :
                #     print(n)
                self.selected_block_id = block_id
                self.start_x = event.x
                self.start_y = event.y
                
            else:
                self.selected_block_id = None
                
        else:
            self.selected_block_id = None
            print("Clicked outside board limits.")
        

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
        #هي لحدود الحركة
        if abs(final_row_delta) > abs(final_col_delta):
            final_col_delta = 0
        else:
            final_row_delta = 0
        #هون استخدمنا التابع للحركة
        move_result = self.Board.make_move(block_id, final_row_delta, final_col_delta)
        if move_result is not None:
            new_state, is_exit = move_result
            if new_state:
                
                self.history_stack.append(self.Board.deep_copy())
                self.Board = new_state
                self.draw_Board()
                new_state.display_grid()
                # self.Board.get_possible_moves_for_board()
                if is_exit:
                    print(True)
                    block_to_exit = self.Board.BlockObjects[block_id]
                    final_coords_on_grid = [
                        (r, c) for r, c in block_to_exit.get_absolute_coords()
                        if 0 <= r < self.Board.rows and 0 <= c < self.Board.cols
                    ]
                    delay_milliseconds = 500
                    self.master.after(
                        delay_milliseconds, 
                        lambda: self.finalize_exit(block_id, final_coords_on_grid)
                    )
                    
            else:
                print("حركة غير مسموح بها")

            self.selected_block_id = None
            self.start_x = None
            self.start_y = None
    

    def finalize_exit(self, block_id, final_coords_on_grid):
        for r_abs, c_abs in final_coords_on_grid:
            if 0 <= r_abs < self.Board.rows and 0 <= c_abs < self.Board.cols:
                if self.Board.Grid[r_abs][c_abs] == block_id:
                    self.Board.Grid[r_abs][c_abs] = 0

        if block_id in self.Board.BlockObjects:
            del self.Board.BlockObjects[block_id]
            self.Board.decrement_moves_to_unlock() 
            print(f"out  .")
            # print("hello final")

        self.draw_Board()
        self.Board.display_grid() 

        if self.Board.is_final_state():
                messagebox.showinfo("تهانينا!", "🎉 تم حل اللغز بنجاح وإفراغ الرقعة!")
                print("تهانينا  تم حل اللغز وإفراغ الرقعة.")
                self.handle_reset()
        

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

    def handle_get_moves_button11(self):
        initial_board_copy = self.Board.deep_copy() 
        result = BFS_solver(initial_board_copy, 500)
        
        solution_path = result["path"]
        execution_time = result["time"]
        memory_used = result["memory"]
        states_explored = result["explored_states"]
        
        time_str = f"{execution_time:.4f} ثانية"
        if solution_path is not None:
            num_moves = len(solution_path)
            messagebox.showinfo(
                "تم العثور على حل (BFS)!", 
                f"عدد الحركات: {num_moves} خطوة.\n"
                f"وقت التنفيذ: {time_str}\n"
                f"الحالات المخزنة: {memory_used}\n"
                f"الحالات المستكشفة: {states_explored}"
            )
            self.print_game_moves(solution_path)
            self.solution_path = solution_path
        else:
            messagebox.showerror(
                "لا يوجد حل", 
                f"لم يتم العثور على حل.\nوقت البحث: {time_str}\nالحالات المفحوصة: {states_explored}"
            )

    def handle_get_moves_button12(self):
        initial_board_copy = self.Board.deep_copy() 
        result = dfs_solver(initial_board_copy)
        
        solution_path = result["path"]
        execution_time = result["time"]
        memory_used = result["memory"]
        states_explored = result["explored_states"]

        time_str = f"{execution_time:.4f} ثانية"
        if solution_path is not None:
            num_moves = len(solution_path)
            messagebox.showinfo(
                "تم العثور على حل (DFS)!", 
                f"عدد الحركات: {num_moves} خطوة.\n"
                f"وقت التنفيذ: {time_str}\n"
                f"الحالات المخزنة: {memory_used}\n"
                f"الحالات المستكشفة: {states_explored}"
            )
            self.solution_path = solution_path
            self.print_game_moves(solution_path)
        else:
            messagebox.showerror("No Solution", f"Execution Time: {time_str}")

    def handle_get_moves_button13(self):
        initial_board_copy = self.Board.deep_copy() 
        result = recursive_dfs_solver(initial_board_copy)
        
        solution_path = result["path"]
        execution_time = result["time"]
        memory_used = result["memory"]
        states_explored = result["explored_states"]

        time_str = f"{execution_time:.4f} ثانية"
        if solution_path is not None:
            num_moves = len(solution_path)
            messagebox.showinfo(
                "تم العثور على حل (Recursive DFS)!", 
                f"عدد الحركات: {num_moves} خطوة.\n"
                f"وقت التنفيذ: {time_str}\n"
                f"الحالات المخزنة: {memory_used}\n"
                f"الحالات المستكشفة: {states_explored}"
            )
            self.solution_path = solution_path
            self.print_game_moves(solution_path)
        else:
            messagebox.showerror("No Solution", f"Execution Time: {time_str}")

    def handle_get_moves_button14(self):
        initial_board_copy = self.Board.deep_copy() 
        result = UCS_solver(initial_board_copy)
        
        solution_path = result["path"]
        execution_time = result["time"]
        memory_used = result["memory"]
        states_explored = result["explored_states"]

        time_str = f"{execution_time:.4f} ثانية"
        if solution_path is not None:
            num_moves = len(solution_path)
            messagebox.showinfo(
                "تم العثور على حل (UCS)!", 
                f"عدد الحركات: {num_moves} خطوة.\n"
                f"وقت التنفيذ: {time_str}\n"
                f"الحالات المخزنة: {memory_used}\n"
                f"الحالات المستكشفة: {states_explored}"
            )
            self.solution_path = solution_path
            self.print_game_moves(solution_path)
        else:
            messagebox.showerror("No Solution", f"Execution Time: {time_str}")

    def handle_get_moves_button15(self):
        initial_board_copy = self.Board.deep_copy() 
        result = hill_climbing_beam_solver(initial_board_copy)
        
        solution_path = result["path"]
        execution_time = result["time"]
        memory_used = result["memory"]
        states_explored = result["explored_states"]

        time_str = f"{execution_time:.4f} ثانية"
        if solution_path is not None:
            num_moves = len(solution_path)
            messagebox.showinfo(
                "تم العثور على حل (Beam Search)!", 
                f"عدد الحركات: {num_moves} خطوة.\n"
                f"وقت التنفيذ: {time_str}\n"
                f"الحالات المخزنة: {memory_used}\n"
                f"الحالات المستكشفة: {states_explored}"
            )
            self.solution_path = solution_path
            self.print_game_moves(solution_path)
        else:
            messagebox.showerror("No Solution", f"Execution Time: {time_str}")

    def handle_get_moves_button16(self):
        initial_board_copy = self.Board.deep_copy() 
        result = a_star_solver(initial_board_copy)
        
        solution_path = result["path"]
        execution_time = result["time"]
        memory_used = result["memory"]
        states_explored = result["explored_states"]

        time_str = f"{execution_time:.4f} ثانية"
        if solution_path is not None:
            num_moves = len(solution_path)
            messagebox.showinfo(
                "تم العثور على حل (A*)!", 
                f"عدد الحركات: {num_moves} خطوة.\n"
                f"وقت التنفيذ: {time_str}\n"
                f"الحالات المخزنة: {memory_used}\n"
                f"الحالات المستكشفة: {states_explored}"
            )
            self.solution_path = solution_path
            self.print_game_moves(solution_path)
        else:
            messagebox.showerror("No Solution", f"Execution Time: {time_str}")
    def print_game_moves(self,moves_list):
    
        directions = {
            (-1, 0): "Top ⬆️",
            (1, 0):  "Bottom ⬇️",
            (0, -1): "Left ⬅️",
            (0, 1):  "Right ➡️"
        }

        print(f"Moves {len(moves_list)}) ---")
        
        for i, move in enumerate(moves_list, 1):
            if not move or len(move) < 3:
                continue
                
            block_name = move[0]      # اسم المكعب مثل B7
            offset = (move[1], move[2]) # الإزاحة (صف، عمود)
            
            direction_text = directions.get(offset, f" moved {offset}")
            
            print(f"step {i}: block {block_name} moved  {direction_text}")
