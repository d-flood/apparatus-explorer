import json
import apparatusexplorer.PySimpleGUIQt as sg


def make_layout(settings):
    if settings['graph_orientation'] == 'rankdir="LR"':
        vertical, horizontal = False, True
    else:
        vertical, horizontal = True, False
    if settings['graph_bg_color'] == '#ffffff00':
        transparent, white = True, False
    else:
        transparent, white = False, True
    graphviz_frame = [
        [sg.Text('Graph Orientation:'), sg.Stretch(),
                sg.Radio('Vertical', '-orientation-', default=vertical, key='-vertical-', enable_events=True), 
                sg.Radio('Horizontal', '-orientation-', default=horizontal, key='horizontal')],
        [sg.Text('Graph Background Color:'), sg.Stretch(), 
                sg.Radio('Transparent', '-graph_bg_color-', default=transparent, key='-graph_transparent-'), 
                sg.Radio('White', '-graph_bg_color-', default=white, key='-graph_white-')],
    ]
    ignore_lac_hint = 'Hide variation units for which the only information\n\
is that one or more witnesses is lacunose.'
    ignore_subr_hint = '''Hide variation units when the only difference between two readings
is that one of the readings has been marked as a "subreading."
This is usually for meaningless spelling differences or scribal errors.'''
    app_settings_frame = [
        [sg.Checkbox('Ignore Lacunose Units', tooltip=ignore_lac_hint, key='ignore_lac', default=settings['ignore']['lac']),
            sg.Checkbox('Ignore Subreadings', tooltip=ignore_subr_hint, key='ignore_subr', default=settings['ignore']['lac'])],
        [sg.Text('Color Theme:'), sg.Stretch(), 
            sg.Drop(['Grey', 'Dark Mode', 'Parchment', 'System Default'],
                      default_value=settings['theme'], key='-theme-', readonly=True)],
        [sg.Text('DPI Awareness:', size=(30, 2)), sg.DropDown(['0', '1', '2', 'True', 'False'],
                  key='-dpi-', readonly=True, default_value=str(settings['dpi']))]
    ]
    return [
        [sg.Frame('GraphViz Settings', graphviz_frame, border_width=5)],
        [sg.Frame('Apparatus Exploer Settings', app_settings_frame, border_width=5)],
        [sg.Button('Save Settings'), sg.Button('Cancel'), sg.Button('Done')]
    ]

def save_settings(main_dir, settings, values):
    if values['-vertical-'] is True:
        settings['graph_orientation'] = ''
    else: 
        settings['graph_orientation'] = 'rankdir="LR"'
    if values['-graph_transparent-'] is True:
        settings['graph_bg_color'] = '#ffffff00'
    else:
        settings['graph_bg_color'] = '#ffffff'
    settings['theme'] = values['-theme-']
    if values['-dpi-'] in ['True', 'False']:
        settings['dpi'] = bool(values['-dpi-'])
    else:
        settings['dpi'] = int(values['-dpi-'])
    settings['ignore']['lac'] = values['ignore_lac']
    settings['ignore']['subr'] = values['ignore_subr']

    with open(f'{main_dir}/resources/settings.json', 'w') as file:
        json.dump(settings, file, indent=4)
    sg.popup_quick_message('Settings Saved!\n\
Theme and DPI changes take affect on app restart.')
    return settings

def set_settings(settings, main_dir, icon):
    if settings['theme'] == 'Grey':
        sg.theme('LightGrey2')
    else:
        sg.theme(settings['theme'])
    layout = make_layout(settings)
    window = sg.Window('Apparatus Explorer Settings', layout, icon=icon)
    window.finalize()

    while True:
        event, values = window.read()

        if event in ['Cancel', sg.WIN_CLOSED, None, 'Done']:
            break

        elif event == 'Save Settings':
            settings = save_settings(main_dir, settings, values)

        # print(f'{event=}\n{values=}')
    window.close()
    return settings