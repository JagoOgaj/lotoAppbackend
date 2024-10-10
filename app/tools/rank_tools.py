from app.constants import share_gain


def jaccard_similarity(set_a, set_b):
    """
    Calcule la similarité de Jaccard entre deux ensembles.

    La similarité de Jaccard est une mesure de la similarité entre deux ensembles
    définie comme le rapport de la taille de l'intersection de l'ensemble à la
    taille de l'union des ensembles. Cette fonction renvoie un nombre compris
    entre 0 et 1, où 0 signifie qu'il n'y a aucune similarité et 1 signifie
    que les ensembles sont identiques.

    Paramètres:
        set_a (iterable): Le premier ensemble d'éléments. Peut être une liste, un ensemble ou tout autre itérable.
        set_b (iterable): Le deuxième ensemble d'éléments. Peut être une liste, un ensemble ou tout autre itérable.

    Retourne:
        float: La similarité de Jaccard entre les deux ensembles.
               Renvoie 0 si les ensembles n'ont pas d'éléments en commun.

    Exemple:
        >>> jaccard_similarity([1, 2, 3], [2, 3, 4])
        0.5
    """
    intersection = len(set(set_a) & set(set_b))
    union = len(set(set_a) | set(set_b))
    return intersection / union if union > 0 else 0


def calculate_jaccard_similarity(
    draw_numbers, draw_stars, player_numbers, player_stars
):
    """
    Calcule la similarité Jaccard pondérée entre les numéros et les étoiles d'un tirage et d'un joueur.

    Cette fonction utilise la mesure de similarité de Jaccard pour évaluer la correspondance
    entre les numéros d'un tirage et les numéros d'un joueur, ainsi qu'entre les étoiles
    du tirage et celles du joueur. Les similarités des numéros et des étoiles sont
    pondérées différemment, avec une plus grande importance donnée aux numéros.

    Paramètres:
        draw_numbers (iterable): Les numéros du tirage (peut être une liste ou un ensemble).
        draw_stars (iterable): Les étoiles du tirage (peut être une liste ou un ensemble).
        player_numbers (iterable): Les numéros choisis par le joueur (peut être une liste ou un ensemble).
        player_stars (iterable): Les étoiles choisies par le joueur (peut être une liste ou un ensemble).

    Retourne:
        int: La similarité Jaccard pondérée entre les numéros et les étoiles,
             exprimée en pourcentage et arrondie à l'entier le plus proche.

    Exemple:
        >>> calculate_jaccard_similarity([1, 2, 3], [1], [1, 2, 4], [1])
        80
    """
    number_weight = 0.80
    star_weight = 0.20

    number_similarity = jaccard_similarity(draw_numbers, player_numbers)
    star_similarity = jaccard_similarity(draw_stars, player_stars)

    final_similarity = (
        number_similarity * number_weight + star_similarity * star_weight
    ) * 100
    return round(final_similarity)


def structure_scores(participants, draw_numbers, draw_stars):
    """
    Structure les scores des participants en fonction de leur similarité avec les numéros
    et les étoiles d'un tirage, et génère un classement des meilleurs scores.

    Cette fonction calcule la similarité de Jaccard entre les numéros et les étoiles d'un
    tirage et ceux de chaque participant. Les scores sont ensuite organisés en fonction
    de leur valeur, et les participants ayant obtenu un score supérieur ou égal à 10 sont
    inclus dans le classement. Le classement est limité aux 10 meilleurs scores.

    Paramètres:
        participants (list): Une liste d'objets participants, où chaque objet contient
                             un identifiant d'utilisateur et les numéros et étoiles du joueur.
        draw_numbers (iterable): Les numéros du tirage (peut être une liste ou un ensemble).
        draw_stars (iterable): Les étoiles du tirage (peut être une liste ou un ensemble).

    Retourne:
        dict: Un dictionnaire représentant le classement final des participants, où la clé
              est le rang et la valeur est une liste contenant les identifiants des utilisateurs
              et leur score. Le dictionnaire ne contient que les participants ayant obtenu
              un score de 10 ou plus, et est limité aux 10 meilleurs scores.

    Exemple:
        >>> participants = [
        ...     Participant(user_id=1, numbers='1,2,3', lucky_numbers='1'),
        ...     Participant(user_id=2, numbers='1,2,4', lucky_numbers='1'),
        ...     Participant(user_id=3, numbers='1,3,5', lucky_numbers='2'),
        ... ]
        >>> draw_numbers = [1, 2, 3]
        >>> draw_stars = [1]
        >>> structure_scores(participants, draw_numbers, draw_stars)
        {1: [[1, 2], 80], 2: [[3], 60]}
    """
    scores_dict = {}
    limit = 10

    for participant in participants:
        player_numbers = set(map(int, participant.numbers.split(",")))
        player_stars = set(map(int, participant.lucky_numbers.split(",")))

        score = calculate_jaccard_similarity(
            draw_numbers, draw_stars, player_numbers, player_stars
        )

        if score >= 10:
            if score not in scores_dict:
                scores_dict[score] = []
            scores_dict[score].append(participant.user_id)

    scores_dict = dict(
        sorted(scores_dict.items(), key=lambda item: item[0], reverse=True)
    )

    final_ranking = {}
    current_rank = 1
    total_ranked = 0

    for score, players in scores_dict.items():
        if total_ranked >= limit:
            break

        nb_tied = len(players)

        final_ranking[current_rank] = [players, score]
        total_ranked += nb_tied

        current_rank += nb_tied

    return final_ranking


