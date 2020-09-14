class WireguardConfig:
    def __init__(self, file_name:str=None):
        self.file_name = file_name
        self.interface = None
        self.peers = None
        self.lines = []

    
    def read_file(self):
        with open(self.file_name, 'r') as input_file:
            self.lines = [line.strip() for line in input_file.read_lines()]


    def write_file(self):
        with open(self.file_name, 'w') as output_file:
            output_file.writelines([line + '\n' for line in self.lines])
