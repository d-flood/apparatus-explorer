from subprocess import call

from PIL import Image, ImageOps

# def make_square(fn, background_color):
#     graph = Image.open(fn)
#     width, height = graph.size
#     if width == height:
#         pass
#     elif width > height:
#         result = Image.new(graph.mode, (width, width), background_color)
#         result.paste(graph, (0, (width - height) // 2))
#         result.save(fn)
#     else:
#         result = Image.new(graph.mode, (height, height), background_color)
#         result.paste(graph, ((height - width) // 2, 0))
#         result.save(fn)
#     return fn

def fix_size(fn):
    target_height = 300
    target_width = 500
    graph = Image.open(fn)
    # h, w = graph.size
    graph = ImageOps.crop(graph, 5)
    target_ratio = target_height / target_width
    im_ratio = graph.height / graph.width
    if target_ratio > im_ratio:
        # It must be fixed by width
        resize_width = target_width
        resize_height = round(resize_width * im_ratio)
    else:
        # Fixed by height
        resize_height = target_height
        resize_width = round(resize_height / im_ratio)

    image_resize = graph.resize((resize_width, resize_height), Image.ANTIALIAS)
    background = Image.new(graph.mode, (target_width, target_height), '#ffffff00')
    offset = (round((target_width - resize_width) / 2), round((target_height - resize_height) / 2))
    background.paste(image_resize, offset)
    background.save(fn)

#####################################################
# This is from TK version and needs to be revised
def make_graph(arcs: list, selected_app: str, ref: str, nodes: list, main_dir, bg_color, text_color, line_color, orientation):
    if isinstance(selected_app, tuple):
        selected_app = f'{selected_app[0]}–{selected_app[1]}'
    graph_data = [f'\t{" ".join(nodes)}']
    for arc in arcs:
        graph_data.append(f'\t{arc["from"]} -> {arc["to"]} [fillcolor="orange", color="{line_color}"]')
    graph_data = '\n'.join(graph_data)

    with open(f'{main_dir}/resources/template.dot', 'r', encoding='utf-8') as file:
        template = file.read()

    template = template.replace('zzz', graph_data)
    template = template.replace('_bg_color_', bg_color)
    template = template.replace('_font_color_', text_color)
    template = template.replace('_orientation_', orientation)
    # filename = f'{ref}U{selected_app}'

    # fn = f'{output_dir}/graphs/{filename}' # since it seems better not to rely on saved pngs,
                                                 # I'll use a temp file instead

    with open('.temp_graph.dot', 'w', encoding='utf-8') as file:
        file.write(template)

    call(f"dot -Tpng .temp_graph.dot -o .temp_graph.png")

    fix_size('.temp_graph.png')
    