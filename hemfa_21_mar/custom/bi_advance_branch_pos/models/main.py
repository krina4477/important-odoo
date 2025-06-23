from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class PosConfig(models.Model):
	_inherit = 'pos.config'

	is_sequence = fields.Boolean(string="Allow Custom Sequence", readonly=False)
	prefix = fields.Char(string="Prefix")


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'


	is_sequence = fields.Boolean(related='pos_config_id.is_sequence', readonly=False)
	prefix = fields.Char(related='pos_config_id.prefix', readonly=False)


class PosSession(models.Model):
	_inherit = "pos.session"

	prefix = fields.Char(string="Prefix", default="New", readonly=True)
	address = fields.Char(string="Address", readonly=True)
	logo = fields.Binary(string="logo")
	contact_address = fields.Char(string="Address", readonly=True)
	phone = fields.Char(string="phone", readonly=True)
	vat = fields.Char(string="vat", readonly=True)
	email = fields.Char(string="email", readonly=True)
	website = fields.Char(string="website", readonly=True)
	com_name = fields.Char(string="Company name")

	@api.model_create_multi
	def create(self, vals):
		res = super(PosSession, self).create(vals)

		for session in res:
			if res.branch_id.prefix:
				session.prefix = res.branch_id.prefix
			else:
				session.prefix = ' '
			if session.config_id.is_sequence:
				session.config_id.sequence_id.prefix = session.config_id.name + "/"

		res.address = res.branch_id.address
		res.logo = res.branch_id.branch_logo
		res.contact_address = res.branch_id.company_id.street
		res.phone = res.branch_id.telephone
		res.vat = res.branch_id.company_id.vat
		res.email = res.branch_id.company_id.email
		res.website = res.branch_id.company_id.website
		res.com_name = res.branch_id.company_id.name
		return res

	def _loader_params_pos_session(self):
		result = super()._loader_params_pos_session()
		result['search_params']['fields'].extend(['address','logo','contact_address','phone','vat','email','website','com_name'])
		return result


class PosOrderReport(models.Model):
	_inherit = "report.pos.order"

	prefix = fields.Char(string="Prefix")

	def _select(self):
		return super(PosOrderReport, self)._select() + ",ps.prefix as prefix"

	def _group_by(self):
		return super(PosOrderReport, self)._group_by() + ", ps.prefix"


class PosOrderInherit(models.Model):
	_inherit = 'pos.order'

	def write(self, vals):
		result = super(PosOrderInherit, self).write(vals)
		for order in self:
			if vals.get('state') and vals['state'] == 'paid':
				if order.branch_id:
					if order.branch_id != False:
						branch = order.branch_id
						if branch.apply_prefix:
							count = 0
							for rec in str(order.name):
								if rec == '-':
									count += 1
							if count != 0:
								val_list = order.name.split('-')
								val_list[0] = branch.prefix
								prefix = branch.prefix
								suffix = val_list[1]
								self.update({
									'name': prefix + '-' + suffix
								})
							else:
								self.update({
									'name': branch.prefix + '-' + order.name
								})
						else:
							count = 0
							for rec in str(order.name):
								if rec == '-':
									count += 1
							if count != 0:
								val_list = order.name.split('-')
								suffix = val_list[1]
								self.update({
									'name': suffix
								})
		return result
