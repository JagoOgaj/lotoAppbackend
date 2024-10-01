from flask import jsonify
import random
import string


def generate_lottery_ranking(lottery_id):
    try:
        # Logique pour récupérer et générer le classement des participants
        # Vous pouvez ajouter votre algorithme de calcul des scores,
        # classement, etc.
        ranking_data = []  # Remplissez ceci avec les résultats du classement

        # Exemple de structure de réponse pour le classement
        return jsonify({
            "message": "Classement des participants récupéré avec succès.",
            "data": ranking_data
        }), 200
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue lors de la génération du classement.",
            "details": str(e)
        }), 500


def generate_random_user():
    # Générer un utilisateur fictif aléatoire
    fake_name = ''.join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=6))
    fake_email = fake_name.lower() + "@example.com"
    numbers = ','.join([str(random.randint(1, 49)) for _ in range(5)])
    lucky_numbers = ','.join([str(random.randint(1, 9)) for _ in range(2)])
    return fake_name, fake_email, numbers, lucky_numbers
