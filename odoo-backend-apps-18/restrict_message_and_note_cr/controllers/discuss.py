# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.mail.controllers.thread import ThreadController
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from datetime import datetime
from werkzeug.exceptions import NotFound
from odoo.tools import frozendict
from odoo.addons.mail.tools.discuss import Store

class ThreadControllerInherit(ThreadController):
    
    
    @http.route("/mail/message/post", methods=["POST"], type="json", auth="public")
    @add_guest_to_context
    def mail_message_post(self, thread_model, thread_id, post_data, context2=None, **kwargs):
        guest = request.env["mail.guest"]._get_guest_from_context()
        guest.env["ir.attachment"].browse(post_data.get("attachment_ids", []))._check_attachments_access(
            kwargs.get("attachment_tokens")
        )
        if context2:
            request.update_context(**context2)
        canned_response_ids = tuple(cid for cid in kwargs.get('canned_response_ids', []) if isinstance(cid, int))
        if canned_response_ids:
            # Avoid serialization errors since last used update is not
            # essential and should not block message post.
            request.env.cr.execute("""
                UPDATE mail_canned_response SET last_used=%(last_used)s
                WHERE id IN (
                    SELECT id from mail_canned_response WHERE id IN %(ids)s
                    FOR NO KEY UPDATE SKIP LOCKED
                )
            """, {
                'last_used': datetime.now(),
                'ids': canned_response_ids,
            })
        thread = request.env[thread_model]._get_thread_with_access(
            thread_id, mode=request.env[thread_model]._mail_post_access, **kwargs
        )
        if not thread:
            raise NotFound()
        if not request.env[thread_model]._get_thread_with_access(thread_id, "write"):
            thread.env.context = frozendict(
                thread.env.context, mail_create_nosubscribe=True, mail_post_autofollow=False
            )
        post_data = {
            key: value
            for key, value in post_data.items()
            if key in thread._get_allowed_message_post_params()
        }
        
        allowed_params = thread._get_allowed_message_post_params()
        
        if post_data['follower_ids']:
            for followers in post_data['follower_ids']:
                allowed_params.update({
                    'follower_ids': followers
                })

        message = thread.sudo().message_post(**self._prepare_post_data(post_data, thread, **kwargs))
        return Store(message, for_current_user=True).get_result()

    @http.route("/mail/thread/messages", methods=["POST"], type="json", auth="user")
    def mail_thread_messages(self, thread_model, thread_id, search_term=None, before=None, after=None, around=None, limit=30):
        domain = [
            ("res_id", "=", int(thread_id)),
            ("model", "=", thread_model),
            ("message_type", "!=", "user_notification"),'|',
            ('follower_ids.partner_id', '=', request.env.user.partner_id.id), '|',
            ('author_id', '=', request.env.user.partner_id.id),
            ('follower_ids', '=', False)
        ]
        res = request.env["mail.message"]._message_fetch(domain, search_term=search_term, before=before, after=after, around=around, limit=limit)
        messages = res.pop("messages")
        if not request.env.user._is_public():
            messages.set_message_done()
        return {
            **res,
            "data": Store(messages, for_current_user=True).get_result(),
            "messages": Store.many_ids(messages),
        }