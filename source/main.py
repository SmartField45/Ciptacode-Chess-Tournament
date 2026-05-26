import tkinter as tk
from tkinter import ttk, messagebox
import database as db
import swiss


class ChessTournamentApp:
    def __init__(self, root: tk.TK):
        self.root = root
        self.root.title("CiptaCode - Chess Tournament Manager")

        self.root.geometry("960x680")
        self.root.minsize(800, 580)

        self.current_tournament_id = None
        self.all_players_cache = []

        db.init_db()
        self._apply_styles()
        self._build_ui()

# ======
# STYLES
# ======
    def _apply_styles(self):
        style = ttk.Style()

        style.theme_use('clam')

        style.configure('TNotebook', background='#1e1e2e')
        style.configure('TNotebook.Tab', background='#2e2e3e',
                        foreground='#cccccc', padding=[14, 6], font=('Helvetica', 10))
        style.map("TNotebook.Tab", background=[
                  ("selected", "#4a4a8a")], foreground=[("selected", "#ffffff")])
        style.configure('Treeview', background='#2b2b3b',
                        foreground='e0e0e0', fieldbackground='#2b2b3b', rowheight=24)
        style.configure('Treeview.Heading', background='#3a3a6a',
                        foreground='#e0c97f', font=('Helvetica', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#5555aa')])

# =================
# HEADER + NOTEBOOK
# =================
    def _build_ui(self):
        hdr = tk.Frame(self.root, bg='#12122a', pady=12)
        hdr.pack(fill='x')
        tk.Label(hdr, text='Chess Tournament Manager', font=(
            'Helvetica', 20, "bold"), fg='#e0c97f', bg='#12122a').pack()

        tk.Label(hdr, text='Swiss System Edition', font=(
            'Helvetica', 9, 'italic'), fg='#888888', bg='#12122a').pack()
        self.status_bar = tk.Label(self.root, text='No Turnament Loaded | Activate The Tournament Tab to Start',
                                   bg='#2e2e4e', fg='#aaaaff', anchor='w', padx=10, pady=4, font=('Helvetica', 9, 'italic'))

        self.status_bar.pack(fill='x')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=8, pady=6)

        self._build_players_tab()
        self._build_tournament_tab()
        self._build_pairings_tab()
        self._build_standings_tab()

# ===============
# TAB 1 - PLAYERS
# ===============
    def _build_players_tab(self):
        frame = ttk.Frame(self.notebook)

        self.notebook.add(frame, text='Players')

        tb = tk.Frame(frame, bg='#252535', pady=6)
        tb.pack(fill='x', padx=4, pady=(4, 0))

        _btn(tb, "Add Player", self._add_player,
             '#2e7d32').pack(side='left', padx=4)
        _btn(tb, "Edit Player", self._edit_player,
             '#1565c0').pack(side='left', padx=4)
        _btn(tb, "Delete Player", self._delete_player,
             '#b71c1c').pack(side='left', padx=4)
        _btn(tb, "Refresh List", self._refresh_players,
             '#e65100').pack(side='left', padx=4)

        tk.Label(tb, text='Search:', bg='#252535',
                 fg='white').pack(side='right', padx=6)

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *_: self._refresh_players())

        tk.Entry(tb, textvariable=self.search_var,
                 width=22).pack(side='right', padx=4)

        cols = ('ID', 'Name', 'Rating', 'Club')
        self.players_tree, _ = _treeview(
            frame, cols, widths=[50, 220, 100, 200])

        self._refresh_players()

    def _refresh_players(self):
        _clear(self.players_tree)

        q = self.search_var.get().lower()
        for p in db.get_all_players():
            if q in p['name'].lower() or q in p['club'].lower():
                self.players_tree.insert('', 'end', values=(
                    p['id'], p['name'], p['rating'], p['club']))

    def _add_player(self):
        d = PlayerDialog(self.root)

        if d.result:
            db.add_player(**d.result)
            self._refresh_players()
            self._refresh_enroll_list()

    def _edit_player(self):
        row = _selected_row(self.players_tree)

        if row is None:
            return _warn('Please select a playe to edit')

        d = PlayerDialog(self.root, initial={
                         'name': row[1], 'rating': row[2], 'club': row[3]})
        if d.result:
            db.update_player(row[0], **d.result)
            self._refresh_players()

    def _delete_player(self):
        row = _selected_row(self.players_tree)

        if row is None:
            return _warn('Select a player first to delete')
        if messagebox.askyesno('Confirm', f"Are you sure you want to delete player'{row[1]}'? This action cannot be undone."):
            db.delete_player(row[0])
            self._refresh_players()
            self._refresh_enroll_list()

