from odoo import api, fields, models, _
from datetime import datetime, timedelta


class AccrualPlan(models.Model):
    _inherit = "hr.leave.accrual.plan"

    employee_level = fields.Selection([
        ('1-1', 'Monthly-30'),
        ('1-2', 'Monthly-45'),
    ], string='Employee Level')

    def _compute_employee_level_plan(self):
        employee_ids = self.env['hr.employee'].sudo().search([])

        for employee_id in employee_ids:
            domain = [('employee_id', '=', employee_id.id), ('state', '=', 'validate')]
            allocation_id = self.env["hr.leave.allocation"].sudo().search(domain,
                                                                          limit=1, order='date_from desc')
            contract = self.env['hr.contract'].sudo().search([
                ('employee_id', '=', employee_id.id),
                ('state', 'in', ['open', 'close'])
            ], limit=1, order='date_start desc')

            today_date = fields.Date.today()
            if not contract or (contract.date_end and contract.date_end <= today_date):
                continue

            age45_date = employee_id.birthday + timedelta(days=(365.25 * 45))
            work15_date = contract.date_start + timedelta(days=(365.25 * 15))

            if not allocation_id.date_to and allocation_id.accrual_plan_id.employee_level == '1-1':
                employee_age = (today_date - employee_id.birthday).days / 365.25 if employee_id.birthday else 0
                work_days = (today_date - contract.date_start).days
                work_years = work_days / 365.25

                if employee_age >= 45 or work_years >= 15:
                    accrual_plan_id = self.search([('employee_level', '=', '1-2')], limit=1)
                    holiday_status_id = accrual_plan_id.time_off_type_id if accrual_plan_id else False

                    if not accrual_plan_id or not holiday_status_id:
                        continue

                    vals = {
                        "name": _("Monthly-45 Allocation of %s" % employee_id.display_name),
                        "date_from": min(age45_date, work15_date),
                        "holiday_type": "employee",
                        "employee_id": employee_id.id,
                        "employee_ids": [(6, 0, [employee_id.id])],
                        "allocation_type": "accrual",
                        "accrual_plan_id": accrual_plan_id.id,
                        "holiday_status_id": holiday_status_id.id,
                        "number_of_days": 0
                    }

                    allocation_id.date_to = min(age45_date, work15_date) - timedelta(days=1)
                    allocation = self.env["hr.leave.allocation"].sudo().create(vals)
                    allocation.action_confirm()
                    allocation.action_validate()
