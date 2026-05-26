# ------
# IMPORT
# ------
import sqlite3
from contextlib import contextmanager

FILE = "chess_tournament.db"

# -----------------------
# CONNECT AND INSTANTIATE
# -----------------------


@contextmanager
def get_connection():
    connection = sqlite3.connect(FILE)

    connection.row_factory = sqlite3.Row  # Access roq['name']

    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with get_connection() as connection:
        connection.executescript("""
            -- Tabel pemain (master)
            CREATE TABLE IF NOT EXISTS players (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                rating  INTEGER DEFAULT 1500,
                club    TEXT    DEFAULT ''
            );
 
            -- Tabel turnamen
            CREATE TABLE IF NOT EXISTS tournaments (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                date          TEXT    DEFAULT '',
                num_rounds    INTEGER DEFAULT 7,
                current_round INTEGER DEFAULT 0,
                status        TEXT    DEFAULT 'pending'  -- pending | ongoing | finished
            );
 
            -- Relasi turnamen ↔ pemain (many-to-many)
            CREATE TABLE IF NOT EXISTS tournament_players (
                tournament_id INTEGER REFERENCES tournaments(id),
                player_id     INTEGER REFERENCES players(id),
                PRIMARY KEY (tournament_id, player_id)
            );
 
            -- Tabel pairing per ronde
            CREATE TABLE IF NOT EXISTS pairings (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER REFERENCES tournaments(id),
                round_num     INTEGER NOT NULL,
                white_id      INTEGER,   -- NULL jika BYE (hitam-nya yang main)
                black_id      INTEGER,   -- NULL jika BYE (putih-nya yang main)
                result        TEXT       -- '1-0' | '0-1' | '1/2-1/2' | 'bye' | NULL
            );
        """)
# ------------
# PLAYERS CRUD
# ------------


def add_player(name: str, rating: int = 1500, club: str = "") -> int:
    with get_connection() as connection:
        cur = connection.execute(
            "INSERT INTO players (name, rating, club) VALUES (?, ?, ?)", (name, rating, club))
        return cur.lastrowid


def update_player(player_id: int, name: str, rating: int, club: str):
    with get_connection() as connection:
        connection.execute(
            "UPDATE players SET name=?, rating=?, club=? WHERE id=?", (name, rating, club, player_id))


def delete_player(player_id: int):
    with get_connection() as connection:
        connection.execute("DELETE FROM players WHERE id=?", (player_id,))


def get_all_players() -> list:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM players ORDER BY rating DESC").fetchall()
        return [dict(r) for r in rows]

# ================
# TOURNAMENTS CRUD
# ================


def create_tournament(name: str, date: str, num_rounds: int) -> int:
    with get_connection() as connection:
        cur = connection.execute(
            "INSERT INTO tournaments (name, date, num_rounds) VALUES (?, ?, ?)", (name, date, num_rounds))
        return cur.lastrowid


def get_all_tournament() -> list:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tournaments ORDER BY id DESC").fetchall()
        return [dict(r) for r in row]


def get_tournament(tournament_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tournaments WHERE id=?", (tournament_id,)).fetchone()
        return dict(row) if row else None


def update_round(tournament_id: int, new_round: int):
    with get_connection() as connection:
        connection.execute(
            "UPDATE tournaments SET current_round=?, status=? WHERE id=?",
            (new_round, 'ongoing', tournament_id))


def finish_tournament(tournament_id: int):
    with get_connection() as connection:
        connection.execute(
            "UPDATE tournaments SET status='finished' WHERE id=?",
            (tournament_id,))

# ==========
# ENROLLMENT
# ==========


def enroll_player(tournament_id: int, player_id: int) -> bool:
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO tournament_players VALUES (?, ?)",
                (tournament_id, player_id))
        return True
    except sqlite3.IntegrityError:
        return False


