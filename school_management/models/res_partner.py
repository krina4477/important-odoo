from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    teacher = fields.Boolean("Teacher", default=False)
    student = fields.Boolean("Student", default=False)

    @api.onchange('teacher', 'student')
    def _onchange_teacher_student(self):
        for partner in self:
            if partner.teacher:
                partner.student = False
            elif partner.student:
                partner.teacher = False
