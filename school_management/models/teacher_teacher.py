from odoo import models, fields, api


class TeacherTeacher(models.Model):
    _name = "teacher.teacher"
    _inherits = {'res.partner': 'contact_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Teacher Information"

    contact_id = fields.Many2one('res.partner')
    course_ids = fields.Many2many("course.info", relation="course_teacher_rel", column1="teacher_id",
                                  column2="course_id")
    user_id = fields.Many2one('res.users')
    experience = fields.Float("Experience")
    class_ids = fields.Many2many("class.info", relation="class_teacher_rel", column1="teacher_id",
                                 column2="class_id", string="Class")
    class_count = fields.Integer(compute='_compute_class_count')
    course_count = fields.Integer(compute='_compute_course_count')

    def show_class(self):
        action = {
            'name': 'class',
            'type': 'ir.actions.act_window',
            'res_model': 'class.info',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.class_ids.ids)],
        }
        return action

    @api.depends('class_ids')
    def _compute_class_count(self):
        for obj in self:
            obj.class_count = len(obj.class_ids)

    def teacher_course(self):
        action = {
            'name': 'course',
            'type': 'ir.actions.act_window',
            'res_model': 'course.info',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.course_ids.ids)],
        }
        return action

    @api.depends('course_ids')
    def _compute_course_count(self):
        for course in self:
            course.course_count = len(course.course_ids)
