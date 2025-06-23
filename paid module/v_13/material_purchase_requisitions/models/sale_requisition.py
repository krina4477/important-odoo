from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import Warning, UserError
from datetime import datetime, date, timedelta


class SaleRequisition(models.Model):
    _name = 'sale.requisition'
    _description = 'Sale requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(
        string='Number',
        index=True,
        readonly=1,
    )
    active = fields.Boolean(string="Active", default=True)
    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=False,
                                 domain="[('appear_in_sale_requisition','=', True)]")
    analytic_account_ids = fields.Many2many('account.analytic.account', related='project_id.analytic_account_ids',
                                            string="Analytic accounts in sale requisition")
    task_id = fields.Many2one(comodel_name="project.task", string="Notification", required=False)
    address = fields.Text(related='task_id.address')
    sap_location = fields.Char(related='task_id.sap_location')
    occupant_name = fields.Char(related='task_id.occupant_name')
    id_number = fields.Char(related='task_id.id_number')
    check_out_date = fields.Date(related='task_id.check_out_date')
    status = fields.Char(related='task_id.status')
    unit_type = fields.Char(related='task_id.unit_type')
    unit_category = fields.Char(related='task_id.unit_category')
    flat_rate = fields.Many2one('flat.rate', related='task_id.flat_rate')
    reference_no = fields.Char(related='task_id.reference_no')

    partner_id = fields.Many2one('res.partner', related='project_id.partner_id')
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic account'
    )
    state = fields.Selection([
        ('draft', 'New'),
        ('first_approve', 'First approve'),
        ('second_approve', 'Second approve'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        track_visibility='onchange',
    )
    request_date = fields.Date(
        string='Requisition Date',
        default=fields.Date.today(),
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
    )
    date_end = fields.Date(
        string='Requisition Deadline',
        readonly=True,
        help='Last date for the product to be needed',
        copy=True,
    )

    requisition_line_ids = fields.One2many(
        'sale.requisition.line',
        'sale_requisition_id',
        string='Sale Requisitions Line', required=True,
        copy=True
    )

    sale_order_id = fields.Many2one('sale.order', string='Sale order')
    sla_state = fields.Selection([('day_one_and_two', 'Day one or two'),
                                  ('day_three', 'Day three'),
                                  ('day_four', 'Day four'),
                                  ('more_then_four_days', 'More then four days')],
                                 string="State of SR switch of days",
                                 default='day_one_and_two')
    number_of_hours = fields.Char(string='Number of hours from PR creation')
    quotation_count = fields.Integer()

    def sla_sale_requisition(self):
        sale_requisition_ids = self.search([('state', 'not in', ['cancelled', 'done', 'reject'])])

        for sale_requisition in sale_requisition_ids:
            time_difference = fields.Datetime.now() - sale_requisition.create_date
            number_of_days, number_of_hours = time_difference.days, time_difference.seconds // 3600
            if number_of_days < 2:
                sale_requisition.sla_state = 'day_one_and_two'
            elif number_of_days == 2:
                sale_requisition.sla_state = 'day_three'
            elif number_of_days == 3:
                sale_requisition.sla_state = 'day_four'
            elif number_of_days > 2:
                sale_requisition.sla_state = 'more_then_four_days'

            number_of_days, number_of_hours = time_difference.days, time_difference.seconds // 3600
            sale_requisition.number_of_hours = str(number_of_days) + " days and " + str(number_of_hours) + " hours"

    def draft_to_first_approve(self):
        for rec in self:
            rec.state = 'first_approve'
            sale_requisition_line_object = self.env['sale.requisition.line']
            sale_requisition_line_object.create({
                'sale_requisition_id': rec.id,
                'is_section': True,
                'name': "JANITORIAL"
            })

            sale_requisition_line_object.create({
                'sale_requisition_id': rec.id,
                'product_id': self.env.ref('material_purchase_requisitions.steel_polish_mobi_300ml_product_sabic').id,
                'is_section': False,
                'quantity': 5,
                'remarks': 'sabic'
            })
            sale_requisition_line_object.create({
                'sale_requisition_id': rec.id,
                'product_id': self.env.ref('material_purchase_requisitions.dac_disinfectant_3ltr_product_sabic').id,
                'is_section': False,
                'quantity': 6,
                'remarks': 'sabic'
            })
            sale_requisition_line_object.create({
                'sale_requisition_id': rec.id,
                'product_id': self.env.ref('material_purchase_requisitions.tide_detergent_powder_7kg_product_sabic').id,
                'is_section': False,
                'quantity': 2,
                'remarks': 'sabic'
            })
            sale_requisition_line_object.create({
                'sale_requisition_id': rec.id,
                'product_id': self.env.ref('material_purchase_requisitions.flush_bowl_cleaner_product_sabic').id,
                'is_section': False,
                'quantity': 1,
                'remarks': 'sabic'
            })
            sale_requisition_line_object.create({
                'sale_requisition_id': rec.id,
                'product_id': self.env.ref('material_purchase_requisitions.clorox_liquid_product_sabic').id,
                'is_section': False,
                'quantity': 2,
                'remarks': 'sabic'
            })
            sale_requisition_line_object.create({
                'sale_requisition_id': rec.id,
                'product_id': self.env.ref('material_purchase_requisitions.trash_bag_product_sabic').id,
                'is_section': False,
                'quantity': 1,
                'remarks': 'sabic'
            })

    def first_approve_to_second_approve(self):
        for rec in self:
            rec.state = 'second_approve'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def approve_and_create_sale_order(self):
        sale_order_object = self.env['sale.order']
        for rec in self:
            sale_requisition_line_ids = []
            for sale_requisition_line in rec.requisition_line_ids:
                if not sale_requisition_line.is_section:
                    sale_requisition_line_ids.append((0, None, {
                        'product_id': sale_requisition_line.product_id.id,
                        'product_uom_qty': sale_requisition_line.quantity,
                        'sale_requisition_line_id': sale_requisition_line.id
                    }))
                else:
                    sale_requisition_line_ids.append((0, None, {
                        'display_type': 'line_section',
                        'name': sale_requisition_line.name
                    }))

            sale_requisition_line_ids.append((0, None, {
                'product_id': self.env.ref('material_purchase_requisitions.flat_rate_product_sabic').id,
                'product_uom_qty': 1,
                'price_unit': rec.flat_rate.amount
            }))
            print("______ flat rate ________", rec.flat_rate.amount)
            sale_requisition_line_ids.append((0, None, {
                'product_id': self.env.ref('material_purchase_requisitions.handling_fees_product_sabic').id,
                'product_uom_qty': 1,
                'price_unit': rec.flat_rate.amount
            }))
            sale_order_id = sale_order_object.create({
                'partner_id': rec.partner_id.id,
                'project_id': rec.project_id.id,
                'task_id': rec.task_id.id,
                'order_line': sale_requisition_line_ids,
                'sale_requisition_id': rec.id,
                'analytic_account_id': rec.analytic_account_id.id,
                'pricelist_id': self.env.ref('material_purchase_requisitions.product_price_list_sabic_restoration_project').id
            })
            rec.sale_order_id = sale_order_id.id
            sale_order_id.order_line.filtered(lambda p: p.product_id.id == self.env.ref('material_purchase_requisitions.handling_fees_product_sabic').id).price_unit = self.compute_handling_fees(sale_order_id)
            rec.quotation_count = 1
            rec.state = 'done'

    def compute_handling_fees(self, rec):
        products_price = 0
        for sale_order_line in rec.order_line:
            if sale_order_line.product_id.type != 'service':
                products_price += sale_order_line.price_subtotal
        products_price = (products_price / 100) * 3
        return products_price

    def action_view_quotation_created(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        form_view = [(self.env.ref('sale.view_order_form').id, 'form')]

        action['views'] = form_view
        action['res_id'] = self.sale_order_id.id
        action['context'] = dict(self._context, default_origin=self.name, create=False)
        return action

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('sale.requisition.seq')
        date_end = fields.Datetime.now() + timedelta(hours=96)
        vals.update({
            'name': name,
            'date_end': date_end
            })
        res = super(SaleRequisition, self).create(vals)
        return res


class SaleRequisitionLine(models.Model):
    _name = 'sale.requisition.line'
    _description = 'Sale requisition line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'product_id'

    name = fields.Char(string="Name")
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Text(string='Description')
    sale_requisition_id = fields.Many2one('sale.requisition', string='Sale requisition')
    quantity = fields.Float(string="Quantity")
    is_section = fields.Boolean(string="Is section")
    remarks = fields.Selection([('sabic', ''), ('old', 'Old'), ('old_rusty', 'Old/Rusty'),
                                ('missing_damage', 'Missing/Damage'),
                                ('broken_damage', 'Broken/Damage'),
                                ('misuse', 'Misuse'),
                                ('missing', 'Missing'),
                                ('damage', 'Damage'),
                                ('broken', 'Broken'),
                                ('old_rusty_cover', 'Old/Rusty cover'),
                                ('not_working', 'Not working'),
                                ('common_use_for_ac_remote', 'Common use for AC remote'),
                                ('system_less_common_use', 'System less-common-use'),
                                ('system_less', 'System less'),
                                ('old_not_cooling_nois', 'Old not cooling nois'),
                                ('old_not_working', "Old/Not working"),
                                ('common_use', 'Common use'),
                                ('no_maintained_required_can_fixe', 'No maintained required can fixe')
                                ],
                               string="Remarks")
    sabic_quantity = fields.Float(string="Sabic Qty", compute="compute_sabic_and_employee_quantity")
    employee_quantity = fields.Float(string="Employee Qty", compute="compute_sabic_and_employee_quantity")

    @api.depends('remarks', 'quantity')
    def compute_sabic_and_employee_quantity(self):
        for rec in self:
            if rec.remarks in ['missing_damage', 'broken_damage', 'misuse', 'missing', 'damage', 'broken']:
                rec.sabic_quantity = 0
                rec.employee_quantity = rec.quantity
            else:
                rec.sabic_quantity = rec.quantity
                rec.employee_quantity = 0

