# Syntonics Filesystem Management

import pandas as pd
from zipfile import ZipFile
from pathlib import Path

# list of acceptable part number characters
acceptable_chars = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'X', '-', 'B'}


def get_pn(name):
    """
    Given a filename, returns the part number if present, else None
    """
    name = str(name)
    if not name:
        return None
    pn = None
    i = 0
    while not pn and i <= len(name) - 11:
        substr = name[0 + i:11 + i]
        valid = True
        for char in substr:
            if char not in acceptable_chars:
                valid = False
                break
        if valid:
            pn = name[0 + i:11 + i]
        i += 1
    return pn


def get_type(name):
    ''' 
    given a filename, returns the filetype if present, else None
    '''
    n = name.lower()
    if 'bom' in n:
        return 'bom'
    # if 'cca' in n:
    #     return 'cca'
    if 'asm' in n or 'assembly' in n or 'assy' in n:
        return 'asm'
    if 'schematic' in n or 'sch' in n:
        return 'sch'
    if 'source' in n or 'src' in n:
        return 'src'
    if 'fab' in n:
        return 'fab'
    return None


def get_extension(name):
    ''' 
    given a filename, returns the extension if present, else None
    '''
    if '.' in name:
        return name[name.index('.'):].lower()
    return None


def get_rev(name, parent=None):
    '''
    given a filename and a parent name, returns the revision if present, if not looks for the parent revision,
    if none returns RX
    '''
    if 'rev' in name.lower():
        ind = name.lower().index('rev')
        if name[ind + 3] in {' ', '-', '_'}:
            return name[ind + 4:ind + 6]
        return name[ind + 3:ind + 5]
    if 'R' in name and name[name.index('R') + 1].isupper() and name[name.index('R') - 1] in {'_', ' ', '-'}:
        return name[name.index('R'):name.index('R') + 2]
    if 'X' in name and name[name.index('X') + 1].isupper() and name[name.index('X') - 1] in {'_', ' ', '-'}:
        return name[name.index('X'):name.index('X') + 2]
    if parent:
        return get_rev(parent)
    return 'RX'


def zip_file(filepath):
    '''
    given a filepath, returns a file location to a zipped version of the file
    '''
    if get_extension(filepath) == '.zip':
        return filepath
    with ZipFile(filepath + '.zip', 'w') as f:
        def get_files(p):
            yield p
            if p.is_dir():
                for file in p.iterdir():
                    yield from get_files(file)

        c = Path(filepath)
        for file in get_files(c):
            f.write(file)
    return filepath + '.zip'


class Node:
    def __init__(self, name, parent):
        self.name = name
        self.pn = get_pn(name)
        self.rev = get_rev(name, str(parent))
        self.parent = parent
        self.type = get_type(name)
        self.extension = get_extension(name)
        self.children = []
        self.filepath = str(self.parent) + '/' + self.name

    def add_child(self, child):
        self.children.append(child)

    def __iter__(self):
        yield from self.children

    def get_all_children_names(self):
        for child in self.children:
            yield child.name
            yield from child.get_all_children_names()

    def get_all_children(self):
        for child in self.children:
            yield child
            yield from child.get_all_children()

    def find_node(self, name):
        if self.name == name:
            return self
        for child in self.children:
            result = Node.find_node(child, name)
            if result:
                return result
        return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Node({self.name},{self.parent})'


filename_map = {}
missing_files = {}  # debug
extra_files = {}

directory = Path()


def make_file_tree(directory, directory_node):
    if directory.is_dir():
        for file in directory.iterdir():
            file_node = Node(file.name, file.parent)
            directory_node.add_child(file_node)
            make_file_tree(file, file_node)
    return directory_node


directory = make_file_tree(directory, Node(directory.name, directory.parent))


def print_all_files(directory):  # debug
    if directory.children:
        for child in directory:
            print(child)
            print_all_files(child)


x_list = []


def assign_node(pn, rev, node):
    if 'B' in pn:
        pn = pn[0:pn.index('B')] + '0' + pn[pn.index('B') + 1:]
    if 'X' in pn:
        x_list.append((pn, rev, node))
        return
    if not pn + rev in filename_map:
        filename_map[pn + rev] = {'parent path': node.parent}
    if node.type in ('src', 'fab'):
        if node.extension == None and not node.type in filename_map[pn + rev]:
            filename = zip_file(node.filepath)
            filename_map[pn + rev][node.type] = filename
        else:
            filename_map[pn + rev][node.type] = node.name
    elif node.type == 'bom':
        if node.extension == '.pdf':
            filename_map[pn + rev]['bom.pdf'] = node.name
        else:
            filename_map[pn + rev]['bom.xlsx'] = node.name
    else:
        filename_map[pn + rev][node.type] = node.name


def make_file_dict(directory):
    for node in directory.get_all_children():
        # print(node.name,node.type)
        if get_type(str(node.parent)) in {'src', 'fab'}:
            continue
        if node.type:
            if node.pn:
                assign_node(node.pn, node.rev, node)
                # print(filename_map[node.pn+node.rev])
            elif get_pn(node.parent):
                assign_node(get_pn(node.parent), get_rev(str(node.parent)), node)

        else:
            if node.pn:
                if 'B00' in node.pn:
                    pn = node.pn[0:node.pn.index('B00')] + '0' + node.pn[node.pn.index('B00') + 1:]
                else:
                    pn = node.pn
                if node.extension:
                    if not pn + node.rev in filename_map:
                        filename_map[pn + node.rev] = {'parent path': node.parent}
                    if not 'extra' in filename_map[pn + node.rev]:
                        filename_map[pn + node.rev]['extra'] = []
                    filename_map[pn + node.rev]['extra'].append(node.name)


make_file_dict(directory)
for pn, rev, node in x_list:
    pn_rev = pn + rev
    seen = False
    for i in range(4, 0, -1):
        if 'X' * i in pn and not seen:
            seen = True
            ind = pn.index('X' * i)
            for key in filename_map:
                # print(key[0:ind]+ ' ' + pn[0:ind] + ' '+ key[ind+i:] +' '+ pn_rev[ind+i:])
                if key[0:ind] == pn[0:ind] and key[ind + i:] == pn_rev[ind + i:]:
                    assign_node(key[0:len(key) - 2], rev, node)

filename_csv_arr = []


def add_file(type, pn_rev, lst):
    if type in filename_map[pn_rev]:
        lst.append(filename_map[pn_rev][type])
    else:
        lst.append(None)
    return lst


for pn_rev in filename_map:
    lst = []
    for el in ['parent path', 'bom.xlsx', 'bom.pdf', 'sch', 'fab', 'src', 'extra']:
        lst = add_file(el, pn_rev, lst)
    filename_csv_arr.append([pn_rev] + lst)

df = pd.DataFrame(filename_csv_arr,
                  columns=['pn+rev', 'parent path', 'bom.xlsx', 'bom.pdf', 'sch', 'fab', 'src', 'extra'])
df.T
df.to_csv('C:\\Users\\syn-plt04\\Desktop\\filemap.csv')
