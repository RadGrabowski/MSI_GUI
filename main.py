from math import ceil, log2
from tkinter.filedialog import asksaveasfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import savemat
from scipy import signal
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
from scipy.integrate import cumtrapz
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from navigator import Navigator
from copy import deepcopy
from opening_window import OpenFile


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
            if x + (right - left) / 2 > fs / 2:
                right = fs / 2 - 0.01

            left_cutoff_entry.delete(0, tk.END)  # removing old values from the entries and inserting the new ones
            right_cutoff_entry.delete(0, tk.END)
            left_cutoff_entry.insert(tk.END, left)
            right_cutoff_entry.insert(tk.END, right)
        start_filtering('Placeholder')


def hover_enter(event):
    """Gets called when hovered inside a subplot. Changes the cursor to a cross."""
    canvas.get_tk_widget().configure(cursor='tcross')


def hover_leave(event):
    """Gets called when hovered outside a subplot. Changes the cursor to a normal arrow."""
    canvas.get_tk_widget().configure(cursor='arrow')


def start_filtering(event):
    """Gets called when the filter type, frequency or order changes. Recalculates then the output based on the newly
    set parameters and plots a new graph on the GUI. """
    global filtered, prev_diff, fs, dt, t
    ax[0, 0].clear()  # clears the subplots before drawing the new ones
    ax[1, 0].clear()
    # diff_check.set('off')
    # differentiate('_')

    try:
        fs = float(sampling_frequency.get())
        dt = 1 / fs
        t = np.linspace(0, sig.size * dt, sig.size, False)

        if filter_type_cbb.get() == 'Off':  # if there is no filter applied, there is no possibility to insert a value in
            # the entries determining filter's parameters
            ax[0, 0].plot(t, sig, color='#1f77b4', lw=1)
            ax[1, 0].magnitude_spectrum(sig, Fs=fs, color='#1f77b4', lw=1, pad_to=2**ceil(log2(abs(sig.size*5))))
            left_cutoff_entry.configure(state='disabled')
            right_cutoff_entry.configure(state='disabled')
            filter_order.configure(state='disabled')
            label.configure(text='No filter applied')
        else:
                left_cutoff_entry.configure(state='normal')
                filter_order.configure(state='normal')
                if left_cutoff_entry.get() == '':
                    left_cutoff_entry.insert(tk.END, round(fs / 5, 2))  # default filtering position if no value was set
                if filter_order.get() == '':
                    filter_order.insert(tk.END, 10)  # default filter order if no value was set
                left = round(float(left_cutoff_entry.get()), 2)

                if filter_type_cbb.get() == 'Lowpass' or filter_type_cbb.get() == 'Highpass':
                    # design of the lowpass or highpass filter, configuration of the red shaded part
                    right_cutoff_entry.configure(state='disabled')
                    label.configure(text='Critical frequency (Hz):')
                    sos = signal.butter(int(filter_order.get()), left, filter_type_cbb.get().lower(), fs=fs,
                                        output='sos')
                    if filter_type_cbb.get() == 'Highpass':
                        ax[1, 0].axvspan(left, fs / 2, alpha=0.3, color='red')
                    else:
                        ax[1, 0].axvspan(0, left, alpha=0.3, color='red')

                if filter_type_cbb.get() == 'Bandpass' or filter_type_cbb.get() == 'Bandstop':
                    # design of the bandpass or bandstop filter, configuration of the red shaded part
                    label.configure(text='Critical frequencies (Hz):')
                    right_cutoff_entry.configure(state='normal')
                    if right_cutoff_entry.get() == '':
                        right_cutoff_entry.insert(tk.END, round(fs / 3, 2))
                    right = round(float(right_cutoff_entry.get()), 2)
                    if right < left:
                        right = left + fs / 10
                        if right > fs / 2:
                            right -= fs / 10
                            left = right - fs / 10

                    sos = signal.butter(int(filter_order.get()), (left, right), filter_type_cbb.get().lower(),
                                        fs=fs, output='sos')
                    ax[1, 0].axvline(right, color='red')

                    if filter_type_cbb.get() == 'Bandstop':
                        ax[1, 0].axvspan(0, left, alpha=0.3, color='red')
                        ax[1, 0].axvspan(right, fs / 2, alpha=0.3, color='red')
                    else:
                        ax[1, 0].axvspan(left, right, alpha=0.3, color='red')

                filtered = signal.sosfilt(sos, sig)  # the original signal is filtered with the designed filter

                ax[0, 0].plot(t, filtered, color='#1f77b4', lw=1)  # time domain plot
                ax[1, 0].magnitude_spectrum(sig, Fs=fs, color='#1f77b4', lw=1, pad_to=2**ceil(log2(abs(sig.size*5))))  # frequency domain, original signal
                ax[1, 0].magnitude_spectrum(filtered, Fs=fs, color='y', lw=1, pad_to=2**ceil(log2(abs(sig.size*5))))  # frequency domain, filtered signal
                ax[1, 0].axvline(left, color='red')  # red line on the cutoff frequency
                ax[1, 0].legend(('Original', 'Filtered'), prop={'size': 8}, loc=1)

    except ValueError as ex:  # when trying to insert incorrect data into the entries, a window informing about
        # it is displayed
        messagebox.showerror(ex, str(ex).capitalize())
        return

    ax[0, 0].set_ylim(auto=True)
    ax[0, 0].ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax[1, 0].set_xlim(0, fs / 2)
    set_titles()
    if event:
        differentiate()
        detrend()
    if toolbar._active is None:
        toolbar.forward()
    canvas.draw()


