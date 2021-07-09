
#Syntonics Filesystem Management

import sklearn 
delimiters = {' ','-','_'}

def get_type(name):
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

class Node:
    def __init__(self,name):
        self.name = name
        self.type = get_type(name)
        self.children = []
    
    def add_child(self,child):
        self.children.append(child)
    
    def get_children(self):
        yield from self.children
    
    def get_all_children_names(self):
        for child in self.children:
            yield child.name
            yield from child.get_all_children_names()
    
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
        return 'Node('+self.name+')'
    
with open('cm.txt') as f:
    filenames = f.read().split('\n')

directory = Node('directory')
parent = None

for file in filenames:
    if file:
        count = 0
        while file and not file[0].isalnum():
            count+=1
            file = file[1:]
        if count < 12 and file:
            new_file = Node(file)
            if count < 8:
                parent = new_file
                directory.add_child(new_file)
            else:
                parent.add_child(new_file)



print(directory)
for child in directory.get_children():
    not_printed = True
    if not child.type:
        not_printed = False
        # print('\t'+ str(child))
    # print(child.children)
    for grandchild in child.get_children():
        if not grandchild.type:
            # if not_printed: 
            #     not_printed = False
            #     # print('\t'+ str(child))
            if str(grandchild)[len(str(grandchild))-4:len(str(grandchild))] == '.pdf':
                print('\t\t'+ str(grandchild))
 
# for file in directory.get_all_children_names():
#     if file[len(file)-4:len(file)] == '.pdf':
#         print(file)
    







   
    # stripped_filenames = set()
    # for filename in filenames:
    #     stripped_filenames.add(filename.strip('+- \\|'))
    # stripped_filenames.remove('')
    
    # pn = []
    # for file in stripped_filenames:
    
    #     if (len(file) > 11 and file[6] == '-' and  file[11] in delimiters):
    #         # if file[len(file-3):len(file)] == 'Rev':
    #         #     print(file)
    #         pn.append(file)
    # print((pn[569][(len(file)-3):len(file)]))
    

    