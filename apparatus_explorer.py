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
from py_files.make_graph import make_graph
from py_files.itsee_to_open_cbgm.itsee_to_open_cbgm import reformat_xml
from py_files.layout import Layout
from py_files.functions import check_make_temp_dirs
from py_files.combine_files import Combine

my_os = platform.system()
if my_os == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

main_dir = os.getcwd()
main_dir = re.sub(r"\\", "/", main_dir)

main = Tk()
######################################
tabControl = ttk.Notebook(main)

app_ex_tab = ttk.Frame(tabControl)
combine_files_tab = ttk.Frame(tabControl)

tabControl.add(app_ex_tab, text="  Apparatus Explorer  ", pad=5)
tabControl.add(combine_files_tab, text="  Combine Files  ", pad=5)
tabControl.pack(expand=1, fill="both")

main_layout = Layout(app_ex_tab, main_dir, main)
combine_layout = Combine(combine_files_tab, main_dir)
#######################################
check_make_temp_dirs(main_dir)
main.title("Apparatus Explorer v.05")
main.iconbitmap(main_dir+"/files/console.ico")

main.mainloop()
