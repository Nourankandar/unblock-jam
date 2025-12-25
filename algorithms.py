
import time
import copy
from Board import Board 
from collections import deque
import heapq

def reconstruct_path(parent_map, start_key, end_key):
    path = []
    current_key = end_key
    while current_key != start_key:
        if current_key not in parent_map:
            return None 
        parent_key, move_details = parent_map[current_key]
        path.append(move_details)
        current_key = parent_key
    path.reverse()
    return path

#---------------------------------------------------
def dfs_solver(initial_board: Board):
    start_time = time.time()
    if initial_board.is_final_state():
        return [], 0.0
    start_key = initial_board.get_hashable_key() 
    stack = [start_key] 
    visited = {start_key} 
    parent_map = {} 
    state_to_board = {start_key: initial_board.deep_copy()} 
    states_processed = 0

    while stack:
        current_key = stack.pop() 
        current_board = state_to_board[current_key]
        states_processed += 1
        try:
            _, all_child_moves = current_board.get_possible_moves_for_board() 
        except Exception as e:
            print(f"error {e}")
            return {
            "path": [],
            "time": execution_time,
            "memory": 1,
            "explored_states": 0,
            "path_length": 0
        }
        
        for child_board, move_details in all_child_moves:
            child_key = child_board.get_hashable_key1()
            
            if child_key not in visited:
                if child_board.is_final_state():
                    parent_map[child_key] = (current_key, move_details)
                    end_time = time.time() 
                    execution_time = end_time - start_time
                    solution_path = reconstruct_path(parent_map, start_key, child_key)
                    print(f"found a solustion {len(solution_path)}. take: {execution_time:.2f} .second")
                    return {
                        "path": solution_path,
                        "time": execution_time,
                        "memory": len(visited), 
                        "explored_states": states_processed, 
                        "path_length": len(solution_path)
                    }
                
                visited.add(child_key)
                parent_map[child_key] = (current_key, move_details)
                state_to_board[child_key] = child_board 
                stack.append(child_key)
                
    end_time = time.time() 
    execution_time = end_time - start_time
    print(f"no soluition{states_processed} state {execution_time:.2f} seconds.")
    return {
        "path": None,
        "time": execution_time,
        "memory": len(visited),
        "explored_states": states_processed,
        "path_length": 0
    }

#-------------------------------------------------------------

def recursive_dfs_solver(initial_board: Board):
    start_time = time.time()
    
    if initial_board.is_final_state():
        return {
            "path": [],
            "time": time.time() - start_time,
            "memory": 1,
            "explored_states": 0,
            "path_length": 0
        }

    start_key = initial_board.get_hashable_key() 
    visited = {start_key} 
    parent_map = {} 
    solution_key = dfs_recursive_helper(initial_board, visited, parent_map, start_key)
    stats = {"count": 0}
    end_time = time.time() 
    execution_time = end_time - start_time
    
    if solution_key is not None:
        solution_path = reconstruct_path(parent_map, start_key, solution_key)
        print(f"found  {len(solution_path)}. take: {execution_time:.2f} seconds")
        return {
            "path": solution_path,
            "time": execution_time,
            "memory": len(visited),
            "explored_states": stats["count"],
            "path_length": len(solution_path)
        }
    else:
        print(f"no solution {execution_time:.2f} second")
        return {
            "path": None,
            "time": execution_time,
            "memory": len(visited),
            "explored_states": stats["count"],
            "path_length": 0
        }
    
def dfs_recursive_helper(current_board: Board, visited: set, parent_map: dict, start_key):
    current_key = current_board.get_hashable_key()
    try:
        _, all_child_moves = current_board.get_possible_moves_for_board() 
    except Exception as e:
        return None
    for child_board, move_details in all_child_moves:
        child_key = child_board.get_hashable_key()
        
        if child_key not in visited:
            if child_board.is_final_state():
                parent_map[child_key] = (current_key, move_details)
                return child_key
            visited.add(child_key)
            parent_map[child_key] = (current_key, move_details)
            solution_key = dfs_recursive_helper(child_board, visited, parent_map, start_key)
            if solution_key is not None:
                return solution_key
    return None

