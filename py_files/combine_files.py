from os import listdir
import re
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb

try:
    from natsort import natsorted
    natural_sort = True
except:
    natural_sort = False


xml_header = '''<?xml version='1.0' encoding='utf-8'?><TEI xmlns="http://www.tei-c.org/ns/1.0">'''

help_string = '''Click "Select Folder" to choose a folder in which 
all the verse collation outputs of a chapter or 
section belong. If these files are in the expected 
format, then they will be combined into one file. 
Ideally the combined file will comprise a full 
chapter or other pericope. The verse collation 
files must be downloaded as the output of the 
Collation Editor
(https://github.com/itsee-birmingham/standalone_collation_editor).

Note: The single-verse collation output files
may be out of order. This will be fixed if the
natsort Python module is installed
(https://pypi.org/project/natsort/)
If you prefer not to use natsort to sort the 
verses properly, then the files must be named
like this: Rom01.01 instead of Rom1.1'''


class Combine:

    def __init__(self, combo_tab, main_dir):

        self.main_dir = main_dir

        self.select_dir_button = Button(combo_tab, text='Select Folder', 
                font=('Times', '12'), command=self.select_directory)
        self.select_dir_button.grid(row=0, column=0, padx=50, pady=20)

        self.combine_button = Button(combo_tab, text='Combine Files',
                font=('Times', '12'), command=self.combine_files)
        self.combine_button.grid(row=1, column=0, padx=50, pady=20)

        self.found_verses = LabelFrame(combo_tab, text='Verses to be combined:',
                font=('Times', '12'))
        self.found_verses.grid(row=0, column=1, columnspan=10, rowspan=2)

        self.help_button = Button(combo_tab, text='Help', font=('Times', '12'),
                command=self.help_me)
        self.help_button.grid(row=2, column=0, padx=50, pady=20)

        self.ready = False

    def select_directory(self):

        self.directory = fd.askdirectory(initialdir=self.main_dir)
        print(self.directory)
        self.files = listdir(self.directory)
        if natural_sort == True:
            self.files = natsorted(self.files)
        else:
            mb.showinfo(title='Attention', message='The "natsort" Python module was not loaded.\n\
Check the order of verse files before combining\n\
them because they may be appended out of order.\n\
Click "Help" for more info.')
            self.files = self.files.sort()
        row = 0
        column = 0
        count = 0
        for f in self.files:
            if f.endswith('.xml'):
                if count == 15 or count == 30 or count == 45 or count == 60 or count == 75:
                    column += 1
                    row = 0
                count += 1
                verse_file = Label(self.found_verses, text=f,
                    font=('Times', '12'), anchor='w', width=15)
                verse_file.grid(row=row, column=column, padx=5, pady=5)
                row += 1
            else:
                continue
        self.ready = True

    def combine_files(self):
        if self.ready == False:
            pass
        else:
            combined_files = ''
            problems = []
            probs = False
            for fn in self.files:
                if fn.endswith('.xml'):
                    try:
                        with open(f'{self.directory}/{fn}', 'r', encoding='utf-8') as file:
                            xml = file.read()
                            pass
                        xml = re.sub('\n', '', xml)
                        xml = re.search(r'<ab(.+)</ab>', xml)
                        xml = xml.group(0)
                        combined_files = f'{combined_files.strip()}{xml}'
                    except:
                        problems.append(fn)
                        probs = True
            combined_files = f'{xml_header}{combined_files}</TEI>'
            if probs == True:
                problems = '\n'.join(problems)
                mb.showwarning(title='Uh-oh', message=f'The following files were not in the expected format:\n\
{problems}\nFiles should be downloaded from the Collation Editor')
            else:
                path_to_save = fd.asksaveasfilename(initialdir=f'{self.main_dir}/collations',
                                defaultextension='.xml', filetypes=[("xml files", '*.xml')])
                with open(path_to_save, 'w', encoding='utf-8') as full_doc:
                    full_doc.write(combined_files)
    
    def help_me(self):
        mb.showinfo(title='Info', message=help_string)
        pass