# -*- coding: utf-8 -*-
import hou
import os
import codecs
from .help_base import *

def get_context(node_type):
    u"""
    指定したノードタイプのヘルプ用のコンテキスト文字列を取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。

    Returns
    -------
    context : string
        ヘルプ用のコンテキスト文字列。
    """
    category = node_type.category().name()
    context = table_to_dir[category]
    return context

def get_node_name(node_type):
    u"""
    指定したノードタイプのヘルプ用のノード名を取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。

    Returns
    -------
    node_name : string
        ヘルプ用のノード名。
    """
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

def set_parm_data(parms, parm_data, parm_def):
    u"""
    パラメータのリストから指定した辞書にパラメータの情報を追加する。

    Parameters
    ----------
    parms : list
        辞書に追加するパラメータのリスト。
    parm_data : dict
        パラメータの情報が追加される辞書。
    parm_def : dict
        デフォルトのパラメータの説明が入ってる辞書。
        この中のパラメータ名がparmsの中に存在する場合はこの情報をparm_dataに追加する。
    """
    temp_type = hou.parmTemplateType
    invalid_types = [temp_type.Separator, temp_type.Label]
    for parm in parms:
        parm_info = {}
        parm_type = parm.type()
        if parm.isHidden() or parm_type in invalid_types:
            continue
        parm_label = parm.label()
        parm_name = parm.name()
        parm_desc = ''
        parm_desc_def = parm_def.get(parm_name)
        if parm_desc_def:
            parm_desc = parm_desc_def
        parm_info['label'] = parm_label
        parm_info['name'] = parm_name
        parm_info['desc'] = parm_desc
        parm_info['folder'] = False
        if parm_type == temp_type.Folder:
            parm_info['folder'] = True
            parm_data.append(parm_info)
            parms = parm.parmTemplates()
            set_parm_data(parms, parm_data, parm_def)
        else:
            parm_data.append(parm_info)

def get_parm_data(node_type, parm_def):
    u"""
    指定したノードタイプのパラメータの情報を取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。
    parm_def : dict
        デフォルトのパラメータの説明が入ってる辞書。

    Returns
    -------
    parm_data : dict
        パラメータの情報が入った辞書。
        label: パラメータのラベル。
        name: パラメータの名前。
        desc: パラメータの説明。
        folder: パラメータがフォルダかどうかのブール値。
    """
    parm_data = []
    parm_temp_group = node_type.parmTemplateGroup()
    parm_temps = parm_temp_group.parmTemplates()
    set_parm_data(parm_temps, parm_data, parm_def)
    return parm_data

def get_parm_descs(parm_data):
    u"""
    パラメータの情報が入った辞書から、ヘルプ用にフォーマットされた説明文字列を取得。

    Parameters
    ----------
    parm_data : dict
        パラメータの情報が入った辞書。

    Returns
    -------
    parm_descs : string
        ヘルプ用にフォーマットされたパラメータの説明文字列。
    """
    parm_descs = []
    for parm_info in parm_data:
        parm_label = parm_info['label']
        parm_name = parm_info['name']
        parm_desc = parm_info['desc']
        parm_desc = '\n\n    '.join(parm_desc.splitlines())
        is_folder = parm_info['folder']
        if is_folder:
            parm = folder_parm_text.format(parm_label)
        else:
            parm = parm_desc_text.format(parm_label, parm_name, parm_desc)
        parm_descs.append(parm)
    return parm_descs

def get_help_file_text(help_file, splitlines=True):
    u"""
    指定したヘルプファイルの文字列を取得。

    Parameters
    ----------
    help_file : string
        読み込むヘルプファイル。
    splitlines : bool
        Trueにすると戻り値を行ごとのリストで返し、Falseなら文字列で返す。

    Returns
    -------
    lines : list or string
        ヘルプファイルの文字列。
        splitlinesがTrueなら行ごとの文字列が入ったリスト。
    """
    if not help_file or not os.path.exists(help_file):
        if splitlines:
            return []
        return ''
    if hou.getenv('HH') in help_file:
        from zipfile import ZipFile
        context = help_file.split('/')[-2]
        node_name = os.path.basename(help_file)
        file_name = '{}/{}'.format(context, node_name)
        help_file = help_file.replace('/' + file_name, '')
        with ZipFile(help_file) as zf:
            with zf.open(file_name) as f:
                lines = f.read()
                if splitlines:
                    lines = lines.splitlines()
    else:
        with codecs.open(help_file, 'r', 'utf-8') as f:
            lines = f.readlines()
            if not splitlines:
                lines = ''.join(lines)
    return lines