def get_enrolled_players(tournament_id: int) -> list:
    with get_connection() as connection:
        row = connection.execute("""
            SELECT p.id, p.name, p.rating, p.club
            FROM players p
            JOIN tournament_players tp ON p.id = tp.player_id
            WHERE tp.tournament_id = ?
            ORDER BY p.rating DESC
        """, (tournament_id,)).fetchall()
        return [dict(r) for r in row]

# =======
# PAIRING
# =======


def save_pairing(tournament_id: int, round_num: int, pairings: list):
    with get_connection() as connection:
        for white_id, black_id in pairings:
            result = "bye" if black_id is None else None

            connection.execute("INSERT INTO pairings (tournament_id, round_num, white_id, black_id, result) VALUES (?,?,?,?,?)",
                               (tournament_id, round_num, white_id, black_id, result))


def get_pairings(tournament_id: int, round_num: int) -> list:
    with get_connection() as connection:
        row = connection.execute("""
            SELECT
                pr.id,
                pr.white_id,
                pw.name AS white_name,
                pr.black_id,
                pb.name AS black_name,
                pr.result
            FROM pairings pr
            LEFT JOIN players pw ON pw.id = pr.white_id
            LEFT JOIN players pb ON pb.id = pr.black_id
            WHERE pr.tournament_id = ? AND pr.round_num = ?
            ORDER BY pr.id
        """, (tournament_id, round_num)).fetchall()
        return [dict(r) for r in row]


def update_pairing_result(pairing_id: int, result: str):
    with get_connection() as connection:
        connection.execute(
            "UPDATE pairings SET result=? WHERE id=?", (result, pairing_id))


def is_round_complete(tournament_id: int, round_num: int) -> bool:
    with get_connection() as connection:
        row = connection.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN result IS NOT NULL THEN 1 ELSE 0 END) as done
            FROM pairings
            WHERE tournament_id=? AND round_num=?
        """, (tournament_id, round_num)).fetchone()
        return row['total'] > 0 and row['total'] == row['done']


def get_previous_pairings_set(tournament_id: int) -> set:
    """Return set of frozenset({id1, id2}) — semua pairing yang pernah terjadi."""
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT white_id, black_id FROM pairings
            WHERE tournament_id=? AND black_id IS NOT NULL
        """, (tournament_id,)).fetchall()
        return {frozenset({r['white_id'], r['black_id']}) for r in rows}


def get_player_with_bye(tournament_id: int) -> set:
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT white_id FROM pairings
            WHERE tournament_id=? AND result='bye'
        """, (tournament_id,)).fetchall()
        return {r['white_id'] for r in rows}


def get_tournament_standings(tournament_id: int) -> list:
    players = get_enrolled_players(tournament_id)
    if not players:
        return []

    points = {p['id']: 0.0 for p in players}

    with get_connection() as connection:
        row = connection.execute("""
            SELECT white_id, black_id, result
            FROM pairings
            WHERE tournament_id=? AND result IS NOT NULL
        """, (tournament_id,)).fetchall()

    opponents = {p['id']: [] for p in players}

    for r in row:
        result = r['result']
        w, b = r['white_id'], r['black_id']

        if result == 'bye':
            if w in points:
                points[w] += 1.0
        elif result == '1-0':
            if w in points:
                points[w] += 1.0
            if w and b:
                opponents[w].append(b)
                opponents[b].append(w)
        elif result == '0-1':
            if b in points:
                points[b] += 1.0
            if w and b:
                opponents[w].append(b)
                opponents[b].append(w)
        elif result == '1/2-1/2':
            if w in points:
                points[w] += 0.5
            if b in points:
                points[b] += 0.5
            if w and b:
                opponents[w].append(b)
                opponents[b].append(w)

    buchholz = {}
    for p in players:
        player_id = p['id']
        buchholz[player_id] = sum(points.get(opp, 0.0)
                                  for opp in opponents[player_id])

    result_list = []
    for p in players:
        result_list.append({
            'player_id': p['id'],
            'name': p['name'],
            'rating': p['rating'],
            'points': points[p['id']],
            'buchholz': buchholz[p['id']]
        })

    return result_list
