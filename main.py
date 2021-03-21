from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import loadmat
from scipy import signal
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from navigator import Navigator
from copy import deepcopy


def click(event):
    """Gets called when clicked on the frequency response subplot. Gathers the coordinates of the click and fills the
    entries with the corresponding values. Then calls the filtering function."""
    x, y = event.xdata, event.ydata
    if filter_type_cbb.get() == 'Off' or event.inaxes != ax[1, 0]:
        pass
    else:
        if filter_type_cbb.get() == 'Lowpass' or filter_type_cbb.get() == 'Highpass':
            left_cutoff_entry.delete(0, tk.END)
            left_cutoff_entry.insert(tk.END, round(x, 2))
        if filter_type_cbb.get() == 'Bandpass' or filter_type_cbb.get() == 'Bandstop':
            left = round(x - (float(right_cutoff_entry.get()) - float(left_cutoff_entry.get())) / 2, 2)
            right = round(x + (float(right_cutoff_entry.get()) - float(left_cutoff_entry.get())) / 2, 2)
            if x - (right - left) / 2 < 0:
                left = 0.01
            if x + (right - left) / 2 > 50:
                right = 49.99

            left_cutoff_entry.delete(0, tk.END)
            right_cutoff_entry.delete(0, tk.END)
            left_cutoff_entry.insert(tk.END, left)
            right_cutoff_entry.insert(tk.END, right)
        start_filtering(None)


def hover_enter(event):
    """Gets called when hovered inside a subplot. Changes the cursor to a cross."""
    canvas.get_tk_widget().configure(cursor='tcross')


def hover_leave(event):
    """Gets called when hovered outside a subplot. Changes the cursor to a normal arrow."""
    canvas.get_tk_widget().configure(cursor='arrow')


def start_filtering(event):
    global filtered
    ax[0, 0].clear()
    ax[1, 0].clear()

    if filter_type_cbb.get() == 'Off':
        ax[0, 0].plot(t, sig, color='#1f77b4', lw=1)
        ax[1, 0].magnitude_spectrum(sig, Fs=fs, color='#1f77b4', lw=1)
        left_cutoff_entry.configure(state='disabled')
        right_cutoff_entry.configure(state='disabled')
        filter_order.configure(state='disabled')
        label.configure(text='No filter applied')
    else:
        try:
            left_cutoff_entry.configure(state='normal')
            filter_order.configure(state='normal')
            if left_cutoff_entry.get() == '':
                left_cutoff_entry.insert(tk.END, 10)
            if filter_order.get() == '':
                filter_order.insert(tk.END, 10)
            left = round(float(left_cutoff_entry.get()), 2)

            if filter_type_cbb.get() == 'Lowpass' or filter_type_cbb.get() == 'Highpass':
                right_cutoff_entry.configure(state='disabled')
                label.configure(text='Critical frequency (Hz):')
                sos = signal.butter(int(filter_order.get()), (left,), filter_type_cbb.get().lower(), fs=fs, output='sos')

                if filter_type_cbb.get() == 'Highpass':
                    ax[1, 0].axvspan(left, 50, alpha=0.3, color='red')
                else:
                    ax[1, 0].axvspan(0, left, alpha=0.3, color='red')

            if filter_type_cbb.get() == 'Bandpass' or filter_type_cbb.get() == 'Bandstop':
                label.configure(text='Critical frequencies (Hz):')
                right_cutoff_entry.configure(state='normal')
                if right_cutoff_entry.get() == '':
                    right_cutoff_entry.insert(tk.END, 20)
                right = round(float(right_cutoff_entry.get()), 2)
                if right < left:
                    right = left + fs/10
                    if right > fs/2:
                        right -= fs/10
                        left = right - fs/10

                sos = signal.butter(int(filter_order.get()), (left, right), filter_type_cbb.get().lower(), fs=fs, output='sos')
                ax[1, 0].axvline(right, color='red')

                if filter_type_cbb.get() == 'Bandstop':
                    ax[1, 0].axvspan(0, left, alpha=0.3, color='red')
                    ax[1, 0].axvspan(right, 50, alpha=0.3, color='red')
                else:
                    ax[1, 0].axvspan(left, right, alpha=0.3, color='red')

                left_cutoff_entry.delete(0, tk.END)
                left_cutoff_entry.insert(tk.END, left)
                right_cutoff_entry.delete(0, tk.END)
                right_cutoff_entry.insert(tk.END, right)

            filtered = signal.sosfilt(sos, sig)

            ax[0, 0].plot(t, filtered, color='#1f77b4', lw=1)
            ax[1, 0].magnitude_spectrum(sig, Fs=fs, color='#1f77b4', lw=1)
            ax[1, 0].magnitude_spectrum(filtered, Fs=fs, color='y', lw=1)

            ax[1, 0].axvline(left, color='red')  # cutoff frequency
            ax[1, 0].legend(('Original', 'Filtered'), prop={'size': 8}, loc=1)

        except ValueError as ex:
            messagebox.showerror(ex, str(ex).capitalize())
            return

    ax[0, 0].set_xlim(0, 1)
    ax[1, 0].set_xlim(0, 50)
    if toolbar._active is None:
        toolbar.forward()
    canvas.draw()


