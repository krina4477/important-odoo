/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

export class DynamicDashboard extends Component {

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.user = user;
        this.state = useState({
            sections: [],
            selectedSection: null,
        });
        const now = new Date();
        const hour = now.getHours();
        let greetingMessage = "Hello";
        if (hour < 12) greetingMessage = "Good Morning";
        else if (hour < 18) greetingMessage = "Good Afternoon";
        else greetingMessage = "Good Evening";

        this.greetingMessage = greetingMessage;

        onWillStart(async () => {
            const [userInfo] = await this.orm.read('res.users', [this.user.userId], ['name', 'image_128']);
            this.userImage = `data:image/png;base64,${userInfo.image_128}`;
            const allowedCompanyIds = this.user.context.allowed_company_ids;

            const sections = await this.orm.searchRead("dashboard.section", [
                ["company_ids", "in", allowedCompanyIds]
            ], ["name", "item_ids"]);

            const sectionItemsMap = {};

            for (const section of sections) {
                sectionItemsMap[section.id] = await this.orm.read("dashboard.item", section.item_ids, [
                    "name",
                    "model_name",
                    "section_id",
                    "action_id",
                    "view_id",
                    "filter_id",
                    "icon",
                    "record_count"
                ]);
            }

            for (const section of sections) {
                section.item_ids = sectionItemsMap[section.id];
            }

            this.state.sections = sections;
            this.state.selectedSection = sections.length ? sections[0] : null;
        });
    }

    get sections() {
        return this.state.sections;
    }

    get selectedSection() {
        return this.state.selectedSection;
    }

    selectSection(section) {
        this.state.selectedSection = section;
    }

    async openItem(item) {
        const { action_id, model_name, filter_id } = item;

        if (!model_name) {
            this.notification.add("No valid action or model found.", { type: "warning" });
            return;
        }
        let domain = [];

        if (filter_id) {
            try {
                const filters = await this.orm.read('ir.filters', [filter_id[0]], ['domain']);
                if (filters.length && filters[0].domain) {
                    domain = filters[0].domain;
                }
            } catch (error) {
                this.notification.add("Failed to load filter domain.", { type: "danger" });
                console.error("Error reading filter domain:", error);
            }
        }

        this.action.doAction({
            type: "ir.actions.act_window",
            name: model_name,
            res_model: model_name,
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: domain,
        });
    }
}

DynamicDashboard.template = "DynamicDashboard";
registry.category("actions").add("dynamic_dashboard", DynamicDashboard);
