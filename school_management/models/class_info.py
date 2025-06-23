from odoo import models, fields, api


class ClassInfo(models.Model):
    _name = "class.info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Class Information"

    name = fields.Char("Class", required=True)
    student_list = fields.One2many("student.student", "class_id", string="Student")
    company_id = fields.Many2one("res.company", string="Company")
    student_count = fields.Integer(compute='_compute_student_count', string='Student Count')
    teacher_ids = fields.Many2many("teacher.teacher", relation="class_teacher_rel", column1="class_id",
                                   column2="teacher_id", string="Teachers")
    teacher_count = fields.Integer(compute='_compute_teacher_count')
    courses_ids = fields.Many2many("course.info", relation="class_course_rel", column1="class_id",
                                   column2="course_id", string="Course")
    course_count = fields.Integer(compute='_compute_course_count')

    def show_student(self):
        action = {
            'name': 'student',
            'type': 'ir.actions.act_window',
            'res_model': 'student.student',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.student_list.ids)],

        }
        return action

    @api.depends('student_list')
    def _compute_student_count(self):
        for student in self:
            student.student_count = len(student.student_list)

    def teacher_show(self):
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

    def course_show(self):
        action = {
            'name': 'course',
            'type': 'ir.actions.act_window',
            'res_model': 'course.info',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.courses_ids.ids)],
        }
        return action

    @api.depends('courses_ids')
    def _compute_course_count(self):
        for course in self:
            course.course_count = len(course.courses_ids)
