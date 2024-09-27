from flask import Blueprint
from app.controllers import AdminController

admin_bp = Blueprint("admin", __name__)

admin_bp.route('/login', methods=['POST'])(AdminController.login_admin)
admin_bp.route('/update-info', methods=['PUT'])(AdminController.update_info)
admin_bp.route('/update-password',
               methods=['PUT'])(AdminController.update_password)
admin_bp.route('/lottery-list', methods=['GET'])(AdminController.lottery_list)
admin_bp.route('/lottery-details/<int:lottery_id>',
               methods=['GET'])(AdminController.lottery_details)
admin_bp.route('/participants_list/<int:lottery_id>',
               methods=['GET'])(AdminController.participants_list)
admin_bp.route('/manage-participants/remove/<int:user_id>',
               methods=['POST'])(AdminController.manage_participants_remove)
admin_bp.route('/manage-participants/add/<int:user_id>',
               methods=['POST'])(AdminController.manage_participants_add)
admin_bp.route('/logout', methods=['POST'])(AdminController.logout_admin)
admin_bp.route('/create-lottery',
               methods=['POST'])(AdminController.lottery_create)
