import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import database as db
import swiss
import elimination

# ========================
# MAIN APPLICATION CLASS
# ========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ChessTournamentApp:
    def __init__(self, root_window: ctk.CTk):
        self.root = root_window
        self.root.title("CiptaCode - Chess Tournament Manager")

        self.root.geometry("1000x720")
        self.root.minsize(800, 600)

        try:
            self.root.iconbitmap('source/logo.ico')
        except tk.TclError:
            pass

        self.current_tournament_id = None
        self.all_players_cache = []
        self.recommended_label = None
        self.standings_tree = None
        self.search_var = None
        self.players_tree = None
        self.tournament_name = None
        self.tournament_date = None
        self.tournament_format_var = None
        self.tournament_rounds_var = None
        self.tournament_tree = None
        self.enroll_listbox = None
        self.enrolled_count_label = None
        self.pairings_tree = None
        self.round_label = None

        db.init_db()
        self._apply_styles()
        self._build_ui()

# ======
# STYLES
# ======
    def _apply_styles(self):
        style = ttk.Style()

        style.theme_use('clam')

        style.configure('TNotebook', background='#242424')
        style.configure('TNotebook.Tab', background='#1f538d',
                        foreground='#ffffff', padding=[14, 6], font=('Segoe UI', 10))
        style.map("TNotebook.Tab", background=[
                  ("selected", "#14375e")], foreground=[("selected", "#ffffff")])
        style.configure('Treeview', background='#242424',
                        foreground='#dce4ee', fieldbackground='#242424', rowheight=24)
        style.configure('Treeview.Heading', background='#1f538d',
                        foreground='#ffffff', font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#14375e')])

# =================
# HEADER + NOTEBOOK
# =================
    def _build_ui(self):
        hdr = ctk.CTkFrame(self.root, bg_color='#12122a', corner_radius=0)
        hdr.pack(fill='x')

        ctk.CTkLabel(hdr, text='Chess Tournament Manager',
                     font=ctk.CTkFont(family="Segoe UI",
                                      size=24, weight="bold"),
                     text_color='#e0c97f').pack(pady=(10, 0))
        ctk.CTkLabel(hdr, text='Swiss System Edition',
                     font=ctk.CTkFont(family="Segoe UI",
                                      size=12, slant="italic"),
                     text_color='gray').pack(pady=(0, 10))

        self.status_bar = ctk.CTkLabel(self.root,
                                       text='No Turnament Loaded | Activate The Tournament Tab to Start',
                                       fg_color="#1f538d",
                                       text_color='#ffffff',
                                       anchor='w',
                                       padx=10,
                                       pady=4,
                                       font=ctk.CTkFont(
                                           family='Segoe UI', size=12, slant='italic')
                                       )

        self.status_bar.pack(fill='x', padx=10, pady=(0, 10))

        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.tab_players = self.notebook.add("Players")
        self.tab_tournament = self.notebook.add("Tournament Manager")
        self.tab_pairings = self.notebook.add("Pairings & Results")
        self.tab_standings = self.notebook.add("Standings")

        self._build_players_tab()
        self._build_tournament_tab()
        self._build_pairings_tab()
        self._build_standings_tab()

# ===============
# TAB 1 - PLAYERS
# ===============
    def _build_players_tab(self):
        tb = tk.Frame(self.tab_players, bg='#252535', pady=6)
        tb.pack(fill='x', pady=(0, 10))

        ctk.CTkButton(tb, text="Add Player", command=self._add_player,
                      fg_color='#2e7d32', hover_color='#1b5e20').pack(side='left', padx=4)
        ctk.CTkButton(tb, text="Edit Player", command=self._edit_player).pack(
            side='left', padx=4)
        ctk.CTkButton(tb, text="Delete Player", command=self._delete_player,
                      fg_color='#b71c1c', hover_color='#7f0000').pack(side='left', padx=4)
        ctk.CTkButton(tb, text="Refresh", command=self._refresh_players,
                      fg_color='#e65100', hover_color='#bf360c').pack(side='left', padx=4)

        ctk.CTkLabel(tb, text='Search:', bg_color='#252535',
                     text_color='white').pack(side='right', padx=6)

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *_: self._refresh_players())

        ctk.CTkEntry(tb, textvariable=self.search_var,
                     placeholder_text="Search players...", width=200).pack(side='right', padx=4)

        cols = ('ID', 'Name', 'Rating', 'Club')
        self.players_tree, _ = _treeview(
            self.tab_players, cols, widths=[50, 250, 100, 250])

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
            return _warn('Please select a player to edit')

        d = PlayerDialog(self.root, initial={
                         'name': row[1], 'rating': row[2], 'club': row[3]})
        if d.result:
            db.update_player(row[0], **d.result)
            self._refresh_players()

    def _delete_player(self):
        row = _selected_row(self.players_tree)

        if row is None:
            return _warn('Select a player first to delete')
        if messagebox.askyesno('Confirm', f"Are you sure you want to delete player '{row[1]}'? This action cannot be undone."):
            db.delete_player(row[0])
            self._refresh_players()
            self._refresh_enroll_list()

