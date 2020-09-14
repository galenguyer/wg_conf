class WireguardConfig:
    def __init__(self, file_name:str=None):
        self.file_name = file_name
        self.interface = None
        self.peers = dict()
        self.lines = []
        self.read_file()
        self.parse_lines()

    
    def read_file(self):
        self.interface = None
        self.peers = dict()
        self.lines = []
        with open(self.file_name, 'r') as input_file:
            self.lines = [line.strip() for line in input_file.readlines()]


    def write_file(self):
        with open(self.file_name, 'w') as output_file:
            output_file.writelines([line + '\n' for line in self.lines])


    @staticmethod
    def parse_line(line):
        data, _, comment = line.partition('#')
        data, comment = data.strip(), comment.strip()
        key, _, value = data.partition('=')
        key, value = key.strip(), value.strip()
        return key, value, comment


    def parse_lines(self):
        data_lines = [self.parse_line(line) for line in self.lines]
        section = dict()
        current_section = ''
        for line in data_lines:
            if line[0] is '':
                continue
            if line[0] in ['[Interface]', '[Peer]']:
                if current_section == '[Interface]':
                    self.interface = section
                if current_section == '[Peer]':
                    self.peers[section['PublicKey']] = section
                section = dict()
                current_section = line[0]
            else:
                section[line[0]] = line[1]
        if current_section == '[Peer]':
            self.peers[section['PublicKey']] = section
        