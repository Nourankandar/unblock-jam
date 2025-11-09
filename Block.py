class Block:
    def __init__(self, block_data):
        self.id = block_data['id']
        self.color = block_data['color']
        self.is_target = block_data['is_target']
        self.start_row = block_data['start_row']
        self.start_col = block_data['start_col']
        self.shape_coords = [tuple(c) for c in block_data['shape_coords']]
    
    def get_absolute_coords(self):
        absolute_coords = []
        for r_rel, c_rel in self.shape_coords:
            r_abs = self.start_row + r_rel
            c_abs = self.start_col + c_rel
            absolute_coords.append((r_abs, c_abs))
        return absolute_coords