# GETTING THE INPUT SIGNAL, EXTRACTING ITS USEFUL DATA
# sig = loadmat(r'C:\Users\ADMIN\Documents\MATLAB\MSI\lab2.mat')
# for key in sig.keys():
#     if isinstance(sig[key], np.ndarray):
#         sig = np.squeeze(sig[key])

t = np.linspace(0, 1, 1000, False)
sig = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 20 * t)
fs = 100
filtered = sig

# BEGIN OF GUI, PLACEMENT OF ELEMENTS, BINDING TO EVENTS, ETC
root = tk.Tk()  # main window
root.geometry('1000x600')  # main window size
root.configure(background='white')  # main window background color
root.title('GUI')  # main window title
figure, ax = plt.subplots(2, 2)
ax[0, 0].plot(t, sig, color='#1f77b4', lw=1)  # upper subplot, time domain
ax[0, 0].set_xlim(0, 1)
ax[1, 0].magnitude_spectrum(sig, Fs=fs, color='#1f77b4', lw=1)  # bottom subplot, frequency domain
ax[1, 0].set_xlim(0, 50)
plt.autoscale(enable=True)

canvas = FigureCanvasTkAgg(figure, root)  # making the plots a Tkinter object and binding it to the main window
canvas.get_tk_widget().place(x=0, y=0, anchor="nw", relwidth=0.8, relheight=1)
canvas.draw()  # needs to be called in order to refresh the plot on the GUI window

can_click = canvas.mpl_connect('button_press_event', click)  # binding the canvas to functions that react to certain behavior
can_enter = canvas.mpl_connect('axes_enter_event', hover_enter)
can_leave = canvas.mpl_connect('axes_leave_event', hover_leave)

# CREATING OF TOOLBAR AND THE CONTROL PANEL WITH ITS CORRESPONDING BUTTONS AND ENTRIES AND PLACING THEM ON THE MAIN WINDOW
panel = tk.LabelFrame(root, bg='white')
panel.place(relx=0.75, rely=0.1, anchor="nw", relwidth=0.23, height=150)
filter_type_cbb = ttk.Combobox(panel, values=['Off', 'Lowpass', 'Highpass', 'Bandpass', 'Bandstop'], state='readonly')
filter_type_cbb.current(0)
filter_type_cbb.config(width=9)
filter_type_cbb.bind('<<ComboboxSelected>>', lambda event: start_filtering(event))
filter_type_cbb.place(relx=0.05, y=20, anchor='w')

label = ttk.Label(panel, text='No filter applied', background='white')
label.place(relx=0.05, y=45, anchor="w", width=135, height=20)

left_cutoff_entry = ttk.Entry(panel, width=6, justify='center')
left_cutoff_entry.bind("<Return>", lambda event: start_filtering(event))
left_cutoff_entry.place(relx=0.05, y=70, anchor="w", width=45, height=20)
left_cutoff_entry.configure(state='disabled')

right_cutoff_entry = ttk.Entry(panel, width=6, justify='center')
right_cutoff_entry.bind("<Return>", lambda event: start_filtering(event))
right_cutoff_entry.place(x=65, y=70, anchor="w", width=45, height=20)
right_cutoff_entry.configure(state='disabled')

filter_order = ttk.Entry(panel, width=6, justify='center')
filter_order.bind("<Return>", lambda event: start_filtering(event))
filter_order.place(relx=0.05, y=120, anchor="w", width=45, height=20)
filter_order.configure(state='disabled')

toolbar = Navigator(canvas, root, filter_type_cbb, [left_cutoff_entry, right_cutoff_entry, filter_order], [can_click, 'button_press_event', click],
                         [can_enter, 'axes_enter_event', hover_enter],
                         [can_leave, 'axes_leave_event', hover_leave])
toolbar.place(relx=0.1, rely=0, anchor="nw")
toolbar.config(background='white')
toolbar._message_label.config(background='white')

root.mainloop()  # call the main window to run
