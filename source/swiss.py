def generate_pairings(players_data: list, previous_pairings: set, players_with_bye: set) -> list:
    if not players_data:
        return []

    sorted_players = sorted(
        players_data, key=lambda x: (-x['points'], -x['rating']))

    result_pairings = []
    paired_ids = set()

# ==========
# HANDLE BYE
# ==========
    if len(sorted_players) % 2 == 1:
        bye_player = _pick_bye_player(sorted_players, players_with_bye)

        result_pairings.append((bye_player['player_id'], None))

        paired_ids.add(bye_player['player_id'])

# =================
# MAIN PAIRING LOOP
# =================
    # ------------------------
    # Arrange Unpaired Players
    # ------------------------
    unpaired = [p for p in sorted_players if p['player_id'] not in paired_ids]

    i = 0

    while i < len(unpaired):
        player1 = unpaired[i]
        if player1['player_id'] in paired_ids:
            i += 1
            continue
        # ------------------------
        # Search for Best Opponent
        # ------------------------
        opponent = _find_opponent(
            player1, unpaired, paired_ids, previous_pairings, i)

        if opponent:
            white_id, black_id = _assign_colors(player1, opponent)

            result_pairings.append((white_id, black_id))
            paired_ids.add(player1['player_id'])
            paired_ids.add(opponent['player_id'])
        else:
            opponent = _find_opponent_forced(unpaired, paired_ids, i)

            if opponent:
                white_id, black_id = _assign_colors(player1, opponent)

                result_pairings.append((white_id, black_id))
                paired_ids.add(player1['player_id'])
                paired_ids.add(opponent['player_id'])
        i += 1

    return result_pairings

# ================
# HELPER FUNCTIONS
# ================


def _pick_bye_player(sorted_players: list, players_with_bye: set) -> dict:
    for player in reversed(sorted_players):
        if player['player_id'] not in players_with_bye:
            return player
    return sorted_players[-1]


def _find_opponent(player1: dict, unpaired: list, paired_ids: set, previous_pairings: set, start_index: int) -> dict | None:
    for j in range(start_index + 1, len(unpaired)):
        candidate = unpaired[j]

        if candidate['player_id'] in paired_ids:
            continue

        pair_key = frozenset({player1['player_id'], candidate['player_id']})

        if pair_key not in previous_pairings:
            return candidate

    return None


def _find_opponent_forced(unpaired: list, paired_ids: set, start_index: int) -> dict | None:
    for j in range(start_index + 1, len(unpaired)):
        candidate = unpaired[j]

        if candidate['player_id'] not in paired_ids:
            return candidate
    return None


def _assign_colors(player1, player2):
    if player1['rating'] >= player2['rating']:
        return player1['player_id'], player2['player_id']
    else:
        return player2['player_id'], player1['player_id']


"""
def _assign_colors(player1: dict, player2: dict) -> tuple:
    if player1['color_history'].count('white') < player1['color_history'].count('black'):
        return player1['player_id'], player2['player_id']
    elif player1['color_history'].count('black') < player1['color_history'].count('white'):
        return player2['player_id'], player1['player_id']
    else:
        return (player1['player_id'], player2['player_id']) if player1['rating'] >= player2['rating'] else (player2['player_id'], player1['player_id'])
"""


def recommended_rounds(num_players: int) -> int:
    """Calculate the recommended number of rounds for a Swiss-system tournament.

    Args:
        num_players: The number of players in the tournament.

    Returns:
        The recommended number of rounds.
    """
    import math

    if num_players <= 1:
        return 1

    return math.ceil(math.log2(num_players)) + 1
