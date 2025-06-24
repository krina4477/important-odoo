from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    username = fields.Char(string="UserName")
    sendername = fields.Char(string="SenderName")
    apikey = fields.Char(string="Api Key")
    pharmacy = fields.Boolean(string="Pharmacy", readonly=False)
    radiology = fields.Boolean(string="Radiology")
    laboratory = fields.Boolean(string="Laboratory")
    ipd = fields.Boolean(string="IPD")
    reception = fields.Boolean(string="Reception")
    payment_at_reception = fields.Boolean(string="Payment at Reception")
    payment_at_pharmacy = fields.Boolean(string="Payment at Pharmacy")

    surgery = fields.Boolean(string="Surgery")
    diet_module = fields.Boolean(string="Diet")
    physiotherapy = fields.Boolean(string="Physiotherapy")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['username'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.username')
        res['sendername'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.sendername')
        res['apikey'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.apikey')
        res['pharmacy'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.pharmacy')
        res['radiology'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.radiology')
        res['laboratory'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.laboratory')
        res['ipd'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.ipd')
        res['reception'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.reception')
        res['payment_at_reception'] = self.env['ir.config_parameter'].sudo().get_param(
            'cr_medical_base.payment_at_reception')
        res['payment_at_pharmacy'] = self.env['ir.config_parameter'].sudo().get_param(
            'cr_medical_base.payment_at_pharmacy')
        res['surgery'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.surgery')
        res['diet_module'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.diet_module',
                                                                              self.diet_module)
        res['physiotherapy'] = self.env['ir.config_parameter'].sudo().get_param('cr_medical_base.physiotherapy')
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.username', self.username)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.sendername', self.sendername)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.apikey', self.apikey)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.pharmacy', self.pharmacy)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.radiology', self.radiology)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.laboratory', self.laboratory)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.ipd', self.ipd)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.reception', self.reception)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.payment_at_reception',
                                                         self.payment_at_reception)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.payment_at_pharmacy',
                                                         self.payment_at_pharmacy)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.surgery', self.surgery)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.diet_module',
                                                         self.diet_module)
        self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.physiotherapy',
                                                         self.physiotherapy)
        super(ResConfigSettings, self).set_values()

    def execute(self):
        super(ResConfigSettings, self).execute()
        module = self.env['ir.module.module']

        module_id = module.search([('name', '=', 'pharmacy')])
        if self.pharmacy:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.pharmacy', self.pharmacy)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        elif not self.pharmacy:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.pharmacy', self.pharmacy)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()

        module_id = module.search([('name', '=', 'radiology')])
        if self.radiology:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.radiology', self.radiology)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        else:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.radiology', self.radiology)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()

        module_id = module.search([('name', '=', 'laboratory')])
        if self.laboratory:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.laboratory', self.laboratory)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        else:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.laboratory', self.laboratory)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()

        module_id = module.search([('name', '=', 'IPD')])
        if self.ipd:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.ipd', self.ipd)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        else:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.ipd', self.ipd)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()

        module_id = module.search([('name', '=', 'reception')])
        if self.reception:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.reception', self.reception)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        else:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.reception', self.reception)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()

        module_id = module.search([('name', '=', 'surgery')])
        if self.surgery:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.surgery', self.surgery)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        else:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.surgery', self.surgery)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()

        module_id = module.search([('name', '=', 'diet_module')])
        if self.diet_module:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.diet_module', self.diet_module)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        else:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.diet_module', self.diet_module)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()

        module_id = module.search([('name', '=', 'physiotherapy')])
        if self.physiotherapy:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.physiotherapy', self.physiotherapy)
            if module_id.state == 'uninstalled':
                module_id[0].button_immediate_install()
        else:
            self.env['ir.config_parameter'].sudo().set_param('cr_medical_base.physiotherapy', self.physiotherapy)
            if module_id.state == 'installed':
                module_id[0].button_immediate_uninstall()


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        res = super(IrHttp, self).session_info()
        if self.env.user.has_group("pharmacy.group_pharmacy"):
            res['is_Pharmacy_Management_User'] = True
        else:
            res['is_Pharmacy_Management_User'] = False
        return res
