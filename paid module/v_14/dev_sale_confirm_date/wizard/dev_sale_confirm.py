# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api


class dev_sale_confirm(models.TransientModel):
    _name = "dev.sale.confirm"
    
    confirm_date = fields.Datetime('Confirmation Date', required="1")

    def confirm_sale_order(self):
        active_ids = self._context.get('active_ids')
        sale_ids = self.env['sale.order'].browse(active_ids)
        for sale in sale_ids:
            sale.date_order = self.confirm_date
            sale.action_confirm()
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: