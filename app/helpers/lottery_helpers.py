from flask import jsonify
import random
import string
from app.schemas import LotteryWinerSchema
from app.tools import (
    distribute_remainder,
    compute_gain,
    structure_scores,
    calculate_jaccard_similarity,
)
from app import db
from app.models import User


def get_formatted_results(
    participants, draw_numbers, draw_stars, reward_price
):
    try:
        ranking_results = structure_scores(
            participants, draw_numbers, draw_stars
        )

        player_winnings, total_sum, remainder = compute_gain(
            ranking_results, reward_price
        )
        print(total_sum)

        if remainder > 0:
            distribute_remainder(player_winnings, remainder)

        formatted_results = []

        schema = LotteryWinerSchema(many=True)

        for rank, players in ranking_results.items():
            for player_id in players:
                winnings = player_winnings.get(player_id, 0)

                user = (
                    db.session.query(User)
                    .filter_by(id=player_id)
                    .one_or_none()
                )
                if user is None:
                    raise Exception(
                        "Une erreur est survenue lors de la récupération de l'utilisateur"
                    )

                score = (
                    int(
                        calculate_jaccard_similarity(
                            draw_numbers,
                            draw_stars,
                            set(
                                map(
                                    int,
                                    participants[
                                        player_id - 1
                                    ].numbers.split(","),
                                )
                            ),
                            set(
                                map(
                                    int,
                                    participants[
                                        player_id - 1
                                    ].lucky_numbers.split(","),
                                )
                            ),
                        )
                    )
                    if player_id in player_winnings
                    else 0
                )

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
    except Exception:
        raise Exception("Une erreur est survenue")


def generate_random_user():
    fake_name = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )
    fake_email = fake_name.lower() + "@example.com"
    numbers = ",".join([str(random.randint(1, 49)) for _ in range(5)])
    lucky_numbers = ",".join([str(random.randint(1, 9)) for _ in range(2)])
    return fake_name, fake_email, numbers, lucky_numbers


def generate_wining_numbers():
    return random.sample(range(1, 50), 5)


def generate_luck_numbers():
    return random.sample(range(1, 10), 2)
