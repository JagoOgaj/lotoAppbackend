from flask import jsonify, request, Blueprint
from app.extensions import db, pwd_context
from app.helpers import admin_role_required, send_email_to_users
from app.schemas import (
    UserLoginSchema,
    UserOverviewInfoSchema,
    UserUpdateSchema,
    UserPasswordUpdateSchema,
    LotteryCreateSchema,
    EntryOverviewSchema,
    EntryAdminAddUserSchema,
    LotteryUpdateSchema,
    UserCreateSchema,
)
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_jwt,
    get_jwt_identity,
)
from marshmallow import ValidationError
from app.models import User, Lottery, Entry, LotteryResult, LotteryRanking
from app.helpers import (
    add_token_to_database,
    revoke_token,
    generate_random_user,
    generate_wining_numbers,
    generate_luck_numbers,
    get_formatted_results,
)
from app.schemas import (
    LotteryOverviewSchema,
    LotteryRankingSchema,
    LotteryWinerSchema,
)
from app.tools import Status, email_sender_results_available, Roles
from datetime import datetime

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/login", methods=["POST"])
def login_admin():
    """
    Route d'authentification pour les administrateurs.

    Cette fonction permet à un utilisateur d'administrer de se connecter en fournissant un email et un mot de passe.
    Seuls les utilisateurs avec un rôle administrateur (identifiés par `_role_id=1`) sont autorisés à accéder à cette route.

    Processus :
    1. Récupère les données JSON de la requête.
    2. Valide et charge les données selon le schéma `UserLoginSchema`.
    3. Vérifie que l'utilisateur existe et qu'il a le rôle administrateur.
    4. Vérifie la validité du mot de passe avec le hash enregistré.
    5. Si toutes les conditions sont remplies, génère un `access_token` et un `refresh_token` pour l'utilisateur, et les enregistre dans la base de données.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 404 si l'utilisateur n'est pas trouvé,
    - 403 si l'utilisateur n'est pas administrateur,
    - 401 si le mot de passe est incorrect,
    - 400 en cas d'erreur de validation des champs ou autre exception.

    Retourne :
        - 201 avec les tokens (`access_token`, `refresh_token`) en cas de succès.
        - JSON avec les messages d'erreur et un code HTTP en cas d'échec.

    Exceptions :
        - `ValidationError` : Erreur dans la validation des champs du formulaire.
        - `Exception` : Autres erreurs capturées pendant l'exécution.

    """
    try:
        data = request.get_json()
        schama = UserLoginSchema()
        data = schama.load(data)

        email = data.get("email")
        password = data.get("password")

        userAdmin = User.query.filter_by(_email=email, _role_id=1).first()
        if not userAdmin:
            return jsonify({"message": "Aucun utilisateur trouvé", "errors": True}), 404
        if not userAdmin.is_admin:
            return (
                jsonify(
                    {
                        "message": "Accès refusé, utilisateur non administrateur",
                        "errors": True,
                    }
                ),
                403,
            )

        if not pwd_context.verify(password, userAdmin.password_hash):
            return (
                jsonify({"message": "Mot de passe incorrect", "errors": True}),
                401,
            )

        access_token = create_access_token(identity=userAdmin.id)
        refresh_token = create_refresh_token(identity=userAdmin.id)

        add_token_to_database(access_token)
        add_token_to_database(refresh_token)

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            201,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de validation des champs",
                    "details": err.messages,
                }
            ),
            400,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "message": str(e),
                    "errors": True,
                }
            ),
            400,
        )


@admin_bp.route("/create", methods=["GET"])
def create_admin():
    """
    Route de création d'un administrateur.

    Cette fonction permet de créer un nouvel utilisateur avec un rôle administrateur.
    Les données du nouvel administrateur sont reçues au format JSON et doivent être validées par le schéma `UserCreateSchema`.

    Processus :
    1. Récupère les données JSON de la requête.
    2. Valide et charge les données selon le schéma `UserCreateSchema`.
    3. Vérifie si l'email fourni existe déjà dans la base de données. Si c'est le cas, renvoie une erreur.
    4. Si l'email est unique, crée un nouvel utilisateur avec le rôle administrateur (`_role_id=1`), hache le mot de passe, et enregistre les informations dans la base de données.
    5. Enregistre le nouvel administrateur dans la base de données via `db.session.add()` et `db.session.commit()`.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 400 si l'email est déjà utilisé,
    - 400 en cas d'erreur de validation des champs ou autre exception.

    Retourne :
        - 201 avec un message de succès si l'utilisateur est créé.
        - JSON avec un message d'erreur et un code HTTP en cas d'échec.

    Exceptions :
        - `ValidationError` : Erreur dans la validation des champs du formulaire.
        - `Exception` : Autres erreurs capturées pendant l'exécution.

    """
    try:
        data = request.get_json()
        schema = UserCreateSchema()
        data = schema.load(data)

        if User.query.filter_by(_email=data["email"]).first():
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "L'email est déjà utilisé.",
                    }
                ),
                400,
            )

        newAdmin = User(
            _first_name=data["first_name"],
            _last_name=data["last_name"],
            _email=data["email"],
            _password_hash=pwd_context.hash(data["password"]),
            _role_id=1,
        )

        db.session.add(newAdmin)
        db.session.commit()

        return (jsonify({"messgae": "Utilisateyr creer"}), 201)

    except ValidationError as err:
        return jsonify({"message": "Une erreur est survenue", "details": err.messages})
    except Exception as e:
        return jsonify({"message": "une erreur est survenu", "details": str(e)})


@admin_bp.route("/account-info", methods=["GET"])
@jwt_required()
@admin_role_required
def account_info():
    try:
        userAdmin = get_current_user()

        if not userAdmin:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        userOverviewInfo = UserOverviewInfoSchema()
        userAdmin_data = userOverviewInfo.dump(userAdmin)
        return jsonify(userAdmin_data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de récupération des informations",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/update-info", methods=["PUT"])
