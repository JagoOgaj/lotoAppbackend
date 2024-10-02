from flask import jsonify, request, Blueprint
from marshmallow import ValidationError
from app.schemas import UserLoginSchema, UserCreateSchema, UserOverviewInfoSchema, UserUpdateSchema, UserPasswordUpdateSchema, EntryRegistrySchema, LotteryHistorySchema, LotteryOverviewSchema
from app.models import User, Entry, Lottery, LotteryResult
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, get_current_user
from app.extensions import db, pwd_context
from app.helpers import add_token_to_database, revoke_token, get_formatted_results
from app.tools.status_tools import Status
from datetime import datetime

user_bp = Blueprint("user", __name__)


@user_bp.route('/login',
               methods=['POST'])
def login_user():
    try:
        data = request.get_json()

        schema = UserLoginSchema()
        data = schema.load(data)

        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(
            _email=email).one_or_none()
        if not user:
            return jsonify(
                {"message": "Aucun utilisateur trouvé", "errors": True}), 404

        if not pwd_context.verify(
                password, user.password_hash):
            return jsonify(
                {"message": "Mot de passe incorrect", "errors": True}), 401

        access_token = create_access_token(
            identity=user.id)
        refresh_token = create_refresh_token(
            identity=user.id)

        add_token_to_database(
            access_token)
        add_token_to_database(
            refresh_token)

        return jsonify({
            "message": "Utilisateur trouvé avec succès.",
            "access_token": access_token, "refresh_token": refresh_token}), 201

    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur de validation des champs",
            "details": err.messages
        }), 400

    except Exception as e:
        return jsonify({"message": str(
            e), "errors": True, }), 400


