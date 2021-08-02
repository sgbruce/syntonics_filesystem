
#Syntonics Filesystem Management

import pandas as pd 
from zipfile import ZipFile 
from pathlib import Path

#list of acceptable part number characters
acceptable_chars = {'1','2','3','4','5','6','7','8','9','0','X','-','B'}

def get_pn(name):
    ''' 
    Given a filename, returns the part number if present, else None
    '''
    name = str(name)
    if not name:
        return None
    pn = None
    i=0
    while not pn and i <= len(name)-11:
        substr = name[0+i:11+i]
        valid = True
        for char in substr:
            if char not in acceptable_chars:
                valid = False
                break
        if valid:
            pn = name[0+i:11+i]
        i+=1
    return pn

def get_type(name):
    ''' 
    given a filename, returns the filetype if present, else None
    '''
    n = name.lower()
    if 'bom' in n:
        return 'bom'
    if 'cca' in n:
        return 'cca'
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
    given a filename, returns the exptension if present, else None
    '''
    if '.' in name:
        return name[name.index('.'):].lower()
    return None


def zip_file(filepath):
    if get_extension(filepath) == '.zip':
        return filepath
    with ZipFile(filepath+'.zip', 'w') as f:
        def get_files(p):
            yield p
            if p.is_dir():
                for file in p.iterdir():
                    yield from get_files(file)
        c = Path(filepath)
        for file in get_files(c):
            f.write(file)
    return filepath+'.zip'
          

class Node:
    def __init__(self,name,parent):
        self.name = name
        self.pn = get_pn(name)
        self.parent = parent
        self.type = get_type(name)
        self.extension = get_extension(name)
        self.children = []
        self.filepath = str(self.parent)+'/'+self.name
    
    def add_child(self,child):
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
    
    def find_node(self,name):
        if self.name == name:
            return self
        for child in self.children():
            result = self.find_node(child,name)
            if result:
                return result
        return None
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'Node({self.name},{self.parent})'


''' *** Test Code *** '''

# with open('cm.txt') as f:
#     filenames = f.read().split('\n')

# directory = Node('directory',None)
# parent = None

# for file in filenames:
#     if file:
#         count = 0
#         while file and not file[0].isalnum():
#             count+=1
#             file = file[1:]
#         if count < 12 and file:
            
#             if count < 8:
#                 new_file = Node(file,directory)
#                 parent = new_file
#                 directory.add_child(new_file)
#             else:
#                 new_file = Node(file,parent)
#                 parent.add_child(new_file)

''' *** End Test Code *** '''

filename_map = {}
missing_files = {}#debug
extra_files = {}


directory = Path()

def make_file_tree(directory,directory_node):
    if directory.is_dir():
        for file in directory.iterdir():
            file_node = Node(file.name,file.parent)
            directory_node.add_child(file_node)
            make_file_tree(file, file_node)
    return directory_node

directory = make_file_tree(directory, Node(directory.name,directory.parent))
        
def print_all_files(directory):#debug
    if directory.children:
        for child in directory:
            print(child)
            print_all_files(child)

# print_all_files(directory)
    

#make metyhod that contains duplicate code below

def assign_node(pn,node):
    if not pn in filename_map:
        filename_map[pn] = {'parent path':node.parent}
                #need to add logic to add source and fab to all if XX and no pn
    if node.type in ('src','fab'):
        if node.extension == None and not node.type in filename_map[node.pn]:
            filename = zip_file(node.filepath)
            filename_map[pn][node.type] = filename
        else:
            filename_map[pn][node.type] = node.name
    else:
        filename_map[pn][node.type] = node.name


def make_file_dict(directory):
    for node in directory.get_all_children():
        if node.type:
            if node.pn:
                assign_node(node.pn,node)
            else:
                assign_node(get_pn(node.parent),node)
                
        else:
            if node.pn:
                if node.extension:
                    if not node.pn in filename_map:
                        filename_map[node.pn] = {'parent path':node.parent}
                    if not 'extra' in filename_map[node.pn]:
                        filename_map[node.pn]['extra'] = []
                    filename_map[node.pn]['extra'].append(node.name)
                
make_file_dict(directory)
print(filename_map)               
                        
                        


'''