def differentiate(callback=None):
    """Called when the radio button value changes in order to differentiate or integrate data."""
    global filtered, prev_diff
    ax[0, 1].clear()
    i = cumtrapz(filtered)
    d = np.diff(filtered)
    differentiated = filtered

    if diff_check.get() == 'off':
        if prev_diff == 'off' and callback is None:
            return
        ax[0, 1].plot(t[:len(filtered)], filtered, color='#1f77b4', lw=1)
        prev_diff = 'off'
        if callback is not None and callback != 'save':  # prevents the plot to blink (the cause is the canvas.draw() command of this function)
            return
    elif diff_check.get() == 'differentiate':
        if prev_diff == 'differentiate' and callback != 'save':
            return
        ax[0, 1].plot(t[:len(d)], d, color='#1f77b4', lw=1)
        prev_diff = 'differentiate'
        differentiated = d
    elif diff_check.get() == 'integrate':
        if prev_diff == 'integrate' and callback != 'save':
            return
        ax[0, 1].plot(t[:len(i)], i, color='#1f77b4', lw=1)
        prev_diff = 'integrate'
        differentiated = i

    set_titles()
    if callback != 'save':
        detrend()
    canvas.draw()
    return differentiated


def detrend():
    """Called when the value of the checkboxes changes in order to detrend the data and draw a detrending line."""
    data = differentiate('save')
    ax[1, 1].clear()
    if trend.get():
        data = signal.detrend(data)
    ax[1, 1].plot(t[:len(data)], data, color='#1f77b4', lw=1)
    set_titles()
    if trend_line.get():
        z = np.polyfit(t[:len(data)], data, 1)
        p = np.poly1d(z)
        ax[1, 1].plot(t, p(t), "k--", dashes=(5, 10), lw=1)
        if -10**-3 < z[0] < 10**-3:
            if -10 ** -3 < z[1] < 10 ** -3:
                ax[1, 1].set_title(f"y = 0", fontsize=10)
            else:
                ax[1, 1].set_title(f"y = {z[1]:.2g}", fontsize=10)
        elif -10**-3 < z[1] < 10**-3:
            ax[1, 1].set_title(f"y = {z[0]:.2g}", fontsize=10)
        elif z[1] < 0:
            ax[1, 1].set_title(f"y = {z[0]:.2g}x {z[1]:.2g}", fontsize=10)  # the line equation
        else:
            ax[1, 1].set_title(f"y = {z[0]:.2g}x +{z[1]:.2g}", fontsize=10)
    start_filtering(None)
    canvas.draw()


def set_titles():
    """Sets the title and axes description on each of the subplots."""
    ax[0, 0].set_title('Time-domain', fontsize=10)
    ax[0, 0].set_xlabel('Time [s]')
    ax[0, 0].set_ylabel('Amplitude')
    ax[0, 0].yaxis.set_major_locator(MaxNLocator(5))
    ax[0, 0].ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax[1, 0].set_title('Frequency-domain', fontsize=10)
    ax[1, 0].yaxis.set_major_locator(MaxNLocator(5))
    ax[1, 0].ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax[0, 1].set_title('Differentiated / integrated', fontsize=10)
    ax[0, 1].set_xlabel('Time [s]')
    ax[0, 1].set_ylabel('Amplitude')
    ax[0, 1].yaxis.set_major_locator(MaxNLocator(5))
    ax[0, 1].ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax[1, 1].set_xlabel('Time [s]')
    ax[1, 1].set_ylabel('Amplitude')
    ax[1, 1].yaxis.set_major_locator(MaxNLocator(5))
    ax[1, 1].ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))


def save():
    """Saves the preprocessed data in a new user-defined .mat file."""
    files = [('MATLAB Files', '*.mat')]
    file = asksaveasfile(filetypes=files, defaultextension=files)
    data = differentiate('save')
    try:
        savemat(file.name, {'signal': data})
    except AttributeError:  # occurs when user closes the save window without saving
        pass


