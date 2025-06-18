from odoo import models, fields


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_type = fields.Selection(
        selection_add=[('file_upload', 'File Upload')],
    )
    upload_mb_limit = fields.Float(string='Upload Size Limit (MB)')
    multi_upload = fields.Boolean(string='Allow Multiple Uploads')