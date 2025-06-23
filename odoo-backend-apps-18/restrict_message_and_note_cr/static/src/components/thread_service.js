/** @odoo-module **/
//Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
//See LICENSE file for full copyright and licensing details.

import { Store } from "@mail/core/common/store_service";
import { patch } from "@web/core/utils/patch";
import { prettifyMessageContent } from "@mail/utils/common/format";

patch(Store.prototype,{

	 async getMessagePostParams({ body, postData, thread, followerIds }) {
        const { attachments, cannedResponseIds, isNote, mentionedChannels, mentionedPartners } =
            postData;
        const subtype = isNote ? "mail.mt_note" : "mail.mt_comment";
        const validMentions = this.getMentionsFromText(body, {
            mentionedChannels,
            mentionedPartners,
        });
        const partner_ids = validMentions?.partners.map((partner) => partner.id) ?? [];
        const recipientEmails = [];
        const recipientAdditionalValues = {};
        if (!isNote) {
            const recipientIds = thread.suggestedRecipients
                .filter((recipient) => recipient.persona && recipient.checked)
                .map((recipient) => recipient.persona.id);
            thread.suggestedRecipients
                .filter((recipient) => recipient.checked && !recipient.persona)
                .forEach((recipient) => {
                    recipientEmails.push(recipient.email);
                    recipientAdditionalValues[recipient.email] = recipient.create_values;
                });
            partner_ids.push(...recipientIds);
        }
        postData = {
            body: await prettifyMessageContent(body, validMentions),
            message_type: "comment",
            subtype_xmlid: subtype,
            follower_ids: [followerIds]
        };
        if (attachments.length) {
            postData.attachment_ids = attachments.map(({ id }) => id);
        }
        if (partner_ids.length) {
            Object.assign(postData, { partner_ids });
        }
        if (thread.model === "discuss.channel" && validMentions?.specialMentions.length) {
            postData.special_mentions = validMentions.specialMentions;
        }
        const params = {
            context: {
                mail_post_autofollow: !isNote && thread.hasWriteAccess,
            },
            post_data: postData,
            thread_id: thread.id,
            thread_model: thread.model,
        };
        if (attachments.length) {
            params.attachment_tokens = attachments.map((attachment) => attachment.access_token);
        }
        if (cannedResponseIds?.length) {
            params.canned_response_ids = cannedResponseIds;
        }
        if (recipientEmails.length) {
            Object.assign(params, {
                partner_emails: recipientEmails,
                partner_additional_values: recipientAdditionalValues,
            });
        }
        return params;
    },
});



import { Thread } from "@mail/core/common/thread_model";
import { user } from "@web/core/user";

patch(Thread.prototype, {

	setup() {
        super.setup();
    },

    async post(body, postData = {}, extraData = {}) {
        let tmpMsg;
        postData.attachments = postData.attachments ? [...postData.attachments] : []; // to not lose them on composer clear
        const { attachments, parentId, mentionedChannels, mentionedPartners } = postData;


	    var followerText = document.querySelectorAll(".buttonFollowersID")[0].textContent;
		var followerIds = followerText.split(',').map(follower => parseInt(follower.trim()));

        const params = await this.store.getMessagePostParams({ body, postData, thread: this, followerIds });


        Object.assign(params, extraData);
        const tmpId = this.store.getNextTemporaryId();
        params.context = { ...user.context, ...params.context, temporary_id: tmpId };
        if (parentId) {
            params.post_data.parent_id = parentId;
        }
        if (this.model !== "discuss.channel") {
            params.thread_id = this.id;
            params.thread_model = this.model;
        } else {
            const tmpData = {
                id: tmpId,
                attachments: attachments,
                res_id: this.id,
                model: "discuss.channel",
            };
            tmpData.author = this.store.self;
            if (parentId) {
                tmpData.parentMessage = this.store.Message.get(parentId);
            }
            const prettyContent = await prettifyMessageContent(
                body,
                this.store.getMentionsFromText(body, {
                    mentionedChannels,
                    mentionedPartners,
                })
            );
            tmpMsg = this.store.Message.insert(
                {
                    ...tmpData,
                    body: prettyContent,
                    isPending: true,
                    thread: this,
                },
                { html: true }
            );
            this.messages.push(tmpMsg);
            if (this.selfMember) {
                this.selfMember.syncUnread = true;
                this.selfMember.seen_message_id = tmpMsg;
                this.selfMember.new_message_separator = tmpMsg.id + 1;
            }
        }
        const data = await this.store.doMessagePost(params, tmpMsg);
        if (!data) {
            return;
        }
        const { Message: messages = [] } = this.store.insert(data, { html: true });
        const [message] = messages;
        this.addOrReplaceMessage(message, tmpMsg);
        if (this.selfMember?.seen_message_id?.id < message.id) {
            this.selfMember.seen_message_id = message;
            this.selfMember.new_message_separator = message.id + 1;
        }
        // Only delete the temporary message now that seen_message_id is updated
        // to avoid flickering.
        tmpMsg?.delete();
        if (message.hasLink && this.store.hasLinkPreviewFeature) {
            rpc("/mail/link_preview", { message_id: message.id }, { silent: true });
        }
        return message;
    }

});
