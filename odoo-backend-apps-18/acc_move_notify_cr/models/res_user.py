# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import _, api, exceptions, fields, models
from odoo.addons.bus.models.bus import channel_with_db, json_dump

DEFAULT_MESSAGE = "Default message"
INFO = "info"
DEFAULT = "default"

class ResUsers(models.Model):
    _inherit = "res.users"

    def notify_info(self, message="Default message", title=None, sticky=False, target=None,id=None):
        title = title or _("DEFAULT")
        self._notify_channel(DEFAULT, message, title, sticky, target,id)

    def _notify_channel(
            self,
            type_message=DEFAULT,
            message=DEFAULT_MESSAGE,
            title=None,
            sticky=False,
            target=None,
            id = None,
    ):
        if not self.env.user._is_admin() and any(user.id != self.env.uid for user in self):
            raise exceptions.UserError(_("Sending a notification to another user is forbidden."))
        if not target:
            target = self.env.user.partner_id
        bus_message = {
            "type": type_message,
            "message": message,
            "title": title,
            "sticky": sticky,
            "id":id,
        }
        self.env["bus.bus"]._sendone(target, "iap_notification",bus_message)
