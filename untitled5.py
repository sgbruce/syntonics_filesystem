#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 15:30:24 2021

@author: sam
"""
from zipfile import ZipFile
from pathlib import Path



with ZipFile('Test'+'.zip', 'w') as f:
    def get_files(p):
        yield p
        if p.is_dir():
            for file in p.iterdir():
                yield from get_files(file)
    c = Path('Test')
    for file in get_files(c):
        f.write(file)
    