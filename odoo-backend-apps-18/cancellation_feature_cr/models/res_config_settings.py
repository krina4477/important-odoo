# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # SALE ORDER RELATED FIELDS
    so_cancel_type = fields.Selection([('cancel', 'Cancel Only'), ('cancel_reset', 'Cancel and Reset to Draft'),
                                       ('cancel_delete', 'Cancel and Delete')],
                                      'Sale Order Cancel Operation Type',
                                      config_parameter='cancellation_feature_cr.so_cancel_type')

    cancel_do = fields.Boolean(string='Cancel Delivery Order', config_parameter='cancellation_feature_cr.cancel_do')
    cancel_invoice_payment = fields.Boolean(string='Cancel Invoice and Payment',
                                            config_parameter='cancellation_feature_cr.cancel_invoice_payment')

    # PURCHASE ORDER RELATED FIELDS
    po_cancel_type = fields.Selection([('cancel', 'Cancel Only'), ('cancel_reset', 'Cancel and Reset to Draft'),
                                       ('cancel_delete', 'Cancel and Delete')],
                                      'Purchase Order Cancel Operation Type',
                                      config_parameter='cancellation_feature_cr.po_cancel_type')
    cancel_receipt_order = fields.Boolean(string='Cancel Receipt Order',
                                          config_parameter='cancellation_feature_cr.cancel_receipt_order')
    cancel_bill_payment = fields.Boolean(string='Cancel Bill',
                                         config_parameter='cancellation_feature_cr.cancel_bill_payment')

    # INVENTORY RELATED FIELDS
    #   ---* STOCK PICKING OPERATIONS

    stock_picking_cancel_type = fields.Selection(
        [('cancel', 'Cancel Only'), ('cancel_reset', 'Cancel and Reset to Draft'),
         ('cancel_delete', 'Cancel and Delete')],
        'Stock Picking Cancel Operation Type',
        config_parameter='cancellation_feature_cr.stock_picking_cancel_type')

    # INVOICE / ACCOUNT RELATED FIELDS
    #   ---* ACCOUNT MOVE OPERATIONS

    invoice_cancel_type = fields.Selection(
        [('cancel', 'Cancel Only'), ('cancel_reset', 'Cancel and Reset to Draft'),
         ('cancel_delete', 'Cancel and Delete')],
        'Invoice Cancel Operation Type',
        config_parameter='cancellation_feature_cr.invoice_cancel_type')

    payment_cancel_type = fields.Selection(
        [('cancel', 'Cancel Only'), ('cancel_reset', 'Cancel and Reset to Draft'),
         ('cancel_delete', 'Cancel and Delete')],
        'Payment Cancel Operation Type',
        config_parameter='cancellation_feature_cr.payment_cancel_type')