# ==================
# TAB 2 - TOURNAMENT
# ==================

    def _build_tournament_tab(self):
        self.tab_tournament.columnconfigure(1, weight=1)
        self.tab_tournament.rowconfigure(0, weight=1)

        # LEFT SIDE - TOURNAMENT LIST
        left = ctk.CTkFrame(self.tab_tournament)
        left.grid(row=0, column=0, sticky='ns', padx=5, pady=5)

        ctk.CTkLabel(left, text="Create Tournament",
                     font=ctk.CTkFont(weight="bold")).pack(pady=10)

        self.tournament_name = ctk.CTkEntry(
            left, placeholder_text="Tournament Name", width=200)
        self.tournament_name.pack(pady=5, padx=10)

        self.tournament_date = ctk.CTkEntry(
            left, placeholder_text="YYYY-MM-DD", width=200)
        self.tournament_date.pack(pady=5, padx=10)

        ctk.CTkLabel(left, text="Format:").pack(pady=(10, 0))

        self.tournament_format_var = ctk.StringVar(value='elimination')
        ctk.CTkOptionMenu(left, variable=self.tournament_format_var, values=[
                          'elimination', 'swiss'], width=200).pack(pady=5)

        ctk.CTkLabel(left, text="Number of Rounds:").pack(pady=(10, 0))

        self.tournament_rounds_var = ctk.StringVar(value='7')
        ctk.CTkOptionMenu(left, variable=self.tournament_rounds_var, values=[
                          str(i) for i in range(1, 16)], width=200).pack(pady=5)

        # RECOMMENDED ROUNDS INFO
        self.recommended_label = ctk.CTkLabel(
            left, text='', text_color='gray', font=ctk.CTkFont(size=11))
        self.recommended_label.pack(pady=5)

        ctk.CTkButton(left, text='Create', command=self._create_tournament,
                      fg_color='#2e7d32', hover_color='#1b5e20', width=200).pack(pady=15)

        # MID - TOURNAMENT LIST
        mid = ctk.CTkFrame(self.tab_tournament, fg_color="transparent")
        mid.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        mid.rowconfigure(0, weight=1)
        mid.columnconfigure(0, weight=1)

        cols = ('ID', 'Name', 'Date', 'Format', 'Rounds', 'Status')
        self.tournament_tree, _ = _treeview(
            mid, cols, widths=[40, 150, 80, 80, 60, 80])

        ctk.CTkButton(mid, text='Activate Selected Tournament', command=self._activate_tournament,
                      fg_color='#7b1fa2', hover_color='#4a148c').pack(pady=10)

        # RIGHT SIDE - ENROLL PLAYERS
        right = ctk.CTkFrame(self.tab_tournament)
        right.grid(row=0, column=2, sticky='ns', padx=5, pady=5)

        ctk.CTkLabel(right, text="Enroll Players",
                     font=ctk.CTkFont(weight="bold")).pack(pady=10)
        ctk.CTkLabel(right, text="Ctrl+Click for multiple",
                     text_color="gray", font=ctk.CTkFont(size=11)).pack()

        self.enroll_listbox = tk.Listbox(right, selectmode='multiple', height=16, width=30,
                                         bg='#2b2b2b', fg='white', selectbackground='#1f538d',
                                         font=('Segoe UI', 10), borderwidth=0, highlightthickness=1)
        self.enroll_listbox.pack(pady=10, padx=10)
        self.enroll_listbox.bind('<<ListboxSelect>>', self._on_enroll_select)

        ctk.CTkButton(right, text='Enroll Selected', command=self._enroll_players,
                      fg_color='#2e7d32').pack(pady=2, padx=10, fill='x')
        ctk.CTkButton(right, text='Refresh List', command=self._refresh_enroll_list,
                      fg_color='#e65100').pack(pady=2, padx=10, fill='x')

        self.enrolled_count_label = ctk.CTkLabel(
            right, text='Enrolled: 0', font=ctk.CTkFont(weight="bold"))
        self.enrolled_count_label.pack(pady=10)

        self._refresh_tournaments()
        self._refresh_enroll_list()

    def _create_tournament(self):
        name = self.tournament_name.get().strip()
        date = self.tournament_date.get().strip()
        format_type = self.tournament_format_var.get()

        if not name:
            return _warn('Tournament name cannot be empty')
        try:
            num_rounds = int(self.tournament_rounds_var.get())
        except ValueError:
            return _warn('Round must be a valid number')

        db.create_tournament(name, date, num_rounds, format_type)
        messagebox.showinfo(
            'Success', f'Tournament "{name}" created successfully!')

        self.tournament_name.delete(0, 'end')
        self.tournament_date.delete(0, 'end')

        self._refresh_tournaments()

    def _refresh_tournaments(self):
        _clear(self.tournament_tree)

        for t in db.get_all_tournament():
            fmt = t.get('format') or 'elimination'
            fmt = fmt.upper()
            self.tournament_tree.insert('', 'end', values=(
                t['id'], t['name'], t['date'], fmt, t['num_rounds'], t['status']
            ))

    def _activate_tournament(self):
        row = _selected_row(self.tournament_tree)

        if row is None:
            return _warn('Please select a tournament to activate')

        self.current_tournament_id = row[0]
        self.status_bar.configure(
            text=f'Activated Tournament: {row[1]} | Format: {row[3].upper()} | Rounds: {row[4]} | Status: {row[5]}',
            text_color='#aaffaa'
        )

        self._refresh_enrolled_count()
        self._refresh_pairings()
        self._refresh_standings()

        enrolled = db.get_enrolled_players(self.current_tournament_id)

        fmt = row[3]
        if fmt.lower() == 'elimination':
            rec_rounds = elimination.recommended_rounds(len(enrolled))
        else:
            rec_rounds = swiss.recommended_rounds(len(enrolled))

        self.recommended_label.configure(
            text=f'Rec. Rounds: {rec_rounds}')

        messagebox.showinfo(
            'Active Tournament', f'Tournament "{row[1]}" is now active! You can start enrolling players and managing pairings.')

    def _on_enroll_select(self, event=None):
        _ = event
        n = len(self.enroll_listbox.curselection())

        if n > 0:
            fmt = 'elimination'
            if self.current_tournament_id:
                t = db.get_tournament(self.current_tournament_id)
                if t:
                    fmt = t.get('format') or 'elimination'

            if fmt.lower() == 'elimination':
                rec = elimination.recommended_rounds(n)
            else:
                rec = swiss.recommended_rounds(n)

            self.recommended_label.configure(
                text=f'{n} players selected. Recommended Rounds: {rec}')

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
            self.enrolled_count_label.configure(text=f'Enrolled: {n}')

