import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.tools import (
    jaccard_similarity,
    compute_gain,
    calculate_jaccard_similarity,
    structure_scores,
    compute_gain,
    distribute_remainder,
)


def test_jaccard_similarity():
    """Teste la similarité de Jaccard."""
    assert jaccard_similarity([1, 2, 3], [2, 3, 4]) == 0.5
    assert jaccard_similarity([], [1, 2]) == 0
    assert jaccard_similarity([1, 2, 3], []) == 0


def test_calculate_jaccard_similarity():
    """Teste la similarité Jaccard pondérée."""
    assert calculate_jaccard_similarity([1, 2, 3], [1], [1, 2, 4], [1]) == 60
    assert calculate_jaccard_similarity([1, 2], [1], [3, 4], [2]) == 0


def test_structure_scores():
    """Teste la structuration des scores des participants."""

    class Participant:
        def __init__(self, user_id, numbers, lucky_numbers):
            self.user_id = user_id
            self.numbers = numbers
            self.lucky_numbers = lucky_numbers

    participants = [
        Participant(user_id=1, numbers="1,2,3", lucky_numbers="1"),
        Participant(user_id=2, numbers="1,2,4", lucky_numbers="1"),
        Participant(user_id=3, numbers="1,3,5", lucky_numbers="2"),
    ]
    draw_numbers = [1, 2, 3]
    draw_stars = [1]

    expected_output = {
        1: [[1], 100],
        2: [[2], 60],
        3: [[3], 40],
    }

    assert structure_scores(participants, draw_numbers, draw_stars) == expected_output


def test_compute_gain():
    """Teste le calcul des gains des joueurs."""
    scores = {
        1: [[1, 2], 80],
        2: [[3], 60],
        3: [[4, 5], 50],
    }
    reward = 1000

    expected_output = ({1: 300.0, 2: 300.0, 3: 200.0, 4: 95.0, 5: 95.0}, 990.0, 10.0)
    assert compute_gain(scores, reward) == expected_output


def test_distribute_remainder():
    """Teste la distribution du montant restant de la récompense."""
    gains = {1: 400.0, 2: 200.0, 3: 120.0}
    remainder = 280.0

    expected_output = {
        1: 555.5555555555555,
        2: 277.77777777777777,
        3: 166.66666666666666,
    }
    assert distribute_remainder(gains, remainder) == expected_output