def get_help_info_from_file(help_file, node_type):
    u"""
    指定したヘルプファイルの文字列から情報を取得。

    Parameters
    ----------
    help_file : string
        読み込むヘルプファイル。
    node_type : hou.NodeType
        ノードタイプ。

    Returns
    -------
    lines : tuple
        intro, description, parametersの3つが入ったタプル。
        intro: ノードの紹介文。
        description: ノードの説明文。
        parameters: パラメータの名前をキー、パラメータの説明文を値に持つ辞書。
    """
    lines = get_help_file_text(help_file)
    intro = ''
    intro_line = None
    description = ''
    parameters = {}
    parm_def_line = None
    parm_labels = [parm.label().lower() for parm in node_type.parmTemplates()]
    parm_names = [parm.name() for parm in node_type.parmTemplates()]
    for i, line in enumerate(lines):
        if not intro and '"""' in line:
            intro = line.replace('"""', '').strip()
            intro_line = i
        if not description and intro_line:
            for desc_line in range(intro_line + 1, len(lines)):
                desc_text = lines[desc_line].lstrip()
                if '== ' in desc_text:
                    continue
                if '@parameters' in desc_text:
                    parm_def_line = desc_line
                    break
                description += desc_text
        if parm_def_line:
            for parm_line in range(parm_def_line + 1, len(lines)):
                parm_text = lines[parm_line]
                if parm_text.strip().startswith('@'):
                    break
                if parm_text.strip()[:-1].lower() in parm_labels:
                    index = parm_labels.index(parm_text.strip()[:-1].lower())
                    parm_name = parm_names[index]
                    next_line = parm_line + 1
                    if next_line >= len(lines):
                        continue
                    next_text = lines[next_line]
                    if '#id:' in next_text or '#channels:' in next_text:
                        if '#id:' in next_text:
                            parm_name = next_text.replace('#id:', '').strip()
                        else:
                            parm_name = next_text.split('/')[-1].strip()
                    else:
                        next_line = parm_line
                    if parm_name in parameters:
                        continue
                    parm_desc = ''
                    desc_start = next_line + 1
                    if desc_start >= len(lines):
                        continue
                    if not lines[desc_start].strip():
                        desc_start += 1
                    for parm_desc_line in range(desc_start, len(lines)):
                        parm_desc_text = lines[parm_desc_line].lstrip()
                        if parm_desc_text.strip().endswith(':') or\
                            parm_desc_text.startswith(':') or\
                            parm_desc_text.startswith('== ') or\
                            parm_desc_text.startswith('@'):
                            break
                        parm_desc += parm_desc_text
                        parameters[parm_name] = parm_desc
    return intro, description, parameters

def get_help_text(node_type, intro, desc, parm_data, example_data):
    u"""
    指定したノードタイプと情報を元にヘルプ用にフォーマットされた文字列を取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。
    intro : string
        ノードの紹介文。
    desc : string
        ノードの説明文。
    parm_data : dict
        パラメータの情報が入った辞書。
        label: パラメータのラベル。
        name: パラメータの名前。
        desc: パラメータの説明。
        folder: パラメータがフォルダかどうかのブール値。

    Returns
    -------
    output_text : string
        ヘルプ用にフォーマットされた文字列。
    """
    node_label = node_type.description()
    context = get_context(node_type)
    node_name = get_node_name(node_type)
    icon = node_type.icon()
    if 'subnet' in icon:
        icon = 'COMMON/subnet'
    parameters = ''
    parm_descs = get_parm_descs(parm_data)
    if parm_descs:
        parameters = parm_text.format(''.join(parm_descs))

    examples = []
    for example_info in example_data:
        example_info['node_name'] = node_name
        example_info['context'] = context
        examples.append(example_text.format(**example_info))

    help_data = {
        'node_label': node_label,
        'context': context,
        'node_name': node_name,
        'icon': icon,
        'introduction': intro,
        'description': '\n\n'.join(desc.splitlines())
    }
    output_text = help_text.format(**help_data)
    output_text += parameters
    output_text += '\n'.join(examples)

    return output_text


def get_hda_file_path(node_type):
    u"""
    指定したノードタイプからhdaファイルのパスを取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。

    Returns
    -------
    hda_file : string
        hdaファイルのパス。
    """
    node_def = node_type.definition()
    if not node_def:
        return
    hda_file = node_def.libraryFilePath()
    return hda_file

def get_official_help_path(node_type):
    u"""
    標準ノードのヘルプファイルのパスを取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。

    Returns
    -------
    help_file : string
        ヘルプファイルのパス。
    """
    context = get_context(node_type)
    node_name = get_node_name(node_type)
    help_file = '{}/help/nodes.zip/{}/{}.txt'.format(
        hou.getenv('HH'), context, node_name)
    return help_file

def get_help_file_path(node_type):
    u"""
    指定したノードタイプのヘルプファイルのパスを取得。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。

    Returns
    -------
    help_file : string
        ヘルプファイルのパス。
    """
    source_path = node_type.sourcePath()
    if source_path == 'Internal' or hou.getenv('HH') in source_path:
        return get_official_help_path(node_type)
    hda_file = get_hda_file_path(node_type)
    if not hda_file:
        return ''
    if hou.getenv('HH') in hda_file:
        return get_official_help_path(node_type)
    file_path = os.path.dirname(hda_file)
    context = get_context(node_type)
    node_name = get_node_name(node_type)
    help_file = '{}/help/nodes/{}/{}.txt'.format(
        os.path.dirname(file_path),
        context,
        node_name)
    return help_file

def export_text(filename, text):
    u"""
    テキストをファイルに書き出し。

    Parameters
    ----------
    filename : string
        書き出し先のファイル名。
    text : string
        テキスト。
    """
    help_path = os.path.dirname(filename)
    if not os.path.exists(help_path):
        os.makedirs(help_path)
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(text)

def export_help_text(node_type, help_text):
    u"""
    指定したノードタイプのヘルプテキストをファイルに書き出し。

    Parameters
    ----------
    node_type : hou.NodeType
        ノードタイプ。
    help_text : string
        ヘルプテキスト。

    Returns
    -------
    export : bool
        書き出せたかどうかのブール値。
    """
    help_file = get_help_file_path(node_type)
    if not help_file:
        return
    if hou.getenv('HH') in help_file:
        hou.ui.displayMessage(
            u'標準ノードのヘルプは書き出せません。',
            severity=hou.severityType.Warning)
        return
    export_text(help_file, help_text)
    return True

def export_example_text(example_data):
    u"""
    Exampleファイルの説明用テキストファイルを書き出し。

    Parameters
    ----------
    example_data : list
        Exampleファイルの情報が入ったリスト
    """
    for example_info in example_data:
        filename = example_info['example_file']
        desc = example_info['example_desc']
        text = '\n\n'.join(desc.splitlines())
        export_text(filename, text)