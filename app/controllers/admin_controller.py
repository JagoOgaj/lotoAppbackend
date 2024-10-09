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
    try:
        data = request.get_json()
        lotteryCreateSchema = LotteryCreateSchema()
        data = lotteryCreateSchema.load(data)
        existing_lottery = Lottery.query.filter_by(status=Status.EN_COUR.value).first()
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
            if start_date < datetime.now():
                raise ValidationError("Le debut doit commencer à partir de demain")

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
                    "message": "Erreur dans la création du tirage",
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
        raise Exception("Pas de resultats trouver")
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

            # Update lottery status
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
                        "player_id": result[
                            "player_id"
                        ],  # Player ID must be part of formatted_results
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
