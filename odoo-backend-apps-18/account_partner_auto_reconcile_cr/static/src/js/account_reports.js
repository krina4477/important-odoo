/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { AccountReportController } from "@account_reports/components/account_report/controller";

class PartnerActionReport extends AccountReportController{

    async reportAction(ev, action, actionParam = null, callOnSectionsSource = false){
        ev?.preventDefault();
        ev?.stopPropagation();

        let actionOptions = this.options;
        if (callOnSectionsSource) {
            // When calling the sections source, we want to keep track of all unfolded lines of all sections
            const allUnfoldedLines =  this.options.sections.length ? [] : [...this.options['unfolded_lines']]

            for (const sectionData of this.options['sections']) {
                const cacheKey = this.getCacheKey(this.options['sections_source_id'], sectionData['id']);
                const sectionOptions = await this.reportOptionsMap[cacheKey];
                if (sectionOptions)
                    allUnfoldedLines.push(...sectionOptions['unfolded_lines']);
            }

            actionOptions = {...this.options, unfolded_lines: allUnfoldedLines};
        }

        const dispatchReportAction = await this.orm.call(
            "account.report",
            "dispatch_report_action",
            [
                this.options['report_id'],
                actionOptions,
                action,
                actionParam,
                callOnSectionsSource,
            ],
        );
    }
};
