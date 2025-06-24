from odoo import models
from odoo.addons.base.models.ir_module import assert_log_admin_access


class ResConfigSettings(models.Model):
    _inherit = 'ir.module.module'

    @assert_log_admin_access
    def button_immediate_install(self):
        for rec in self:
            if rec.name == 'pharmacy':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.pharmacy', True)
            if rec.name == 'IPD':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.ipd', True)
            if rec.name == 'laboratory':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.laboratory', True)
            if rec.name == 'reception':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.reception', True)
            if rec.name == 'diet_module':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.diet_module', True)
            if rec.name == 'radiology':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.radiology', True)
            if rec.name == 'physiotherapy':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.physiotherapy', True)
            if rec.name == 'radiology':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.radiology', True)
            if rec.name == 'surgery':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.surgery', True)
        res = super().button_immediate_install()
        return res

    @assert_log_admin_access
    def module_uninstall(self):
        res = super().module_uninstall()
        for rec in self:
            if rec.name == 'pharmacy':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.pharmacy', False)
            if rec.name == 'IPD':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.ipd', False)
            if rec.name == 'laboratory':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.laboratory', False)
            if rec.name == 'reception':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.reception', False)
            if rec.name == 'diet_module':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.diet_module', False)
            if rec.name == 'radiology':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.radiology', False)
            if rec.name == 'physiotherapy':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.physiotherapy', False)
            if rec.name == 'radiology':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.radiology', False)
            if rec.name == 'surgery':
                self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.surgery', False)
        return res