#------------------------------------------------------------------
def BFS_solver(initial_board,max_iterations):
    start_time = time.time()
    if initial_board.is_final_state():
        return []
    start_key = initial_board.get_hashable_key()
    # print(start_key)
    visited = {start_key}
    queue = deque([(initial_board,start_key, 0)])
    # print(queue)
    parent_map = {}
    # state_to_board = {start_key: initial_board}
    # print(state_to_board)
    states_processed = 0
    iterations = 0
    max_depth_reached = 0
    # and iterations < max_iterations
    current_layer_start_time = time.time()
    while queue  : 
        current_board, current_key, current_depth = queue.popleft()
        states_processed += 1
        # current_board = state_to_board[current_key]
        if current_depth > max_depth_reached:
            time_for_previous_layer = time.time() - current_layer_start_time
            print(f"Time for Depth {max_depth_reached}: {time_for_previous_layer:.4f} seconds")
            
            max_depth_reached = current_depth
            print(f"--- STARTING Depth {max_depth_reached} ---")

            current_layer_start_time = time.time()
        # print(current_board)
        try:
            _, all_child_moves = current_board.get_possible_moves_for_board() 
            # print(all_child_moves)
        except Exception:
            print("error")
            end_time = time.time()
            execution_time = end_time - start_time
            return {
                "path": [],
                "time": execution_time,
                "memory": 1,
                "explored_states": 0,
                "path_length": 0
            }
        new_depth = current_depth + 1
        for child_board, move_details in all_child_moves:
            child_key = child_board.get_hashable_key()
            # print(child_key)
            if child_key not in visited:
                if child_board.is_final_state():
                    parent_map[child_key] = (current_key, move_details)
                    end_time = time.time() 
                    execution_time = time.time() - start_time
                    solution_path = reconstruct_path(parent_map, start_key, child_key)
                    return {
                        "path": solution_path,
                        "time": execution_time,
                        "memory": len(visited),
                        "explored_states": states_processed,
                        "path_length": len(solution_path)
                    }
                visited.add(child_key)
                parent_map[child_key] = (current_key, move_details)
                # state_to_board[child_key] = child_board
                queue.append((child_board,child_key, new_depth))
        
        # iterations+= 1
        
    end_time = time.time() 
    execution_time = end_time - start_time
    if iterations >= max_iterations:
        print("max")
    if not queue:
        print("no solutions")
    return {
        "path": None,
        "time": execution_time,
        "memory": len(visited),
        "explored_states": states_processed,
        "path_length": 0
    }

#-------------------------------------------------
#هاد التابع بركز ع اقل تكلفة بالمسار 
# التكلفة هي طبيعة الكتلة و اتجاه حركتها
#التكلفة بتقل لما بتقرب عالاطراف وبتقل اكتر وقت تخرج كتلة برا الرقعة 
#وكمان حسب الكتلة كيف مكونة وتكلفتها 

