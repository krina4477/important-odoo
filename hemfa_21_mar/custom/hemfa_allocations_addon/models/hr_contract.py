from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    allocation_ids = fields.One2many("hr.leave.allocation", "contract_id", readonly=True, tracking=True)

    @api.constrains('state')
    def _check_state(self):
        for rec in self:
            if rec.state == 'open':

                today_date = fields.Date.today()
                this_year = today_date.year
                birth_date = rec.employee_id.birthday
                employee_age = (rec.date_start - birth_date).days / 365.25
                work_days = (today_date - rec.date_start).days

                age45_date = birth_date + timedelta(days=(365.25 * 45))
                work_years = work_days / 365.25
                work15_date = rec.date_start + timedelta(days=(365.25 * 15))

                vals = rec._prepare_allocation()
                accrual_plan_obj = rec.env['hr.leave.accrual.plan'].sudo()

                if employee_age >= 45:
                    accrual_plan_id = accrual_plan_obj.search([('employee_level', '=', '1-2')], limit=1)
                    holiday_status_id = accrual_plan_id.time_off_type_id if accrual_plan_id else False

                    if not accrual_plan_id:
                        raise ValidationError(_('Accrual plan not found!'))
                    if not holiday_status_id:
                        raise ValidationError(_('Accrual plan holiday status not found!'))

                    vals['name'] = _("Monthly-45 Allocation of %s" % rec.employee_id.display_name)
                    vals['accrual_plan_id'] = accrual_plan_id.id
                    vals['holiday_status_id'] = holiday_status_id.id

                else:
                    accrual_plan_id = accrual_plan_obj.search([('employee_level', '=', '1-1')], limit=1)
                    holiday_status_id = accrual_plan_id.time_off_type_id if accrual_plan_id else False

                    if not accrual_plan_id:
                        raise ValidationError(_('Accrual plan not found!'))
                    if not holiday_status_id:
                        raise ValidationError(_('Accrual plan holiday status not found!'))

                    vals['name'] = _("Monthly-30 Allocation of %s" % rec.employee_id.display_name)
                    vals['accrual_plan_id'] = accrual_plan_id.id
                    vals['holiday_status_id'] = holiday_status_id.id

                if rec.allocation_ids:
                    for allocation in rec.allocation_ids:
                        allocation.action_refuse()
                        allocation.action_draft()
                        allocation.unlink()

                if employee_age < 45 and (age45_date < today_date or work_years >= 15):
                    start_date = min(age45_date, work15_date)

                    vals['date_to'] = start_date - timedelta(days=1)
                    allocation = rec.env["hr.leave.allocation"].create(vals)
                    allocation.action_confirm()
                    allocation.action_validate()

                    accrual_plan_id = accrual_plan_obj.search([('employee_level', '=', '1-2')], limit=1)
                    holiday_status_id = accrual_plan_id.time_off_type_id if accrual_plan_id else False

                    vals['date_from'] = start_date
                    vals['date_to'] = datetime(this_year, 12, 31).date()
                    vals['name'] = _("Monthly-45 Allocation of %s" % rec.employee_id.display_name)
                    vals['accrual_plan_id'] = accrual_plan_id.id
                    vals['holiday_status_id'] = holiday_status_id.id

                    allocation = rec.env["hr.leave.allocation"].create(vals)
                    allocation.action_confirm()
                    allocation.action_validate()

                else:
                    allocation = rec.env["hr.leave.allocation"].create(vals)
                    allocation.action_confirm()
                    allocation.action_validate()

    def _prepare_allocation(self):
        vals = {
            "contract_id": self.id,
            "date_from": self.date_start,
            "holiday_type": "employee",
            "employee_id": self.employee_id.id,
            "employee_ids": [(6, 0, [self.employee_id.id])],
            "allocation_type": "accrual",
            "number_of_days": 0
        }
        return vals


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    contract_id = fields.Many2one("hr.contract", readonly=True)
