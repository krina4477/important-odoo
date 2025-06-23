{
    'name': 'Financial Custody Management',
    'version': '1.2',
    'category': 'Accounting',
    'summary': 'Comprehensive solution for managing financial custody processes including cash requests, approvals, and reconciliations.',
    'description': """
Financial Custody Management Module
===================================

This module provides a comprehensive solution for managing financial custody requests, approval workflows, reconciliations, and payments. It simplifies and automates the financial custody process within an organization, ensuring transparency, accuracy, and traceability for all transactions.

**Main Features:**
- Request and track cash custody for business expenses.
- Submit detailed expense reports with automatic journal entry generation.
- Multi-step approval process (Draft -> Submitted -> Approved -> Cashed -> Expense Report -> Reconciled).
- Reconciliation process to ensure accurate financial records and payments.
- Linked multi-step payments for custody settlement, both receiving and paying back amounts.
- Automatic creation of linked cash requests for custody recomposition with validation.
- Analytic distribution support for expense lines.
- Custody difference settlement with calculation of remaining amounts to pay or receive.
- Integrated logging and messaging via Odoo's chatter for transparency.
- Ability to reset journal entries and payments to draft, ensuring flexibility.
- Detailed error validation for draft, submitted, and reconciled stages.
- Customizable workflows for adjusting approval flows and controls.
- Full support for both permanent and temporary custody types.

**Key Workflows:**
1. **Cash Request Submission**: Employees request cash custody for business expenses, selecting the type (permanent/temporary) and entering required details.
2. **Approval Process**: Custody requests are reviewed and approved by managers, with automatic notifications.
3. **Expense Reporting**: After using custody funds, employees submit expense reports with detailed expense lines and optional purchase payments.
4. **Custody Recomposition**: New cash requests can be created for custody recomposition based on remaining amounts.
5. **Payment Settlements**: Employees can receive or pay back the custody balance with automatic journal entry creation for inbound or outbound payments.
6. **Reconciliation Process**: Once expense reports are submitted, the system automatically generates journal entries and reconciles the custody, ensuring the financial accuracy of records.

**Custom Validation and Error Handling:**
- Custody recomposition checks for linked draft requests before proceeding.
- Validation of linked cash requests ensures no duplication or incomplete transactions.
- Payments linked to custody requests are tracked with multi-payment support.
- Automatic recalculation of remaining amounts based on payments and expenses.

**Additional Features:**
- Customizable analytic accounting distribution for expense lines.
- Integrated with Odoo Accounting and HR for seamless employee and journal tracking.
- Full control over financial records with the ability to reset transactions back to draft.
- Custody recomposition stops if there are any linked requests in a draft state or beyond.

**Integrations:**
- Integrated with Odoo Accounting and HR modules.
- Analytic distribution for tracking expense lines with cost centers or projects.
- Compatible with Odoo's purchase and base accounting kit for extended features.

**Security & Access:**
- Role-based access control with detailed security groups for employees, managers, and administrators.
- Approval flows designed to respect security rules, with audit trails for all actions.

    """,
    'author': 'Loai Souboh',
    'license': 'LGPL-3',
    'depends': ['account', 'hr', 'base_accounting_kit', 'purchase'],
    'data': [
        'data/sequence.xml',
        'data/mail_subtype.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'reports/report_cash_request_action.xml',
        'reports/report_cash_request_template.xml',
        'views/cash_request_views.xml',
        'views/res_company_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'financial_custody/static/src/css/custom_button.css',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'maintainer': 'Loai Souboh',
}
