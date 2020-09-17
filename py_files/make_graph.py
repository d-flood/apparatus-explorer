def make_graph(arcs, index, ref, nodes):
    from subprocess import call
    import re

    graph_data = ''
    if nodes == None:
        for arc in arcs:
            graph_data = f'\t{graph_data}{arc.get("from")} -> {arc.get("to")} [fillcolor="orange"]\n'
    else:
        for node in nodes:
            graph_data = f'\t{graph_data}{node.get("n")} [fillcolor="orange"]\n'
    
    with open('files/template.dot', 'r', encoding='utf-8') as template_fn:
        template = template_fn.read()
        pass

    template = re.sub('zzz', graph_data, template)
    filename = f'{ref}U{index.replace(" ", "")}'

    with open(f'files/dot/{filename}.dot', 'w', encoding='utf-8') as new_fn:
        new_fn.write(template)
        pass
    
    call(f"dot -Tpng files/dot/{filename}.dot -o files/graphs/{filename}.png")

    return filename

# This function appears to be unecessary because GraphViz output is consistent 
# def resize_png(filename):
#     from PIL import Image
#     graph_image = Image.open(f'files/graphs/{filename}.png')
#     graph_image = graph_image.resize((300, 300), Image.ANTIALIAS)
#     graph_image.save(f'files/graphs/{filename}.png')
#     filename = f'{filename}.png'
#     return filename