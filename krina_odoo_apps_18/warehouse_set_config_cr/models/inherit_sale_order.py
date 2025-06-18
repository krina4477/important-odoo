# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('partner_id.zip')
    def _compute_warehouse_id(self):
        super()._compute_warehouse_id()

        Warehouse = self.env['stock.warehouse']
        geolocator = Nominatim(user_agent="zip_distance")

        for order in self:
            customer_zip = order.partner_id.zip
            custom_warehouse = None

            if customer_zip and customer_zip.isdigit():
                customer_zip_int = int(customer_zip)

                # Manual ZIP range matching
                manual_warehouses = Warehouse.search([
                    ('warehouse_range_type', '=', 'manually'),
                    ('company_id', 'in', [order.company_id.id, False])
                ])
                for warehouse in manual_warehouses:
                    if (warehouse.from_range and warehouse.to_range and
                            warehouse.from_range.isdigit() and warehouse.to_range.isdigit()):
                        from_zip = int(warehouse.from_range)
                        to_zip = int(warehouse.to_range)

                        if from_zip <= customer_zip_int <= to_zip:
                            custom_warehouse = warehouse
                            break

                # Distance API matching
                if not custom_warehouse:
                    try:
                        customer_location = geolocator.geocode(customer_zip)
                        if customer_location:
                            customer_coords = (customer_location.latitude, customer_location.longitude)
                            min_distance = float('inf')

                            distance_warehouses = Warehouse.search([
                                ('warehouse_range_type', '=', 'distance_api'),
                                ('company_id', 'in', [order.company_id.id, False])
                            ])
                            for wh in distance_warehouses:
                                wh_zip = wh.partner_id.zip
                                if not wh_zip:
                                    continue
                                warehouse_location = geolocator.geocode(wh_zip)
                                if not warehouse_location:
                                    continue
                                warehouse_coords = (warehouse_location.latitude, warehouse_location.longitude)
                                distance = geodesic(customer_coords, warehouse_coords).miles

                                if distance < min_distance:
                                    min_distance = distance
                                    custom_warehouse = wh
                    except Exception:
                        pass

            if custom_warehouse:
                order.warehouse_id = custom_warehouse
