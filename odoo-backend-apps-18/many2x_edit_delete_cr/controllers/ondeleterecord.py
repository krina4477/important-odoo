# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import models

from odoo import http
from odoo.http import request, content_disposition


class OnDeleteRecordController(http.Controller):

    @http.route('/ondeletebtnclick', type='json', auth='user')
    def ondeletebtnclickrecord(self, delete_id,model_name):
        if delete_id:
            delete_record = request.env[model_name].browse(delete_id)
            delete_record.unlink()
            return True
        else:
            return False