from app.constants import share_gain


def jaccard_similarity(set_a, set_b):
    intersection = len(
        set(set_a) & set(set_b))
    union = len(set(set_a) | set(set_b))
    return intersection / \
        union if union > 0 else 0


def calculate_jaccard_similarity(
        draw_numbers, draw_stars, player_numbers, player_stars):
    number_weight = 0.80
    star_weight = 0.20

    number_similarity = jaccard_similarity(
        draw_numbers, player_numbers)
    star_similarity = jaccard_similarity(
        draw_stars, player_stars)

    final_similarity = (number_similarity * number_weight +
                        star_similarity * star_weight) * 100
    return round(final_similarity)


def structure_scores(
        participants, draw_numbers, draw_stars):
    scores_dict = {}
    limit = 10

    for participant in participants:
        player_numbers = set(
            map(int, participant.numbers.split(',')))
        player_stars = set(map(
            int, participant.lucky_numbers.split(',')))

        score = calculate_jaccard_similarity(
            draw_numbers, draw_stars, player_numbers, player_stars)

        if score >= 10:
            if score not in scores_dict:
                scores_dict[score] = []
            scores_dict[score].append(
                participant.user_id)

    scores_dict = dict(
        sorted(
            scores_dict.items(),
            key=lambda item: item[0],
            reverse=True))

    final_ranking = {}
    current_rank = 1
    total_ranked = 0

    for score, players in scores_dict.items():
        if total_ranked >= limit:
            break

        nb_tied = len(players)

        final_ranking[current_rank] = players
        total_ranked += nb_tied

        current_rank += nb_tied

    return final_ranking


def compute_gain(
        scores_dict, reward_price):
    gain_per_players = {}

    ranks = sorted(
        map(int, scores_dict.keys()))

    for rank in ranks:
        players = scores_dict[rank]
        gap_between_next_rank = len(
            players)

        if gap_between_next_rank == 1:
            gain_player = reward_price * \
                share_gain[rank]
            gain_per_players[players[0]
                             ] = gain_player
        else:
            end = min(
                rank + gap_between_next_rank, 11)

            gain_player = sum(
                map(lambda x: reward_price *
                    share_gain[x], range(rank, end))
            ) / gap_between_next_rank
            for player in players:
                gain_per_players[player] = gain_player

    total_distributed = sum(
        gain_per_players.values())
    remainder = reward_price - \
        total_distributed

    return gain_per_players, total_distributed, remainder


def distribute_remainder(
        gain_per_players, remainder):
    total_distributed = sum(
        gain_per_players.values())
    if total_distributed == 0:
        return gain_per_players

    for player, gain in gain_per_players.items():
        additional_gain = (
            gain / total_distributed) * remainder
        gain_per_players[player] += additional_gain

    return gain_per_players