# ==================
# TAB 2 - TOURNAMENT
# ==================

    def _build_tournament_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Tournament Manager')

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        # LEFT SIDE - TOURNAMENT LIST
        left = tk.LabelFrame(frame, text='Create New Tournament',
                             bg='#1e1e2e', fg='#e0c97f', padx=12, pady=10)
        left.grid(row=0, column=0, sticky='ns', padx=(8, 4), pady=8)

        labels = ['Tournament Name:', 'Date (YYYY-MM-DD):', 'Round:']
        defaults = ['My Chess Tournament', '2000-01-01', '1']

        self.tournament_name = _labeled_entry(
            left, labels[0], 0, default=defaults[0])
        self.tournament_date = _labeled_entry(
            left, labels[1], 1, default=defaults[1])
        self.tournament_rounds_var = tk.StringVar(value='7')

        tk.Label(left, text=labels[2], bg='#1e1e2e', fg='#cccccc').grid(
            row=2, column=0, sticky='w', pady=5)

        sp = tk.Spinbox(left, from_=1, to=15, width=22,
                        textvariable=self.tournament_rounds_var)
        sp.grid(row=2, column=1, pady=5)

        # RECCOMMENDED ROUNDS INFO
        self.recommended_label = tk.Label(
            left, text='', bg='#1e1e2e', fg='#aaaaff', font=('Helvetica', 8, 'italic'))
        self.recommended_label.grid(row=3, column=0, columnspan=2)

        _btn(left, 'Create Tournament', self._create_tournament, '#2e7d32',
             width=22).grid(row=4, column=0, columnspan=2, pady=10)

        # MID - TOURNAMENT LIST
        mid = tk.LabelFrame(frame, text='Existing Tournaments',
                            bg='#1e1e2e', fg='#e0c97f', padx=8, pady=8)
        mid.grid(row=0, column=1, sticky='nsew', padx=4, pady=8)
        mid.rowconfigure(0, weight=1)
        mid.columnconfigure(0, weight=1)

        cols = ('ID', 'Name', 'Date', 'Rounds', 'Status')
        self.tournament_tree, _ = _treeview(
            mid, cols, widths=[40, 160, 100, 60, 80], height=14)

        _btn(mid, 'Activate Tournament', self._activate_tournament,
             '#7b1fa2', width=25).pack(pady=5)

        # RIGHT SIDE - ENROLL PLAYERS
        right = tk.LabelFrame(frame, text='Enroll Players',
                              bg='#1e1e2e', fg='#e0c97f', padx=8, pady=8)
        right.grid(row=0, column=2, sticky='ns', padx=(4, 8), pady=8)

        tk.Label(right, text='Select Players to Enroll in the Active Tournament (Ctrl + Click to Select Multiple)',
                 bg='#1e1e2e', fg='#cccccc').pack()

        self.enroll_listbox = tk.Listbox(
            right, selectmode='multiple', height=14, width=26, bg='#2b2b3b', fg='#e0e0e0', selectbackground='#5555aa')
        self.enroll_listbox.pack(pady=4)
        self.enroll_listbox.bind('<<ListboxSelect>>', self._on_enroll_select)

        _btn(right, 'Enroll Selected Players',
             self._enroll_players, '#2e7d32').pack(fill='x')
        _btn(right, "Refresh Player List", self._refresh_enroll_list,
             '#e65100').pack(fill='x', pady=3)

        self.enrolled_count_label = tk.Label(
            right, text='Enrolled Players: 0', bg='#1e1e2e', fg='#aaffaa', font=('Helvetica', 9, 'bold'))
        self.enrolled_count_label.pack(pady=3)

        self._refresh_tournaments()
        self._refresh_enroll_list()

    def _create_tournament(self):
        name = self.tournament_name.get().strip()
        date = self.tournament_date.get().strip()

        if not name:
            return _warn('Tournament name cannot be empty')
        try:
            round = int(self.tournament_rounds_var.get())
        except ValueError:
            return _warn('Round must be a valid number')

        db.create_tournament(name, date, round)

        messagebox.showinfo(
            'Success', f'Tournament "{name}" created successfully!')

        self.tournament_name.delete(0, 'end')
        self.tournament_date.delete(0, 'end')

        self._refresh_tournaments()

    def _refresh_tournaments(self):
        _clear(self.tournament_tree)

        for t in db.get_all_tournament():
            self.tournament_tree.insert('', 'end', values=(
                t['id'], t['name'], t['date'], t['num_rounds'], t['status']
            ))

    def _activate_tournament(self):
        row = _selected_row(self.tournament_tree)

        if row is None:
            return _warn('Please select a tournament to activate')

        self.current_tournament_id = row[0]
        self.status_bar.config(
            text=f'Activated Tournament: {row[1]} | Rounds: {row[3]} | Status: {row[4]}', fg='#aaffaa')

        self._refresh_enrolled_count()
        self._refresh_pairings()
        self._refresh_standings()

        enrolled = db.get_enrolled_players(self.current_tournament_id)

        recommended_rounds = swiss.recommended_rounds(len(enrolled))

        self.recommended_label.config(
            text=f'Recommended Rounds for {len(enrolled)} players: {recommended_rounds} rounds')
        messagebox.showinfo(
            'Active Tournament', f'Tournament "{row[1]}" is now active! You can start enrolling players and managing pairings.')

    def _on_enroll_select(self, event):
        n = len(self.enroll_listbox.curselection())

        if n > 0:
            recommended = swiss.recommended_rounds(n)

            self.recommended_label.config(
                text=f'{n} players selected. Recommended Rounds: {recommended}')

    def _refresh_enroll_list(self):
        self.enroll_listbox.delete(0, 'end')
        self.all_players_cache = db.get_all_players()

        for p in self.all_players_cache:
            self.enroll_listbox.insert(
                'end', f"{p['name']} (Rating: {p['rating']})")

    def _enroll_players(self):
        if not self.current_tournament_id:
            return _warn('Activate a tournament first before enrolling players')

        selected_indices = self.enroll_listbox.curselection()

        if not selected_indices:
            return _warn('Select at least 1 player to enroll')

        ok = sum(db.enroll_player(self.current_tournament_id,
                 self.all_players_cache[i]['id']) for i in selected_indices)

        messagebox.showinfo(
            'Enrollment Complete', f'{ok} players enrolled successfully! \n({len(selected_indices)-ok} were already enrolled)')

        self._refresh_enrolled_count()

    def _refresh_enrolled_count(self):
        if self.current_tournament_id:
            n = len(db.get_enrolled_players(self.current_tournament_id))

            self.enrolled_count_label.config(text=f'Enrolled Players: {n}')