@jwt_required()
@admin_role_required
def update_info():
    """
    Route pour récupérer les informations du compte administrateur.

    Cette fonction permet à un utilisateur administrateur d'accéder à ses informations de compte.
    Elle est protégée par deux décorateurs :
    - `@jwt_required()`: Nécessite une authentification JWT valide.
    - `@admin_role_required`: Nécessite que l'utilisateur soit un administrateur.

    Processus :
    1. Récupère l'utilisateur actuellement connecté via `get_current_user()`.
    2. Vérifie que l'utilisateur est bien un administrateur. Si aucun utilisateur n'est trouvé, renvoie une erreur 404.
    3. Sérialise les informations de l'utilisateur administrateur avec le schéma `UserOverviewInfoSchema`.
    4. Retourne les données sérialisées sous forme de JSON.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 404 si aucun utilisateur n'est trouvé.
    - 400 en cas d'erreur de validation des données.
    - 500 pour toute autre exception non prévue.

    Retourne :
        - 200 avec les informations de l'utilisateur administrateur en cas de succès.
        - JSON avec un message d'erreur et un code HTTP en cas d'échec.

    Exceptions :
        - `ValidationError` : Erreur dans la récupération ou la validation des informations de l'utilisateur.
        - `Exception` : Toute autre erreur rencontrée pendant l'exécution.
    """
    try:
        userAdmin = get_current_user()
        if not userAdmin:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        data = request.get_json()
        userUpdateInfoSchema = UserUpdateSchema()
        user_data = userUpdateInfoSchema.load(data)

        if "first_name" in user_data:
            userAdmin.first_name = user_data["first_name"]
        if "last_name" in user_data:
            userAdmin.last_name = user_data["last_name"]
        if "email" in user_data:
            userAdmin.email = user_data["email"]

        db.session.commit()
        return (
            jsonify({"message": "Vos informations ont été mises à jour avec succès."}),
            200,
        )
    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de mise à jours des informations",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/update-password", methods=["PUT"])
@jwt_required()
@admin_role_required
def update_password():
    """
    Route pour mettre à jour le mot de passe d'un administrateur.

    Cette fonction permet à un administrateur de mettre à jour son mot de passe.
    Elle est protégée par deux décorateurs :
    - `@jwt_required()`: Nécessite une authentification JWT valide.
    - `@admin_role_required`: Nécessite que l'utilisateur soit un administrateur.

    Processus :
    1. Récupère l'utilisateur actuellement connecté via `get_current_user()`.
    2. Vérifie que l'utilisateur existe. Si aucun utilisateur n'est trouvé, renvoie une erreur 404.
    3. Récupère les données JSON envoyées dans la requête et les valide via le schéma `UserPasswordUpdateSchema`.
    4. Vérifie si l'ancien mot de passe est correct. Si ce n'est pas le cas, renvoie une erreur 400.
    5. Vérifie que le nouveau mot de passe est différent de l'ancien. Si le nouveau mot de passe est le même que l'ancien, renvoie une erreur 400.
    6. Met à jour le hash du mot de passe de l'administrateur avec le nouveau mot de passe.
    7. Enregistre la mise à jour dans la base de données et renvoie un message de succès.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 404 si aucun utilisateur n'est trouvé.
    - 400 si l'ancien mot de passe est incorrect ou si le nouveau mot de passe est le même que l'ancien.
    - 400 en cas d'erreur de validation des données.
    - 500 pour toute autre exception non prévue.

    Retourne :
        - 200 avec un message de succès si le mot de passe est mis à jour.
        - JSON avec un message d'erreur et un code HTTP en cas d'échec.

    Exceptions :
        - `ValidationError` : Erreur de validation des données envoyées par l'utilisateur.
        - `Exception` : Toute autre erreur inattendue rencontrée pendant l'exécution.
    """
    try:
        userAdmin = get_current_user()

        if not userAdmin:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        data = request.get_json()
        userUpdatePassword = UserPasswordUpdateSchema()
        userAdmin_data = userUpdatePassword.load(data)
        if not pwd_context.verify(
            userAdmin_data["old_password"], userAdmin.password_hash
        ):
            return (
                jsonify(
                    {
                        "message": "L'ancien mot de passe est incorrect.",
                        "errors": True,
                    }
                ),
                400,
            )

        if pwd_context.verify(userAdmin_data["new_password"], userAdmin.password_hash):
            return (
                jsonify(
                    {
                        "message": "Le nouveau mot de passe doit être différent de l'ancien.",
                        "errors": True,
                    }
                ),
                400,
            )

        userAdmin.password_hash = userAdmin_data["new_password"]
        db.session.commit()
        return (
            jsonify({"message": "Votre mot de passe à été mises à jour avec succès."}),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de mise à jour de votre mot de passe",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/delete-lottery/<int:lottery_id>", methods=["DELETE"])
