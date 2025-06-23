# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Mruthul Raj(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from odoo import models


class PosSession(models.Model):
    """The class PosSession is used to inherit pos.session"""

    _inherit = 'pos.session'


    #
    # def _loader_params_pos_session(self):
    #     res = super(PosSession, self)._loader_params_pos_session()
    #     fields = res.get('search_params').get('fields')
    #     fields.extend(['sales_user_id'])
    #     res['search_params']['fields'] = fields
    #     return res

    def load_pos_data(self):
        """Load POS data and add `res_users` to the response dictionary.
        return: A dictionary containing the POS data.
        """
        res = super(PosSession, self).load_pos_data()
        domain = [('id', 'in', self.config_id.crm_team_id.member_ids.ids)]
        res['res_users'] = self.env['res.users'].search_read(domain,fields=['name'])
        return res
