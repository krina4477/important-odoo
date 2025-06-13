from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
import base64
import mimetypes

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    def _save_lines(self, question, answer, comment=None, overwrite_existing=True, filename=None):
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])
        if old_answers and not overwrite_existing:
            raise UserError(_("This answer cannot be overwritten."))

        if question.question_type == 'file_upload':
            if not isinstance(answer, list):
                answer = [answer]
            if not isinstance(filename, list):
                filename = [filename] * len(answer)

            for i, single_answer in enumerate(answer):
                current_filename = filename[i] or f"uploaded_image_{i+1}.png"

                base64_data = single_answer.split(',')[1] if ',' in single_answer else single_answer
                padding = len(base64_data) % 4
                if padding:
                    base64_data += '=' * (4 - padding)

                try:
                    decoded_bytes = base64.b64decode(base64_data)
                    file_size_mb = len(decoded_bytes) / (1024 * 1024)
                except Exception:
                    raise ValidationError(_('Uploaded image is not valid base64.'))

                if question.upload_mb_limit and file_size_mb > question.upload_mb_limit:
                    raise ValidationError(
                        _('Uploaded image exceeds the size limit of %s MB.') % question.upload_mb_limit
                    )

                mimetype = mimetypes.guess_type(current_filename or "")[0] or "image/png"
                encoded_string = base64.b64encode(decoded_bytes).decode('utf-8')

                attachment = self.env['ir.attachment'].create({
                    'name': current_filename,
                    'datas': encoded_string,
                    'res_model': 'survey.user_input.line',
                    'res_id': self.id,
                    'mimetype': mimetype,
                    'public': True,
                })

                vals = {
                    'user_input_id': self.id,
                    'question_id': question.id,
                    'file_upload': encoded_string,
                    'file_mimetype': mimetype,
                    'attachment_ids': [(4, attachment.id)], 
                }

                if overwrite_existing and i < len(old_answers):
                    line = old_answers[i]
                    line.write(vals)
                else:
                    line = self.env['survey.user_input.line'].create(vals)

                line.write({
                    'image_attachment_ids': [(4, attachment.id)],
                })

        else:
            return super()._save_lines(
                question, answer, comment=comment,
                overwrite_existing=overwrite_existing
            )


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    file_upload = fields.Binary('Uploaded File')
    image_attachment_ids = fields.Many2many('ir.attachment', string="Uploaded Images")
    file_mimetype = fields.Char(string='File MIME Type', default='image/png')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'res_id',
        domain=lambda self: [('res_model', '=', self._name)],
        string='Uploaded Files'
    )

