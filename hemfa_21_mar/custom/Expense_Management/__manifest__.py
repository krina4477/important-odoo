{
    'name': 'Expense Management',
    'version': '2.2',
    'category': 'Accounting',
    'author': 'Loai Souboh',
    'summary': 'Manage expenses from cash and bank journals with real-time analytics, approval workflows, and dynamic currency exchange handling in Odoo.',
    'description': """
Expense Management Module

This module allows users to record, manage, and approve expenses using cash and bank journals in Odoo.

Key Features:
- Create and manage expenses linked to cash or bank journals.
- Submit, approve, and confirm expenses with customizable approval workflows.
- Generate automatic journal entries for confirmed expenses, supporting both same-currency and multi-currency transactions.
- Dynamic handling of exchange rates in expense reports when the journal currency differs from the company currency.
- Real-time expense reporting with support for pivot tables and graphical analysis.
- Full integration with the Odoo accounting system.
- Chatter integration for tracking changes and communication.
- Detailed reporting with analytic account distributions displayed for each expense line.
- Integrated expense line details with partner, reference, and analytic distributions in custom reports.

Ideal for:
- Businesses that need to track and manage expenses for different journals (bank, cash) across multiple currencies.
- Companies requiring approval workflows for expense management with real-time visibility.
- Organizations seeking detailed financial reporting, including analytics and exchange rate management, for better decision-making.
    """,
    'depends': ['base', 'account', 'mail', 'branch'],
    'data': [
        'security/expense_security.xml',
        'security/ir.model.access.csv',
        'reports/report_expense_action.xml',
        'reports/expense_report_custom.xml',
        'views/expense_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
