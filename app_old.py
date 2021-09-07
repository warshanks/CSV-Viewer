from tkinter import *
from tkinter import ttk, filedialog
from numpy import index_exp
import pandas as pd
import os
import glob
import pyperclip3 as pc

def browse_button():
    global file_path
    cwd = os.getcwd()
    file_path= filedialog.askopenfilename(initialdir=cwd, filetypes=[("CSV file","*.csv")])
    # read the selected file into a pandas DataFrame
    tree_main.delete(*tree_main.get_children())             # delete previous tree
    tree_stats.delete(*tree_stats.get_children())
    tree_focus.delete(*tree_focus.get_children())
    txt.delete("1.0", END)
    insert_data()
    basic_stats()
    insert_tree_stats()

def insert_data():
    global data
    global columns
    data = pd.read_csv(file_path)
    columns = data.columns.values
    columns_tupel = tuple(columns)
    # Define Columns
    tree_main['columns'] = columns_tupel
    # Formate Columns
    tree_main.column('#0', width=0, stretch=NO)
    for col in columns:
        tree_main.column(col, anchor=W, width=80)
    # Create Headings
    tree_main.heading('#0', text='')
    for col in columns:
        tree_main.heading(col, text=col, anchor=W)
    # Add Data
    records = data.to_records(index=False)
    result = list(records)
    for counter, row in enumerate(result):
        tree_main.insert(parent='', index='end', iid=str(counter), text='', values=tuple(row))

def basic_stats():
    numCols = data.shape[1]
    numRows = data.shape[0]
    dups = data.duplicated().sum() 
    if dups > 0 : x = 'yes' 
    else : x = 'no'
    statsContent.config(text=f"Rows: {numRows} / Cols: {numCols} / Duplicates: {x}")

def insert_tree_stats():
    tree_stats['columns'] = ('Column', 'Data Type', 'Missing Values')
    tree_stats.column('#0', width=0, stretch=NO)
    tree_stats.column('Column',anchor=W)
    tree_stats.column('Data Type',anchor=W)
    tree_stats.column('Missing Values', anchor=W, width=80, stretch=NO)
    tree_stats.heading('#0', text='')
    tree_stats.heading('Column',text='Column', anchor=W)
    tree_stats.heading('Data Type',text='Data Type', anchor=W)
    tree_stats.heading('Missing Values',text='Missing Values', anchor=W)
    df_types = pd.DataFrame(data.dtypes)
    df_types['missing'] = data.isnull().sum(axis=0).values.tolist()
    df_records = df_types.to_records()
    for counter, row in enumerate(list(df_records)):
        tree_stats.insert(parent='', index='end', iid=str(counter), text='', values=tuple(row))

def select_item(event):
    global index
    index = tree_main.selection()[0]
    tree_focus.delete(*tree_focus.get_children())       # delete prev tree
    # insert data into tree_focus
    tree_focus['columns'] = ('Column', 'Content')
    tree_focus.column('#0', width=0, stretch=NO)
    tree_focus.column('Column',anchor=W, width=80)
    tree_focus.column('Content',anchor=W, width=80)
    tree_focus.heading('#0', text='')
    tree_focus.heading('Column',text='Column', anchor=W)
    tree_focus.heading('Content',text='Content', anchor=W)
    # create DataFrame to query data
    select_data = data.iloc[[index]]
    columns = select_data.columns.values.tolist()
    values = select_data.values.tolist()[0]
    df_dict = {'columns': columns, 'content': values}
    df_select = pd.DataFrame(df_dict)
    df_records = df_select.to_records()
    for counter, row in enumerate(list(df_records)):
        lst = [row[1], row[2]]
        tree_focus.insert(parent='', index='end', iid=str(counter), text='', values=tuple(lst))

def show_content(event):
    global index_focus
    index_focus = tree_focus.selection()[0]
    select_data = data.iloc[[index]]
    columns = select_data.columns.values.tolist()
    values_ = select_data.values.tolist()[0]
    str = values_[int(index_focus)]
    txt.delete("1.0", END)
    txt.insert(END, str)

