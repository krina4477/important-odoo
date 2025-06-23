from odoo import models,fields


class LightspeedAuth(models.Model):
    _name = 'lightspeed.auth'
    _description = 'Lightspeed OAuth Authentication'

    user_id = fields.Many2one('res.users', string='User')
    access_token = fields.Char('Access Token')
    refresh_token = fields.Char('Refresh Token')
    token_received = fields.Datetime('Token Received')

    def save_access_token(self, access_token_data):
        """ Store access token and related information """
        self.create({
            'user_id': self.env.user.id,  # Or associate it with a specific user
            'access_token': access_token_data['access_token'],
            'refresh_token': access_token_data.get('refresh_token'),
            'token_received': fields.Datetime.now(),
        })