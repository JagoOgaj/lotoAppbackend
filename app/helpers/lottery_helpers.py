from flask import jsonify
import random
from app.schemas import LotteryWinerSchema
from app.tools import distribute_remainder, compute_gain, structure_scores
from app.models import User
from faker import Faker

fake = Faker()


def get_formatted_results(participants, draw_numbers, draw_stars, reward_price, db):
    """
    Génére les résultats formatés des participants à un tirage de loterie.

    Cette fonction calcule les résultats d'un tirage en structurant les scores des
    participants, en calculant les gains et en formatant les résultats pour chaque
    joueur. Les résultats sont retournés sous forme de liste de dictionnaires
    contenant les informations des joueurs, leur rang, leur score et leurs gains.

    Args:
        participants (list): Liste des participants au tirage.
        draw_numbers (list): Numéros gagnants du tirage.
        draw_stars (list): Numéros étoiles gagnants du tirage.
        reward_price (float): Montant total des récompenses à distribuer.
        db (SQLAlchemy Session): Session de la base de données pour les requêtes.

    Returns:
        list: Une liste de résultats formatés, où chaque résultat est un
        dictionnaire contenant les informations suivantes :
            - player_id (int): L'identifiant du joueur.
            - rank (int): Le rang du joueur dans le tirage.
            - name (str): Le nom complet du joueur.
            - score (int): Le score du joueur.
            - winnings (float): Les gains du joueur.

    Raises:
        Exception: Lève une exception si une erreur se produit lors du traitement,
        comme une erreur de récupération d'utilisateur ou de calcul de gains.

    Example:
        results = get_formatted_results(participants, draw_numbers, draw_stars, reward_price, db)
    """
    try:
        ranking_results = structure_scores(participants, draw_numbers, draw_stars)

        player_winnings, total_sum, remainder = compute_gain(
            ranking_results, reward_price
        )

        if remainder > 0:
            distribute_remainder(player_winnings, remainder)

        formatted_results = []

        schema = LotteryWinerSchema(many=True)

        for rank, (players_ids, score) in ranking_results.items():
            for player_id in players_ids:
                winnings = player_winnings.get(player_id, 0)

                user = db.session.query(User).filter_by(id=player_id).one_or_none()
                if user is None:
                    raise Exception(
                        "Une erreur est survenue lors de la récupération de l'utilisateur"
                    )
                score = score

                formatted_results.append(
                    {
                        "player_id": player_id,
                        "rank": rank,
                        "name": user.full_name,
                        "score": score,
                        "winnings": winnings,
                    }
                )

        validated_results = schema.dump(formatted_results)

        return validated_results
    except Exception as e:
        raise Exception(str(e))


def generate_random_user():
    """
    Génère un utilisateur fictif avec des informations aléatoires.

    Cette fonction utilise la bibliothèque Faker pour créer un nom et un email
    aléatoires. Elle génère également des numéros de loterie et des numéros chance,
    qui sont des listes de nombres représentées sous forme de chaînes, prêtes à
    être utilisées dans le contexte d'un tirage de loterie.

    Returns:
        tuple: Un tuple contenant les informations de l'utilisateur généré,
        comprenant :
            - fake_name (str): Le nom aléatoire de l'utilisateur.
            - fake_email (str): L'adresse email aléatoire de l'utilisateur.
            - numbers (str): Une chaîne contenant 5 numéros de loterie aléatoires,
              séparés par des virgules.
            - lucky_numbers (str): Une chaîne contenant 2 numéros chance aléatoires,
              séparés par des virgules.

    Example:
        user_info = generate_random_user()
        print(user_info)  # ("John Doe", "john.doe@example.com", "3,12,23,34,45", "4,8")
    """
    fake_name = fake.name()
    fake_email = fake.email()
    numbers = ",".join([str(random.randint(1, 49)) for _ in range(5)])
    lucky_numbers = ",".join([str(random.randint(1, 9)) for _ in range(2)])
    return fake_name, fake_email, numbers, lucky_numbers


def generate_wining_numbers():
    """
    Génère des numéros de loterie gagnants.

    Cette fonction tire au sort 5 numéros distincts parmi les nombres allant de
    1 à 49, représentant les numéros gagnants d'un tirage de loterie.

    Returns:
        list: Une liste de 5 entiers uniques représentant les numéros gagnants
        de la loterie, triés dans l'ordre croissant.

    Example:
        winning_numbers = generate_winning_numbers()
        print(winning_numbers)  # [3, 12, 25, 34, 47]
    """
    return random.sample(range(1, 50), 5)


def generate_luck_numbers():
    """
    Génère des numéros chance pour la loterie.

    Cette fonction tire au sort 2 numéros distincts parmi les nombres allant de
    1 à 9, représentant les numéros chance d'un tirage de loterie.

    Returns:
        list: Une liste de 2 entiers uniques représentant les numéros chance
        de la loterie.

    Example:
        luck_numbers = generate_luck_numbers()
        print(luck_numbers)  # [4, 8]
    """
    return random.sample(range(1, 10), 2)
