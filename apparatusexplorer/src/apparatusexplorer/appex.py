import ctypes
from distutils.spawn import find_executable
import json
import pathlib
import re
import subprocess

from apparatusexplorer.combine_xml import combine_xml_files_interface
from apparatusexplorer.itsee_to_open_cbgm.itsee_to_open_cbgm import reformat_xml
import apparatusexplorer.process_graph as pg
from apparatusexplorer.set_settings import set_settings
import apparatusexplorer.xml_processing as xp
import apparatusexplorer.PySimpleGUIQt as sg

sg.LOOK_AND_FEEL_TABLE['Parchment'] = {'BACKGROUND': '#FFE9C6',
                                        'TEXT': '#533516',
                                        'INPUT': '#EAC8A3',
                                        'TEXT_INPUT': '#2F1B0A',
                                        'SCROLL': '#B39B73',
                                        'BUTTON': ('white', '#C55741'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 3, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        }
sg.LOOK_AND_FEEL_TABLE['DarkMode'] = {'BACKGROUND': '#161D20',
                                        'TEXT': '#039386',
                                        'INPUT': '#32434B',
                                        'TEXT_INPUT': '#89DDFF',
                                        'SCROLL': '#B39B73',
                                        'BUTTON': ('white', '#2E3437'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 3, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        }

def okay_or_cancel(message: str, title: str):
    layout = [[sg.Text(message, pad=(10, 10))],
        [sg.Button('Okay'), sg.Stretch(), sg.Button('Cancel')]]
    popup = sg.Window(title, layout, icon=icon)
    response, _ = popup.read()
    popup.close()
    return response

def okay_popup(message: str, title: str):
    layout = [[sg.Text(message, pad=(10, 10))],
        [sg.Button('Okay')]]
    popup = sg.Window(title, layout, icon=icon)
    popup.read()
    popup.close()

def readme_popup(main_dir, icon):
    with open(f'{main_dir}/resources/README.txt', 'r', encoding='utf-8') as file:
        readme = file.read()
    layout = [[sg.Multiline(readme, size=(100, 50))],
        [sg.Button('Close', pad=(10, 10))]]
    popup = sg.Window('About', layout, icon=icon)
    popup.read()
    popup.close()

def set_buttons(window, app, ab):
    ##### VERSE BUTTONS
    if ab.getprevious() is None or ab.getprevious().tag != 'ab':
        window['-prev_verse-'].update(disabled=True)
    else:
        window['-prev_verse-'].update(disabled=False)
    if ab.getnext() is None or ab.getnext().tag != 'ab':
        window['-next_verse-'].update(disabled=True)
    else:
        window['-next_verse-'].update(disabled=False)
    ##### APP BUTTONS
    if app is None:
        window['-next_app-'].update(disabled=True)
        window['-prev_app-'].update(disabled=True)
        return
    next_app = app.getnext()
    if next_app is None or (next_app.tag == 'seg' and next_app.getnext() is None):
        window['-next_app-'].update(disabled=True)
    elif next_app.tag == 'app':
        window['-next_app-'].update(disabled=False)
    else:
        window['-next_app-'].update(disabled=False)
    if app.getprevious() is None or app.getprevious().getprevious() is None:
        window['-prev_app-'].update(disabled=True)
    else:
        window['-prev_app-'].update(disabled=False)

def enable_editing_buttons(window):
    menu = [['File', ['Save As', '---', 'Combine XML Files', '---', 'Settings', 'About']]]
    window['-update_reading-'].update(disabled=False)
    window['-add_arc-'].update(disabled=False)
    window['-delete_arc-'].update(disabled=False)
    window['-update_verse-'].update(disabled=False)
    window['-save_xml-'].update(disabled=False)
    window['-menu-'].update(menu_definition=menu)
    window['-delete_reading-'].update(disabled=False)

def update_ref(window, ref):
    window['-verse-'].update(value=ref)

def prepare_focus(focus):
    if isinstance(focus, int):
        return [focus]
    elif isinstance(focus, tuple):
        return [i for i in range(focus[0], focus[1]+1)]

def update_basetext(basetext, window, selected_app):
    index = 2
    words = basetext.split()
    i = None
    for i, word in zip(range(len(words)), words):
        window[f'bt{i}'].update(value=f'{word}\n{index}', visible=True, background_color=determine_focus(index, selected_app))
        index += 2
    for n in range(i+1, 50):
        window[f'bt{n}'].update(visible=False)

def determine_focus(unit, focus):
    if focus is None:
        return sg.DEFAULT_BACKGROUND_COLOR
    if unit in prepare_focus(focus) or unit == focus:
        return selected_app_color
    else:
        return sg.DEFAULT_BACKGROUND_COLOR

def update_units_row(units: list, window, focus):
    i = -1
    if focus is not None:
        for i, unit in zip(range(len(units)), units):
            unit_str = str(unit).replace('(', '')
            unit_str = unit_str.replace(')', '')
            unit_str = unit_str.replace(', ', '–')
            unit_str = unit_str.replace('\'', '')
            window[f'unit{i}'].update(value=f'{unit_str}', visible=True, background_color=determine_focus(unit, focus))
    for n in range(i+1, 20):
        window[f'unit{n}'].update(visible=False)

def format_rdgs(rdgs):
    to_return = []
    for rdg in rdgs:
        if rdg['text'] is None:
            text = ''
        else:
            text = rdg['text']
        if rdg['type'] is None:
            rdg['type'] = '    '
        to_return.append(f'{rdg["name"]}\t{rdg["type"]}\t\t] {text:<75}{rdg["wits"].replace(" ", ", "):<100}')
        # to_return.append('_'*40)
    return '\n'.join(to_return)

def update_rdgs(rdgs, window):
    if rdgs is None:
        window['-rdgs-'].update(value='')
    else:
        window['-rdgs-'].update(value=format_rdgs(rdgs))

def update_arcs_text(window, arcs):
    to_display = []
    for arc in arcs:
        to_display.append(f"{arc['from']} ➜ {arc['to']}")
    to_display = '\n'.join(to_display)
    window['-graph-'].update(value=to_display)

def update_arcs_graph(window, main_dir, ref, selected_app, arcs, nodes):
    if isinstance(selected_app, tuple):
        selected_app = f'{selected_app[0]}–{selected_app[1]}'
    # graph_fn = f'{ref}U{selected_app}.png' this is for unique files names. Using a temp file instead
    # graph_path = pathlib.Path(f'{output_dir}/graphs/{graph_fn}')
    graph_path = '.temp_graph.png'
    blank_graph = f'{main_dir}/resources/blank_graph.png'
    # It would be better not to generate a new graph every click,
    # but this leads to the png not matching the current xml element.
    # Perhaps if the png can be tied to a document.
    # if graph_path.exists():
    #     window['-graph-'].update(filename=graph_path.as_posix())
    # else:
    if selected_app is not None:
        pg.make_graph(arcs, selected_app, ref, nodes, main_dir, graph_bg_color, graph_text_color, line_color, orientation)
        window['-graph-'].update(filename=graph_path)
    else:
        window['-graph-'].update(filename=blank_graph)

def update_arcs(window, arcs, dot_exists, ref, selected_app, main_dir, nodes):
    if selected_app is None:
        return
    if dot_exists:
        update_arcs_graph(window, main_dir, ref, selected_app, arcs, nodes)
    else:
        update_arcs_text(window, arcs)
    
def update_available_names(rdgs, window):
    names = ['']
    if rdgs is not None:
        [names.append(rdg['name']) for rdg in rdgs]
    window['-stemma_from-'].update(values=names)
    window['-stemma_to-'].update(values=names)
    window['-edit_rdg-'].update(values=names)

def is_different(value_a, value_b):
    if value_a != value_b:
        return True
    sg.popup_quick_message('"From" and "To" cannot be equal')
    return False 

def add_arc_main(arcs, values: dict, app, selected_app, ref, nodes, main_dir):
    if selected_app is None:
        return arcs, app
    if is_different(values['-stemma_from-'], values['-stemma_to-']) is False:
        return arcs, app
    new_arcs, app = xp.add_arc(app, values['-stemma_from-'], values['-stemma_to-'])
    if new_arcs is not None:
        arcs = new_arcs
        pg.make_graph(arcs, selected_app, ref, nodes, main_dir, graph_text_color, graph_text_color, line_color, orientation)
        return arcs, app
    sg.popup_quick_message('Relationship already exists')
    return arcs, app

def delete_arc_main(values, arcs, app, selected_app, ref, nodes, main_dir):
    if selected_app is None:
        return arcs, app
    if is_different(values['-stemma_from-'], values['-stemma_to-']) is False:
        return arcs, app
    arcs, app = xp.delete_arc(app, values['-stemma_from-'], values['-stemma_to-'])
    pg.make_graph(arcs, selected_app, ref, nodes, main_dir, graph_bg_color, graph_text_color, line_color, orientation)
    return arcs, app

def refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes):
    update_ref(window, ref)
    update_basetext(basetext, window, selected_app)
    update_units_row(all_apps, window, selected_app)
    update_rdgs(rdgs, window)
    update_available_names(rdgs, window)
    if selected_app is not None:
        update_arcs(window, arcs, dot_exists, ref, selected_app, main_dir, nodes)

def open_graph():
    subprocess.Popen('.temp_graph.png', shell=True)

def is_xml_reformatted(xml_fn):
    with open(xml_fn, 'r', encoding='utf-8') as file:
        tree = file.read()
    see_if_reformatted = re.search('<teiHeader>', tree)
    if see_if_reformatted == None:
        return False
    else:
        return True

def save_settings(settings, main_dir):
    with open(f'{main_dir}/resources/settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

#########################################################################
#########################################################################
"""Layout and Main Loop"""
#########################################################################
def initial_basetext_rows():
    row1 = []
    row2 = []
    row3 = []
    row4 = []
    key = 0
    for _ in range(20):
        row1.append(sg.Text('', visible=False, key=f'bt{key}', justification='center', pad=(2, 3)))
        row1.append(sg.Stretch())
        key += 1
    for _ in range(20):
        row2.append(sg.Text('', visible=False, key=f'bt{key}', justification='center', pad=(2, 3)))
        row2.append(sg.Stretch())
        key += 1
    for _ in range(20):
        row3.append(sg.Text('', visible=False, key=f'bt{key}', justification='center', pad=(2, 3)))
        row3.append(sg.Stretch())
        key += 1
    for _ in range(20):
        row4.append(sg.Text('', visible=False, key=f'bt{key}', justification='center', pad=(2, 3)))
        row4.append(sg.Stretch())
        key += 1
    return row1, row2, row3, row4

def initial_units_row():
    row = []
    for i in range(20):
        row.append(sg.Text('', visible=False, key=f'unit{i}', justification='center', pad=(2, 3)))
    return row

def get_graph_element():
    dot_exists = find_executable('dot')
    if dot_exists:
        graph_elem = sg.Image(filename=f'{main_dir}/resources/blank_graph.png', key='-graph-', enable_events=True)
    else:
        graph_elem = sg.Text('', key='-graph-')
    return [[graph_elem]], dot_exists

def get_layout(settings):
    units_row = initial_units_row()
    bt1, bt2, bt3, bt4 = initial_basetext_rows()
    menu = [['File', ['!Save As', '---', 'Combine XML Files', '---', 'Settings', 'About']]]
    verse_frame = [[sg.Stretch(), sg.Button('<Prev', key='-prev_verse-', disabled=True), sg.Input('', key='-verse-'), sg.Button('Next>', key='-next_verse-', disabled=True), sg.Stretch()],
                   [sg.Stretch(), sg.Button('Update', key='-update_verse-', disabled=True), sg.Stretch()]]
    units_frame = [[sg.Button(' <Prev ', key='-prev_app-', disabled=True)] + units_row + [sg.Button(' Next> ', key='-next_app-', disabled=True)]]

    basetext_frame = [bt1, bt2, bt3, bt4]

    edit_readings_frame = [
        [sg.Text('')],
        [sg.Text('Reading:'), sg.Combo(['        '], readonly=True, key='-edit_rdg-')],
        [sg.Text('Type:'), sg.Combo(['Defective', 'Orthographic', 'Lacunose', 'Subreading'], readonly=True, key='-edit_type-')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Button('Update', key='-update_reading-', disabled=True)],
        [sg.Button('Delete', key='-delete_reading-', disabled=True)]
    ]
    edit_stemma_frame = [
        [sg.Text('')],
        [sg.Combo(['        '], readonly=True, key='-stemma_from-'),
                sg.Text('➜', justification='center'),
                sg.Combo(['        '], readonly=True, key='-stemma_to-')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Button('Add Relationship', key='-add_arc-', disabled=True)],
        [sg.Button('Delete Relationship', key='-delete_arc-', disabled=True)]
    ]
    stemma_frame, dot_exists = get_graph_element()

    xml_input_frame = [
        [sg.Text('TEI XML Collation File:'), 
            sg.Input(settings['last_opened'], key='-xml_input-'), 
            sg.FileBrowse('Browse', file_types=(("XML Files", "*.xml"),)),
            sg.Button('Load File'),
            sg.Button('Save', key='-save_xml-', disabled=True)]
    ]

    layout = [
        [sg.Menu(menu, key='-menu-')],
        [sg.Text('XML TEI Apparatus Explorer and Editor', justification='center')],
        [sg.Frame('', verse_frame, border_width=3)],
        [sg.Frame('Variation Units', units_frame)],
        [sg.Frame('Basetext', basetext_frame)],
        [sg.MultilineOutput('', key='-rdgs-')],
        [sg.Frame('Local Stemma', stemma_frame),
                        sg.Frame('Edit Readings', edit_readings_frame), 
                        sg.Frame('Edit Local Stemma', edit_stemma_frame)],
        [sg.Frame('', xml_input_frame)]
    ]

    return layout, dot_exists

def main():
    settings = get_settings(main_dir)
    layout, dot_exists = get_layout(settings)
    window = sg.Window('Apparatus Explorer v 0.9', layout, icon=icon, size=(1800, 500))
    root = None
    ###########################################################
    '''Main Loop'''
    ###########################################################
    ref = basetext = all_apps = selected_app = rdgs = nodes = ab = tree = initial_fn = app = arcs = None
    while True:
        event, values = window.read()
        
        if event in [sg.WINDOW_CLOSED, None]:
            break

        elif event == 'Load File':
            if values['-xml_input-'] != '':
                xml_file = values['-xml_input-']
                if is_xml_reformatted(xml_file) is False:
                    sg.popup_quick_message('Reformatting XML file...')
                    xml_file = reformat_xml(xml_file)
                    window['-xml_input-'].update(value=xml_file)
                try:
                    tree, root, ab, ref, basetext, all_apps, selected_app, rdgs, arcs, nodes, app = xp.initialize_apparatus(xml_file, settings['ignore'])
                    refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)
                    set_buttons(window, app, ab)
                    enable_editing_buttons(window)
                    initial_fn = values['-xml_input-']
                except:
                    okay_popup('Failed to load XML file.\n\
XML file must be the output of the ITSEE and INTF Collation Editor.', 'Failed to Parse XML')
            else:
                sg.popup_quick_message('Select a valid XML TEI encoded apparatus.')

        elif event == '-update_verse-':
            ref, basetext, all_apps, app, selected_app, rdgs, arcs, nodes, ab = xp.load_new_verse(root, values['-verse-'], settings['ignore'])
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)
            set_buttons(window, app, ab)

        elif event == '-next_verse-':
            ref, basetext, all_apps, app, selected_app, rdgs, arcs, nodes, ab = xp.verse_from_ab(ab.getnext(), settings['ignore'])
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)
            set_buttons(window, app, ab)

        elif event == '-prev_verse-':
            ref, basetext, all_apps, app, selected_app, rdgs, arcs, nodes, ab = xp.verse_from_ab(ab.getprevious(), settings['ignore'])
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)
            set_buttons(window, app, ab)

        elif event == '-next_app-':
            selected_app, rdgs, arcs, nodes, app = xp.load_app(app, 'next')
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)
            set_buttons(window, app, ab)

        elif event == '-prev_app-':
            selected_app, rdgs, arcs, nodes, app = xp.load_app(app, 'prev')
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)
            set_buttons(window, app, ab)

        elif event == '-save_xml-':
            response = okay_or_cancel('Overwrite the original file?\n\
To save a copy, select "Save As" from the File menu.', 'Save Collation')
            if response == 'Okay':
                xp.save_xml(tree, initial_fn)
                settings['last_opened'] = initial_fn
                save_settings(settings, main_dir)

        elif event == '-update_reading-':
            if selected_app is None or values['-edit_rdg-'] in ['', '        ', None]:
                continue
            app, rdgs = xp.update_reading_type(app, values['-edit_type-'], values['-edit_rdg-'])
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)

        elif event == '-delete_reading-':
            if selected_app is None or values['-edit_rdg-'] in ['', '        ', None]:
                continue
            app, rdgs = xp.delete_rdg(app, values['-edit_rdg-'])
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)

        elif event == '-add_arc-':
            if selected_app is None:
                continue
            arcs, app = add_arc_main(arcs, values, app, selected_app, ref, nodes, main_dir)
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)

        elif event == '-delete_arc-':
            if selected_app is None:
                continue
            arcs, app = delete_arc_main(values, arcs, app, selected_app, ref, nodes, main_dir)
            refresh_gui(window, ref, basetext, all_apps, selected_app, rdgs, arcs, dot_exists, main_dir, nodes)

        elif event == '-graph-':
            open_graph()

        elif event == 'Save As':
            new_fn = sg.popup_get_file('', no_window=True, file_types=(("XML Files", "*.xml"),), save_as=True)
            if new_fn:
                fn = xp.save_xml(tree, new_fn)
                settings['last_opened'] = fn
                save_settings(settings, main_dir)
                okay_popup(f'Saved to\n{fn}', 'Saved!')

        elif event == 'Settings':
            settings = set_settings(settings, main_dir, icon)

        elif event == 'About':
            readme_popup(main_dir, icon)

        elif event == 'Combine XML Files':
            result = combine_xml_files_interface(settings, icon, main_dir)
            if result is not None:
                settings = result
                save_settings(settings, main_dir)

        # print(event, values)
    
    window.close()

