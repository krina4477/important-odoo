{
    'name': 'Journal Branch Selection',
    'version': '1.4',
    'author': 'Loai Souboh',
    'depends': ['account', 'branch'],  # Make sure to include the necessary modules
    'data': [
        'security/ir_rule.xml',
        'views/account_journal_view.xml',
        'views/account_journal_tree_view.xml',  # Optional
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
}
