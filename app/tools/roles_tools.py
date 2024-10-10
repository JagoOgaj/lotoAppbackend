from enum import Enum


class Roles(Enum):
    """
    Enumération représentant les différents rôles d'utilisateur dans le système.

    Cette classe définit les rôles disponibles pour les utilisateurs, chacun ayant des permissions
    et des responsabilités spécifiques dans le système. Les rôles sont utilisés pour gérer l'accès
    et les autorisations des utilisateurs.

    Attributs:
        ADMIN (str): Représente un utilisateur avec des droits d'administration.
                     Les administrateurs ont accès à toutes les fonctionnalités et
                     peuvent effectuer des actions critiques dans le système.

        USER (str): Représente un utilisateur régulier du système.
                    Les utilisateurs peuvent accéder aux fonctionnalités de base
                    mais n'ont pas de droits d'administration.

        FAKE (str): Représente un utilisateur fictif ou non authentique.
                    Ce rôle peut être utilisé pour des tests ou des scénarios spécifiques
                    où une distinction doit être faite entre les utilisateurs authentiques
                    et ceux qui ne le sont pas.

    Exemple:
        >>> user_role = Roles.ADMIN
        >>> print(user_role)
        Roles.ADMIN
    """

    ADMIN = "ADMIN"
    USER = "USER"
    FAKE = "FAKE"
