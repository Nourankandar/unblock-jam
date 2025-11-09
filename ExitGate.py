
class ExitGate:
    def __init__(self,gate_data):
        self.id = gate_data['id']
        self.side = gate_data['side']
        self.is_wall = gate_data['is_wall']
        self.required_color = gate_data['required_color']
        self.required_length = gate_data['required_length']
        self.contact_coords = [tuple(c) for c in gate_data['contact_coords']]
    def __repr__(self):
        """
        تُرجع تمثيلاً نصياً للكائن، مما يجعله قابلاً للطباعة.
        """
        return (f"Gate ID: {self.id} | "
                f"Side: {self.side} | "
                f"Required Color: {self.required_color} | ")
                # f"Required Length: {self.required_length} | "
                # f"Coords: {self.contact_coords}")