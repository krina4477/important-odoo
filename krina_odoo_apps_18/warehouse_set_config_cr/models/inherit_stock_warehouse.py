from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "stock.warehouse"

    warehouse_range_type = fields.Selection([('manually', 'Manually'), ('distance_api', 'Distance Api')], string="Warehouse Range")
    from_range = fields.Char("From")
    to_range = fields.Char("To")

    @api.constrains('from_range', 'to_range', 'warehouse_range_type')
    def _check_zip_range_overlap(self):
        for warehouse in self:
            if warehouse.warehouse_range_type != 'manually':
                continue

            # Skip if either range is missing or non-digit
            if not (warehouse.from_range and warehouse.to_range):
                continue

            if not (warehouse.from_range.isdigit() and warehouse.to_range.isdigit()):
                raise ValidationError("From and To ZIP ranges must be numeric.")

            from_zip = int(warehouse.from_range)
            to_zip = int(warehouse.to_range)

            if from_zip > to_zip:
                raise ValidationError("From range must be less than or equal to To range.")

            # Search for overlapping ranges in other warehouses
            overlapping_warehouses = self.search([
                ('id', '!=', warehouse.id),
                ('warehouse_range_type', '=', 'manually'),
            ]).filtered(lambda wh: (
                    wh.from_range and wh.to_range and
                    wh.from_range.isdigit() and wh.to_range.isdigit() and
                    int(wh.from_range) <= to_zip and int(wh.to_range) >= from_zip
            ))

            if overlapping_warehouses:
                raise ValidationError(
                    f"The ZIP range [{warehouse.from_range} - {warehouse.to_range}] overlaps with another warehouse: "
                    f"{', '.join(overlapping_warehouses.mapped('name'))}."
                )