def get_theme(theme):
    if theme == 'Parchment':
        return '#6D4F33', '#A3EAAC', 'Parchment', 'black'
    elif theme == 'Grey' or theme == 'Gray':
        return 'black', '#A3EAAC', 'LightGrey2', 'black'
    elif theme == 'Dark Mode':
        return '#CBCB41', '#213E58', 'DarkMode', 'white'
    elif theme == 'System Default':
        return 'black', '#A3EAAC', 'SystemDefaultForReal', 'black'

def get_settings(main_dir):
    try:
        with open(f'{main_dir}/resources/settings.json', 'r') as file:
            settings = json.load(file)
    except:
        settings = {
            'graph_orientation': 'rankdir="LR"',
            'theme': 'Parchment',
            'dpi': True,
            'last_opened': '',
            'last_opened_dir': '',
            'graph_bg_color': '#ffffff00',
            'ignore': {'lac': False, 'subr': False}
        }
        with open(f'{main_dir}/resources/settings.json', 'w') as file:
            json.dump(settings, file, indent=4)
    return settings

main_dir = pathlib.Path(__file__).parent.as_posix()
settings = get_settings(main_dir)
orientation = settings['graph_orientation'] # rankdir="LR" for horizontal, empty str for vertical 
graph_bg_color = settings['graph_bg_color']
graph_text_color, selected_app_color, color_theme, line_color = get_theme(settings['theme'])
sg.theme(color_theme)
icon = f'{main_dir}/resources/apparatusexplorer.ico'
sg.set_options(font=('Cambria', 12), element_padding=(3, 5))

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(settings['dpi']) # High resolution Windows machines have scaling issues
except:
    pass
