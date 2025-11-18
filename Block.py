class Block:
    def __init__(self, block_data):
        self.id = block_data['id']
        self.color = block_data['color']
        self.start_row = block_data['start_row']
        self.start_col = block_data['start_col']
        self.shape_coords = [tuple(c) for c in block_data['shape_coords']]
        self.direction = block_data.get('direction', 'both')
    
    def get_absolute_coords(self):
        absolute_coords = []
        for r_rel, c_rel in self.shape_coords:
            r_abs = self.start_row + r_rel
            c_abs = self.start_col + c_rel
            absolute_coords.append((r_abs, c_abs))
        return absolute_coords
    
     #هي الدالة بتحسب طول وعرض الكتلة 
    def get_dimensions(self):
        if not self.shape_coords:
            return (0, 0)
        
        r_rel_min = min(r_rel for r_rel, c_rel in self.shape_coords)
        r_rel_max = max(r_rel for r_rel, c_rel in self.shape_coords)
        c_rel_min = min(c_rel for r_rel, c_rel in self.shape_coords)
        c_rel_max = max(c_rel for r_rel, c_rel in self.shape_coords)

        rows_span = r_rel_max - r_rel_min + 1
        cols_span = c_rel_max - c_rel_min + 1
        
        return (rows_span, cols_span)
    
    def copy(self):
        block_data = {
            'id': self.id,
            'color': self.color,
            'start_row': self.start_row,
            'start_col': self.start_col,
            'shape_coords': [[r, c] for r, c in self.shape_coords]
        }
        new_block = Block(block_data)
        return new_block
    def get_border_coords(self):
        """
        ترجع مجموعة (set) من الإحداثيات المطلقة للخلايا التي تلامس
        الكتلة (الـ Block) ولكنها لا تنتمي إليها.
        """
        block_coords = set(self.get_absolute_coords())
        border_coords = set()
        
        neighbors_deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        

        for r_abs, c_abs in block_coords:

            for dr, dc in neighbors_deltas:
                r_neighbor = r_abs + dr
                c_neighbor = c_abs + dc
                neighbor_coord = (r_neighbor, c_neighbor)
                border_coords.add(neighbor_coord)
        
        final_border_coords = border_coords - block_coords
        
        return final_border_coords
    def __repr__(self):
        """
        تُرجع تمثيلاً نصيًا واضحًا وموجزًا للكائن،
        يتم استخدامه عند طباعة الكائن مباشرة.
        """
        return (f"Block(ID={self.id}, Color='{self.color}', "
                f"Start=({self.start_row}, {self.start_col}), "
                f"Shape={len(self.shape_coords)} cells)")