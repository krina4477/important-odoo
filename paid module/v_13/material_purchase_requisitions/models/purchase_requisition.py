# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import Warning, UserError


class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'documents.mixin']      # odoo11
    _order = 'id desc'

    def _get_document_tags(self):
        return self.company_id.requisition_tags

    def _get_document_folder(self):
        return self.company_id.requisition_folder

    def _check_create_documents(self):
        return self.company_id.documents_requisition_settings and super()._check_create_documents()
    
    #@api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise Warning(_('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
        return super(MaterialPurchaseRequisition, self).unlink()
    
    name = fields.Char(
        string='Number',
        index=True,
        readonly=1,
    )
    project_task_id = fields.Many2one(comodel_name="project.project", string="project for task", required=False, )
    task_id = fields.Many2one(comodel_name="project.task", string="Notification", required=False, )
    product_id = fields.Many2one('product.product', related='requisition_line_ids.product_id', string='Product', readonly=False)
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approval'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Order Created'),
        ('receive', 'Received'),
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
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        copy=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True,
        copy=True,
    )
    approve_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        readonly=True,
        copy=False,
    )
    reject_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager Reject',
        readonly=True,
    )
    approve_employee_id = fields.Many2one(
        'hr.employee',
        string='Approved by',
        readonly=True,
        copy=False,
    )
    reject_employee_id = fields.Many2one(
        'hr.employee',
        string='Rejected by',
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True,
        copy=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,
    )
    requisition_line_ids = fields.One2many(
        'material.purchase.requisition.line',
        'requisition_id',
        string='Purchase Requisitions Line',
        copy=True,
    )
    partner_id = fields.Many2many(
        'res.partner',
        string='Vendors',
    )
    date_end = fields.Date(
        string='Requisition Deadline', 
        readonly=True,
        help='Last date for the product to be needed',
        copy=True,
    )
    date_done = fields.Date(
        string='Date Done', 
        readonly=True, 
        help='Date of Completion of Purchase Requisition',
    )
    managerapp_date = fields.Date(
        string='Department Approval Date',
        readonly=True,
        copy=False,
    )
    manareject_date = fields.Date(
        string='Department Manager Reject Date',
        readonly=True,
    )
    userreject_date = fields.Date(
        string='Rejected Date',
        readonly=True,
        copy=False,
    )
    userrapp_date = fields.Date(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    receive_date = fields.Date(
        string='Received Date',
        readonly=True,
        copy=False,
    )
    reason = fields.Text(
        string='Reason for Requisitions',
        required=False,
        copy=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic account',
        copy=True,
        required=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True,
    )
    is_internal = fields.Boolean(string="",compute="get_is_internal"  )
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Internal Picking',
        readonly=True,
        copy=False,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Requisition Responsible',
        copy=True,
        required=True,
    )
    employee_confirm_id = fields.Many2one(
        'hr.employee',
        string='Confirmed by',
        readonly=True,
        copy=False,
    )
    confirm_date = fields.Date(
        string='Confirmed Date',
        readonly=True,
        copy=False,
    )
    
    purchase_order_ids = fields.One2many(
        'purchase.order',
        'custom_requisition_id',
        string='Purchase Ordes',
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,
    )

    sale_id = fields.Many2one(string='Sale Order', comodel_name='sale.order', required=True)
    sale_order_id = fields.Many2one(string=' ', comodel_name='sale.order', related='sale_id',)
    hours_between_so_pr = fields.Char(string='Hours Between SO and PR' ,compute="_compute_hours_between_so_pr")

    create_date_requisition = fields.Datetime (string='Create date requisition' , compute ="_compute_create_date_requisition")
    create_date_sale_order = fields.Datetime(string='Create date sale order', comodel_name='sale.order',related='sale_id.create_date')
    sla_state = fields.Selection([('day_one_and_two', 'Day one or two'),
                                  ('day_three', 'Day three'),
                                  ('day_four', 'Day four'),
                                  ('more_then_four_days', 'More then four days')],
                                 string="State of PR switch of days",
                                 default='day_one_and_two')
    number_of_hours = fields.Char(string='Number of hours from PR creation')
    request_type = fields.Selection([('operation', 'Operation'),
                                  ('administrative', 'Administrative'),
                                  ('hr', 'HR')],
                                 string="Request Type",required=True)
    def sla_purchase_requisition(self):
        purchase_requisition_ids = self.search([('state', 'not in', ['cancelled', 'received'])])

        for purchase_requisition in purchase_requisition_ids:
            time_difference = fields.Datetime.now() - purchase_requisition.create_date
            number_of_days, number_of_hours = time_difference.days, time_difference.seconds // 3600
            if number_of_days < 2:
                purchase_requisition.sla_state = 'day_one_and_two'
            elif number_of_days == 2:
                purchase_requisition.sla_state = 'day_three'
            elif number_of_days == 3:
                purchase_requisition.sla_state = 'day_four'
            elif number_of_days > 2:
                purchase_requisition.sla_state = 'more_then_four_days'

            number_of_days, number_of_hours = time_difference.days, time_difference.seconds // 3600
            purchase_requisition.number_of_hours = str(number_of_days) + " days and " + str(number_of_hours) + " hours"


    @api.onchange('sale_id')
    def _compute_create_date_requisition(self):
            if self.create_date:
                self.create_date_requisition = self.create_date
            else:
                self.create_date_requisition = fields.Datetime.now()
            if self.state == 'draft':
                self.requisition_line_ids = False
                for line in self.sale_id.order_line:
                    if line.display_type not in ['line_section', 'line_note']:
                        self.env['material.purchase.requisition.line'].create({
                            'product_id': line.product_id.id,
                            'requisition_id': self.id,
                            'description': line.name,
                            'qty': line.product_uom_qty,
                            'task_id': line.task_id.id,
                        })


    @api.onchange('sale_id')
    def _compute_hours_between_so_pr(self):
        if self.sale_id:
            diff = self.create_date_requisition - self.create_date_sale_order
            days, seconds = diff.days, diff.seconds
            hours = seconds // 3600
            self.hours_between_so_pr = str(days) + " days " + str(hours) + " hours"
        else :
            self.hours_between_so_pr = ""


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            for line in rec.requisition_line_ids:
                line.partner_id = rec.partner_id

    @api.depends('delivery_picking_id')
    def get_is_internal(self):
        if self.delivery_picking_id:
            self.is_internal = True
        else:
            self.is_internal = False

    def get_partner_in_all_lines(self):
        if self.requisition_line_ids and self.partner_id:
            for line in self.requisition_line_ids:
                line.partner_id = [(6,0,self.partner_id.ids)]
    
    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        date_end = fields.Datetime.now() + timedelta(hours=96)
        vals.update({
            'name': name,
            'date_end': date_end
        })
        res = super(MaterialPurchaseRequisition, self).create(vals)
        return res
        
    #@api.multi
    def requisition_confirm(self):
        for rec in self:
            manager_mail_template = self.env.ref('material_purchase_requisitions.email_confirm_material_purchase_requistion')
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'dept_confirm'
            if manager_mail_template:
                manager_mail_template.send_mail(self.id)
            
    #@api.multi
    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.userreject_date = fields.Date.today()

    #@api.multi
    def manager_approve(self):
        for rec in self:
            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            employee_mail_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition_iruser_custom')
            email_iruser_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition')
            employee_mail_template.sudo().send_mail(self.id)
            email_iruser_template.sudo().send_mail(self.id)
            rec.state = 'ir_approve'

    #@api.multi
    def user_approve(self):
        for rec in self:
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    #@api.multi
    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        pick_vals = {
            'product_id' : line.product_id.id,
            'product_uom_qty' : line.qty,
            'product_uom' : line.uom.id,
            'location_id' : self.location_id.id,
            'location_dest_id' : self.dest_location_id.id,
            'name' : line.product_id.name,
            'picking_type_id' : self.custom_picking_type_id.id,
            'picking_id' : stock_id.id,
            'custom_requisition_line_id' : line.id,
            'company_id' : line.requisition_id.company_id.id,
            'analytic_account_id': line.requisition_id.analytic_account_id.id
        }
        return pick_vals

    @api.model
    def _prepare_po_line(self, line=False, purchase_order=False):
        po_line_vals = {
                 'product_id': line.product_id.id,
                 'name':line.description,
                 'product_qty': line.qty,
                 'product_uom': line.uom.id,
                 'date_planned': fields.Date.today(),
                 'price_unit': 0,
                 'taxes_id': [(6, 0, line.product_id.supplier_taxes_id.ids)],
                 'order_id': purchase_order.id,
                 'account_analytic_id': self.analytic_account_id.id,
                 'custom_requisition_line_id': line.id
        }
        return po_line_vals
    
    #@api.multi
    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        #internal_obj = self.env['stock.picking.type'].search([('code','=', 'internal')], limit=1)
        #internal_obj = self.env['stock.location'].search([('usage','=', 'internal')], limit=1)
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
#         if not internal_obj:
#             raise UserError(_('Please Specified Internal Picking Type.'))
        for rec in self:
            if not rec.requisition_line_ids:
                raise Warning(_('Please create some requisition lines.'))
            if any(line.requisition_type =='internal' for line in rec.requisition_line_ids):
                if not rec.location_id.id:
                        raise Warning(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id.id:
                        raise Warning(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise Warning(_('Select Destination location under the picking details.'))
#                 if not rec.employee_id.dest_location_id.id or not rec.employee_id.department_id.dest_location_id.id:
#                     raise Warning(_('Select Destination location under the picking details.'))
                picking_vals = {
                        'partner_id' : rec.employee_id.address_home_id.id,
                        #'min_date' : fields.Date.today(),
                        'location_id' : rec.location_id.id,
                        'location_dest_id' : rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                        'picking_type_id' : rec.custom_picking_type_id.id,#internal_obj.id,
                        'note' : rec.reason,
                        'custom_requisition_id' : rec.id,
                        'origin' : rec.name,
                        'company_id' : rec.company_id.id,
                        
                    }
                stock_id = stock_obj.sudo().with_context(from_valid_source=True).create(picking_vals)
                delivery_vals = {
                        'delivery_picking_id' : stock_id.id,
                    }
                rec.write(delivery_vals)
                
            po_dict = {}
            for line in rec.requisition_line_ids:
                if line.requisition_type =='internal':
                    pick_vals = rec._prepare_pick_vals(line, stock_id)
                    move_id = move_obj.sudo().create(pick_vals)
                #else:
                if line.requisition_type == 'purchase': #10/12/2019
                    if not line.partner_id:
                        raise Warning(_('Please enter atleast one vendor on Requisition Lines for Requisition Action Purchase'))
                    for partner in line.partner_id:
                        if partner not in po_dict:
                            po_vals = {
                                'partner_id':partner.id,
                                'currency_id':rec.env.user.company_id.currency_id.id,
                                'date_order':fields.Date.today(),
#                                'company_id':rec.env.user.company_id.id,
                                'company_id':rec.company_id.id,
                                'task_id':rec.task_id.id,
                                'custom_requisition_id':rec.id,
                                'origin': rec.name,
                            }
                            purchase_order = purchase_obj.create(po_vals)
                            po_dict.update({partner:purchase_order})
                            po_line_vals = rec._prepare_po_line(line, purchase_order)
#                            {
#                                     'product_id': line.product_id.id,
#                                     'name':line.product_id.name,
#                                     'product_qty': line.qty,
#                                     'product_uom': line.uom.id,
#                                     'date_planned': fields.Date.today(),
#                                     'price_unit': line.product_id.lst_price,
#                                     'order_id': purchase_order.id,
#                                     'account_analytic_id': rec.analytic_account_id.id,
#                            }
                            purchase_line_obj.sudo().create(po_line_vals)
                        else:
                            purchase_order = po_dict.get(partner)
                            po_line_vals = rec._prepare_po_line(line, purchase_order)
#                            po_line_vals =  {
#                                 'product_id': line.product_id.id,
#                                 'name':line.product_id.name,
#                                 'product_qty': line.qty,
#                                 'product_uom': line.uom.id,
#                                 'date_planned': fields.Date.today(),
#                                 'price_unit': line.product_id.lst_price,
#                                 'order_id': purchase_order.id,
#                                 'account_analytic_id': rec.analytic_account_id.id,
#                            }
                            purchase_line_obj.sudo().create(po_line_vals)
                rec.state = 'stock'
    
    #@api.multi
    def action_received(self):
        for rec in self:
            rec.receive_date = fields.Date.today()
            rec.state = 'receive'
    
    #@api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
    
    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            rec.department_id = rec.employee_id.sudo().department_id.id
            rec.dest_location_id = rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id 

    #@api.multi
    def show_picking(self):
        for rec in self:
            res = self.env.ref('stock.action_picking_tree_all')
            res = res.read()[0]
            res['domain'] = str([('custom_requisition_id','=',rec.id)])
        return res
        
    #@api.multi
    def action_show_po(self):
        for rec in self:
            purchase_action = self.env.ref('purchase.purchase_rfq')
            purchase_action = purchase_action.read()[0]
            purchase_action['domain'] = str([('origin_id','=',rec.id)])
        return purchase_action


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        # '&',
        # ('res_model', '=', 'project.project'), ('res_id', '=', project.id)
        for record in self:
            if record.res_model == 'material.purchase.requisition':
                if self.env['material.purchase.requisition'].sudo().browse(record.res_id).state not in ['draft', 'dept_confirm', 'ir_approve']:
                    raise Warning(
                        _('You can not delete attachment in this state.'))
        return super(IrAttachment, self).unlink()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    documents_requisition_settings = fields.Boolean(related='company_id.documents_requisition_settings', readonly=False,
                                                string="Requisition")
    requisition_folder = fields.Many2one('documents.folder', related='company_id.requisition_folder', readonly=False,
                                     string="requisition default workspace")
    requisition_tags = fields.Many2many('documents.tag', 'requisition_tags_table',
                                    related='company_id.requisition_tags', readonly=False,
                                    string="Requisition Tags")

    @api.onchange('requisition_folder')
    def on_requisition_folder_change(self):
        if self.requisition_folder != self.requisition_tags.mapped('folder_id'):
            self.requisition_tags = False


class ResCompany(models.Model):
    _inherit = "res.company"

    def _domain_company(self):
        company = self.env.company
        return ['|', ('company_id', '=', False), ('company_id', '=', company.id)]

    documents_requisition_settings = fields.Boolean()
    requisition_folder = fields.Many2one('documents.folder', string="Requisition Workspace", domain=_domain_company,
                                     default=lambda self: self.env.ref('documents.documents_internal_folder',
                                                                       raise_if_not_found=False))
    requisition_tags = fields.Many2many('documents.tag', 'requisition_tags_table')