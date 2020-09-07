'''
Create fingerprint for a url(a node)
'''


# library
import hashlib
import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# func



def request_fingerprint(node):
    '''
    request the fingerprint of a node

    node : node representing a page

    return : a string as the node's fingerprint
    '''

    def to_bytes(str, encoding='utf-8'):
        '''
        string to byte

        str : a string to encode
        encoding : encoding type, default='utf-8'

        return : bytes
        '''
        return str.encode(encoding)
    
    hasher = hashlib.sha1()

    # components those defining a unique page
    components = []  # components to represent a node.
    components.append(node.url)
    # components.append(node.title)
    components.append(node.content)
    # to be complemented

    for part in components:
        try:
            hasher.update(to_bytes(part))
        except:
            hasher.update(part)

    return hasher.hexdigest()


if __name__ == '__main__':
    pass