@jwt_required()
@admin_role_required
def delete_lottery(lottery_id):
    """
    Route pour supprimer une loterie et ses données associées.

    Cette fonction permet de supprimer une loterie, ainsi que tous les utilisateurs de rôle participant (rôle 3)
    et les entrées associées à cette loterie, ainsi que les résultats de la loterie s'ils existent.

    La route est protégée par deux décorateurs :
    - `@jwt_required()`: Nécessite une authentification JWT valide.
    - `@admin_role_required`: Nécessite que l'utilisateur soit un administrateur.

    Processus :
    1. Récupère la loterie à supprimer via l'ID fourni dans l'URL. Si aucune loterie n'est trouvée avec cet ID, renvoie une erreur 404.
    2. Récupère tous les utilisateurs ayant un rôle de participant (rôle 3) et qui ont des entrées pour cette loterie, et les supprime de la base de données.
    3. Supprime toutes les entrées liées à cette loterie de la base de données.
    4. Supprime les résultats de la loterie, s'ils existent.
    5. Supprime la loterie elle-même.
    6. Valide toutes les suppressions en effectuant des commits dans la base de données après chaque suppression.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 404 si aucune loterie n'est trouvée avec l'ID fourni.
    - 500 pour toute autre erreur rencontrée pendant le processus de suppression.

    Retourne :
        - 200 avec un message de succès si la suppression est effectuée avec succès.
        - JSON avec un message d'erreur et un code HTTP en cas d'échec.

    Exceptions :
        - `Exception` : Toute erreur inattendue rencontrée pendant l'exécution du processus de suppression.
    """
    try:
        lottery = Lottery.query.get(lottery_id)
        if not lottery:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "La loterie avec cet ID n'existe pas.",
                    }
                ),
                404,
            )
        users_to_delete = User.query.filter(
            User._role_id == 3, User.entries.any(lottery_id=lottery_id)
        ).all()

        for user in users_to_delete:
            db.session.delete(user)
            db.session.commit()

        entries = Entry.query.filter_by(lottery_id=lottery_id).all()

        for entry in entries:
            db.session.delete(entry)
            db.session.commit()

        lottery_result = LotteryResult.query.filter_by(
            lottery_id=lottery_id
        ).one_or_none()
        if lottery_result:
            db.session.delete(lottery_result)
            db.session.commit()

        db.session.delete(lottery)
        db.session.commit()

        return (
            jsonify({"message": "La loterie a été supprimée avec succès."}),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue lors de la suppression de la loterie.",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/create-lottery", methods=["POST"])
@jwt_required()
@admin_role_required
def lottery_create():
    """
    Route pour créer une nouvelle loterie.

    Cette fonction permet à un administrateur de créer un nouveau tirage de loterie.
    La création d'un nouveau tirage est soumise à des règles de validation, telles que l'absence d'un autre tirage en cours
    et la validation des dates de début et de fin.

    Processus :
    1. Récupère les données JSON envoyées dans la requête et les valide avec `LotteryCreateSchema`.
    2. Vérifie s'il existe déjà une loterie en cours (statut "EN_COUR"). Si une loterie est active, aucune nouvelle loterie ne peut être créée tant que celle-ci n'est pas terminée, sauf si le nouveau tirage est de type "SIMULATION".
    3. Valide les dates de début et de fin. La date de fin ne peut pas être antérieure ou égale à la date de début, et la date de début ne peut pas être dans le passé.
    4. Si le statut est "SIMULATION", la loterie est créée sans dates de début et de fin, sinon, les dates sont obligatoires.
    5. Enregistre la nouvelle loterie dans la base de données.
    6. Envoie un email aux utilisateurs pour les informer de la création du tirage.
    7. Valide et sauvegarde les modifications dans la base de données.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 400 si les données sont invalides ou si un tirage est déjà en cours.
    - 500 pour toute autre exception non prévue.

    Retourne :
        - 201 avec un message de succès si le tirage est créé.
        - JSON avec un message d'erreur et un code HTTP en cas d'échec.

    Exceptions :
        - `ValidationError` : Erreur dans la validation des données envoyées pour la création du tirage.
        - `Exception` : Toute autre erreur inattendue rencontrée pendant le processus de création.
    """
    try:
        data = request.get_json()
        lotteryCreateSchema = LotteryCreateSchema()
        data = lotteryCreateSchema.load(data)
        existing_lottery = Lottery.query.filter_by(_status=Status.EN_COUR.value).first()
        if existing_lottery:
            if data["status"] not in [
                Status.SIMULATION.value,
                Status.SIMULATION_TERMINE.value,
            ]:
                return (
                    jsonify(
                        {
                            "errors": True,
                            "message": "Un tirage est déjà en cours. Veuillez terminer celui-ci avant d'en créer un nouveau.",
                            "details": {
                                "status": [
                                    "Un tirage est déjà en cours. Veuillez terminer celui-ci avant d'en créer un nouveau."
                                ]
                            },
                        }
                    ),
                    400,
                )
        if "start_date" in data and "end_date" in data:
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
            if start_date >= end_date:
                raise ValidationError(
                    "La date de fin ne peux pas etre inferieur ou egal à la date de debut"
                )
            if start_date < datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ):
                raise ValidationError("Le debut doit commencer à partir de aujourd'hui")

        if data["status"] == Status.SIMULATION.value:
            new_lottery = Lottery(
                _name=data["name"],
                _start_date=None,
                _end_date=None,
                _status=data["status"],
                _reward_price=data["reward_price"],
                _max_participants=data["max_participants"],
            )
        else:
            start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
            new_lottery = Lottery(
                _name=data["name"],
                _start_date=start_date,
                _end_date=end_date,
                _status=data["status"],
                _reward_price=data["reward_price"],
                _max_participants=data["max_participants"],
            )
        if data["status"] not in [
            Status.SIMULATION.value,
            Status.SIMULATION_TERMINE.value,
        ]:
            send_email_to_users()
        db.session.add(new_lottery)
        db.session.commit()
        return (
            jsonify({"message": "Le tirage a été créé avec succès."}),
            201,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": err.messages[0],
                    "details": err.messages,
                }
            ),
            400,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/update-lottery/<int:lottery_id>", methods=["PUT"])
