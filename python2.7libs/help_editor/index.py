# -*- coding: utf-8 -*-
import hou
import os
import codecs

index_text = (
u'''/*
Title: HDA一覧
Description: HDA一覧
Author: koidtaka
*/
# HDA一覧
''')

category_text = (
u'''
## {}
''')

node_text = (
u'''
- [{node_label}](../{context}/{node_name}/{node_name})
''')


def get_node_name(node_type):
    node_comp = node_type.nameComponents()
    name_space = node_comp[1]
    base_name = node_comp[2]
    version = node_comp[3]
    if name_space:
        name_space += '--'
    if version:
        version = '-' + version
    node_name = '{}{}{}'.format(name_space, base_name, version)
    return node_name

def export_help_from_all_hda():
    output_text = index_text
    hda_files = hou.hda.loadedFiles()
    node_types = {}
    for hda_file in set(hda_files):
        if hou.getenv('HFS') in hda_file or 'packages' in hda_file:
            continue
        hda_defs = hou.hda.definitionsInFile(hda_file)
        for hda_def in hda_defs:
            node_type = hda_def.nodeType()
            node_def = node_type.definition()
            if not node_def:
                return
            context = node_type.category().name()
            node_label = node_type.description()
            node_name = get_node_name(node_type)
            node_list = node_types.get(context)
            if node_list:
                node_list.append([node_name, node_label])
            else:
                node_types[context] = [[node_name, node_label]]

    for context, node_list in node_types.items():
        output_text += category_text.format(context)
        for node_name, node_label in sorted(node_list):
            node_data = {
                'context': context,
                'node_label': node_label,
                'node_name': node_name
            }
            output_text += node_text.format(**node_data)

    help_file = 'J:/www/Phile/content/Environment/11_ENV_TECH/Houdini/HDA/All/HDA_index.md'
    with codecs.open(help_file, 'w', 'utf-8') as f:
        f.write(output_text)