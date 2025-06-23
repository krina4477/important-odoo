from odoo import models, fields, api
from datetime import datetime, timedelta


class StudentStudent(models.Model):
    _name = "student.student"
    _inherits = {'res.partner': 'contact_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Student Information"

    def set_default_number(self):
        return "New"

    number = fields.Char(default=set_default_number)
    contact_id = fields.Many2one('res.partner')
    age = fields.Integer("Age")
    birth_date = fields.Date("Birth Date")
    class_id = fields.Many2one("class.info", string="Class")
    user_id = fields.Many2one('res.users')

    def action_view_sale_order(self):
        action = {
            'name': 'Sale Orders for Student',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.contact_id.id)],
        }
        return action

    @api.onchange("birth_date")
    def onchange_birth_date(self):
        if self.birth_date:
            self.age = (datetime.today().date() - datetime.strptime(str(self.birth_date),
                                                                    '%Y-%m-%d').date()) // timedelta(days=365)
            date = self.birth_date
            print("you are", self.age, "years and", date.month, "months old")
