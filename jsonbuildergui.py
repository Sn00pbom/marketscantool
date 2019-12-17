from tkinter import *
import json


def print_select(selected):
    names = ['a', 'b', 'c', 'd']
    vals = [1, 2.0, True, [1, 2, 3]]
    for i in selected:
        ii = int(i)
        print(names[ii], vals[ii])


def run():
    root = Tk()
    root.title('JSON Builder')
    root.geometry("400x200")


    lb = Listbox(root, selectmode=EXTENDED)
    lb.pack()


    for item in ["one", "two", "three", "four"]:
        lb.insert(END, item)

    b = Button(root, text='Button',
               command=lambda: print_select(lb.curselection()))
    b.pack()

    mainloop()


if __name__ == '__main__':
    run()
