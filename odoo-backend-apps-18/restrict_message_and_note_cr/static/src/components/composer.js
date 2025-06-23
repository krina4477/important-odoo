/** @odoo-module **/
// Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
// See LICENSE file for full copyright and licensing details.

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { FollowerList } from "@mail/core/web/follower_list";
import {
    Component,
    markup,
    onMounted,
    useChildSubEnv,
    useEffect,
    useRef,
    useState,
    useExternalListener,
    toRaw,
} from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";



patch(Composer.prototype, {
    setup(){
        super.setup();
    },
     _onClickCountFollower() {
        var followers = [];
        var followers_id = [];
        document.querySelectorAll('input[name="custom_follower"]:checked').forEach(function(checkbox) {
		    followers.push(checkbox.value);
		    followers_id.push(checkbox.getAttribute('follower_id'));
		});
		document.getElementsByClassName('buttonFollowersCount')[0].textContent = followers.length;
		document.getElementsByClassName('buttonFollowersID')[0].textContent = followers_id;
     },

});

patch(Composer.prototype, {

	async _sendMessage(value, postData, extraData) {
		let follower_list = []

        document.querySelectorAll("input[name=custom_follower]:checked").forEach((checkbox) => {
		    follower_list.push(checkbox.value);
		});

        const thread = toRaw(this.props.composer.thread);
        const postThread = toRaw(this.thread);
        const post = postThread.post.bind(postThread, value, postData, extraData);
        if (postThread.model === "discuss.channel") {
            // feature of (optimistic) temp message
            post();
        } else {
            await post();
        }
        if (thread.model === "mail.box") {
            this.notifySendFromMailbox();
        }
        this.suggestion?.clearRawMentions();
        this.suggestion?.clearCannedResponses();
        this.props.messageToReplyTo?.cancel();
    }
});

patch(Composer,{
     components: {
        ...Composer.components,
         Dropdown,
        FollowerList,
    },
    defaultProps: {
        ...Composer.defaultProps,
        hasFollowers: true,
    },
});


patch(Dropdown.prototype, {
	onOpened() {
		super.onOpened()
		if (this.target) {

            if (this.target.classList.contains("o-mail-Followers-button")) {
                if(document.querySelectorAll(".buttonFollowersID").length) {
		            var followerTextArray = [document.querySelectorAll(".buttonFollowersID")[0].textContent];
				    var followerIds = followerTextArray[0].split(',').map(Number);

		            document.querySelectorAll('input[type="checkbox"][name="custom_follower"]').forEach(checkbox => {
					    const followerId = Number(checkbox.getAttribute('follower_id'));

					    if (followerIds.includes(followerId)) {
					         checkbox.checked = true
					    }
					});
               }
            }

        }
	},

})