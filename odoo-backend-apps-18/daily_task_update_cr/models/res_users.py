# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _


class ResUsers(models.Model):
	_inherit = "res.users"

	def get_task_details(self, user_id):
		if user_id:
			tasks = self.env['project.task'].search([('manager_id','=', user_id.id)])
			return tasks

	@api.model
	def _daily_task_update(self):
		superuser_id = self.env['res.users'].browse(SUPERUSER_ID)
		users = self.search([])
		for user_id in users:
			tasks = self.env['project.task'].search([('manager_id', '=', user_id.id)])
			if tasks:
				template_id = self.env['ir.model.data']._xmlid_to_res_id('daily_task_update_cr.daily_task_update_to_manager', raise_if_not_found=False)
				template_browse = self.env['mail.template'].browse(template_id)
				if template_browse:
					email_values = {
						'email_from': superuser_id.email,
						'email_to': user_id.login or user_id.partner_id.email,
						'author_id': user_id.partner_id.id
					}
					return template_browse.with_context(user_id=user_id).send_mail(user_id.id,  force_send=True, email_values=email_values)
		return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: