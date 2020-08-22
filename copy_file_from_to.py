# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:14:16 2018

@author: dbanker
"""

import argparse, shutil
parser = argparse.ArgumentParser()
parser.add_argument('--from_path', dest='from_path')
parser.add_argument('--to_path', dest='to_path')
args = parser.parse_args()
from_path = args.from_path
to_path = args.to_path
print(from_path)
print(to_path)
shutil.copyfile(from_path, to_path)
print('File copied!')