def UCS_solver(initial_board):
    start_time = time.time()
    if initial_board.is_final_state():
        return {
            "path": [],
            "time": execution_time,
            "memory": 1,
            "explored_states": 0,
            "path_length": 0
        }
    
    start_key = initial_board.get_hashable_key()
    visited = {start_key: 0} 
    priority_queue = []
    counter = 0 
    heapq.heappush(priority_queue, (0, counter, initial_board, start_key))
    parent_map = {}
    states_count = 0
    while priority_queue:
        curr_cost, _, curr_board, curr_key = heapq.heappop(priority_queue)
        if curr_board.is_final_state(): 
            execution_time = time.time() - start_time
            solution_path = reconstruct_path(parent_map, start_key, curr_key) 
            return {
                "path": solution_path,
                "time": execution_time,
                "memory": len(visited),
                "explored_states": states_count,
                "path_length": len(solution_path)
            }
        states_count += 1
        if states_count % 1000 == 0:
            print(f"Iterations: {states_count} | Queue Size: {len(priority_queue)} | Cost: {curr_cost}")

        _, all_child_moves = curr_board.get_possible_moves_for_board()
        
        for child_board, move_details in all_child_moves:
            child_key = child_board.get_hashable_key()
            block_id, row_off, col_off = move_details
            moved_block = curr_board.BlockObjects[block_id]
            move_cost = moved_block.cost
            direction_bonus = 0
            if moved_block.direction == 'horizontal': 
                if (col_off > 0 and moved_block.cols > child_board.cols / 2) or \
                (col_off < 0 and moved_block.cols <= child_board.cols / 2):
                    direction_bonus = 2 

            elif moved_block.direction == 'vertical':
                if (row_off > 0 and moved_block.rows > child_board.rows / 2) or \
                (row_off < 0 and moved_block.rows <= child_board.rows / 2):
                    direction_bonus = 2 

            exit_bonus = 100 if len(child_board.BlockObjects) < len(curr_board.BlockObjects) else 0
            
            new_total_cost = max(0, curr_cost + move_cost - direction_bonus - exit_bonus)
            
            if child_key not in visited or new_total_cost < visited[child_key]:
                visited[child_key] = new_total_cost
                parent_map[child_key] = (curr_key, move_details)
                counter += 1
                heapq.heappush(priority_queue, (new_total_cost, counter, child_board, child_key))
                
    return {
        "path": None,
        "time": execution_time,
        "memory": len(visited),
        "explored_states": states_count,
        "path_length": 0
    }
#------------------------------------------------------
# هون اهم شي  المسافة والقرب من البوابات
def hill_climbing_solver(initial_board):
    start_time = time.time()
    current_board = initial_board
    path = [] 
    states_processed = 0
    visited = {current_board.get_hashable_key()}
    while not current_board.is_final_state():

        states_processed += 1
        _, all_child_moves = current_board.get_possible_moves_for_board()
        if not all_child_moves:
            execution_time = time.time() - start_time
            print("No more moves available, stuck!")
            return {
                "path": None,
                "time": execution_time,
                "memory": len(visited),
                "explored_states": states_processed,
                "path_length": 0
            }
        best_child = None
        best_score = float('inf')
        best_move_details = None
        for child_board, move_details in all_child_moves:
            child_key = child_board.get_hashable_key()
            if child_key in visited:
                continue
            score = calculate_board_heuristic(child_board)
            if score < best_score:
                best_score = score
                best_child = child_board
                best_move_details = move_details

        if best_child is None:
            print("we are stuck in  (Local Maxima).")
            execution_time = time.time() - start_time
            return {
                "path": None,
                "time": execution_time,
                "memory": len(visited),
                "explored_states": states_processed,
                "path_length": 0
            }
        current_board = best_child
        visited.add(current_board.get_hashable_key())
        path.append(best_move_details)
        
        if len(path) > 500:
            execution_time = time.time() - start_time
            return {
                "path": None,
                "time": execution_time,
                "memory": len(visited),
                "explored_states": states_processed,
                "path_length": 0
            }
    execution_time = time.time() - start_time
    return {
        "path": path,
        "time": execution_time,
        "memory": len(visited),
        "explored_states": states_processed,
        "path_length": len(path)
    }

def calculate_board_heuristic(board):
    h = len(board.BlockObjects) * 100 
    for block_id, block in board.BlockObjects.items():
        possible_gates = board.check_gate_arround(block_id)
        if possible_gates:
            if board.check_ifCanBolckGetOutThisGate(block_id, possible_gates):
                h -= 80 
            else:
                h += 10 
        else:
            matching_gates = [g for g in board.ExitGates.values() 
                             if g.required_color.lower() == block.color.lower()]
            if matching_gates:
                dists = []
                for gate in matching_gates:
                    block_span = block.get_block_span(gate.side)
                    if block_span <= gate.required_length:
                        for g_row, g_col in gate.contact_coords:
                            dist = abs(block.start_row - g_row) + abs(block.start_col - g_col)
                            if gate.side in ["Left", "Right"]:
                                dist += abs(block.start_row - g_row) * 10 
                            else:
                                dist += abs(block.start_col - g_col) * 10
                            dists.append(dist)
                    else:
                        h += 200
                if dists:
                    h += min(dists)
                else:
                    h += 150 
            else:
                h += 50
    return h