# ============================
# TAB 3 - PAIRINGS AND RESULTS
# ============================
    def _build_pairings_tab(self):
        # Toolbar
        tb = ctk.CTkFrame(self.tab_pairings, fg_color="transparent")
        tb.pack(fill='x', pady=(0, 10))

        self.round_label = ctk.CTkLabel(
            tb, text='Round: N/A', font=ctk.CTkFont(size=16, weight="bold"), text_color='#e0c97f')
        self.round_label.pack(side='left', padx=12)

        ctk.CTkButton(tb, text='Generate Pairings', command=self._generate_pairings,
                      fg_color='#6a1b9a', hover_color='#4a148c').pack(side='left', padx=5)
        ctk.CTkButton(tb, text='Refresh', command=self._refresh_pairings,
                      fg_color='#e65100', hover_color='#d84315').pack(side='left', padx=5)

        # Pairing Treeview
        cols = ('Number', 'White Player', 'Black Player', 'Result')

        self.pairings_tree, _ = _treeview(
            self.tab_pairings, cols, widths=[60, 250, 250, 150])
        self.pairings_tree.bind('<Double-1>', self._input_result)

        ctk.CTkLabel(self.tab_pairings, text='Double-click a pairing to input result',
                     text_color='gray').pack(pady=5)

    def _refresh_pairings(self):
        _clear(self.pairings_tree)

        if not self.current_tournament_id:
            return

        t = db.get_tournament(self.current_tournament_id)

        if not t:
            return

        self.round_label.configure(
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

        t_format = t.get('format') or 'elimination'

        if t_format.lower() == 'elimination':
            if t['current_round'] == 0:
                prev_results = []
            else:
                prev_results = db.get_pairings(
                    self.current_tournament_id, t['current_round'])

            pairings = elimination.generate_pairings(
                players, prev_results, t['current_round'])
        else:  # Swiss format
            standings = db.get_tournament_standings(self.current_tournament_id)
            previous_pairings = db.get_previous_pairings_set(
                self.current_tournament_id)
            byes = db.get_player_with_bye(self.current_tournament_id)
            pairings = swiss.generate_pairings(
                standings, previous_pairings, byes)

        next_round = t['current_round'] + 1
        db.save_pairing(self.current_tournament_id, next_round, pairings)
        db.update_round(self.current_tournament_id, next_round)

        self._refresh_pairings()
        self._update_status_bar()

    def _input_result(self, event=None):
        _ = event
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

            t = db.get_tournament(self.current_tournament_id)

            if t and t['status'] != 'finished':
                if t['current_round'] >= t['num_rounds'] and db.is_round_complete(self.current_tournament_id, t['current_round']):
                    db.finish_tournament(self.current_tournament_id)

                    self._update_status_bar()
                    self._refresh_pairings()

                    standings = db.get_tournament_standings(
                        self.current_tournament_id)

                    if standings:
                        standings.sort(
                            key=lambda x: (-x['points'], -x['buchholz'], -x['rating']))
                        winner = standings[0]

                        messagebox.showinfo(
                            'Tournament Completed',
                            f'🏆 THE TOURNAMENT IS COMPLETE ! 🏆\n\nCONGRATS {winner["name"]} AS WINNER WITH {winner["points"]} POINTS! 🎉\nCHECK STANDINGS FOR THE COMPLETE LEADERBOARD.'
                        )

    def _update_status_bar(self):
        if self.current_tournament_id:
            t = db.get_tournament(self.current_tournament_id)

            if t:
                fmt = t.get('format') or 'elimination'
                self.status_bar.configure(
                    text=f"Activated: {t['name']} | Format: {fmt.upper()} | Rounds: {t['current_round']} / {t['num_rounds']} | Status: {t['status'].upper()}"
                )

# =================
# TAB 4 - STANDINGS
# =================
    def _build_standings_tab(self):
        tb = ctk.CTkFrame(self.tab_standings, fg_color="transparent")
        tb.pack(fill='x', pady=(0, 10))

        ctk.CTkButton(tb, text='Refresh Standings',
                      command=self._refresh_standings).pack(side='left')

        cols = ('Rank', 'Player Name', 'Points', 'Buchholz', 'Rating')
        self.standings_tree, _ = _treeview(
            self.tab_standings, cols, widths=[60, 300, 80, 100, 100])

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
        self.win = ctk.CTkToplevel(parent)
        self.win.title('Player Information')
        self.win.geometry('350x250')
        self.win.attributes('-topmost', True)
        self.win.grab_set()

        try:
            self.win.after(200, lambda: self.win.iconbitmap('source/logo.ico'))
        except tk.TclError:
            pass

        ctk.CTkLabel(self.win, text="Name:").grid(
            row=0, column=0, padx=15, pady=15, sticky='w')
        self.e_name = ctk.CTkEntry(self.win, width=200)
        self.e_name.grid(row=0, column=1, pady=15)

        ctk.CTkLabel(self.win, text="Rating:").grid(
            row=1, column=0, padx=15, pady=5, sticky='w')
        self.e_rating = ctk.CTkEntry(self.win, width=200)
        self.e_rating.grid(row=1, column=1, pady=5)

        ctk.CTkLabel(self.win, text="Club:").grid(
            row=2, column=0, padx=15, pady=15, sticky='w')
        self.e_club = ctk.CTkEntry(self.win, width=200)
        self.e_club.grid(row=2, column=1, pady=15)

        if initial:
            self.e_name.insert(0, initial.get('name', ''))
            self.e_rating.insert(0, str(initial.get('rating', '400')))
            self.e_club.insert(0, initial.get('club', ''))
        else:
            self.e_rating.insert(0, '400')

        bf = ctk.CTkFrame(self.win, fg_color="transparent")
        bf.grid(row=3, column=0, columnspan=2, pady=20)

        ctk.CTkButton(bf, text="Save", command=self._save,
                      fg_color='#2e7d32', width=100).pack(side='left', padx=10)
        ctk.CTkButton(bf, text="Cancel", command=self.win.destroy,
                      fg_color='#b71c1c', width=100).pack(side='left', padx=10)

        self.win.wait_window()

    def _save(self):
        name = self.e_name.get().strip()

        if not name:
            return _warn('Player name cannot be empty')
        try:
            rating = int(self.e_rating.get())
        except ValueError:
            return _warn('Rating must be a valid number')

        self.result = {
            'name': name,
            'rating': rating,
            'club': self.e_club.get().strip()
        }

        self.win.destroy()


class ResultDialog:
    def __init__(self, parent: tk.Widget, white: str, black: str):
        self.result = None
        self.win = ctk.CTkToplevel(parent)
        self.win.title("Match Result")
        self.win.geometry("300x250")
        self.win.attributes("-topmost", True)
        self.win.grab_set()

        try:
            self.win.after(200, lambda: self.win.iconbitmap('source/logo.ico'))
        except tk.TclError:
            pass

        ctk.CTkLabel(self.win, text=f"White: {white}", font=ctk.CTkFont(
            weight="bold")).pack(pady=(15, 2))
        ctk.CTkLabel(self.win, text="VS", text_color="gray").pack()
        ctk.CTkLabel(self.win, text=f"Black: {black}", font=ctk.CTkFont(
            weight="bold")).pack(pady=(2, 15))

        self.result_var = tk.StringVar(value='1-0')
        rf = ctk.CTkFrame(self.win, fg_color="transparent")
        rf.pack()

        ctk.CTkRadioButton(rf, text="White wins (1-0)",
                           variable=self.result_var, value="1-0").pack(pady=5, anchor='w')
        ctk.CTkRadioButton(rf, text="Black wins (0-1)",
                           variable=self.result_var, value="0-1").pack(pady=5, anchor='w')
        ctk.CTkRadioButton(rf, text="Draw (½-½)", variable=self.result_var,
                           value="1/2-1/2").pack(pady=5, anchor='w')

        bf = ctk.CTkFrame(self.win, fg_color="transparent")
        bf.pack(pady=20)

        ctk.CTkButton(bf, text="Save Result", command=self._save,
                      fg_color='#2e7d32', width=120).pack(side='left', padx=5)
        ctk.CTkButton(bf, text="Cancel", command=self.win.destroy,
                      fg_color='#b71c1c', width=100).pack(side='left', padx=5)

        self.win.wait_window()

    def _save(self):
        self.result = self.result_var.get()
        self.win.destroy()

# ================
# HELPER FUNCTIONS
# ================


def _treeview(parent, columns, widths=None):
    wrapper = ctk.CTkFrame(parent, fg_color="transparent")
    wrapper.pack(fill='both', expand=True, padx=5, pady=5)

    tree = ttk.Treeview(wrapper, columns=columns, show='headings')
    for i, col in enumerate(columns):
        tree.heading(col, text=col)
        if widths and i < len(widths):
            tree.column(col, width=widths[i], anchor='center')

    sb = ttk.Scrollbar(wrapper, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')
    return tree, sb


def _clear(tree):
    tree.delete(*tree.get_children())


def _selected_row(tree):
    sel = tree.selection()
    return tree.item(sel[0])['values'] if sel else None


def _warn(msg):
    messagebox.showwarning('Warning', msg)


# ===========
# ENTRY POINT
# ===========
if __name__ == '__main__':
    root = ctk.CTk()
    app = ChessTournamentApp(root)
    root.mainloop()