# ============================
# TAB 3 - PAIRINGS AND RESULTS
# ============================
    def _build_pairings_tab(self):
        frame = ttk.Frame(self.notebook)

        self.notebook.add(frame, text='Pairings & Results')

        # Toolbar
        tb = tk.Frame(frame, bg='#252535', pady=7)
        tb.pack(fill='x', padx=4)

        self.round_label = tk.Label(
            tb, text='Round: N/A', font=('Helvetica', 12, 'bold'), bg='#252535', fg='#e0c97f')
        self.round_label.pack(side='left', padx=12)

        _btn(tb, 'Generate Pairings', self._generate_pairings,
             '#6a1b9a').pack(side='left', padx=5)
        _btn(tb, 'Refresh', self._refresh_pairings,
             '#e65100').pack(side='left', padx=5)

        # Pairing Treeview
        cols = ('Number', 'White Player', 'Black Player', 'Result')

        self.pairings_tree, _ = _treeview(
            frame, cols, widths=[40, 220, 220, 130], height=22)
        self.pairings_tree.bind('<Double-1>', self._input_result)

        tk.Label(frame, text='Double-click a pairing to input result',
                 fg='#888888', font=('Helvetica', 9)).pack(pady=2)

    def _refresh_pairings(self):
        _clear(self.pairings_tree)

        if not self.current_tournament_id:
            return

        t = db.get_tournament(self.current_tournament_id)

        if not t:
            return

        self.round_label.config(
            text=f"Round: {t['current_round']} / {t['num_rounds']} ({t['status']})")

        for i, p in enumerate(db.get_pairings(self.current_tournament_id, t['current_round']), 1):
            white = p['white_name'] or 'BYE'
            black = p['black_name'] or 'BYE'

            result = p['result'] or 'Not Recorded'

            self.pairings_tree.insert('', 'end', values=(
                i, white, black, result), iid=str(p['id']))

    def _generate_pairings(self):
        if not self.current_tournament_id:
            return _warn('Activate a tournament first to generate pairings')

        t = db.get_tournament(self.current_tournament_id)

        if t['current_round'] >= t['num_rounds']:
            messagebox.showinfo('Done', 'All rounds have been completed')
            return

        if t['current_round'] > 0:
            if not db.is_round_complete(self.current_tournament_id, t['current_round']):
                return _warn('Complete all pairings result before generating next round pairings')

        players = db.get_enrolled_players(self.current_tournament_id)

        if len(players) < 2:
            return _warn('At least 2 players are required to generate pairings')

        standings = db.get_tournament_standings(self.current_tournament_id)
        previous_pairings = db.get_previous_pairings_set(
            self.current_tournament_id)
        byes = db.get_player_with_bye(self.current_tournament_id)

        pairings = swiss.generate_pairings(standings, previous_pairings, byes)

        next_round = t['current_round'] + 1

        db.save_pairing(self.current_tournament_id, next_round, pairings)
        db.update_round(self.current_tournament_id, next_round)

        self._refresh_pairings()
        self._update_status_bar()

    def _input_result(self, event):
        selected = self.pairings_tree.selection()

        if not selected:
            return

        pairing_id = int(selected[0])
        vals = self.pairings_tree.item(selected[0])['values']
        white_name, black_name = vals[1], vals[2]

        if black_name == 'BYE':
            messagebox.showinfo(
                'BYE', f'{white_name} has a BYE this round and is awarded 1 point')
            return

        d = ResultDialog(self.root, white=white_name, black=black_name)

        if d.result:
            db.update_pairing_result(pairing_id, d.result)
            self._refresh_pairings()
            self._refresh_standings()

    def _update_status_bar(self):
        if self.current_tournament_id:
            t = db.get_tournament(self.current_tournament_id)

            if t:
                self.status_bar.config(
                    text=f"Activated Tournament: {t['name']} | Rounds: {t['current_round']} / {t['num_rounds']} | Status: {t['status']}")

