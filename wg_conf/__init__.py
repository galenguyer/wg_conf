from itertools import groupby

class WireguardConfig:
    def __init__(self, file_name:str=None):
        self._file_name = file_name
        self.interface = None
        self.peers = dict()
        self._lines = []
        self.read_file()
        self.parse_lines()

    
    def read_file(self):
        self.interface = None
        self.peers = dict()
        self._lines = []
        with open(self._file_name, 'r') as input_file:
            self._lines = [line.strip() for line in input_file.readlines()]


    def write_file(self):
        with open(self._file_name, 'w') as output_file:
            output_file.writelines([line + '\n' for line in self._lines])


    @staticmethod
    def parse_line(line):
        data, _, comment = line.partition('#')
        data, comment = data.strip(), comment.strip()
        key, _, value = data.partition('=')
        key, value = key.strip(), value.strip()
        return key, value, comment


    def parse_lines(self):
        self.interface = None
        self.peers = dict()
        self._lines = [line for line, _ in groupby(self._lines)]
        data_lines = [self.parse_line(line) for line in self._lines]
        section = dict()
        current_section = ''
        for line in data_lines:
            if line[0] == '':
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
        if current_section == '[Interface]':
            self.interface = section

    
    def add_interface_attr(self, key, value, comment=None):
        if comment == None:
            new_line = f'{key} = {value}'
        else:
            new_line = f'{key} = {value} # {comment}'
        section_started = False
        index = 0
        for line in self._lines:
            if line.strip() == '[Interface]':
                section_started = True
            if section_started and line.strip() in ['', '[Peer]']:
                break
            index = index + 1
        for i in range(0, index):
            if self.parse_line(self._lines[i])[0].lower() == key.lower():
                raise Exception(f'Key {key} already found in Interface. Use set_interface_attr to overwrite.')
        self._lines.insert(index, new_line)
        self.parse_lines()


    def del_interface_attr(self, key):
        section_started = False
        index = 0
        for line in self._lines:
            if line.strip() == '[Interface]':
                section_started = True
            if section_started and line.strip() in ['', '[Peer]']:
                break
            index = index + 1
        for i in range(0, index):
            if self.parse_line(self._lines[i])[0].lower() == key.lower():
                self._lines.pop(i)
        self.parse_lines()


    def set_interface_attr(self, key, value, comment=None):
        section_started = False
        index = 0
        for line in self._lines:
            if line.strip() == '[Interface]':
                section_started = True
            if section_started and line.strip() in ['', '[Peer]']:
                break
            index = index + 1
        for i in range(0, index):
            if self.parse_line(self._lines[i])[0].lower() == key.lower():
                raise Exception(f'Attribute {key} already found in Interface. Use set_interface_attr to overwrite.')
        self.del_interface_attr(key)
        self.add_interface_attr(key, value, comment)


    def add_peer_attr(self, publickey, key, value, comment=None):
        if comment == None:
            new_line = f'{key} = {value}'
        else:
            new_line = f'{key} = {value} # {comment}'
        index = 0
        start_index = 0
        end_index = 0
        section_started = False
        correct_section = False
        for line in self._lines:
            if line.strip() == '[Peer]':
                section_started = True
                start_index = index
            if section_started and not correct_section:
                pline = self.parse_line(line)
                if pline[0].lower() == 'publickey' and pline[1] == publickey:
                    correct_section = True
            if correct_section and line.strip() in ['', '[Peer]']:
                break
            end_index = end_index + 1
            index = index + 1
        for i in range(start_index, min(end_index, (len(self._lines)-1))):
            if self.parse_line(self._lines[i])[0].lower() == key.lower():
                raise Exception(f'Key {key} already found in Peer {publickey}. Use set_peer_attr to overwrite.')
        self._lines.insert(end_index, new_line)
        self.parse_lines()


    def del_peer_attr(self, publickey, key):
        index = 0
        start_index = 0
        end_index = 0
        section_started = False
        correct_section = False
        for line in self._lines:
            if line.strip() == '[Peer]':
                section_started = True
                start_index = index
            if section_started and not correct_section:
                pline = self.parse_line(line)
                if pline[0].lower() == 'publickey' and pline[1] == publickey:
                    correct_section = True
            if correct_section and line.strip() in ['', '[Peer]']:
                break
            end_index = end_index + 1
            index = index + 1
        for i in range(start_index, min(end_index, (len(self._lines)-1))):
            if self.parse_line(self._lines[i])[0].lower() == key.lower():
                self._lines.pop(i)
        self.parse_lines()


    def set_peer_attr(self, publickey, key, value, comment=None):
        index = 0
        start_index = 0
        end_index = 0
        section_started = False
        correct_section = False
        for line in self._lines:
            if line.strip() == '[Peer]':
                section_started = True
                start_index = index
            if section_started and not correct_section:
                pline = self.parse_line(line)
                if pline[0].lower() == 'publickey' and pline[1] == publickey:
                    correct_section = True
            if correct_section and line.strip() in ['', '[Peer]']:
                break
            end_index = end_index + 1
            index = index + 1
        for i in range(start_index, min(end_index, (len(self._lines)-1))):
            if self.parse_line(self._lines[i])[0].lower() == key.lower():
                raise Exception(f'Attribute {key} already found in Peer {publickey}. Use set_peer_attr to overwrite.')
        self.del_peer_attr(publickey, key)
        self.add_peer_attr(publickey, key, value, comment)


    def create_peer(self, publickey):
        for line in self._lines:
            if self.parse_line(line)[1] == publickey:
                raise Exception(f'A peer with the public key {publickey} already exists, cannot create a new one')
        self._lines.append('')
        self._lines.append('[Peer]')
        self._lines.append(f'PublicKey = {publickey}')
        self.parse_lines()


    def del_peer(self, publickey):
        index = 0
        start_index = 0
        end_index = 0
        section_started = False
        correct_section = False
        for line in self._lines:
            if line.strip() == '[Peer]':
                section_started = True
                start_index = index
            if section_started and not correct_section:
                pline = self.parse_line(line)
                if pline[0].lower() == 'publickey' and pline[1] == publickey:
                    correct_section = True
            if correct_section and line.strip() in ['', '[Peer]']:
                break
            end_index = end_index + 1
            index = index + 1
        for _ in range(start_index, min(end_index, (len(self._lines)))):
            self._lines.pop(start_index)
        self.parse_lines()


    def get_peer_keys(self):
        return self.peers.keys()


    def get_peer(self, publickey):
        return self.peers.get(publickey)


if __name__ == '__main__':
    print('This is a library and not meant to be called directly. Please import it using "import wg_conf"')
