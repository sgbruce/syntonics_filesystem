
#Syntonics Filesystem Management

import pandas as pd 
from zipfile import ZipFile 


acceptable_chars = {'1','2','3','4','5','6','7','8','9','0','X','-','B'}
feature_vectors = {}
def get_pn(name):
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

def get_extension(name):
    if '.' in name:
        return name[name.index('.'):].lower()
    return None


# def zip_file(name,parent_name):
    # with ZipFile(name+'.zip', 'w') as f:
    
        # for file in file_paths:
        #   f.write(file)
    # return name+'.zip'
      

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
                new_file.parent = directory
                directory.add_child(new_file)
            else:
                new_file.parent = parent
                parent.add_child(new_file)

filename_map = {}
missing_files = {}
extra_files = {}

for child in directory:
    pn = get_pn(child.name)
    path = 'directory/'+child.name
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
                        elif gc.type == 'fab' and gc.extension == '.zip':
                            filename_map[path]['FAB_'+str(get_pn(gc.name))] = gc.name
                        elif gc.type == 'src' and gc.extension == '.zip':
                            filename_map[path]['SRC_'+str(get_pn(gc.name))] = gc.name
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
                elif gc.type == 'fab' and gc.extension == '.zip':
                    filename_map[path]['FAB'] = gc.name
                elif gc.type == 'src' and gc.extension == '.zip':
                    filename_map[path]['SRC'] = gc.name
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

filename_csv_arr = []
for path in filename_map:
    if 'X' in get_pn(path):
        vals = list(filename_map[path].values())
        for i in range(0,len(vals)-4,5):
            row = [path,vals[0+i],vals[1+i],vals[2+i],vals[3+i],vals[4+i]]
            filename_csv_arr.append(row)
        
    else:
        filename_csv_arr.append([path]+ list(filename_map[path].values()))

df = pd.DataFrame(filename_csv_arr,columns = ['path','BOM.xls','BOM.pdf','SCH','FAB','SRC'])
df.T
df.to_csv('filemap.csv')
with open('extra_files.txt','w') as f:
    for key in extra_files:
        f.write(key+'\n')
        for val in extra_files[key]:
            f.write('\t'+val+'\n')
                
              
                
      


    