@jwt_required()
@admin_role_required
def update_lottery(lottery_id):
    """
    Route pour mettre à jour les informations d'une loterie existante.

    Cette fonction permet à un administrateur de modifier les détails d'une loterie spécifiée par son ID.
    Les mises à jour peuvent inclure le nom, les dates de début et de fin, le statut, le nombre maximum de participants
    et le prix de récompense.

    Paramètres :
        lottery_id (int) : L'ID de la loterie à mettre à jour. Ce paramètre est requis et doit être un entier.

    Processus :
    1. Récupère la loterie à mettre à jour à partir de l'ID fourni. Si la loterie n'est pas trouvée, renvoie une erreur 404.
    2. Récupère les données JSON envoyées dans la requête et les valide avec `LotteryUpdateSchema`.
    3. Si un nouveau nom est fourni, met à jour le nom de la loterie.
    4. Vérifie et met à jour les dates de début et de fin, avec plusieurs validations :
        - La date de fin ne doit pas être antérieure ou égale à la date de début.
        - La nouvelle date de début ne doit pas être antérieure à l'ancienne date de début.
        - La date de début ne doit pas être supérieure ou égale à la date de fin.
    5. Met à jour le statut de la loterie si un nouveau statut est fourni.
    6. Met à jour le nombre maximum de participants et le prix de récompense si ces valeurs sont fournies.
    7. Valide et sauvegarde les modifications dans la base de données.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 404 si la loterie n'est pas trouvée ou si les données envoyées sont invalides.
    - 400 pour les erreurs de validation des données.
    - 500 pour toute autre exception non prévue.

    Retourne :
        - 200 avec un message de succès si les informations de la loterie ont été mises à jour.
        - JSON avec un message d'erreur et un code HTTP en cas d'échec.

    Exceptions :
        - `ValidationError` : Erreur dans la validation des données envoyées pour la mise à jour.
        - `Exception` : Toute autre erreur inattendue rencontrée pendant le processus de mise à jour.
    """
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()
        if lottery is None:
            return (
                jsonify({"errors": True, "message": "Loterie non trouvée."}),
                404,
            )

        data = request.get_json()
        lotteryUpdateSchema = LotteryUpdateSchema()
        lottery_data = lotteryUpdateSchema.load(data)

        if "name" in lottery_data:
            lottery.name = lottery_data["name"]
        # Vérification des dates
        if "start_date" in lottery_data and "end_date" in lottery_data:
            start_date = datetime.strptime(lottery_data["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(lottery_data["end_date"], "%Y-%m-%d")

            if end_date <= start_date:
                return (
                    jsonify(
                        {
                            "message": "La date de fin ne doit pas etre inferieur ou egal a la date de debut du tirage",
                            "errors": True,
                            "details": {
                                "end_date": [
                                    "La date de fin ne doit pas etre inferieur ou egal a la date de debut du tirage"
                                ]
                            },
                        }
                    ),
                    404,
                )

            if start_date < lottery.start_date:
                return (
                    jsonify(
                        {
                            "message": "La nouvelle date de debut ne doit pas etre inferieur a l'ancienne",
                            "errors": True,
                            "details": {
                                "start_date": [
                                    "La nouvelle date de debut ne doit pas etre inferieur a l'ancienne"
                                ]
                            },
                        }
                    ),
                    404,
                )

            lottery.start_date = start_date
            lottery.end_date = end_date

        elif "start_date" in lottery_data:
            start_date = datetime.strptime(lottery_data["start_date"], "%Y-%m-%d")

            if start_date < lottery.start_date:
                return (
                    jsonify(
                        {
                            "message": "La nouvelle date de debut ne doit pas etre inferieur a l'ancienne",
                            "errors": True,
                            "details": {
                                "start_date": [
                                    "La nouvelle date de debut ne doit pas etre inferieur a l'ancienne"
                                ]
                            },
                        }
                    ),
                    404,
                )

            if start_date >= lottery.end_date:
                return (
                    jsonify(
                        {
                            "message": "La nouvelle date de debut ne doit pas etre superieur ou egal a la date de fin",
                            "errors": True,
                            "details": {
                                "start_date": [
                                    "La nouvelle date de debut ne doit pas etre superieur ou egal a la date de fin"
                                ]
                            },
                        }
                    ),
                    404,
                )

            lottery.start_date = start_date

        elif "end_date" in lottery_data:
            end_date = datetime.strptime(lottery_data["end_date"], "%Y-%m-%d")

            if end_date <= lottery.start_date:
                return (
                    jsonify(
                        {
                            "message": "La date de fin ne doit pas etre inferieur ou egal a la date de debut du tirage",
                            "errors": True,
                            "details": {
                                "end_date": [
                                    "La date de fin ne doit pas etre inferieur ou egal a la date de debut du tirage"
                                ]
                            },
                        }
                    ),
                    404,
                )

            if end_date < lottery.end_date:
                return (
                    jsonify(
                        {
                            "message": "La nouvelle date de fin ne doit pas etre inferieur a l'ancienne",
                            "errors": True,
                            "details": {
                                "end_date": [
                                    "La nouvelle date de fin ne doit pas etre inferieur a l'ancienne"
                                ]
                            },
                        }
                    ),
                    404,
                )

            lottery.end_date = end_date

            lottery.end_date = end_date
        if "status" in lottery_data:
            lottery.status = lottery_data["status"]
        if "max_participants" in lottery_data:
            lottery.max_participants = lottery_data["max_participants"]
        if "reward_price" in lottery_data:
            lottery.reward_price = lottery_data["reward_price"]

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Les informations du tirage ont été mises à jour avec succès."
                }
            ),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de récupération de l'historique",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/lottery-list", methods=["GET"])
@jwt_required()
@admin_role_required
def lottery_list():
    """
    Route pour récupérer la liste de toutes les loteries existantes.

    Cette fonction permet à un administrateur de récupérer toutes les loteries enregistrées dans le système.
    Elle met également à jour le statut des loteries qui ont atteint leur date de fin et ne sont pas encore terminées
    ou en simulation.

    Processus :
    1. Récupère toutes les loteries à partir de la base de données.
    2. Pour chaque loterie, vérifie si le statut est différent de `TERMINE`, `SIMULATION`, ou `SIMULATION_TERMINE`.
       - Si la date actuelle est supérieure ou égale à la date de fin de la loterie, le statut de la loterie est mis à jour à `EN_VALIDATION`.
    3. Utilise `LotteryOverviewSchema` pour sérialiser les données des loteries.
    4. Renvoie la liste des loteries avec un message de succès.

    En cas d'erreur, renvoie un message approprié avec le code HTTP correspondant :
    - 400 pour les erreurs de validation lors de la récupération des loteries.
    - 500 pour toute autre exception non prévue.

    Retourne :
        - 200 avec un message de succès et la liste des tirages.

    Exceptions :
        - `ValidationError` : Erreur dans la validation des données lors de la récupération des loteries.
        - `Exception` : Toute autre erreur inattendue rencontrée pendant le processus de récupération.
    """
    try:
        lotteries = Lottery.query.all()
        current_date = datetime.utcnow()
        for lottery in lotteries:
            if lottery.status not in [
                Status.TERMINE.value,
                Status.SIMULATION.value,
                Status.SIMULATION_TERMINE.value,
            ]:
                if current_date >= lottery.end_date:
                    lottery.status = Status.EN_VALIDATION.value
                    db.session.commit()

        lotteryListSchema = LotteryOverviewSchema(many=True)
        result = lotteryListSchema.dump(lotteries)
        return (
            jsonify(
                {
                    "message": "Liste des tirages récupérée avec succès.",
                    "data": result,
                }
            ),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur dans la récupération de toute les tirages",
                    "details": err.messages,
                }
            ),
            400,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/lottery-details/<int:lottery_id>", methods=["GET"])
