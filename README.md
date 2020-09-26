# wg_conf

![GitHub](https://img.shields.io/github/license/galenguyer/wg_conf?style=for-the-badge) 
![PyPI](https://img.shields.io/pypi/v/wg-conf?style=for-the-badge)
![Travis (.org)](https://img.shields.io/travis/galenguyer/wg_conf?style=for-the-badge)

Python library to read, edit, and save [Wireguard](https://www.wireguard.com/) configuration files

### Installation

Install using pip:
```
python3 -m pip install wg-conf
```

### Methods

Load a configuration file:
```
import wg_conf

wc = wg_conf.WireguardConfig('/etc/wireguard/wg0.conf')
```

Write a configuration file to disk:
```
wc.write_file()
```

##### Edit the interface

Add an attribute to the interface
```
wc.add_interface_attr('AttributeKey', 'AttributeValue')
```
add_interface_attr **will not** overwrite an existing attribute. If you are sure you want to overwrite an existing attribute, use `set_interface_attr` with the same parameters. Otherwise, an Exception will be thrown if you try to overwrite an existing attribute


Remove an attribute from the interface
```
wc.del_interface_attr('AttributeKey')
```
If no matching attribute is found, no change will be made

##### Edit a peer

Add an attribute to a peer
```
wc.add_peer_attr('PeerPublicKey', 'AttributeKey', 'AttributeValue')
```
add_peer_attr **will not** overwrite an existing attribute. If you are sure you want to overwrite an existing attribute, use `set_peer_attr` with the same parameters. Otherwise, an Exception will be thrown if you try to overwrite an existing attribute


Remove an attribute from a peer
```
wc.del_interface_attr('PeerPublicKey', 'AttributeKey')
```
If no matching peer or attribute is found, no change will be made

##### Create or remove a peer

Create a peer given a public key:
```
wc.create_peer('PeerPublicKey')
```
You can now use `add_peer_attr` to configure the peer as you wish

Delete a peer given a public key:
```
wc.del_peer('PeerPublicKey')
```

### Build pypi package
Build a binary and source distribution for pypi
```
python3 setup.py sdist bdist_wheel
```
Push to pypi
```
python3 -m twine upload dist/*
```