# =================
# TAB 4 - STANDINGS
# =================
    def _build_standings_tab(self):
        frame = ttk.Frame(self.notebook)

        self.notebook.add(frame, text='Standings')

        tb = tk.Frame(frame, bg='#252535', pady=6)
        tb.pack(fill='x', padx=4)

        _btn(tb, 'Refresh Standings', self._refresh_standings,
             '#1565c0').pack(side='left', padx=8)

        cols = ('Rank', 'Player Name', 'Points', 'Buchholz', 'Rating')
        self.standings_tree, _ = _treeview(
            frame, cols, widths=[55, 220, 70, 90, 80], height=24)

    def _refresh_standings(self):
        _clear(self.standings_tree)

        if not self.current_tournament_id:
            return

        standings = db.get_tournament_standings(self.current_tournament_id)
        standings.sort(
            key=lambda x: (-x['points'], -x['buchholz'], -x['rating']))

        for rank, s in enumerate(standings, 1):
            self.standings_tree.insert('', 'end', values=(
                rank,
                s['name'],
                s['points'],
                f"{s['buchholz']:.1f}",
                s['rating']
            ))

# ===============
# DIALOGS CLASSES
# ===============


class PlayerDialog:
    def __init__(self, parent: tk.Widget, initial: dict = None):
        self.result = None

        win = _dialog_window(parent, 'Player Information', '320x210')

        fields = [
            ('Name:', 'name', ''),
            ('Rating:', 'rating', '400'),
            ('Club:', 'club', '')
        ]

        entries = {}

        for i, (label, key, default) in enumerate(fields):
            tk.Label(win, text=label, bg='#1e1e2e', fg='#cccccc').grid(
                row=i, column=0, padx=12, pady=7, sticky='w')

            e = tk.Entry(win, width=25, bg='#2b2b3b',
                         fg='#e0e0e0', insertbackground='white')
            e.grid(row=i, column=1, padx=10, pady=7)
            e.insert(0, initial.get(key, default) if initial else default)
            entries[key] = e

        bf = tk.Frame(win, bg='#1e1e2e')
        bf.grid(row=3, column=0, columnspan=2, pady=10)

        _btn(bf, 'Save', lambda: self._save(win, entries),
             '#2e7d32').pack(side='left', padx=6)
        _btn(bf, 'Cancel', lambda: win.destroy(),
             '#b71c1c').pack(side='left', padx=6)

        win.wait_window()

    def _save(self, win, entries):
        name = entries['name'].get().strip()

        if not name:
            return _warn('Player name cannot be empty')
        try:
            rating = int(entries['rating'].get())
        except ValueError:
            return _warn('Rating must be a valid number')

        self.result = {
            'name': name,
            'rating': rating,
            'club': entries['club'].get().strip()
        }

        win.destroy()


