from odoo import models, fields, api


class CourseInfo(models.Model):
    _name = "course.info"
    _inherits = {'product.template': 'product_tmpl_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Course Details"

    def set_default_number(self):
        return "New"

    number = fields.Char(default=set_default_number)
    product_tmpl_id = fields.Many2one("product.template")
    teacher_ids = fields.Many2many("teacher.teacher", relation="course_teacher_rel", column1="course_id",
                                   column2="teacher_id", string="Teacher")
    teacher_count = fields.Integer(compute='_compute_teacher_count', string='Teachers Count')
    class_ids = fields.Many2many("class.info", relation="class_course_rel", column1="course_id", column2="class_id")

    def show_teacher(self):
        action = {
            'name': 'teacher',
            'type': 'ir.actions.act_window',
            'res_model': 'teacher.teacher',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.teacher_ids.ids)],
        }
        return action

    @api.depends('teacher_ids')
    def _compute_teacher_count(self):
        for teacher in self:
            teacher.teacher_count = len(teacher.teacher_ids)
