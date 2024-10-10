from enum import Enum


class Status(Enum):
    """
    Enumération représentant les différents statuts d'un tirage.

    Cette classe définit les statuts possibles pour un tirage, permettant de suivre
    son état tout au long de son cycle de vie. Les statuts sont utilisés pour
    gérer le flux d'un tirage, indiquant s'il est en cours, en attente de validation,
    terminé ou s'il s'agit d'une simulation.

    Attributs:
        EN_COUR (str): Indique que le tirage est actuellement en cours.
                       Les participants peuvent encore jouer ou modifier leurs choix.

        EN_VALIDATION (str): Indique que le tirage est en attente de validation.
                             Cela signifie que les résultats sont en cours de vérification
                             avant d'être officiellement annoncés.

        TERMINE (str): Indique que le tirage est terminé.
                       Les résultats sont finalisés et aucun changement n'est possible.

        SIMULATION (str): Indique que le tirage est en mode simulation.
                          Cela permet aux utilisateurs de tester des scénarios sans affecter
                          les tirages réels.

        SIMULATION_TERMINE (str): Indique que la simulation du tirage est terminée.
                                   Les résultats de la simulation sont disponibles, mais
                                   cela ne concerne pas les tirages réels.

    Exemple:
        >>> current_status = Status.EN_COUR
        >>> print(current_status)
        Status.EN_COUR
    """

    EN_COUR = "EN_COUR"
    EN_VALIDATION = "EN_VALIDATION"
    TERMINE = "TERMINE"
    SIMULATION = "SIMULATION"
    SIMULATION_TERMINE = "SIMULATION_TERMINE"
