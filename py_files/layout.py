import ctypes
import os
import platform
import re
from distutils.spawn import find_executable
from tkinter import *
from tkinter import messagebox, ttk
from tkinter import filedialog as fd
from lxml import etree as ET
from py_files.get_basetext import get_basetext, create_full_reference
from py_files.export_docx import export_docx
from py_files.make_graph import make_graph #, resize_png
from py_files.itsee_to_open_cbgm.itsee_to_open_cbgm import reformat_xml
from py_files.functions import router

class Layout:

    def __init__(self, main, main_dir, root):

        self.main_dir = main_dir
        self.main_window = main
        self.does_dot_exist = find_executable('dot')
        self.main_color = '#f4f4f4'
        self.root = root

        # FRAMES
        self.xml_dir_frame  = LabelFrame(main, text="")
        self.xml_dir_frame.grid(row=8, column=0, columnspan=3, pady=10, padx=10)

        self.ref_frame = LabelFrame(main, text="")
        self.ref_frame.grid(row=0, column=0, columnspan=3, pady=10, padx=10)

        self.index_frame = LabelFrame(main, text="")
        self.index_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=10)

        self.temp_frame = LabelFrame(self.index_frame) #packed after prev_index_btn

        self.basetext_frame = LabelFrame(main, text="")
        self.basetext_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10)

        self.rdgs_frame = LabelFrame(main, text=" Type\t    Readings", font=("Times", "12"))
        self.rdgs_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10)

        self.rdgs_left_frame = LabelFrame(self.rdgs_frame, borderwidth=0)
        self.rdgs_left_frame.pack(side=LEFT, padx=10)

        self.rdgs_wits_frame = LabelFrame(self.rdgs_frame, borderwidth=0)
        self.rdgs_wits_frame.pack(side=LEFT, padx=10)

        self.rdgs_type_frame = LabelFrame(self.rdgs_frame, borderwidth=0)
        self.rdgs_type_frame.pack(side=LEFT, padx=10)

        self.gen_frame = LabelFrame(main, text="Genealogical Relationships", 
                    font=("Times", "12"), bg=self.main_color)
        self.gen_frame.grid(row=5, column=0, pady=10, padx=10)

        edit_arc_frame = LabelFrame(main, text="Edit Relationships",
                        font=("Times", "12"))
        edit_arc_frame.grid(row=5, column=1, padx=20, pady=20)

        edit_rdg_type = LabelFrame(main, text='Edit Reading Type',
                        font=('Times', '12'))
        edit_rdg_type.grid(row=5, column=2, padx=20, pady=20)

        # LABELS
        self.xml_dir_label = Label(self.xml_dir_frame, text="XML Collation File Path: ",
                    font=("Times", "12"))
        self.xml_dir_label.grid(row=0, column=0)

        self.arc_label_1 = Label(edit_arc_frame, text="-->", font=("Times", "12"))
        self.arc_label_1.grid(row=0, column=2, padx=10)

        # BUTTONS

        self.load_xml_button = Button(self.xml_dir_frame, 
            text="Load/Refresh XML File", 
            font=("Times", "12"), 
            command=self.load_xml)
        self.load_xml_button.grid(row=0, column=3, padx=10)

        self.browse_button = Button(self.xml_dir_frame, text="Browse", font=("Times", "12"),
                        command=self.browse)
        self.browse_button.grid(row=0, column=2, padx=10)

        self.save_xml_btn = Button(self.xml_dir_frame, 
            text="Save and Exit", 
            font=("Times", "12"), 
            command=self.save_exit)
        self.save_xml_btn.grid(row=0, column=4, padx=10)

        self.export_button = Button(self.xml_dir_frame, text="Export docx",
                font=("Times", "12"), command=self.export_app_as_docx)
        self.export_button.grid(row=0, column=5, padx=10)

        self.prev_vrs_btn = Button(self.ref_frame, text="<Prev", font=("Times", "12"),
                        command=self.prev_btn_cmd, state=DISABLED)
        self.prev_vrs_btn.grid(row=0, column=0)

        self.next_vrs_btn = Button(self.ref_frame, text="Next>", font=("Times", "12"),
                        command=self.next_btn_cmd, state=DISABLED)
        self.next_vrs_btn.grid(row=0, column=2)

        self.prev_index_button = Button(self.index_frame, text="<Prev", font=("Times", "12"),
                            command=self.prev_index_cmd, state=DISABLED)
        self.prev_index_button.pack(side=LEFT, padx=10)
        self.temp_frame.pack(side=LEFT)

        self.next_index_button = Button(self.index_frame, text="Next>", font=("Times", "12"),
                            command=self.next_index_cmd, state=DISABLED)
        self.next_index_button.pack(side=RIGHT, padx=10)

        self.update_arc_button = Button(edit_arc_frame, text="Add", font=("Times", "12"),
                            command=self.add_arc)
        self.update_arc_button.grid(row=0, column=4, padx=30, pady=30)

        self.delete_arc_button = Button(edit_arc_frame, text="Delete", 
                            font=("Times", "12"), command=self.delete_arc)
        self.delete_arc_button.grid(row=0, column=5, padx=30, pady=30)

        self.add_rdg_type_button = Button(edit_rdg_type, text="Change", 
                                    font=("Times", "12"), command=self.change_rdg) #packed after rdg combobox
        self.delete_rdg_type_button = Button(edit_rdg_type, text="Delete", 
                                        font=("Times", "12"), command=self.delete_rdg) #packed after rdg combobox

        # ENTRY WIDGETS
        self.arc_entry_1 = Entry(edit_arc_frame, width=3, font=("Times", "12"))
        self.arc_entry_1.grid(row=0, column=1, padx=10)
        self.arc_entry_1.bind('<Return>', self.on_enter)
        self.arc_entry_2 = Entry(edit_arc_frame, width=3, font=("Times", "12"))
        self.arc_entry_2.grid(row=0, column=3, padx=10)
        self.arc_entry_2.bind('<Return>', self.on_enter)

        self.xml_dir_entry = Entry(self.xml_dir_frame, width=50, font=("Times", "12"))
        self.xml_dir_entry.grid(row=0, column=1)

        self.ref_entry = Entry(self.ref_frame, width=30, font=("Times", "12"))
        self.ref_entry.grid(row=0, column=1, padx=50)

        # other widgets
        self.rdg_combobox = ttk.Combobox(edit_rdg_type, width=3)
        self.rdg_combobox.pack(side=LEFT, padx=10, pady=20)
        self.rdg_type_combobox = ttk.Combobox(edit_rdg_type, values=['orthographic', 'deficient', 'lac', 'om'])
        self.rdg_type_combobox.pack(side=LEFT, padx=10, pady=20)
        self.add_rdg_type_button.pack(side=LEFT, padx=10, pady=20)
        self.delete_rdg_type_button.pack(side=LEFT, padx=10, pady=20)

    def disable_enable_buttons(self, current):
        # set verse nav buttons
        if current.getprevious().tag != "ab":
            self.prev_vrs_btn.config(state=DISABLED)
        else:
            self.prev_vrs_btn.config(state=NORMAL)
        if current.getnext() == None:
            self.next_vrs_btn.config(state=DISABLED)
        else:
            self.next_vrs_btn.config(state=NORMAL)
        try:
            app_prev = self.app.getprevious()
            if app_prev == None:
                prev_index_button.config(state=DISABLED)
            elif app_prev.tag == "seg":
                app_prev = app_prev.getprevious()
        except:
            app_prev = None
        if app_prev == None:
            self.prev_index_button.config(state=DISABLED)
        else:
            self.prev_index_button.config(state=NORMAL)
        # set index next button
        try:
            app_next = self.app.getnext()
            if app_next == None:
                next_index_button.config(state=DISABLED)
            elif app_next.tag == "seg":
                app_next = app_next.getnext()
        except:
            app_next = None
        if app_next == None:
            self.next_index_button.config(state=DISABLED)
        else:
            self.next_index_button.config(state=NORMAL)

    def update_index(self, current):
        verse = re.sub("-APP", "", current.get('verse'))
        apps = current.findall('app')
        if self.app == None:
            i_from = 0
            i_to = -1
        elif self.app.tag == "app":
            i_from = int(self.app.get('from'))
            i_to = int(self.app.get('to'))
        for widget in self.temp_frame.winfo_children():
            widget.destroy()
        self.temp_frame.pack(side=LEFT)
        # find and display all variation indexes
        if apps == []:
            app_label = Label(self.temp_frame, text="No Variation Units",
                        font=("Times", "12"))
            app_label.pack(side=LEFT, padx=10)
        else:
            if self.app.get('from') == self.app.get('to'):
                index = self.app.get('from')
            else:
                index = self.app.get('from')+" - "+self.app.get('to')
            for app_unit in apps:
                if app_unit.get('from') == app_unit.get('to'):
                    app_index = app_unit.get('from')
                else:
                    app_index = f"{app_unit.get('from')} - {app_unit.get('to')}"
                app_label = Label(self.temp_frame, text=app_index, font=("Times", "12"))
                app_label.pack(side=LEFT, padx=15)
                if app_index == index:
                    app_label.config(bg="spring green")
        self.ref_entry.delete(0, END)
        self.ref_entry.insert(0, verse)
        self.fill_basetext(i_from, i_to)
        self.get_arcs(index)

    def updater(self, change, direction):
        if change == 'initial startup':
            current, self.app = router(change, direction, self.tree, self.ref_entry.get(), None)
        else: current, self.app = router(change, direction, self.tree, self.ref_entry.get(), self.app)
        self.update_index(current)
        self.disable_enable_buttons(current)

    def browse(self):
        xml_dir = fd.askopenfilename(
            initialdir=f'{self.main_dir}/collations')
        self.xml_dir_entry.insert(0, xml_dir)

    def get_arcs(self, index):
        if self.app == None:
            pass
        else:
            rdgs = self.app.findall('rdg')
            rdgs_values = []
            for rdg in rdgs:
                rdgs_values.append(rdg.get('n'))
            self.rdg_combobox.config(values=rdgs_values)
            for widget in self.rdgs_left_frame.winfo_children():
                widget.destroy()
            for widget in self.rdgs_wits_frame.winfo_children():
                widget.destroy()
            for widget in self.rdgs_type_frame.winfo_children():
                widget.destroy()
            for rdg in rdgs:
                if rdg.get('type'):
                    if rdg.get('type') == 'om':
                        rdg_type_text = 'omit\t'
                    elif rdg.get('type') == 'orthographic':
                        rdg_type_text = 'orth\t'
                    elif rdg.get('type') == 'deficient':
                        rdg_type_text = 'defi\t'
                    elif rdg.get('type') == 'lac':
                        rdg_type_text = 'lacu\t'
                    else:
                        rdg_type_text = f'{rdg.get("type")}\t'
                else:
                    rdg_type_text = 'none\t'    
                if rdg.text:
                    greek_text = rdg.text
                else:
                    greek_text = ''
                rdg_label = Label(
                    self.rdgs_left_frame, 
                    text=f"{rdg_type_text}   {rdg.get('n')}   {greek_text}", 
                    font=("Times", "12"), wraplength=1000, padx=3)
                rdg_label.pack(side=TOP, anchor=W)
                rdg_wits = Label(
                    self.rdgs_wits_frame, width=75,
                    text=f"{rdg.get('wit').replace(' ', '  ')}", anchor='w',
                    font=("Times", "12"), wraplength=1000)
                rdg_wits.pack(side=TOP)
            arcs = self.app.findall('note/graph/arc')
            self.populate_relationships(arcs, index)


    def populate_relationships(self, arcs, index):
        for widget in self.gen_frame.winfo_children():
            widget.destroy()
        if self.does_dot_exist == None:
            if arcs == []:
                arc_label = Label(self.gen_frame, text="No Arcs Present",
                            font=("Times", "12"))
                arc_label.pack(side=TOP)
            else:
                for arc in arcs:
                    arc_label = Label(
                        self.gen_frame, 
                        text=f"{arc.get('from')} --> {arc.get('to')}", 
                        font=("Times", "12"))
                    arc_label.pack(side=TOP)
        else:
            if arcs == []:
                nodes = self.app.findall('note/graph/node')
            else:
                nodes = None
            filename = make_graph(arcs, index, self.ref_entry.get(), nodes)
            filename = f'{filename}.png'
            graph_image = PhotoImage(file=f'files/graphs/{filename}')
            arc_label = Label(
                self.gen_frame, image=graph_image, 
                height=350, width=400, bg=self.main_color)
            arc_label.image = graph_image
            arc_label.pack()

    def load_xml(self):
        cx_fname = self.xml_dir_entry.get()
        if cx_fname == "":
            messagebox.showinfo(title="Uh-oh", 
            message="File path field is blank. Type in the file path\
(location) or click 'Browse'")
        elif '.xml' not in cx_fname:
            messagebox.showwarning(title='Uh-oh', 
            message="Input must be an XML (.xml) output file from the ITSEE Collation Editor")
        else:
            with open(cx_fname, 'r', encoding='utf-8') as file:
                self.tree = file.read()
            see_if_reformatted = re.search('<teiHeader>', self.tree)
            if see_if_reformatted == None:
                user_response = messagebox.askokcancel(
                    message='The XML input file needs to be reformatted.\n\
select "Ok" to reformat the XML input using an\n\
included utility created by Joey McCollum')
                if user_response == True:
                    reformatted_path = reformat_xml(cx_fname)
                    self.xml_dir_entry.delete(0, END)
                    self.xml_dir_entry.insert(0, reformatted_path)
                    self.load_xml()
                else:
                    return None
            else:
                self.tree = re.sub("xml:id", "verse", self.tree)
                self.tree = re.sub("<TEI xmlns=\"http://www.tei-c.org/ns/1.0\">", "<TEI>", self.tree)
                self.tree = re.sub("<?xml version='1.0' encoding='UTF-8'?>", "", self.tree)
                with open(cx_fname, 'w', encoding='utf-8') as file:
                    file.write(self.tree)
                parser = ET.XMLParser(remove_blank_text=True)
                self.tree = ET.parse(cx_fname, parser)
                self.updater("initial startup", "None")

    def save_exit(self):
        try:
            if self.tree == None:
                pass
            else:
                self.write_new_xml()
        except:
            pass
        self.root.destroy()

    def prev_btn_cmd(self):
        self.updater("verse", "prev")

    def next_btn_cmd(self):
        self.updater("verse", "next")

    def prev_index_cmd(self):
        self.updater("index", "prev")

    def next_index_cmd(self):
        self.updater("index", "next")

    def fill_basetext(self, i_from, i_to):
        ref = str(self.ref_entry.get())
        basetext = get_basetext(ref, self.main_dir)
        index_list = []
        for i in range(i_from, i_to+1):
            if i % 2 == 0:
                index_list.append(str(i))
        index = []
        count = 2
        for i in range(len(basetext)):
            count_str = str(count)
            index.append(count_str)
            count += 2
        for widget in self.basetext_frame.winfo_children():
            widget.destroy()
        for ind, word, in zip(index, basetext):
            index_label = Label(self.basetext_frame, text=ind+"\n"+word,
                            font=("Times", "12"))
            index_label.pack(side=LEFT, padx=5)
            if ind in index_list:
                index_label.config(bg="spring green")

    def write_new_xml(self):
        self.tree.write(self.xml_dir_entry.get(), encoding="utf-8", pretty_print=True)
        with open(self.xml_dir_entry.get(), 'r', encoding='utf-8') as file:
            new_file = file.read()
        new_file = re.sub("verse", "xml:id", new_file)
        new_file = re.sub(
            "<TEI>", 
            "<?xml version='1.0' encoding='UTF-8'?>\n<TEI xmlns=\"http://www.tei-c.org/ns/1.0\">", 
            new_file)
        with open(self.xml_dir_entry.get(), 'w', encoding='utf-8') as file:
            file.write(new_file)

    def add_arc(self):
        if self.arc_entry_1.get() == "" or self.arc_entry_2.get() == "":
            messagebox.showinfo(title="Uh-oh", 
            message="Remember to fill both boxes in the 'Edit Relationships' section")
        else:
            arc = ET.Element("arc")
            arc.set('from', self.arc_entry_1.get())
            arc.set('to', self.arc_entry_2.get())
            arc_parent = self.app.find("note/graph")
            arc_parent.append(arc)
            self.updater('arc update', 'None')
            self.write_new_xml()
        
    def delete_arc(self):
        if self.arc_entry_1.get() == "" or self.arc_entry_2.get() == "":
            messagebox.showinfo(title="Uh-oh", 
            message="Remember to fill both boxes in the 'Edit Relationships' section")
        else:
            arcs = self.app.findall('note/graph/arc')
            for arc in arcs:
                if arc.get('from') == self.arc_entry_1.get() and arc.get('to') == self.arc_entry_2.get():
                    arc.getparent().remove(arc)
            self.updater('arc update', 'None')
            self.write_new_xml()

    def export_app_as_docx(self):
        result = export_docx(self.tree, self.main_dir)
        messagebox.showinfo(message=result)

    def change_rdg(self):
        new_rdg_type = self.rdg_type_combobox.get()
        rdg_n = self.rdg_combobox.get()
        rdg = self.app.find(f".//rdg[@n='{rdg_n}']")
        rdg.set('type', new_rdg_type)
        self.updater('arc update', 'None')

    def delete_rdg(self):
        rdg_n = self.rdg_combobox.get()
        rdg = self.app.find(f".//rdg[@n='{rdg_n}']")
        rdg.attrib.pop('type', None)
        self.updater('arc update', 'None')
    
    def on_enter(self, event):
        self.add_arc()  