@user_bp.route('/register',
               methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        schema = UserCreateSchema()
        data = schema.load(data)

        if User.query.filter_by(
                _email=data['email']).first():
            return jsonify(
                {"errors": True, "message": "L'email est déjà utilisé."}), 400

        new_user = User(
            _first_name=data['first_name'],
            _last_name=data['last_name'],
            _email=data['email'],
            _password_hash=pwd_context.hash(
                data['password']),
            _role_id=2
        )

        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(
            identity=new_user.id)
        refresh_token = create_refresh_token(
            identity=new_user.id)

        return jsonify({
            "message": "Utilisateur créé avec succès.",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201

    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur de validation des champs",
            "details": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@user_bp.route('/account-info',
               methods=['GET'])
@jwt_required()
def account_info():
    try:
        user = get_current_user()
        if not user:
            return jsonify(
                {'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        userOverviewInfo = UserOverviewInfoSchema()
        user_data = userOverviewInfo.dump({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "notification": user.notification
        })

        return jsonify(user_data)
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


@user_bp.route('/update-info',
               methods=['PUT'])
@jwt_required()
def update_info():
    try:
        user = get_current_user()

        if not user:
            return jsonify(
                {'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        data = request.get_json()
        userUpdateInfoSchema = UserUpdateSchema()
        user_data = userUpdateInfoSchema.load(
            data)

        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'email' in user_data:
            user.email = user_data['email']
        if 'notification' in user_data:
            user.notification = user_data['notification']

        db.session.commit()

        return jsonify(
            {"message": "Vos informations ont été mises à jour avec succès."}), 200
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


@user_bp.route('/update-password',
               methods=['PUT'])
@jwt_required()
def update_password():
    try:
        user = get_current_user()

        if not user:
            return jsonify(
                {'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        data = request.get_json()
        userUpdatePassword = UserPasswordUpdateSchema()
        user_data = userUpdatePassword.load(
            data)
        if not pwd_context.verify(
                user_data['old_password'],
                user.password_hash):
            return jsonify({'message': "L'ancien mot de passe est incorrect.", "errors": True, "details": {
                           "password": "L'ancien mot de passe est incorrect."}}), 400

        if pwd_context.verify(
                user_data['new_password'], user.password_hash):
            return jsonify({'message': "Le nouveau mot de passe doit être différent de l'ancien.", "errors": True, "details": {
                           "new_password": "Le nouveau mot de passe doit être différent de l'ancien."}}), 400

        user.password_hash = user_data['new_password']
        db.session.commit()
        return jsonify(
            {"message": "Votre mot de passe à été mises à jour avec succès."}), 200

    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur de mise à jour de votre mot de passe",
            "details": {
                "new_password": err.messages.get("new_password", [])
            }
        }), 400
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@user_bp.route('/logout',
               methods=['POST'])
@jwt_required()
def logout_user():
    try:
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        revoke_token(jti, user_id)
        return jsonify(
            {"message": "Déconnexion réussie."}), 200
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@user_bp.route('/lottery-registry',
               methods=['POST'])
@jwt_required()
def lottery_registry():
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify(
                {'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        data = request.get_json()
        entryRegistrySchema = EntryRegistrySchema()
        entryResgistryData = entryRegistrySchema.load(
            data)

        lottery = Lottery.query.get(
            entryResgistryData['lottery_id'])
        if not lottery:
            return jsonify(
                {'message': 'Loterie non trouvée.', "errors": True}), 404

        if lottery.status in [
                Status.TERMINE] or not lottery.is_active:
            return jsonify(
                {'message': 'La loterie n\'est pas active ou n\'est pas en cours.', "errors": True}), 400

        new_entry = Entry(
            user_id=user_id,
            lottery_id=entryResgistryData['lottery_id'],
            numbers=entryResgistryData['numbers'],
            lucky_numbers=entryResgistryData['lucky_numbers']
        )

        db.session.add(new_entry)
        db.session.commit()

        return jsonify({
            "message": "Inscription à la loterie réussie.",
        }), 201

    except ValidationError as err:
        return jsonify({
            "errors": True,
            "message": "Erreur d'enregistrement",
            "details": err.messages
        }), 400
    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue",
            "details": str(e)
        }), 500


@user_bp.route('/lottery/results/<int:lottery_id>',
               methods=['GET'])
@jwt_required()
def get_lottery_results(lottery_id):
    try:
        lottery = Lottery.query.filter_by(
            id=lottery_id).one_or_none()

        if not lottery:
            return jsonify({
                "errors": True,
                "message": "Tirage non trouvé."
            }), 404

        lottery_result = LotteryResult.query.filter_by(
            lottery_id=lottery_id).one_or_none()

        if not lottery_result:
            return jsonify({
                "errors": True,
                "message": "Aucun résultat trouvé pour ce tirage."
            }), 404

        return jsonify({
            "lottery_name": lottery.name,
            # Directement sous forme de
            # chaîne
            "winning_numbers": lottery_result.winning_numbers,
            # Directement sous forme de
            # chaîne
            "lucky_numbers": lottery_result.winning_lucky_numbers
        }), 200

    except Exception as e:
        return jsonify({
            "errors": True,
            "message": "Une erreur est survenue lors de la récupération des résultats du tirage.",
            "details": str(e)
        }), 500


@user_bp.route('/lottery-history',
               methods=['GET'])
@jwt_required()
def lottery_history_user():
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify(
                {'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        user_entries = Entry.query.filter_by(
            user_id=user_id).all()
        if not user_entries:
            return jsonify({
                "message": "Aucune participation trouvée pour cet utilisateur.",
                "errors": True,
                "emptyEntries": True
            }), 404

        lotteries = []
        current_date = datetime.utcnow()

        for entry in user_entries:
            lottery = Lottery.query.get(
                entry.lottery_id)

            if current_date >= lottery.end_date and lottery.status not in [
                    Status.TERMINE, Status.EN_VALIDATION]:
                lottery.status = Status.EN_VALIDATION
                db.session.commit()

            # Formater la date pour
            # l'affichage
            date_participation = entry.date.strftime(
                '%d %B %Y')
            date_tirage = lottery.end_date.strftime(
                '%d %B %Y')

            lotteries.append({
                "id": lottery.id,
                "date": date_participation,
                "statut": lottery.status,
                "numerosJoues": ', '.join(map(str, entry.numbers)),
                "numerosChance": ', '.join(map(str, entry.chance_numbers)),
                "dateTirage": date_tirage
            })

        schema = LotteryHistorySchema(
            many=True)
        result = schema.dump(lotteries)

        return jsonify({
            "message": "Historique des participations récupéré avec succès.",
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


@user_bp.route('/lottery/current',
               methods=['GET'])
@jwt_required()
def get_current_lottery():
    try:
        user = get_current_user()
        if not user:
            return jsonify(
                {'message': 'Aucun utilisateur trouvé', "errors": True}), 404

        current_lottery = Lottery.query.filter_by(
            status=Status.EN_COUR).one_or_none()

        if not current_lottery:
            return jsonify(
                {"errors": False, "message": "Aucun tirage en cours trouvé."}), 404
        is_registered = Entry.query.filter_by(
            user_id=user.id, lottery_id=current_lottery.id).one_or_none()
        if is_registered:
            return jsonify(
                {"errors": True, "message": "Vous êtes déjà inscrit à cette loterie."}), 400

        lottery_schema = LotteryOverviewSchema()
        result = lottery_schema.dump(
            current_lottery)

        return jsonify(result), 200

    except Exception as e:
        return jsonify(
            {"errors": True, "message": "Une erreur est survenue", "details": str(e)}), 500


@user_bp.route('/lottery-details/<int:lottery_id>',
               methods=['GET'])
@jwt_required()
def lottery_details(lottery_id):
    try:
        lottery = Lottery.query.filter_by(
            id=lottery_id).one_or_none()
        if lottery is None:
            return jsonify({
                "errors": True,
                "message": "Loterie non trouvée."
            }), 404

        current_date = datetime.utcnow()
        if current_date >= lottery.end_date and lottery.status not in [
                Status.TERMINE, Status.EN_VALIDATION]:
            lottery.status = Status.EN_VALIDATION
            db.session.commit()
        lotteryOverviewschema = LotteryOverviewSchema()
        result = lotteryOverviewschema.dump(
            lottery)
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


@user_bp.route('/lottery-rank/<int:lottery_id>',
               methods=['GET'])
@jwt_required()
def lottery_rank(lottery_id):
    try:
        lottery_result = db.session.query(
            LotteryResult).filter_by(lottery_id=lottery_id).first()
        if not lottery_result:
            return jsonify(
                {"message": "Pas de résultats pour se tirage", "errors": True}), 404

        draw_numbers = set(map(
            int, lottery_result.winning_numbers.split(',')))
        draw_stars = set(
            map(int, lottery_result.winning_lucky_numbers.split(',')))

        participants = db.session.query(
            Entry).filter_by(lottery_id=lottery_id).all()

        if not participants:
            return jsonify(
                {"message": "Pas de participants pour se tirage", "errors": True}), 404

        lottery = db.session.query(
            Lottery).filter_by(id=lottery_id).first()
        reward_price = lottery.reward_price

        formatted_results = get_formatted_results(
            participants, draw_numbers, draw_stars, reward_price)
        if formatted_results:
            return jsonify(
                {"message": "Les resultats du tirage", "data": formatted_results})
        raise Exception(
            "Pas de resultats trouver")
    except Exception as e:
        return jsonify(
            {"errors": True, "message": "Une erreurs est survenue", "details": str(e)}), 500
