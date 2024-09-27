from flask import Blueprint
from app.controllers import UserController

user_bp = Blueprint("user", __name__)

user_bp.route('/login', methods=['POST'])(UserController.login_user)
user_bp.route('/register', methods=['POST'])(UserController.register_user)
user_bp.route('/account-info/<int:user_id>',
              methods=['GET'])(UserController.account_info)
user_bp.route('update-info', methods=['PUT'])(UserController.update_info)
user_bp.route('update-password',
              methods=['PUT'])(UserController.update_password)
user_bp.route('logout', methods=['POST'])(UserController.logout_user)
user_bp.route('/lottery-registry',
              methods=['GET'])(UserController.lottery_registry)
user_bp.route('/lottery-history',
              methods=['GET'])(UserController.lottery_history_user)
user_bp.route('/lottery-details/<int:lottery_id>',
              methods=['GET'])(UserController.lottery_details)
user_bp.route('/lottery-rank/<int:lottery_id>',
              methods=['GET'])(UserController.lottery_rank)
