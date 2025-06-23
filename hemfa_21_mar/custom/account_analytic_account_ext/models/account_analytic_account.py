
from odoo import api, fields, models, tools, _

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def action_view_invoice(self):
        self.ensure_one()
        query = self.env['account.move.line']._search(
            [('move_id.move_type', 'in', self.env['account.move'].get_sale_types())])
        query.order = None
        query.add_where('account_move_line.analytic_distribution ? %s', [str(self.id)])
        query_string, query_param = query.select('DISTINCT account_move_line.move_id')
        self._cr.execute(query_string, query_param)
        move_ids = [line.get('move_id') for line in self._cr.dictfetchall()]
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', move_ids)],
            "context": {"create": False, 'default_move_type': 'out_invoice'},
            "name": _("Customer Invoices"),
            'view_mode': 'tree,form',
        }
        return result

    def action_view_vendor_bill(self):
        self.ensure_one()
        query = self.env['account.move.line']._search(
            [('move_id.move_type', 'in', self.env['account.move'].get_purchase_types())])
        query.order = None
        query.add_where('account_move_line.analytic_distribution ? %s', [str(self.id)])
        query_string, query_param = query.select('DISTINCT account_move_line.move_id')
        self._cr.execute(query_string, query_param)
        move_ids = [line.get('move_id') for line in self._cr.dictfetchall()]
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', move_ids)],
            "context": {"create": False, 'default_move_type': 'in_invoice'},
            "name": _("Vendor Bills"),
            'view_mode': 'tree,form',
        }
        return result

    
