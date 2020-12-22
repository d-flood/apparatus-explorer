import lxml.etree as et

########################################################################
'''Simple Functions'''
########################################################################
def get_xml_file(fn):
    with open(fn, 'r', encoding='utf-8') as file:
        xml = file.read()
    # TODO: replace with proper ns handling
    xml = xml.replace('<TEI xmlns="http://www.tei-c.org/ns/1.0">', '<TEI>')
    xml = xml.replace('xml:id=', 'verse=')
    with open('temp.xml', 'w', encoding='utf-8') as file:
        file.write(xml)
    parser = et.XMLParser(remove_blank_text=True, encoding='UTF-8')
    tree = et.parse('temp.xml', parser)
    return tree.getroot(), tree

def construct_basetext(ab):
    # this is the element containing a whole verse unit
    # this is the verse str
    # begin constructing lemma
    basetext = []
    for elem in ab:
        if elem.tag == 'seg':
            basetext.append(elem.text)
        elif elem.tag == 'app' and elem.find('lem').get('type') != 'om':
            basetext.append(elem.find('lem').text)
    return ' '.join(basetext)

def get_all_apps(ab):
    apps = ab.findall('app')
    app_units = []
    for app in apps:
        if app.get('from') == app.get('to'):
            app_units.append(int(app.get('from')))
        else:
            app_units.append((int(app.get('from')), int(app.get('to'))))
    return app_units

def get_focus_app(app):
    if app.get('from') == app.get('to'):
        return int(app.get('from'))
    else:
        return (int(app.get("from")), (int(app.get("to"))))

def get_all_rdgs(app):
    readings = []
    rdgs = app.findall('rdg')
    for rdg in rdgs:
        wits = rdg.get('wit')
        # wits = sorted(wits.split()) # this was an attempt to sort mss maj>min, but it didn't work.
        # wits = ' '.join(wits)
        if rdg.get('type') == 'subreading':
            rdg_type = 'subr'
        else:
            rdg_type = rdg.get('type')
        readings.append({'name': rdg.get('n'), 
                         'type': rdg_type, 
                         'text': rdg.text, 
                         'wits': wits})
    return readings

def get_arcs(app):
    graph = app.find('note/graph')
    arcs = []
    all_arcs = graph.findall('arc')
    for arc in all_arcs:
        arcs.append({'from': arc.get('from'), 'to': arc.get('to')})
    all_nodes = graph.findall('node')
    nodes = []
    for node in all_nodes:
        nodes.append(node.get('n'))
    return arcs, nodes

def select_verse(root, verse):
    verse = f'{verse}-APP'
    ab = root.find(f'ab[@verse="{verse}"]')
    return ab

def save_xml(tree, fn):
    et.indent(tree, '    ')
    tree.write(fn, pretty_print=True, encoding='utf-8')
    with open(fn, 'r', encoding='utf-8') as file:
        to_save = file.read()
    to_save = to_save.replace('<TEI>', '<TEI xmlns="http://www.tei-c.org/ns/1.0">')
    to_save = to_save.replace('verse=', 'xml:id=')
    with open(fn, 'w', encoding='utf-8') as file:
        file.write(to_save)
    return fn

##########################################################################
'''Complex Functions'''
##########################################################################
# This gets the xml file finds the first app of the first verse
def initialize_apparatus(fn):
    root, tree = get_xml_file(fn)
    ab = root.find('ab')
    ref = ab.get('verse').replace('-APP', '')
    basetext = construct_basetext(ab)
    all_apps = get_all_apps(ab)
    app = ab.find('app')
    selected_app = get_focus_app(app)
    rdgs = get_all_rdgs(app)
    arcs, nodes = get_arcs(app)
    return tree, root, ab, ref, basetext, all_apps, selected_app, rdgs, arcs, nodes, app

def load_new_verse(root, verse):
    ab = select_verse(root, verse)
    ref = ab.get('verse').replace('-APP', '')
    basetext = construct_basetext(ab)
    all_apps = get_all_apps(ab)
    app = ab.find('app')
    selected_app = get_focus_app(app)
    rdgs = get_all_rdgs(app)
    arcs, nodes = get_arcs(app)
    return ref, basetext, all_apps, app, selected_app, rdgs, arcs, nodes, ab

def verse_from_ab(ab):
    ref = ab.get('verse').replace('-APP', '')
    basetext = construct_basetext(ab)
    all_apps = get_all_apps(ab)
    app = ab.find('app')
    selected_app = get_focus_app(app)
    rdgs = get_all_rdgs(app)
    arcs, nodes = get_arcs(app)
    return ref, basetext, all_apps, app, selected_app, rdgs, arcs, nodes, ab

def load_app(app, direction: str):
    if direction == 'next':
        while True:
            app = app.getnext()
            if app.tag == 'app':
                break
    elif direction == 'prev':
        while True:
            app = app.getprevious()
            if app.tag == 'app':
                break
    selected_app = get_focus_app(app)
    rdgs = get_all_rdgs(app)
    arcs, nodes = get_arcs(app)
    return selected_app, rdgs, arcs, nodes, app

####################################################
'''Editing XML File'''
####################################################
def update_reading_type(app, new_attrib: str, name: str):
    if new_attrib == 'Defective':
        new_attrib = 'def'
    elif new_attrib == 'Orthographic':
        new_attrib = 'orth'
    elif new_attrib == 'Omit':
        new_attrib = 'om'
    elif new_attrib == 'Lacunose':
        new_attrib = 'lac'
    elif new_attrib == 'Subreading':
        new_attrib = 'subr'
    rdg = app.find(f'rdg[@n="{name}"]')
    rdg.attrib['type'] = new_attrib
    rdgs = get_all_rdgs(app)
    return app, rdgs

def delete_rdg(app, rdg_n):
    rdgs = app.findall('rdg')
    for rdg in rdgs:
        if rdg.attrib['n'] == rdg_n:
            rdg.attrib.pop('type')
            break
    all_rdgs = get_all_rdgs(app)
    return app, all_rdgs

def add_arc(app, arc_from: str, arc_to: str):
    all_arcs, _ = get_arcs(app)
    # test to see if new arc is a duplicate
    for arc in all_arcs:
        if arc == {'from': arc_from, 'to': arc_to}:
            return None, app
    new_arc = et.Element('arc')
    new_arc.attrib['from'] = arc_from
    new_arc.attrib['to'] = arc_to
    arc_parent = app.find('note/graph')
    arc_parent.append(new_arc)
    all_arcs, _ = get_arcs(app)
    return all_arcs, app

def delete_arc(app, arc_from: str, arc_to: str):
    arcs = app.findall('note/graph/arc')
    for arc in arcs:
        if arc.attrib['from'] == arc_from and arc.attrib['to'] == arc_to:
            arc.getparent().remove(arc)
    all_arcs, _ = get_arcs(app)
    return all_arcs, app
