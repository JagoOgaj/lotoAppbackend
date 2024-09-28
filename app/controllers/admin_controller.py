# app/controllers/admin_controller.py
from flask import jsonify, request, Blueprint
from app.extensions import db, pwd_context
from app.helpers import admin_role_required
from app.schemas import UserLoginSchema, UserOverviewInfoSchema, UserUpdateSchema, UserPasswordUpdateSchema, LotteryCreateSchema, LotteryListSchema, EntryOverviewSchema, EntryAdminAddUserSchema
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_current_user, get_jwt, get_jwt_identity
from marshmallow import ValidationError
from app.models import User, Lottery, Entry
from app.helpers import add_token_to_database, revoke_token
from app.schemas.lottery_schemas import LotteryOverviewSchema
from app.tools import Status

admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/login', methods=['POST'])
@jwt_required()
@admin_role_required
def login_admin():
    try:
        data = request.get_json()
        schama = UserLoginSchema()
        data = schama.load(data)

        email = data.get('email')
        password = data.get('password')

        userAdmin = User.query.filter_by(_email=email).first()
        if not userAdmin:
            return jsonify({"errors": "Aucun utilisateur trouvé"}), 404

        if not pwd_context.verify(password, userAdmin.password_hash):
            return jsonify({"message": "Mot de passe incorrect", "errors": True}), 401

        access_token = create_access_token(identity=userAdmin.id)
        refresh_token = create_refresh_token(identity=userAdmin.id)

        add_token_to_database(access_token)
        add_token_to_database(refresh_token)

        return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 201

    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur de validation des champs",
            "details": err.messages
        }), 400

    except Exception as e:
        return jsonify({"message": str(e), "errors": True, }), 400


@admin_bp.route('/account-info', methods=['GET'])
@jwt_required()
@admin_role_required
def account_info():
    try:
        userAdmin = get_current_user()

        if not userAdmin:
            return jsonify({'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        userOverviewInfo = UserOverviewInfoSchema()
        userAdmin_data = userOverviewInfo.dump(userAdmin)
        return jsonify(userAdmin_data)
    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur de récupération des informations",
            "details": err.messages
        }), 400
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@admin_bp.route('/update-info', methods=['PUT'])
@jwt_required()
@admin_role_required
def update_info():
    try:
        userAdmin = get_current_user()
        if not userAdmin:
            return jsonify({'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        data = request.get_json()
        userUpdateInfoSchema = UserUpdateSchema()
        user_data = userUpdateInfoSchema.load(data)

        if 'first_name' in user_data:
            userAdmin.first_name = user_data['first_name']
        if 'last_name' in user_data:
            userAdmin.last_name = user_data['last_name']
        if 'email' in user_data:
            userAdmin.email = user_data['email']

        db.session.commit()
        return jsonify({"message": "Vos informations ont été mises à jour avec succès."}), 200
    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur de mise à jours des informations",
            "details": err.messages
        }), 400
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@admin_bp.route('/update-password', methods=['PUT'])
@jwt_required()
@admin_role_required
def update_password():
    try:
        userAdmin = get_current_user()

        if not userAdmin:
            return jsonify({'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        data = request.get_json()
        userUpdatePassword = UserPasswordUpdateSchema()
        userAdmin_data = userUpdatePassword.load(data)
        if not pwd_context.verify(userAdmin_data['old_password'], userAdmin.password_hash):
            return jsonify({'message': "L'ancien mot de passe est incorrect.", "errors": True}), 400

        if pwd_context.verify(userAdmin_data['new_password'], userAdmin.password_hash):
            return jsonify({'message': "Le nouveau mot de passe doit être différent de l'ancien.", "errors": True}), 400

        userAdmin.password_hash = userAdmin_data['new_password']
        db.session.commit()
        return jsonify({"message": "Votre mot de passe à été mises à jour avec succès."}), 200

    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur de mise à jour de votre mot de passe",
            "details": err.messages
        }), 400
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@admin_bp.route('/create-lottery', methods=['POST'])
@jwt_required()
@admin_role_required
def lottery_create():
    try:
        data = request.get_json()
        lotteryCreateSchema = LotteryCreateSchema()
        data = lotteryCreateSchema.load(data)

        existing_lottery = Lottery.query.filter_by(
            status=Status.EN_COUR).first()
        if existing_lottery:
            return jsonify({
                "errors": True,
                "message": "Un tirage est déjà en cours. Veuillez terminer celui-ci avant d'en créer un nouveau."
            }), 400

        new_lottery = Lottery(
            _name=data['name'],
            _start_date=data['start_date'],
            _end_date=data['end_date'],
            _status=data['status'],
            _reward_price=data['reward_price'],
            _max_participants=data['max_participants']
        )
        # envoyer un mail au Users pour nouveau tirage

        db.session.add(new_lottery)
        db.session.commit()
        return jsonify({"message": "Le tirage à été créé avec succès."}), 201
    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur dans la création du tirage",
            "details": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@admin_bp.route('/lottery-list', methods=['GET'])