class ResultDialog:
    def __init__(self, parent: tk.Widget, white: str, black: str):
        self.result = None

        win = _dialog_window(parent, 'Input Match Result', '300x200')

        tk.Label(win, text=f'White: {white}', font=(
            'Helvetica', 11, 'bold'), bg='#1e1e2e', fg='#ffffff').pack(pady=(10, 2))
        tk.Label(win, text='vs', bg='#1e1e2e', fg='#888888').pack()
        tk.Label(win, text=f'Black: {black}', font=(
            'Helvetica', 11, 'bold'), bg='#1e1e2e', fg='#ffffff').pack(pady=(2, 10))

        self.result_var = tk.StringVar(value='1-0')

        options = [
            ('White wins (1-0)', '1-0'),
            ('Black wins (0-1)', '0-1'),
            ('Draw (½-½)', '1/2-1/2')
        ]

        rf = tk.Frame(win, bg='#1e1e2e')
        rf.pack()

        for text, val in options:
            tk.Radiobutton(rf, text=text, variable=self.result_var, value=val,
                           bg='#1e1e2e', fg='#cccccc', selectcolor='#2b2b3b', activebackground='#1e1e2e').pack(anchor='w')

        bf = tk.Frame(win, bg='#1e1e2e')
        bf.pack(pady=8)

        _btn(bf, 'Save Result', lambda: self._save(
            win), '#2e7d32').pack(side='left', padx=6)
        _btn(bf, 'Cancel', lambda: win.destroy(),
             '#b71c1c').pack(side='left', padx=6)

    def _save(self, win):
        self.result = self.result_var.get()
        win.destroy()

# ================
# HELPER FUNCTIONS
# ================


def _btn(parent, text, command, bg, width=None) -> tk.Button:
    kw = dict(text=text, command=command, bg=bg, fg='white', activebackground=bg,
              relief='flat', padx=8, pady=4, font=('Helvetica', 9, 'bold'), cursor='hand2')

    if width:
        kw['width'] = width
    return tk.Button(parent, **kw)


def _treeview(parent, columns, widths=None, height=18):
    wrapper = tk.Frame(parent)

    wrapper.pack(fill='both', expand=True, padx=5, pady=5)

    tree = ttk.Treeview(wrapper, columns=columns,
                        show='headings', height=height)

    for i, col in enumerate(columns):
        tree.heading(col, text=col)

        if widths and i < len(widths):
            tree.column(col, width=widths[i])

    sb = ttk.Scrollbar(wrapper, orient='vertical', command=tree.yview)

    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)

    sb.pack(side='right', fill='y')

    return tree, sb


def _labeled_entry(parent, label, row, default='') -> tk.Entry:
    tk.Label(parent, text=label, bg='#1e1e2e', fg='#cccccc').grid(
        row=row, column=0, sticky='w', pady=5)

    e = tk.Entry(parent, width=24, bg='#2b2b3b',
                 fg='#e0e0e0', insertbackground='white')

    e.grid(row=row, column=1, pady=5)
    e.insert(0, default)

    return e


def _dialog_window(parent, title, size):
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry(size)

    win.resizable(False, False)
    win.configure(bg='#1e1e2e')
    win.grab_set()

    return win


def _clear(tree: ttk.Treeview):
    tree.delete(*tree.get_children())


def _selected_row(tree: ttk.Treeview):
    selected = tree.selection()

    return tree.item(selected[0])['values'] if selected else None


def _warn(message):
    messagebox.showwarning('Warning', message)


# ===========
# ENTRY POINT
# ===========
if __name__ == '__main__':
    root = tk.Tk()
    app = ChessTournamentApp(root)
    root.mainloop()
