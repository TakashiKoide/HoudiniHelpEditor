# -*- coding: utf-8 -*-

table_to_dir = {
    'Object': 'obj',
    'Sop': 'sop',
    'Particle': 'part',
    'Dop': 'dop',
    'ChopNet': 'chopnet',
    'Chop': 'chop',
    'Driver': 'out',
    'Shop': 'shop',
    'Cop2': 'cop2',
    'CopNet': 'copnet',
    'Vop': 'vop',
    'VopNet': 'vex',
    'Top': 'top',
    'Lop': 'lop',
}

category_to_label = {
    'Object': 'object node',
    'Sop': 'geometry node',
    'Dop': 'dynamics node',
    'Chop': 'channel node',
    'Driver': 'render node',
    'Shop': 'shader node',
    'Cop2': 'compositing node',
    'Vop': 'VOP node',
    'Top': 'TOP node',
    'Lop': 'LOP node',
}

help_text = (
u'''= {node_label} =

#type: node
#context: {context}
#internal: {node_name}
#icon: {icon}

"""{introduction}"""
== 概要 ==
{description}
''')

parm_text = (
u'''
@parameters パラメータ

{}
''')

folder_parm_text = (
u'''== {} ==
''')

parm_desc_text = (
u'''{}:
    #id: {}

    {}
''')

example_text = (
u'''
:load_example: {example_label}
    #examplefile: /examples/nodes/{context}/{node_name}/{example_name}.hda
    #path: /examples/nodes/{context}/{node_name}/{example_name}
    #include: yes
''')