def compute_gain(scores_dict, reward_price):
    """
    Calcule les gains des joueurs en fonction de leur classement et du prix de la récompense.

    Cette fonction distribue un prix total basé sur le classement des joueurs, en utilisant un
    système de partage des gains défini par un dictionnaire `share_gain`. Les gains sont
    calculés pour chaque joueur en fonction de leur rang et du nombre de joueurs ayant le même
    rang.

    Paramètres:
        scores_dict (dict): Un dictionnaire représentant les scores des joueurs, où chaque clé
                            est le rang et la valeur est une liste contenant les identifiants des
                            joueurs et leur score.
        reward_price (float): Le montant total de la récompense à distribuer entre les joueurs
                              selon leur classement.

    Retourne:
        tuple: Un tuple contenant trois éléments :
            - dict: Un dictionnaire où chaque clé est l'identifiant d'un joueur et la valeur
                    est le montant de gain correspondant.
            - float: Le montant total distribué aux joueurs.
            - float: Le montant restant de la récompense après distribution.

    Exemple:
        >>> scores = {
        ...     1: [[1, 2], 80],
        ...     2: [[3], 60],
        ...     3: [[4, 5], 50],
        ... }
        >>> reward = 1000
        >>> compute_gain(scores, reward)
        ({1: 400.0, 2: 300.0, 3: 200.0}, 900.0, 100.0)
    """
    gain_per_players = {}

    ranks = sorted(map(int, scores_dict.keys()))

    for rank in ranks:
        players, score = scores_dict[rank]
        gap_between_next_rank = len(players)

        if gap_between_next_rank == 1:
            gain_player = reward_price * share_gain[rank]
            gain_per_players[players[0]] = gain_player
        else:
            end = min(rank + gap_between_next_rank, 11)

            gain_player = (
                sum(
                    map(
                        lambda x: reward_price * share_gain[x],
                        range(rank, end),
                    )
                )
                / gap_between_next_rank
            )
            for player in players:
                gain_per_players[player] = gain_player

    total_distributed = sum(gain_per_players.values())
    remainder = reward_price - total_distributed

    return gain_per_players, total_distributed, remainder


def distribute_remainder(gain_per_players, remainder):
    """
    Distribue le montant restant de la récompense aux joueurs proportionnellement à leurs gains.

    Cette fonction ajuste les gains de chaque joueur en fonction du montant restant après la
    distribution initiale des gains. Chaque joueur reçoit une part du montant restant proportionnelle
    à son gain par rapport au total des gains distribués.

    Paramètres:
        gain_per_players (dict): Un dictionnaire où chaque clé est l'identifiant d'un joueur et
                                  la valeur est le montant de gain correspondant à ce joueur.
        remainder (float): Le montant restant de la récompense à distribuer entre les joueurs.

    Retourne:
        dict: Un dictionnaire mis à jour avec les gains des joueurs, incluant le montant
              restant distribué proportionnellement.

    Exemple:
        >>> gains = {1: 400.0, 2: 300.0, 3: 200.0}
        >>> remainder = 100.0
        >>> distribute_remainder(gains, remainder)
        {1: 440.0, 2: 330.0, 3: 220.0}
    """
    total_distributed = sum(gain_per_players.values())
    if total_distributed == 0:
        return gain_per_players

    for player, gain in gain_per_players.items():
        additional_gain = (gain / total_distributed) * remainder
        gain_per_players[player] += additional_gain

    return gain_per_players
