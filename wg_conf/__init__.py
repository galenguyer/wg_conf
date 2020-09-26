"""
Simple library to read, edit, and save Wireguard configuration files
"""

from itertools import groupby

class WireguardConfig:
    """
    representation of the wireguard configuration file,
    allowing easy access to peer and interface properties
    """
    def __init__(self, file_name:str=None):
        self._file_name = file_name
        self.interface = None
        self.peers = dict()
        self._lines = []
        self.read_file()
        self.parse_lines()


    def read_file(self):
        """read the config file into the line array"""
        self.interface = None
        self.peers = dict()
        self._lines = []
        with open(self._file_name, 'r') as input_file:
            self._lines = [line.strip() for line in input_file.readlines()]


    def write_file(self):
        """write all lines to the given file"""
        with open(self._file_name, 'w') as output_file:
            output_file.writelines([line + '\n' for line in self._lines])


    @staticmethod
    def parse_line(line):
        """parse each line by key = value # comment"""
        data, _, comment = line.partition('#')
        data, comment = data.strip(), comment.strip()
        key, _, value = data.partition('=')
        key, value = key.strip(), value.strip()
        return key, value, comment


    def parse_lines(self):
        """
        read each line, parse it, and put it into the correct object
        on the config object
        """
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
        """add a given key and value to the interface with an optional comment"""
        if comment is None:
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
                raise Exception(f'Attribute {key} already found in Interface. ' + \
                    'Use set_interface_attr to overwrite.')
        self._lines.insert(index, new_line)
        self.parse_lines()


    def del_interface_attr(self, key):
        """
        remove an attribute from the interface.
        complete silently if the key is not found
        """
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
        """
        attempt to delete and then add an attribute to the interface
        this ensures it will overwrite an existing attribute or just add it if it doens't exist
        """
        self.del_interface_attr(key)
        self.add_interface_attr(key, value, comment)


    def add_peer_attr(self, publickey, key, value, comment=None):
        """add a given key and value with optional comment to a peer as specified by public key"""
        if comment is None:
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
                raise Exception(f'Attribute {key} already found in Peer {publickey}. ' + \
                    'Use set_peer_attr to overwrite.')
        self._lines.insert(end_index, new_line)
        self.parse_lines()


    def del_peer_attr(self, publickey, key):
        """delete a given attribute by key from a peer as specified by public key"""
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
        """
        attempt to delete and then add an attribute to a peer as specified by public key
        this ensures it will overwrite an existing attribute or just add it if it doens't exist
        """
        self.del_peer_attr(publickey, key)
        self.add_peer_attr(publickey, key, value, comment)


    def create_peer(self, publickey):
        """create a new peer given a public key"""
        for line in self._lines:
            if self.parse_line(line)[1] == publickey:
                raise Exception(f'A peer with the public key {publickey} already exists, ' + \
                    'cannot create a new one')
        self._lines.append('')
        self._lines.append('[Peer]')
        self._lines.append(f'PublicKey = {publickey}')
        self.parse_lines()


    def del_peer(self, publickey):
        """attempt to delete a peer specified by a public key"""
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
        """return all peer keys"""
        return self.peers.keys()


    def get_peer(self, publickey):
        """return a peer by a given publickey"""
        return self.peers.get(publickey)


if __name__ == '__main__':
    print('This is a library and not meant to be called directly. ' + \
        'Please import it using "import wg_conf"')
