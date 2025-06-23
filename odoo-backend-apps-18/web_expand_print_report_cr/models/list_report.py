# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ListPDF(models.Model):
    _name = 'print.pdf.report'
    _description = "Print PDF Report"

    name = fields.Char("Name")

    def get_pdf(self, image):
        pdf = self.env['ir.actions.report']._render_qweb_pdf("web_expand_print_report_cr.action_pdf_report",self.ids,data={'pdf_html':image})[0]
        return pdf