import argparse
#import xml.etree.ElementTree as ET
import csv
import re
import collections
from lxml import etree

parser = argparse.ArgumentParser()
parser.add_argument('--input_file_path', dest='input_file_path')
parser.add_argument('--output_file_path', dest='output_file_path')
args = parser.parse_args()

#tree = ET.parse(args.input_file_path)
#root = tree.getroot()

raw_tree = etree.parse(args.input_file_path)
xml_root = raw_tree.getroot()
nice_tree = collections.OrderedDict()

for tag in xml_root.iter():
    path = re.sub('\[[0-9]+\]', '', raw_tree.getpath(tag))
    if path not in nice_tree:
        nice_tree[path] = []
    if len(tag.keys()) > 0:
        nice_tree[path].extend(attrib for attrib in tag.keys() if attrib not in nice_tree[path])

for path, attribs in nice_tree.items():
    indent = int(path.count('/') - 1)
    print('{0}{1}: {2} [{3}]'.format('    ' * indent, indent, path.split('/')[-1],
                                     ', '.join(attribs) if len(attribs) > 0 else '-'))


print('pause')