@jwt_required()
@admin_role_required
def lottery_details(lottery_id):
    """
    Récupère les détails d'une loterie à partir de son identifiant.

    Cette méthode permet de récupérer les informations d'une loterie spécifique,
    y compris son statut, ainsi que les numéros gagnants et les numéros chanceux associés.
    Si la loterie n'est pas trouvée, ou si une erreur se produit lors de la récupération des données,
    un message d'erreur approprié est renvoyé.

    Args:
        lottery_id (int): L'identifiant unique de la loterie pour laquelle les détails sont demandés.

    Returns:
        tuple: Un tuple contenant un objet JSON avec les détails de la loterie,
               ainsi qu'un code de statut HTTP.
               - En cas de succès (200):
                   - 'message': Un message confirmant la récupération des détails de la loterie.
                   - 'data': Les détails de la loterie sous forme de dictionnaire.
                   - 'numbers': Un dictionnaire contenant les numéros gagnants et les numéros chanceux.
               - En cas d'erreur (404, 400 ou 500):
                   - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                   - 'message': Un message décrivant l'erreur.
                   - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        ValidationError: Si une erreur de validation se produit lors de la récupération des détails de la loterie.
        Exception: Pour toute autre erreur inattendue.
    """
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()
        if lottery is None:
            return (
                jsonify({"errors": True, "message": "Loterie non trouvée."}),
                404,
            )
        if lottery.status not in [
            Status.TERMINE.value,
            Status.SIMULATION.value,
            Status.SIMULATION_TERMINE.value,
        ]:
            current_date = datetime.utcnow()
            if current_date >= lottery.end_date:
                lottery.status = Status.EN_VALIDATION.value
                db.session.commit()

        lotteryOverviewschema = LotteryOverviewSchema()
        result = lotteryOverviewschema.dump(lottery)
        lottery_result = LotteryResult.query.filter_by(
            lottery_id=lottery_id
        ).one_or_none()
        winning_numbers = ""
        lucky_numbers = ""
        if lottery_result:
            winning_numbers = lottery_result.winning_numbers
            lucky_numbers = lottery_result.winning_lucky_numbers
        return (
            jsonify(
                {
                    "message": "Details du tirage",
                    "data": result,
                    "numbers": {
                        "winning_numbers": winning_numbers,
                        "lucky_numbers": lucky_numbers,
                    },
                }
            ),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de récupération de l'historique",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/participants-list/<int:lottery_id>", methods=["GET"])
@jwt_required()
@admin_role_required
def participants_list(lottery_id):
    """
    Récupère la liste des participants d'une loterie spécifiée.

    Cette méthode permet de récupérer tous les participants inscrits à une loterie
    donnée en fonction de son identifiant. Si la loterie n'est pas trouvée, une erreur 404
    est renvoyée. Les informations des participants sont retournées sous forme de liste.

    Args:
        lottery_id (int): L'identifiant unique de la loterie pour laquelle on souhaite obtenir la liste des participants.

    Returns:
        tuple: Un tuple contenant un objet JSON avec la liste des participants et un code de statut HTTP.
               - En cas de succès (200):
                   - 'message': Un message confirmant la récupération réussie de la liste des participants.
                   - 'data': Une liste d'objets représentant les participants de la loterie.
               - En cas d'erreur (400 ou 500):
                   - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                   - 'message': Un message décrivant l'erreur.
                   - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        ValidationError: Si une erreur de validation se produit lors de la récupération des participants.
        Exception: Pour toute autre erreur inattendue.
    """
    try:
        lottery = Lottery.query.get_or_404(lottery_id)
        participants = Entry.query.filter_by(lottery_id=lottery.id).all()

        entry_schema = EntryOverviewSchema(many=True)
        result = entry_schema.dump(participants)

        return (
            jsonify(
                {
                    "message": "Liste des participants récupérée avec succès.",
                    "data": result,
                }
            ),
            200,
        )
    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de récupération des participants",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue lors de la récupération des participants.",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/lottery-rank/<int:lottery_id>", methods=["GET"])
@jwt_required()
@admin_role_required
def lottery_rank(lottery_id):
    """
    Récupère le classement des participants pour un tirage de loterie spécifique.

    Cette méthode permet de récupérer les résultats et le classement des participants
    pour un tirage de loterie donné. Si la loterie ou les résultats ne sont pas trouvés,
    des messages d'erreur appropriés sont renvoyés.

    Args:
        lottery_id (int): L'identifiant unique du tirage de loterie pour lequel le classement est demandé.

    Returns:
        tuple: Un tuple contenant un objet JSON avec les classements des participants
               et un code de statut HTTP.
               - En cas de succès (200):
                   - 'message': Un message confirmant la récupération réussie des classements.
                   - 'data': Une liste d'objets représentant les classements des participants.
               - En cas d'erreur (404 ou 500):
                   - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                   - 'message': Un message décrivant l'erreur.
                   - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait se produire lors de la récupération des résultats ou des classements.
    """
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()

        if not lottery:
            return (
                jsonify({"errors": True, "message": "Lottery draw not found."}),
                404,
            )

        lottery_result = LotteryResult.query.filter_by(lottery_id=lottery_id).first()

        if lottery_result is None:
            return jsonify({"message": "Aucun résultat pour se tirage"})

        rankings = (
            db.session.query(LotteryRanking)
            .filter_by(lottery_result_id=lottery_result.id)
            .all()
        )

        if not rankings:
            return (
                jsonify(
                    {
                        "message": "No rankings found for this draw.",
                        "errors": True,
                    }
                ),
                404,
            )
        schema = LotteryWinerSchema(many=True)
        results = []
        for ranking in rankings:
            user = db.session.query(User).filter_by(id=ranking.player_id).one_or_none()
            if user is None:
                name = "Inconnu"
            name = user.full_name
            results.append(
                {
                    "name": name,
                    "rank": ranking.rank,
                    "score": ranking.score,
                    "winnings": ranking.winnings,
                }
            )

        validated_results = schema.dump(results)

        return jsonify(
            {
                "message": "Rankings retrieved successfully",
                "data": validated_results,
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "An error occurred during the draw validation.",
                    "details": str(e),
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreurs est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/manage-participants/remove", methods=["DELETE"])
@jwt_required()
@admin_role_required
def manage_participants_remove():
    """
    Supprime la participation d'un utilisateur à un tirage de loterie.

    Cette méthode permet de retirer un utilisateur de la liste des participants d'un tirage de loterie.
    Elle vérifie d'abord si le tirage est encore actif avant d'effectuer la suppression.
    Si l'utilisateur est trouvé, sa participation ainsi que les résultats associés sont supprimés.

    Returns:
        tuple: Un tuple contenant un objet JSON avec un message de confirmation
               et un code de statut HTTP.
               - En cas de succès (200):
                   - 'message': Un message confirmant la suppression réussie de la participation.
               - En cas d'erreur (400, 403 ou 404):
                   - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                   - 'message': Un message décrivant l'erreur.
               - En cas d'erreur inattendue (500):
                   - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait se produire lors de la suppression.
    """
    try:
        data = request.get_json()

        lottery_id = data.get("lottery_id")
        if not lottery_id:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "L'ID du tirage est requis.",
                    }
                ),
                400,
            )

        lottery = Lottery.query.get_or_404(lottery_id)
        if lottery.status in [Status.TERMINE.value, Status.SIMULATION_TERMINE.value]:
            return (
                jsonify(
                    {
                        "message": "Le tirage est déjà terminé.",
                        "errors": True,
                    }
                ),
                403,
            )

        user_id = data.get("user_id")

        entry = Entry.query.filter_by(user_id=user_id, lottery_id=lottery_id).first()
        if not entry:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "Aucune participation trouvée pour cet utilisateur dans ce tirage.",
                    }
                ),
                404,
            )

        user = User.query.filter_by(id=user_id, _role_id=3).one_or_none()
        if user:
            db.session.delete(user)
            db.session.commit()

        lottery_result = LotteryResult.query.filter_by(lottery_id=lottery_id).first()
        if lottery_result:
            db.session.delete(lottery_result)
            db.session.commit()

        db.session.delete(entry)
        db.session.commit()

        return (
            jsonify({"message": "Participation supprimée avec succès."}),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/manage-participants/add/<int:lottery_id>", methods=["PUT"])
@jwt_required()
@admin_role_required
def manage_particiants_add(lottery_id):
    """
    Ajoute un participant à un tirage de loterie.

    Cette méthode permet d'ajouter un nouvel utilisateur en tant que participant à un tirage de loterie spécifique.
    Elle vérifie d'abord si le tirage est actif et si l'utilisateur n'est pas déjà inscrit.
    Si l'utilisateur n'existe pas, il sera créé, et sa participation sera enregistrée.

    Args:
        lottery_id (int): L'identifiant unique du tirage de loterie auquel le participant doit être ajouté.

    Returns:
        tuple: Un tuple contenant un objet JSON avec un message de confirmation
               et un code de statut HTTP.
               - En cas de succès (201):
                   - 'message': Un message confirmant l'ajout réussi du participant.
                   - 'entry_id': L'identifiant de l'entrée du participant.
               - En cas d'erreur (403, 400 ou 404):
                   - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                   - 'message': Un message décrivant l'erreur.
                   - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        ValidationError: En cas d'erreur de validation des données entrantes.
        Exception: Pour toute erreur inattendue qui pourrait se produire lors de l'ajout du participant.
    """
    try:
        data = request.get_json()
        entryAdminAddUserSchema = EntryAdminAddUserSchema()
        entry_data = entryAdminAddUserSchema.load(data)

        lottery = Lottery.query.get_or_404(lottery_id)
        if lottery.status in [Status.TERMINE.value, Status.SIMULATION_TERMINE.value]:
            return (
                jsonify(
                    {
                        "message": "Le tirage est déjà terminé.",
                        "errors": True,
                    }
                ),
                403,
            )
        user = User.query.filter_by(
            _email=entry_data["user"]["email"], _role_id=2
        ).one_or_none()
        if user:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "Il existe un utilisateur avec cette email",
                        "details": {
                            "email": ["Il existe un utilisateur avec cette email"]
                        },
                    }
                ),
                404,
            )
        new_user = User(
            _first_name=entry_data["user"]["full_name"],
            _last_name="fake",
            _email=entry_data["user"]["email"],
            _password_hash=pwd_context.hash("123"),
            _role_id=3,
        )

        db.session.add(new_user)
        db.session.commit()

        existing_entry = Entry.query.filter_by(
            user_id=new_user.id, lottery_id=lottery.id
        ).first()
        if existing_entry:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "L'utilisateur est déjà inscrit à ce tirage.",
                    }
                ),
                400,
            )

        new_entry = Entry(
            user_id=new_user.id,
            lottery_id=lottery.id,
            numbers=entry_data["numbers"],
            lucky_numbers=entry_data["numbers_lucky"],
        )

        db.session.add(new_entry)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Participant ajouté avec succès.",
                    "entry_id": new_entry.id,
                }
            ),
            201,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur d'enregistrement",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/lottery/validate/<int:lottery_id>", methods=["POST"])