def lookup_data():
    inputValue = txtBox.get("1.0","end-1c")
    # clear main, focus and txtBox
    tree_main.delete(*tree_main.get_children())
    tree_focus.delete(*tree_focus.get_children())
    txtBox.delete('1.0', END)
    # open window to ask which column to search in
    search = Toplevel(root)
    search.title("Select Column")
    search.geometry("400x100")
    search_frame = LabelFrame(search, text="Which column?", fg="black")
    search_frame.pack(padx=10, pady=10)
    # dropDown
    variable = StringVar(search)
    variable.set(columns[0])
    # style OptionMenu
    opt = OptionMenu(search_frame, variable, *columns)
    opt.config(width=90)
    opt.config(fg='black')
    opt.pack()
    
    def search_main():
        print(variable.get())
        search.destroy()
        tree_main.delete(*tree_main.get_children())  
        #todo

    search_Button = Button(search_frame, text="Search", fg="black", command=search_main)
    search_Button.pack()
    

    # search pandas DataFrame
    # check type of serach parameter
    

def delete_many():
    # functiont hat deltet the output on the gui
    tree_main.delete(*tree_main.get_children())             # delete previous tree
    tree_stats.delete(*tree_stats.get_children())
    tree_focus.delete(*tree_focus.get_children())
    txt.delete("1.0", END)

def clipboard(event):
    try: 
        m.tk_popup(event.x_root, event.y_root)
        col = tree_main.identify_column(event.x)
        col = col[1:]
        col = int(col) - 1
        index = tree_main.selection()[0]
        copy_to_clipboard = data.iloc[[index]].values[0][col]
        pc.copy(copy_to_clipboard)
    finally:
        m.grab_release()

## ININT GUI
root = Tk()
root.title("CSV Viewer")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
root.columnconfigure(0, weight=0)
root.columnconfigure(1, weight=1)

## STYLING
style = ttk.Style(root)
style.theme_use("default")
style.configure("Treeview.heading", 
    background = "silver",
    foreground = "black",
)
style.map('Treeview', background=[('selected', 'red')]) 

## WIDGETS
button_frame = Frame(root)
# Open Button
openButton = Button(button_frame, text="Open File...", fg="black", command=browse_button)
# Open in new Window
openNewWinButton = Button(button_frame, text="Open File in new Window", fg="black")    # ToDo
# Reset Button
resetButton = Button(button_frame, text="Reset", fg="black", command=delete_many)      # ToDo
# Statistics of the CSV-File
statsFrame = Frame(root)
statsHeader = Label(statsFrame, text="Basic stats of file", fg="black")
statsContent = Label(statsFrame, fg="black")
# TreeView Stats
tree_stats = ttk.Treeview(statsFrame)

# TreeView Main
tree_frame = Frame(root)
txtBox = Text(tree_frame, height=1, width=50, fg="black", bg="white")
buttonSearch = Button(tree_frame, text="Search", fg="black", comman=lookup_data)
tree_scroll = Scrollbar(tree_frame)
tree_main = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
tree_scroll.config(command=tree_main.yview)

# FOCUS SECTION
focus_frame = Frame(root)

# TreeView Focus
tree_focus = ttk.Treeview(focus_frame)

# Text of content
txt = Text(focus_frame, bg="white", fg="black", padx=5, width=40)

# misc
m = Menu(root, tearoff = 0)
m.add_command(label = 'Copy to Clipboard')

## LAYOUT 
# Column 1 (left side)
button_frame.grid(column=0, row=0, sticky="N")
openButton.grid(column=0, row=0, sticky="N")
openNewWinButton.grid(column=0, row=1, sticky="N")
resetButton.grid(column=0, row=2, sticky="N")

statsFrame.grid(column=0, row=1, sticky="NW")
statsHeader.grid(column=0, row=0, sticky="N")
statsContent.grid(column=0, row=1, sticky="NW")
tree_stats.grid(column=0, row=2, sticky="NW")


# Column 2 (right side)
tree_frame.grid(column=1, row=0, sticky="NW")
txtBox.grid(column=0, row=0, sticky="NE")
buttonSearch.grid(column=1, row=0, sticky="NE")
tree_main.grid(column=0, row=1, sticky="NW")
tree_scroll.grid(column=1, row=1, sticky="NWS")

focus_frame.grid(column=1, row=1, sticky="NW")
tree_focus.grid(column=0, row=0, sticky="NW")
txt.grid(column=1, row=0)


## BINDINGS
tree_main.bind('<ButtonRelease-1>', select_item)
tree_main.bind('<ButtonRelease-2>', clipboard)
tree_focus.bind('<ButtonRelease-1>', show_content)

root.mainloop()