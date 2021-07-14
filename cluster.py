
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
    if 'step' in n:
        return 'step'
    return None

def get_extension(name):
    if '.' in name:
        return name[name.index('.'):].lower()
    return None

class Node:
    def __init__(self,name):
        self.name = name
        self.type = get_type(name)
        self.extension = get_extension(name)
        self.children = []
    
    def add_child(self,child):
        self.children.append(child)
    
    def __iter__(self):
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

# for file in directory:
#     valid_count = 0
#     for child in file:
#         if child.type:
#             valid_count+=1
#     if valid_count >1:
#         child.type = 'cca'

'''
.xlsx/.xls = BOM
.docx = Rework
.gwk = Unknown
.jpg = rework/mod/installation/drawing
.ppt = user guide
.pptx = rework/conversion
.max = unknown
.sch = schematic
.zip = fab/source/cam/unnamed
.dsn = unknown
.pcb = unknown
.bmp = unknown
.brd = unknown
.pdf = schematic/assembly/bom
.csv = bom (deeper is pick place output)
.step = step
.ipc = unknown
.txt = random
.rep = unknown
'''

print(directory)
# extensions = set()
# for child in directory:
    # not_printed = True
    # if not child.type:
    #     not_printed = False
        # print('\t'+ str(child))
    # print(child.children)
    # for grandchild in child:
    #     extensions |= {grandchild.extension}
    #     # if not grandchild.type:
    #         # if not_printed: 
    #         #     not_printed = False
    #         #     # print('\t'+ str(child))
    #         # if str(grandchild)[len(str(grandchild))-4:len(str(grandchild))] == '.pdf':
    #         #     print('\t\t'+ str(grandchild))
    #     if not grandchild.extension  and not grandchild.type:
    #         # print('\t\t'+ str(grandchild))

acceptable_chars = {'1','2','3','4','5','6','7','8','9','0','X','-'}
feature_vectors = {}

def get_pn(name):
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

def get_rev(name):
    rev = None
    i = 0
    while not rev and i <= len(name)-2:
        substr = name[0+i:2+i]
        if substr[0] in ('R','X') and substr[1].isalpha():
            rev = substr
        i+=1
    return rev

for child in directory:
    vec = {'pn': get_pn(child.name),'node':child,'type':child.type,'ext':child.extension,'rev':get_rev(child.name)}
    if child.name in feature_vectors:
        print('DANGER1',child.name)
    feature_vectors[child.name] = vec
    for grandchild in child:
        vec = {'pn': get_pn(grandchild.name),'node':grandchild,'type':grandchild.type,'ext':grandchild.extension,'rev':get_rev(grandchild.name)}
    if grandchild.name in feature_vectors:
        print('DANGER2',grandchild.name)
    feature_vectors[grandchild.name] = vec
print(feature_vectors['Source Documents'])
        
            

# print(extensions)

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
    

    