@jwt_required()
@admin_role_required
def validate_lottery(lottery_id):
    """
    Valide un tirage de loterie et génère les résultats.

    Cette méthode permet de valider un tirage de loterie en vérifiant les numéros gagnants et les numéros chanceux fournis.
    Si les numéros ne sont pas fournis, des numéros aléatoires sont générés.
    La méthode met également à jour le statut de la loterie et enregistre les résultats des participants.

    Args:
        lottery_id (int): L'identifiant unique du tirage de loterie à valider.

    Returns:
        tuple: Un tuple contenant un objet JSON avec un message de confirmation et un code de statut HTTP.
            - En cas de succès (200):
                - 'message': Un message confirmant que la génération des résultats a réussi.
            - En cas d'erreur (400 ou 404):
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'message': Un message décrivant l'erreur.
                - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait se produire lors de la validation du tirage.
    """
    try:
        data = request.get_json()
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()

        if not lottery:
            return (
                jsonify({"errors": True, "message": "Lottery draw not found."}),
                404,
            )

        if (
            lottery.status == Status.EN_VALIDATION.value
            or lottery.status == Status.SIMULATION.value
        ):
            winning_numbers = ""
            lucky_numbers = ""
            if data["lucky_numbers"] != "" and data["winning_numbers"] != "":
                winning_numbers_list = [
                    int(num)
                    for num in data["winning_numbers"].split(",")
                    if num.isdigit()
                ]
                lucky_numbers_list = [
                    int(num)
                    for num in data["lucky_numbers"].split(",")
                    if num.isdigit()
                ]

                if len(winning_numbers_list) != 5:
                    return (
                        jsonify(
                            {
                                "message": "Il doit y avoir exactement 5 numéros gagnants.",
                                "errors": True,
                                "details": {
                                    "winning_numbers": [
                                        "Il doit y avoir exactement 5 numéros gagnants."
                                    ]
                                },
                            }
                        ),
                        404,
                    )
                if len(lucky_numbers_list) != 2:
                    return (
                        jsonify(
                            {
                                "message": "Il doit y avoir exactement 2 numéros chanceux.",
                                "errors": True,
                                "details": {
                                    "lucky_numbers": [
                                        "Il doit y avoir exactement 2 numéros chanceux."
                                    ]
                                },
                            }
                        ),
                        404,
                    )

                if not all(1 <= num <= 49 for num in winning_numbers_list):
                    return (
                        jsonify(
                            {
                                "message": "Les numéros gagnants doivent être entre 1 et 49.",
                                "errors": True,
                                "details": {
                                    "winning_numbers": [
                                        "Les numéros gagnants doivent être entre 1 et 49."
                                    ]
                                },
                            }
                        ),
                        404,
                    )
                if not all(1 <= num <= 9 for num in lucky_numbers_list):
                    return jsonify(
                        {
                            "message": "Les numéros chanceux doivent être entre 1 et 9.",
                            "errors": True,
                            "details": {
                                "lucky_numbers": [
                                    "Les numéros chanceux doivent être entre 1 et 9."
                                ]
                            },
                        }
                    )

                if len(set(winning_numbers_list)) != 5:
                    return (
                        jsonify(
                            {
                                "message": "Les numéros gagnants ne doivent pas contenir de doublons.",
                                "errors": True,
                                "details": {
                                    "winning_numbers": [
                                        "Les numéros gagnants ne doivent pas contenir de doublons."
                                    ]
                                },
                            }
                        ),
                        404,
                    )
                if len(set(lucky_numbers_list)) != 2:
                    return (
                        jsonify(
                            {
                                "message": "Les numéros chanceux ne doivent pas contenir de doublons.",
                                "errors": True,
                                "details": {
                                    "lucky_numbers": [
                                        "Les numéros chanceux ne doivent pas contenir de doublons."
                                    ]
                                },
                            }
                        ),
                        404,
                    )
                winning_numbers = data["winning_numbers"]
                lucky_numbers = data["lucky_numbers"]
            else:
                winning_numbers = ",".join(map(str, generate_wining_numbers()))
                lucky_numbers = ",".join(map(str, generate_luck_numbers()))

            lottery_result = LotteryResult(
                lottery_id=lottery_id,
                winning_numbers=winning_numbers,
                winning_lucky_numbers=lucky_numbers,
            )

            db.session.add(lottery_result)
            db.session.commit()

            if lottery.status == Status.EN_VALIDATION.value:
                lottery.status = Status.TERMINE.value
            elif lottery.status == Status.SIMULATION.value:
                lottery.status = Status.SIMULATION_TERMINE.value

            lottery_result = (
                db.session.query(LotteryResult).filter_by(lottery_id=lottery_id).first()
            )

            draw_numbers = set(map(int, lottery_result.winning_numbers.split(",")))
            draw_stars = set(map(int, lottery_result.winning_lucky_numbers.split(",")))

            participants = (
                db.session.query(Entry).filter_by(lottery_id=lottery_id).all()
            )

            if not participants:
                return (
                    jsonify(
                        {
                            "message": "Pas de participants pour se tirage",
                            "errors": True,
                        }
                    ),
                    404,
                )

            lottery = db.session.query(Lottery).filter_by(id=lottery_id).first()
            reward_price = lottery.reward_price

            formatted_results = get_formatted_results(
                participants, draw_numbers, draw_stars, reward_price, db
            )

            players_ids = []
            for result in formatted_results:
                players_ids.append(result["player_id"])
                schema = LotteryRankingSchema()
                ranking_data = schema.load(
                    {
                        "lottery_result_id": lottery_result.id,
                        "player_id": result["player_id"],
                        "rank": result["rank"],
                        "score": result["score"],
                        "winnings": result["winnings"],
                    }
                )

                new_ranking = LotteryRanking(**ranking_data)
                db.session.add(new_ranking)
                db.session.commit()

            for player_id in players_ids:
                user = User.query.filter_by(id=player_id).one_or_none()
                if user and user.role_name == Roles.USER.value:
                    email_sender_results_available(user.email, lottery.name)

            return jsonify({"message": "La generation des résultats est resussi"}), 200

        else:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "The draw must have a status of 'EN_VALIDATION' or 'SIMULATION' to be validated.",
                    }
                ),
                400,
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "An error occurred during the draw validation.",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/lottery/results/<int:lottery_id>", methods=["GET"])
@jwt_required()
@admin_role_required
def get_lottery_results(lottery_id):
    """
    Récupère les résultats d'un tirage de loterie spécifié.

    Cette méthode permet d'obtenir les numéros gagnants et les numéros chanceux d'un tirage de loterie spécifique en fonction de son identifiant.
    Elle vérifie d'abord l'existence de la loterie, puis des résultats associés avant de renvoyer les informations demandées.

    Args:
        lottery_id (int): L'identifiant unique du tirage de loterie dont on souhaite récupérer les résultats.

    Returns:
        tuple: Un tuple contenant un objet JSON avec les détails du tirage de loterie et un code de statut HTTP.
            - En cas de succès (200):
                - 'lottery_name': Le nom du tirage de loterie.
                - 'winning_numbers': Les numéros gagnants du tirage.
                - 'lucky_numbers': Les numéros chanceux du tirage.
            - En cas d'erreur (404):
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'message': Un message décrivant l'erreur.
            - En cas d'erreur inattendue (500):
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'message': Un message indiquant qu'une erreur s'est produite lors de la récupération des résultats.
                - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait survenir lors de la récupération des résultats.
    """
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()

        if not lottery:
            return (
                jsonify({"errors": True, "message": "Tirage non trouvé."}),
                404,
            )

        lottery_result = LotteryResult.query.filter_by(
            lottery_id=lottery_id
        ).one_or_none()

        if not lottery_result:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "Aucun résultat trouvé pour ce tirage.",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "lottery_name": lottery.name,
                    "winning_numbers": lottery_result.winning_numbers,
                    "lucky_numbers": lottery_result.winning_lucky_numbers,
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue lors de la récupération des résultats du tirage.",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/populate-fake-users/<int:lottery_id>", methods=["POST"])
@jwt_required()
@admin_role_required
def populate_fake_users(lottery_id):
    """
    Remplit la loterie spécifiée avec des utilisateurs fictifs.

    Cette méthode permet d'ajouter des participants fictifs à un tirage de loterie spécifique en fonction de son identifiant.
    Les utilisateurs fictifs sont générés aléatoirement et ajoutés tant que le nombre maximal de participants n'est pas atteint.

    Args:
        lottery_id (int): L'identifiant unique du tirage de loterie auquel ajouter des utilisateurs fictifs.

    Returns:
        tuple: Un tuple contenant un objet JSON avec un message de confirmation et un code de statut HTTP.
            - En cas de succès (201):
                - 'message': Un message indiquant que les participants fictifs ont été ajoutés.
                - 'total_participants': Le nombre total de participants après ajout.
            - En cas d'erreur (400):
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'message': Un message décrivant l'erreur (si le tirage n'est ni en simulation ni en cours).
            - En cas d'erreur inattendue (500):
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'message': Un message indiquant qu'une erreur s'est produite lors de la génération des utilisateurs fictifs.
                - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait survenir lors de l'ajout des utilisateurs fictifs.
    """
    try:
        lottery = Lottery.query.get_or_404(lottery_id)

        if lottery.status not in [Status.SIMULATION.value, Status.EN_COUR.value]:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "Ce tirage n'est ni en simulation ni en cours.",
                    }
                ),
                400,
            )
        i = 0
        while i <= (lottery.max_participants - lottery.participant_count):
            (
                fake_name,
                fake_email,
                numbers,
                lucky_numbers,
            ) = generate_random_user()

            new_user = User(
                _first_name=fake_name,
                _last_name="fake",
                _email=fake_email,
                _password_hash=pwd_context.hash("123"),
                _role_id=3,
            )

            db.session.add(new_user)
            db.session.commit()

            existing_entry = Entry.query.filter_by(
                user_id=new_user.id, lottery_id=lottery_id
            ).first()
            if existing_entry:
                continue

            new_entry = Entry(
                user_id=new_user.id,
                lottery_id=lottery_id,
                numbers=numbers,
                lucky_numbers=lucky_numbers,
            )

            db.session.add(new_entry)
            i += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Participants fictifs ajoutés aléatoirement.",
                    "total_participants": lottery.participant_count,
                }
            ),
            201,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue lors de la génération d'utilisateurs fictifs.",
                    "details": str(e),
                }
            ),
            500,
        )


@admin_bp.route("/logout", methods=["POST"])
@jwt_required()
@admin_role_required
def logout_admin():
    """
    Déconnexion de l'administrateur.

    Cette méthode permet à un administrateur de se déconnecter en révoquant le jeton JWT associé à la session en cours.
    Une fois le jeton révoqué, l'administrateur ne pourra plus accéder aux ressources protégées sans se reconnecter.

    Returns:
        tuple: Un tuple contenant un objet JSON avec un message de confirmation et un code de statut HTTP.
            - En cas de succès (200):
                - 'message': Un message indiquant que la déconnexion a été effectuée avec succès.
            - En cas d'erreur inattendue (500):
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'message': Un message indiquant qu'une erreur est survenue lors de la déconnexion.
                - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait survenir lors de la déconnexion.
    """
    try:
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        revoke_token(jti, user_id)
        return jsonify({"message": "Déconnexion réussie."}), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )
