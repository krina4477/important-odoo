# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_requisition_id = fields.Many2one(
        'sale.requisition',
        string='Sale requisition',
        copy=False
    )
    appear_in_sale_requisition = fields.Boolean(string="Appear in sale requisition", related='project_id.appear_in_sale_requisition',
                                                help="When this option is checked this project will appear "
                                                     "in sale requisition and extra info will appear in all "
                                                     "tasks of this project.")

    def _find_mail_template_order_sale(self,):
        self.ensure_one()
        template_id=self.env.ref('material_purchase_requisitions.mail_template_sale_order', raise_if_not_found=False)
        return template_id

    def recalculate_handling_fees(self):
        for rec in self:
            rec.order_line.filtered(lambda p: p.product_id.id == self.env.ref('material_purchase_requisitions.handling_fees_product_sabic').id).price_unit = self.compute_handling_fees()

    def compute_handling_fees(self):
        products_price = 0
        for sale_order_line in self.order_line:
            if sale_order_line.product_id.type != 'service':
                products_price += sale_order_line.price_subtotal
        products_price = (products_price / 100) * 3
        return products_price


    def action_quotation_send_order_sale(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template_order_sale()
        lang = self.env.context.get('lang')
        template = self._find_mail_template_order_sale()
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_requisition_line_id = fields.Many2one(
        'sale.requisition.line',
        string='Sale requisition line',
        copy=False
    )

