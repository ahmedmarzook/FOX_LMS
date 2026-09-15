from . import models

# from . import controllers

from odoo.api import Environment, SUPERUSER_ID


def post_init_hook(env):
    # env = Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].set_param("validation_active", True)


def uninstall_hook(env):
    # env = Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].set_param("validation_active", False)
