# Part of Softhealer Technologies.
{
    "name": "Global Custom Fields",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "16.0.3",

    "license": "OPL-1",

    "category": "Extra Tools",

    "summary": "Add New Field Module, Make Global Dynamic Fields, Create New Field App, Assign Custom Fields Odoo, Update Global Custom Field, Update Global Custom Tab Odoo",

    "description": """
    Currently, in odoo, you can't create dynamic custom fields and tabs. This module is useful to create and add a dynamic field & dynamic tab in any form view without any technical knowledge.""",

    "depends": ['base', 'web'],

    "data": [
        "security/base_security.xml",
        "security/ir.model.access.csv",
        "views/form_views.xml",
        "views/form_tab_views.xml",
    ],
    'assets': {
        'web.assets_qweb': [
            'sh_global_custom_fields/static/src/xml/*.xml'
        ]
    },
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/RN8oRhrrYvw",
    "installable": True,
    "auto_install": False,
    "application": True,

    "price": "150",
    "currency": "EUR",
    'uninstall_hook': 'uninstall_hook',
    'assets': {

        'web.assets_backend': [
            'sh_global_custom_fields/static/src/js/form_controller.js'
        ]
    }
}
