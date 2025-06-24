from odoo import tools
from odoo import api, fields, models


class OpdReport(models.Model):
    _name = "opd.report"
    _description = "Opd Analysis Report"
    _auto = False

    name = fields.Char("seq")
    patient_id = fields.Many2one('res.partner', string='Patient', readonly=True)
    doctor_department_id = fields.Many2one('doctor.department', string="Doctor Department", readonly=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor', readonly=True)
    appointment_date = fields.Date("Appointment Date", readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending'), ('confirm', 'Confirm'),
         ('sent', 'Done'), ('cancel', 'Cancel')], readonly=True, string="Status")
    weekdays = fields.Char("WeekDay Name", readonly=True)

    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Sex', readonly=True)
    date_of_birth = fields.Date('Date of Birth', help='Date Of Birth', readonly=True)
    age = fields.Char('Age', readonly=True)
    blood_group = fields.Selection(
        [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'),
         ('O-', 'O-')], 'Blood Group', readonly=True)
    email = fields.Char("Email", help='abc@gmail.com', readonly=True)
    mobile = fields.Char("Mobile", help='1234567890', readonly=True)
    street = fields.Char("Street", readonly=True)
    street2 = fields.Char("Street2", readonly=True)
    city = fields.Char("City", readonly=True)
    zip = fields.Char("Zip Code", readonly=True)
    state_id = fields.Many2one("res.country.state", string='State', readonly=True)
    country_id = fields.Many2one('res.country', string='Country', readonly=True)

    chief_complaints = fields.Many2one('chief.complaints', string="Chief Complaints", readonly=True)
    local_examination = fields.Many2one('local.examination', string="Local Examination", readonly=True)
    system_examination = fields.Many2one('system.examination', string="System Examination", readonly=True)

    follow_up_date = fields.Date(string="Followup Date", readonly=True)

    def _select_opd(self, fields=None):
        if not fields:
            fields = {}
        select_ = """
                    o.id as id,
                    o.name as name,
                    o.patient_id as patient_id,
                    o.doctor_id as doctor_id,
                    o.doctor_department_id as doctor_department_id,
                    o.appointment_date as appointment_date,
                    o.state as state,
                    o.weekdays as weekdays,
                    o.sex as sex,
                    o.date_of_birth as date_of_birth,
                    o.age as age,
                    o.blood_group as blood_group,
                    o.email as email,
                    o.mobile as mobile,
                    o.street as street,
                    o.street2 as street2,
                    o.city as city,
                    o.zip as zip,
                    o.state_id as state_id,
                    o.country_id as country_id,
                    o.chief_complaints as chief_complaints,
                    o.local_examination as local_examination,
                    o.system_examination as system_examination,
                    o.follow_up_date as follow_up_date
                """
        for field in fields.values():
            select_ += field
        return select_

    def _from_opd(self, from_clause=''):

        from_ = """
                    opd_opd o 
                %s
        """ % from_clause
        return from_

    def _group_by_opd(self, groupby=''):
        groupby_ = """
                    o.patient_id,
                    o.doctor_id,
                    o.id, 
                    o.sex,
                    o.date_of_birth,
                    o.age,
                    o.blood_group,
                    o.email,
                    o.mobile,
                    o.street,
                    o.street2,
                    o.city,
                    o.zip,
                    o.state_id,
                    o.country_id
                     %s
        """ % (groupby)
        return groupby_

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        if not fields:
            fields = {}
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        return '%s (SELECT %s FROM %s WHERE o.is_follow_up_opd IS TRUE OR o.is_normal_opd IS TRUE GROUP BY %s)' % \
               (with_, self._select_opd(fields), self._from_opd(from_clause), self._group_by_opd(groupby))

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