for child in directory:
    pn = get_pn(child.name)
    path = child.filepath
    if pn:
        if 'X' in pn:
            filename_map[path] = {}
            try:
                part_numbers = set(get_pn(gc.name) for gc in child)
                if None in part_numbers:
                    part_numbers.remove(None)
            
                for part in part_numbers:
                    filename_map[path]['BOM_'+part+'.xlsx'] = None
                    filename_map[path]['BOM_'+part+'.pdf'] = None
                    filename_map[path]['FAB_'+part] = None
                    filename_map[path]['SCH_'+part] = None
                    filename_map[path]['SRC_'+part] = None
                    for gc in child:
                        if gc.extension in ('.xlsx','.xls') and gc.type in (None,'bom'):
                            filename_map[path]['BOM_'+get_pn(gc.name)+'.xlsx'] = gc.name
                        elif gc.extension == '.pdf' and gc.type == 'bom':
                            filename_map[path]['BOM_'+get_pn(gc.name)+'.pdf'] = gc.name
                        elif gc.type == 'sch':
                            filename_map[path]['SCH_'+str(get_pn(gc.name))] = gc.name
                        elif gc.type == 'fab':
                            filename_map[path]['FAB_'+str(get_pn(gc.name))] = zip_file(gc.filepath).split('/')[-1]
                        elif gc.type == 'src':
                            filename_map[path]['SRC_'+str(get_pn(gc.name))] = zip_file(gc.filepath).split('/')[-1]
            except:
                print(child,child.children)
                print(set(get_pn(gc.name) for gc in child))
                raise Exception()
        else:
            if not path in filename_map:
                filename_map[path] = {'BOM.xlsx':None,'BOM.pdf':None,'SCH':None,'FAB':None,'SRC':None}
            for gc in child:
                if gc.extension in ('.xlsx','.xls') and gc.type in (None,'bom'):
                    filename_map[path]['BOM.xlsx'] = gc.name
                elif gc.extension == '.pdf' and gc.type == 'bom':
                    filename_map[path]['BOM.pdf'] = gc.name
                elif gc.type == 'sch':
                    filename_map[path]['SCH'] = gc.name
                elif gc.type == 'fab':
                    filename_map[path]['FAB'] = zip_file(gc.filepath).split('/')[-1]
                elif gc.type == 'src':
                    filename_map[path]['SRC'] = zip_file(gc.filepath).split('/')[-1]
        for key in filename_map[path]:
            if not filename_map[path][key]:
                if path in missing_files:
                    missing_files[path].append(key)
                else:
                    missing_files[path] = [key,]
        files = set(filename_map[path].values())
        for gc in child:
            if not gc.name in files:
                if path in extra_files:
                    extra_files[path].append(gc.name)
                else:
                    extra_files[path] = [gc.name,]
'''
# filename_csv_arr = []
# for path in filename_map:
#     if 'X' in get_pn(path):
#         vals = list(filename_map[path].values())
#         for i in range(0,len(vals)-4,5):
#             row = [path,vals[0+i],vals[1+i],vals[2+i],vals[3+i],vals[4+i]]
#             filename_csv_arr.append(row)
        
#     else:
#         filename_csv_arr.append([path]+ list(filename_map[path].values()))

# df = pd.DataFrame(filename_csv_arr,columns = ['path','BOM.xls','BOM.pdf','SCH','FAB','SRC'])
# df.T
# df.to_csv('filemap.csv')
# with open('extra_files.txt','w') as f:
#     for key in extra_files:
#         f.write(key+'\n')
#         for val in extra_files[key]:
#             f.write('\t'+val+'\n')
                
                
      


    