#محسن **************
#------------------------------------------------------------
def hill_climbing_beam_solver(initial_board, beam_width=3):
    start_time = time.time()
    current_states = [(calculate_board_heuristic(initial_board), initial_board, [])]
    visited = {initial_board.get_hashable_key()}
    states_count = 0
    while current_states:
        candidates = []
        
        for curr_score, curr_board, curr_path in current_states:
            
            if curr_board.is_final_state():
                execution_time = time.time() - start_time
                return {
                    "path": curr_path,
                    "time": execution_time,
                    "memory": len(visited),
                    "explored_states": states_count,
                    "path_length": len(curr_path)
                }
            
            states_count += 1
            _, all_child_moves = curr_board.get_possible_moves_for_board()
            
            for child_board, move_details in all_child_moves:
                child_key = child_board.get_hashable_key()
                
                if child_key not in visited:
                    visited.add(child_key)
                    score = calculate_board_heuristic(child_board)
                    
                    candidates.append((score, child_board, curr_path + [move_details]))

        candidates.sort(key=lambda x: x[0])
        if candidates:
            best_current_score = candidates[0][0]
            print(f"Checking {len(candidates)} moves... Best Score found: {best_current_score} | Beam Width: {len(current_states)}")

        current_states = candidates[:beam_width]
        
        if not current_states:
            print("Stuck! No more paths to explore.")
            break
            
        if len(visited) > 10000: 
            print("Search space too large, stopping.")
            break

    execution_time = time.time() - start_time
    return {
        "path": None,
        "time": execution_time,
        "memory": len(visited),
        "explored_states": states_count,
        "path_length": 0
    }

# -------------------------------------------------------------
def a_star_solver(initial_board):
    start_time = time.time()
    start_key = initial_board.get_hashable_key()
    actual_steps_taken_so_far = {start_key: 0} #هذي التكلفة
    h_score = calculate_board_heuristic(initial_board) #هذه تكلفة تقديرية
    f_score = 0 + h_score #وهي الواقعية
    priority_queue = []
    counter = 0
    heapq.heappush(priority_queue, (f_score, counter, initial_board, 0))
    
    parent_map = {}
    states_explored_count = 0
    while priority_queue:
        (total_expected_cost, 
         _, 
         current_board, 
         actual_steps_from_start) = heapq.heappop(priority_queue)
        
        current_state_key = current_board.get_hashable_key()

        if current_board.is_final_state():
            execution_time = time.time() - start_time
            solution_path = reconstruct_path(parent_map, start_key, current_state_key)
            return {
                "path": solution_path,
                "time": execution_time,
                "memory": len(actual_steps_taken_so_far),
                "explored_states": states_explored_count,
                "path_length": len(solution_path)
            }
        states_explored_count += 1
        if states_explored_count % 1000 == 0:
            print(f"Explored: {states_explored_count} | Queue: {len(priority_queue)} | Current Total Cost: {total_expected_cost}")

        _, all_possible_moves = current_board.get_possible_moves_for_board()
        
        for child_board, move_details in all_possible_moves:
            child_state_key = child_board.get_hashable_key()
            new_actual_steps = actual_steps_from_start + 1
            if child_state_key not in actual_steps_taken_so_far or new_actual_steps < actual_steps_taken_so_far[child_state_key]:
                
                actual_steps_taken_so_far[child_state_key] = new_actual_steps
                parent_map[child_state_key] = (current_state_key, move_details)
                
                estimated_remaining = calculate_board_heuristic(child_board)
                
                total_path_cost_estimate = new_actual_steps + estimated_remaining
                
                counter += 1
                heapq.heappush(priority_queue, (total_path_cost_estimate, 
                                               counter, 
                                               child_board, 
                                               new_actual_steps))
                                               
    execution_time = time.time() - start_time
    return {
        "path": None,
        "time": execution_time,
        "memory": len(actual_steps_taken_so_far),
        "explored_states": states_explored_count,
        "path_length": 0
    }