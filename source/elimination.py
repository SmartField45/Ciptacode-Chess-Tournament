import math


def generate_pairings(enrolled_players: list, previous_pairings_results: list, current_round: int) -> list:
    if not enrolled_players:
        return []

    result_pairings = []

    # ==========================
    # ROUND 1: Initial Pairings
    # ==========================
    if current_round == 0:
        sorted_players = sorted(
            enrolled_players, key=lambda x: x['rating'], reverse=True)
        num_players = len(sorted_players)

        next_power_of_2 = 2 ** math.ceil(math.log2(num_players))
        num_byes = next_power_of_2 - num_players

        paired_ids = set()

        # Berikan Bye ke unggulan teratas
        for i in range(num_byes):
            player = sorted_players[i]
            result_pairings.append((player['id'], None))
            paired_ids.add(player['id'])

        unpaired = [p for p in sorted_players if p['id'] not in paired_ids]

        for i in range(len(unpaired) // 2):
            p1 = unpaired[i]
            p2 = unpaired[-(i + 1)]

            result_pairings.append((p1['id'], p2['id']))

        return result_pairings

    # ==========================
    # ROUND NEXT: Pairings based on previous results
    # ==========================
    advancing_players = []

    for match in previous_pairings_results:
        result = match['result']
        white = match['white_id']
        black = match['black_id']

        if result == '1-0':
            advancing_players.append(white)
        elif result == '0-1':
            advancing_players.append(black)
        elif result == 'bye':
            advancing_players.append(white)
        elif result == '1/2-1/2':
            advancing_players.append(white)
    for i in range(0, len(advancing_players), 2):
        if i + 1 < len(advancing_players):
            p1_id = advancing_players[i]
            p2_id = advancing_players[i+1]
            result_pairings.append((p1_id, p2_id))
        else:
            result_pairings.append((advancing_players[i], None))

    return result_pairings


def recommended_rounds(num_players: int) -> int:
    if num_players <= 1:
        return 1
    return math.ceil(math.log2(num_players))
