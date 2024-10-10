# Dictionnaire `share_gain` :
#     Ce dictionnaire associe des niveaux (clés) à un pourcentage de gain (valeurs) correspondant.
#     Chaque clé représente un niveau (de 1 à 10) et chaque valeur représente la part de gain (en pourcentage) associée à ce niveau.
#
#     Clés :
#         1 à 10 : représentent différents niveaux d'un système hiérarchique de gains.
#
#     Valeurs :
#         0.40 à 0.01 : le pourcentage de gain associé au niveau correspondant. Le niveau 1 correspond à un gain de 40%,
#         et ainsi de suite jusqu'au niveau 10, qui correspond à un gain de 1%.
#
# Exemple d'utilisation :
#     Pour accéder au pourcentage de gain pour le niveau 3 :
#     ```
#     gain_niveau_3 = share_gain[3]
#     ```
share_gain = {
    1: 0.40,
    2: 0.20,
    3: 0.12,
    4: 0.07,
    5: 0.06,
    6: 0.05,
    7: 0.04,
    8: 0.03,
    9: 0.02,
    10: 0.01,
}