@jwt_required()
@admin_role_required
def lottery_list():
    try:
        lotteries = Lottery.query.all()

        lotteryListSchema = LotteryListSchema(many=True)
        result = lotteryListSchema.dump(lotteries)
        return jsonify({
            "message": "Liste des tirages récupérée avec succès.",
            "data": result
        }), 200

    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur dans la récupération de toute les tirages",
            "details": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@admin_bp.route('/lottery-details/<int:lottery_id>', methods=['GET'])
@jwt_required()
@admin_role_required
def lottery_details(lottery_id):
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()
        if lottery is None:
            return jsonify({
                "errors": True,
                "message": "Loterie non trouvée."
            }), 404
        lotteryOverviewschema = LotteryOverviewSchema()
        result = lotteryOverviewschema.dump(lottery)
        return jsonify({
            "message": "Details du tirage",
            "data": result
        }), 200

    except ValidationError as err:

        return jsonify({
            "errors": True,
            "message": "Erreur de récupération de l'historique",
            "details": err.messages
        }), 400
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@admin_bp.route('/participants_list/<int:lottery_id>', methods=['GET'])
@jwt_required()
@admin_role_required
def participants_list(lottery_id):
    try:
        lottery = Lottery.query.get_or_404(lottery_id)
        if lottery.status in [Status.TERMINE, Status.SIMULATION_TERMINE]:
            return jsonify({"message": "Le tirage est déjà terminé.", "errors": True}), 403
        participants = Entry.query.filter_by(lottery_id=lottery.id).all()

        entry_schema = EntryOverviewSchema(many=True)
        result = entry_schema.dump(participants)

        return jsonify({
            "message": "Liste des participants récupérée avec succès.",
            "data": result
        }), 200
    except ValidationError as err:

        return jsonify({
            "errors": True,
            "message": "Erreur de récupération des participants",
            "details": err.messages
        }), 400
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue lors de la récupération des participants.",
            "details": str(e)
        }), 500


@admin_bp.route('/lottery-rank/<int:lottery_id>', methods=['GET'])
@jwt_required()
@admin_role_required
def lottery_rank(lottery_id):
    pass


@admin_bp.route('/manage-participants/remove/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_role_required
def manage_participants_remove(user_id):
    try:
        data = request.get_json()

        lottery_id = data.get('lottery_id')
        if not lottery_id:
            return jsonify({"errors": True, "message": "L'ID du tirage est requis."}), 400

        lottery = Lottery.query.get_or_404(lottery_id)
        if lottery.status in [Status.TERMINE, Status.SIMULATION_TERMINE]:
            return jsonify({"message": "Le tirage est déjà terminé.", "errors": True}), 403

        entry = Entry.query.filter_by(
            user_id=user_id, lottery_id=lottery_id).first()
        if not entry:
            return jsonify({"errors": True, "message": "Aucune participation trouvée pour cet utilisateur dans ce tirage."}), 404

        db.session.delete(entry)
        db.session.commit()

        return jsonify({"message": "Participation supprimée avec succès."}), 200

    except Exception as e:
        return jsonify({"errors": True, "message": "Une erreur est survenue", "details": str(e)}), 500


@admin_bp.route('/lottery-rank/<int:lottery_id>', methods=['POST'])
@jwt_required()
@admin_role_required
def lottery_rank(lottery_id):
    try:
        data = request.get_json()
        entryAdminAddUserSchema = EntryAdminAddUserSchema()
        entry_data = entryAdminAddUserSchema.load(data)

        lottery = Lottery.query.get_or_404(lottery_id)
        if lottery.status in [Status.TERMINE, Status.SIMULATION_TERMINE]:
            return jsonify({"message": "Le tirage est déjà terminé.", "errors": True}), 403

        user = User.query.filter_by(email=entry_data['email']).first()
        if not user:
            return jsonify({"errors": True, "message": "Utilisateur non trouvé avec cet email."}), 404

        existing_entry = Entry.query.filter_by(
            user_id=user.id, lottery_id=lottery.id).first()
        if existing_entry:
            return jsonify({"errors": True, "message": "L'utilisateur est déjà inscrit à ce tirage."}), 400

        new_entry = Entry(
            user_id=user.id,
            lottery_id=lottery.id,
            numbers=entry_data['numbers'],
            lucky_numbers=entry_data['numbers_lucky']
        )

        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Participant ajouté avec succès.", "entry_id": new_entry.id}), 201

    except ValidationError as err:
        return jsonify({"errors": True, "message": "Erreur d'enregistrement", "details": err.messages}), 400
    except Exception as e:
        return jsonify({"errors": True, "message": "Une erreur est survenue", "details": str(e)}), 500


@admin_bp.route('/logout', methods=['POST'])
@jwt_required()
@admin_role_required
def logout_admin():
    try:
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        revoke_token(jti, user_id)
        return jsonify({"message": "Déconnexion réussie."}), 200
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500
