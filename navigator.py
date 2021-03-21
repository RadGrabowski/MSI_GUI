from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk


class Navigator(NavigationToolbar2Tk):
    """Extends the navigation toolbar for managing the figure"""

    def __init__(self, canvas, window, filter_type, entries, *events):
        self.events = events
        self.type = filter_type
        self.entries = entries
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
        )
        super().__init__(canvas, window)

    def connections_manage(self):
        """Handles the event functions being connected to the plot. For example, if the pan option is turned on, all
        the event functions get disconnected in order to perform the panning correctly. After turning it off, the event
        functions get reconnected again."""

        if self._active is None:
            for event in self.events:
                self.canvas.mpl_disconnect(event[0])
            for entry in self.entries:
                entry.configure(state='disabled')
        else:
            for event in self.events:
                event[0] = self.canvas.mpl_connect(event[1], event[2])
            for entry in self.entries:
                if self.type.get() != 'Off':
                    entry.configure(state='normal')
            if self.type.get() == 'Lowpass' or self.type.get() == 'Highpass':
                self.entries[1].configure(state='disabled')

    def zoom(self, *args):
        """The event functions get connected/disconnected depending on the zoom function being on or off."""
        self.connections_manage()
        super().zoom(*args)

    def pan(self, *args):
        """The event functions get connected/disconnected depending on the pan function being on or off."""
        self.connections_manage()
        super().pan(*args)

    def mouse_move(self, event):
        """Overrides the original method to customize the cursor data being displayed while moving the mouse."""

        self._set_cursor(event)
        if event.inaxes and event.inaxes.get_navigate():
            try:
                s = event.inaxes.format_coord(round(event.xdata, 2), round(event.ydata, 2))
            except (ValueError, OverflowError):
                pass
            else:
                if len(self.mode):
                    self.set_message('%s, %s' % (self.mode, s))
                else:
                    self.set_message(s)
        else:
            self.set_message(self.mode)