def center(window, width, height):
    """Puts the given window in the center of the screen."""
    frm_width = window.winfo_rootx() - window.winfo_x()
    win_width = width + 2 * frm_width
    titlebar_height = window.winfo_rooty() - window.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = (window.winfo_screenwidth() // 2) - (win_width // 2)
    y = (window.winfo_screenheight() // 2) - (win_height // 2) - 15
    window.geometry(f'{width}x{height}+{x}+{y}')
    window.deiconify()


# BEGIN OF GUI, PLACEMENT OF ELEMENTS, BINDING TO EVENTS, ETC
if __name__ == '__main__':
    opening_window = tk.Tk()
    center(opening_window, 250, 110)
    start_window = OpenFile(opening_window)
    opening_window.mainloop()

    sig = start_window.get_params
    if sig.size == 0:
        quit()
    filtered = sig
    fs = 5000
    dt = 1/fs
    t = np.linspace(0, sig.size*dt, sig.size, False)

    root = tk.Tk()  # main window
    center(root, 1070, 650)
    root.configure(background='white')  # main window background color
    root.title('GUI for signal pre-processing')  # main window title
    figure, ax = plt.subplots(2, 2)
    ax[0, 0].plot(t, sig, color='#1f77b4', lw=1)  # upper subplot, time domain
    ax[1, 0].magnitude_spectrum(sig, Fs=fs, color='#1f77b4', lw=1, pad_to=2**ceil(log2(abs(sig.size*5))))  # bottom subplot, frequency domain
    ax[1, 0].set_xlim(0, fs / 2)
    plt.subplots_adjust(hspace=0.33, wspace=0.28)

    for x in ax:
        for y in x:
            y.tick_params(axis='x', labelsize=8)
            y.tick_params(axis='y', labelsize=8)

    canvas = FigureCanvasTkAgg(figure, root)  # making the plots a Tkinter object and binding it to the main window
    canvas.get_tk_widget().place(x=0, y=0, anchor="nw", relwidth=0.8, relheight=1)

    can_click = canvas.mpl_connect('button_press_event',
                                   click)  # binding the canvas to functions that react to certain behavior
    can_enter = canvas.mpl_connect('axes_enter_event', hover_enter)
    can_leave = canvas.mpl_connect('axes_leave_event', hover_leave)

    # CREATING OF TOOLBAR AND THE CONTROL PANEL WITH ITS CORRESPONDING BUTTONS AND ENTRIES AND PLACING THEM ON THE MAIN
    # WINDOW
    s = ttk.Style()
    s.configure('White.TCheckbutton', background='white')
    s.configure('White.TRadiobutton', background='white')
    panel = tk.LabelFrame(root, bg='white')
    panel.place(relx=0.75, rely=0.1, anchor="nw", relwidth=0.23, height=230)
    filter_type_cbb = ttk.Combobox(panel, values=['Off', 'Lowpass', 'Highpass', 'Bandpass', 'Bandstop'], state='readonly')
    filter_type_cbb.current(0)
    filter_type_cbb.config(width=9)
    filter_type_cbb.bind('<<ComboboxSelected>>', lambda event: start_filtering(event))
    filter_type_cbb.place(relx=0.05, y=20, anchor='w')

    save_button = ttk.Button(panel, text='Save', command=save, width=5)
    save_button.place(relx=0.95, y=20, anchor='e')

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

    ttk.Label(panel, text='Order', background='white').place(relx=0.05, y=95, anchor="w", width=135, height=20)
    ttk.Label(panel, text='Fs', background='white').place(x=65, y=95, anchor="w", width=20, height=20)

    filter_order = ttk.Entry(panel, width=6, justify='center')
    filter_order.bind("<Return>", lambda event: start_filtering(event))
    filter_order.place(relx=0.05, y=120, anchor="w", width=45, height=20)
    filter_order.configure(state='disabled')

    sampling_frequency = ttk.Entry(panel, width=6, justify='center')
    sampling_frequency.bind("<Return>", lambda event: start_filtering(event))
    sampling_frequency.place(x=65, y=120, anchor="w", width=45, height=20)
    sampling_frequency.insert(0, fs)

    diff_check = tk.StringVar(value='off')
    prev_diff = 'off'
    trend = tk.BooleanVar(value=False)
    trend_line = tk.BooleanVar(value=False)

    ttk.Radiobutton(panel, text='Off', var=diff_check, value='off', style='White.TRadiobutton',
                    command=lambda: differentiate()).place(relx=0.05, y=140)
    ttk.Radiobutton(panel, text='Differentiate', var=diff_check, value='differentiate', style='White.TRadiobutton',
                    command=lambda: differentiate()).place(relx=0.05, y=160)
    ttk.Radiobutton(panel, text='Integrate', var=diff_check, value='integrate', style='White.TRadiobutton',
                    command=lambda: differentiate()).place(relx=0.05, y=180)
    ttk.Checkbutton(panel, text='Detrend', style='White.TCheckbutton', var=trend,
                    command=lambda: detrend()).place(relx=0.05, y=200)
    ttk.Checkbutton(panel, text='Detrending line', style='White.TCheckbutton', var=trend_line,
                    command=lambda: detrend()).place(relx=0.4, y=200)

    toolbar = Navigator(canvas, root, filter_type_cbb,
                        [left_cutoff_entry, right_cutoff_entry, filter_order, sampling_frequency, filter_type_cbb],
                        [can_click, 'button_press_event', click],
                        [can_enter, 'axes_enter_event', hover_enter],
                        [can_leave, 'axes_leave_event', hover_leave])
    toolbar.place(relx=0.1, rely=0, anchor="nw")
    toolbar.config(background='white')
    toolbar._message_label.config(background='white')

    differentiate('save')
    detrend()
    root.mainloop()  # call the main window to run
