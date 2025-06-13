{
    'name': 'Survey Image Upload Option',
    'version': '18.0.0.1',

    'description': """
        This module adds an image upload option to survey questions in Odoo.
    """,

    'author': 'Candidroot Pvt.Ltd.',
    'website': 'https://www.candidroot.com/',
    'depends': [
        'survey', 'base'
    ],
    'data': [
        'views/survey_question_view.xml',
        'views/survey_template.xml',
        'views/survey_template_print.xml',
        'views/survey_user_input.xml',
    ],
    'assets': {
        'survey.survey_assets': [
            'survey_image_upload_option_cr/static/src/js/survey_print.js',
            'survey_image_upload_option_cr/static/src/js/multi_image.js',
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
