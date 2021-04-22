import os
from tkinter.filedialog import askopenfilename
from scipy.io import loadmat
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading


class OpenFile:
    """Provides a tkinter window asking for a .mat file and retrieves the data from it."""

    def __init__(self, window):
        """Main setup of the window and its elements."""

        self.window = window
        self.window.resizable(0, 0)
        self.window.title('Open')
        self.name = tk.StringVar()
        self._params = np.empty(0)

        self.label = tk.Label(self.window, text='Enter a valid path name (.mat)')
        self.label.place(relx=0.5, y=20, anchor='center')
        self.entry = ttk.Entry(self.window, width=30, textvariable=self.name)
        self.entry.place(relx=0.5, y=50, anchor='center')
        self.open_button = ttk.Button(self.window, text='Browse', command=self.open_file)
        self.open_button.place(relx=0.45, y=85, anchor='e')
        self.button = ttk.Button(self.window, text='Run GUI', command=self.run)
        self.button.place(relx=0.55, y=85, anchor='w')
        self.label2 = tk.Label(self.window)

    @property
    def get_params(self):
        """Returns the depth scale, x-scale, y-scale and the scan array."""
        return self._params

    def open_file(self):
        """Opens the system open window in order to load a file."""
        filename = askopenfilename(parent=self.window, filetypes=[('mat files', '*mat'), ('All files', '*')])
        self.label.configure(text='Enter a valid path name (.mat)')
        self.name.set(filename)

    def load_data(self):
        """Provides filtration and normalization of the imported data array. Sets the resolution scales.
        After completion the window gets destroyed."""

        self.label2['text'] = 'Loading file'

        _main_data = loadmat(self.name.get())
        for key in _main_data.keys():
            if isinstance(_main_data[key], np.ndarray):
                _main_data = np.squeeze(_main_data[key])

        if len(_main_data.shape) != 1:
            self.label2['text'] += "\nThe file is not a vector!"
            self.window.configure(cursor='arrow')
            self.button.configure(state='normal')
            self.open_button.configure(state='normal')
            self.entry.configure(state='normal')
            return

        self._params = _main_data
        self.window.after(1000, self.window.destroy)

    def run(self):
        """Handles whether the provided file name is correct and has the right extension.
        If so, the function to load the file is called."""

        if os.path.exists(self.name.get()):
            if not self.name.get().lower().endswith('.mat'):
                self.label.configure(text='Wrong file type')
            else:
                loading_thread = threading.Thread(target=self.load_data)
                self.label.configure(text="Please wait for the data to be loaded")
                self.window.configure(cursor='watch')
                self.button.configure(state='disabled')
                self.open_button.configure(state='disabled')
                self.entry.configure(state='disabled')
                self.label2.place(relx=0.5, y=130, anchor='n')
                loading_thread.daemon = True
                loading_thread.start()
        else:
            self.label.configure(text="File not found")
