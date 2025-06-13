from odoo import http
from odoo.http import request
from odoo.addons.survey.controllers.main import Survey

class SurveyFileUploadController(Survey):

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        result = super().survey_submit(survey_token, answer_token, **post)

        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return result

        survey_sudo = access_data['survey_sudo']
        answer_sudo = access_data['answer_sudo']

        file_uploads = post.get('file_upload')
        filenames = post.get('filename')
        question_id = post.get('question_id')

        if isinstance(file_uploads, str):
            file_uploads = [file_uploads]
        if isinstance(filenames, str):
            filenames = [filenames]

        if file_uploads and filenames and question_id:
            question = request.env['survey.question'].sudo().browse(int(question_id))
            if question and question.question_type == 'file_upload':
                for file_data, filename in zip(file_uploads, filenames):
                    if ',' in file_data:
                        file_data = file_data.split(',')[1] 

                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': filename,
                        'datas': file_data,
                        'res_model': 'survey.user_input',
                        'res_id': answer_sudo.id,
                        'mimetype': 'image/png',
                    })

                    answer_sudo._save_lines(question, file_data, filename=filename)

        return result
