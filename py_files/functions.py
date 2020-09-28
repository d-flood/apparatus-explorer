from os import mkdir

import lxml


def router(change, direction, tree, ref_entry, app):
    root = tree.getroot()
    ab = f"{ref_entry}-APP"
    if change == "verse":
        current = root.find(f".//ab[@verse='{ab}']")
        if direction == "next":
            current = current.getnext()
        elif direction == "prev":
            current = current.getprevious()
        elif direction == "None":
            pass
        app = current.find('app')
    elif change == "index":
        current = root.find(f".//ab[@verse='{ab}']")
        if direction == "next":
            app = app.getnext()
            if app.tag == "seg":
                app = app.getnext()
        if direction == "prev":
            app = app.getprevious()
            if app.tag == "seg":
                app = app.getprevious()
    elif change == "initial startup":
        if ref_entry == "":
            current = root.find("ab")
        else:
            current = root.find(f".//ab[@verse='{ab}']")
        app = current.find('app')
    elif change == "arc update":
        current = root.find(f".//ab[@verse='{ab}']")
    return current, app


def check_make_temp_dirs(main_dir):
    temp_directories = (
        f'{main_dir}/exported',
        f'{main_dir}/files/dot',
        f'{main_dir}/files/graphs'
    )

    for temp_directory in temp_directories:
        try:
            mkdir(temp_directory)
        except FileExistsError:
            pass
