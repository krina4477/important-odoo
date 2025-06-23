/** @odoo-module **/

import { Domain } from "@web/core/domain";
import { makeContext } from "@web/core/context";
import { SearchModel } from "@web/search/search_model";

import { patch } from "@web/core/utils/patch";
import {constructDateDomainCustom} from '@indian_quarter_date_filter_groupby/js/date'
import {getPeriodOptionsCustom} from '@indian_quarter_date_filter_groupby/js/date'


patch(SearchModel.prototype, {
//    setup(services) {
//        super.setup(...arguments);
////        this.optionGenerators = getPeriodOptionsCustom(this.referenceMoment);
//    },
    getFullComparison() {
        let searchItem = null;
        for (const queryElem of this.query.slice().reverse()) {
            const item = this.searchItems[queryElem.searchItemId];
            if (item.type === "comparison") {
                searchItem = item;
                break;
            } else if (item.type === "favorite" && item.comparison) {
                searchItem = item;
                break;
            }
        }
        if (!searchItem) {
            return null;
        } else if (searchItem.type === "favorite") {
            return searchItem.comparison;
        }
        const { dateFilterId, comparisonOptionId } = searchItem;
        const { fieldName, fieldType, description: dateFilterDescription } = this.searchItems[
            dateFilterId
        ];
        const selectedGeneratorIds = this._getSelectedGeneratorIds(dateFilterId);
        // compute range and range description
        const { domain: range, description: rangeDescription } = constructDateDomainCustom(
            this.referenceMoment,
            fieldName,
            fieldType,
            selectedGeneratorIds
        );
        // compute comparisonRange and comparisonRange description
        const {
            domain: comparisonRange,
            description: comparisonRangeDescription,
        } = constructDateDomainCustom(
            this.referenceMoment,
            fieldName,
            fieldType,
            selectedGeneratorIds,
            comparisonOptionId
        );
        return {
            comparisonId: comparisonOptionId,
            fieldName,
            fieldDescription: dateFilterDescription,
            range: range.toList(),
            rangeDescription,
            comparisonRange: comparisonRange.toList(),
            comparisonRangeDescription,
        };
    },

    _getDateFilterDomain(dateFilter, generatorIds, key = "domain") {
        const dateFilterRange = constructDateDomainCustom(this.referenceMoment, dateFilter, generatorIds);
        return dateFilterRange[key];
    },

    _enrichItem(searchItem) {
        if (searchItem.type === "field" && searchItem.fieldType === "properties") {
            return { ...searchItem };
        }
        const queryElements = this.query.filter(
            (queryElem) => queryElem.searchItemId === searchItem.id
        );
        const isActive = Boolean(queryElements.length);
        const enrichSearchItem = Object.assign({ isActive }, searchItem);
        function _enrichOptions(options, selectedIds) {
            return options.map((o) => {
                const { description, id, groupNumber } = o;
                const isActive = selectedIds.some((optionId) => optionId === id);
                return { description, id, groupNumber, isActive };
            });
        }
        switch (searchItem.type) {
            case "comparison": {
                const { dateFilterId } = searchItem;
                const dateFilterIsActive = this.query.some(
                    (queryElem) =>
                        queryElem.searchItemId === dateFilterId &&
                        !queryElem.generatorId.startsWith("custom")
                );
                if (!dateFilterIsActive) {
                    return null;
                }
                break;
            }
            case "dateFilter":
                enrichSearchItem.options = _enrichOptions(
                    getPeriodOptionsCustom(this.referenceMoment, searchItem.optionsParams),
                    queryElements.map((queryElem) => queryElem.generatorId)
                );
                break;
            case "dateGroupBy":
                enrichSearchItem.options = _enrichOptions(
                    this.intervalOptions,
                    queryElements.map((queryElem) => queryElem.intervalId)
                );
                break;
            case "field":
            case "field_property":
                enrichSearchItem.autocompleteValues = queryElements.map(
                    (queryElem) => queryElem.autocompleteValue
                );
                break;
        }
        return enrichSearchItem;
    }
})


