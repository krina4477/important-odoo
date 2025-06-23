##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from . import controllers
from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


def _assign_account_parent(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.account']._parent_store_compute()
