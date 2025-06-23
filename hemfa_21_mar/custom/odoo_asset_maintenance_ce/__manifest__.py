# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Account Asset Maintenance Management',
    'price' : 79.0,
    'version' : '5.3.1',
    'license': 'Other proprietary',
    'depends' : [
            'account',
            'maintenance',
            'odoo_account_asset',
            'material_purchase_requisitions',
#            'document',
            'odoo_account_asset_extend_ce'
                ],
    'currency': 'EUR',
    'category': 'Accounting',
    'summary' : 'Maintenance Management of Account Asset',
    'description': """
Odoo Asset Maintenance
Odoo Asset Maintenance
Approve Maintenance
Start Maintenance,
asset Maintenance
Compelete Maintenance,
Create Requsition,
Maintenance Request Report
Maintenance PDF Report
Maintenance Diagnosis
Maintenance Activity
Maintenance Team
            """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_asset_maintenance_ce/616',#'https://youtu.be/DvGCBI3feqI',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'data' : [
                'security/ir.model.access.csv',
                'data/maintenance_sequence.xml',
                'report/maintenance_request_report.xml',
                'views/maintenance_request_view.xml',
                'views/maintenance_stage_view.xml',
                'views/material_purchase_requisition_view.xml',
                'views/maintenance_team_view.xml',
                'views/maintenance_diagnosis_view.xml',
                'views/maintenance_activity_view.xml',
                'views/asset_view.xml',
                'views/asset_categories_view.xml',
                'views/asset_menu_view.xml',
              ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
