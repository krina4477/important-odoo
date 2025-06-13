/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SearchModel } from "@web/search/search_model";
import { DEFAULT_INTERVAL, getIntervalOptions, getPeriodOptions, rankInterval, yearSelected } from "@web/search/utils/dates";

patch(SearchModel.prototype , {

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
                // ADD Show Previous 12 Monthos
                searchItem.optionsParams.endMonth = 0;
                searchItem.optionsParams.endYear = 0;
                searchItem.optionsParams.startMonth = -11;
                searchItem.optionsParams.startYear = -1;

                enrichSearchItem.options = _enrichOptions(
                    getPeriodOptions(this.referenceMoment, searchItem.optionsParams),
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
     },

     toggleDateFilter(searchItemId, generatorId) {
        const searchItem = this.searchItems[searchItemId];
        if (searchItem.type !== "dateFilter") {
            return;
        }
        const generatorIds = generatorId ? [generatorId] : searchItem.defaultGeneratorIds;
        for (const generatorId of generatorIds) {
            const isYear = generatorId.startsWith("year");
            const index = this.query.findIndex(
                (queryElem) =>
                    queryElem.searchItemId === searchItemId &&
                    "generatorId" in queryElem &&
                    queryElem.generatorId === generatorId
            );

            if (index >= 0) {
                this.query.splice(index, 1);
                if (!yearSelected(this._getSelectedGeneratorIds(searchItemId))) {
                    // This is the case where generatorId was the last option
                    // of type 'year' to be there before being removed above.
                    // Since other options of type 'month' or 'quarter' do
                    // not make sense without a year we deactivate all options.
                    this.query = this.query.filter(
                        (queryElem) => queryElem.searchItemId !== searchItemId
                    );
                }

                const hasMonthGeneratorId = this.query.some(
                    (queryElem) => queryElem.generatorId && queryElem.generatorId.includes("month")
                );

                if (!hasMonthGeneratorId) {
                    const yearIndex = this.query.findIndex(
                        (queryElem) => queryElem.generatorId && queryElem.generatorId.includes("year")
                    );

                    if (yearIndex >= 0) {
                        this.query.splice(yearIndex, 1);
                    }
                }

            } else {
                if (generatorId.startsWith("custom")) {
                    const comparisonId = this._getActiveComparison()?.id;
                    this.query = this.query.filter(
                        (queryElem) =>
                            ![searchItemId, comparisonId].includes(queryElem.searchItemId)
                    );
                    this.query.push({ searchItemId, generatorId });
                    continue;
                }
                this.query = this.query.filter(
                    (queryElem) =>
                        queryElem.searchItemId !== searchItemId ||
                        !queryElem.generatorId.startsWith("custom")
                );
                this.query.push({ searchItemId, generatorId });
                if (!yearSelected(this._getSelectedGeneratorIds(searchItemId))) {
                    // Here we add 'year' as options if no option of type
                    // year is already selected.
                    const { defaultYearId } = getPeriodOptions(
                        this.referenceMoment,
                        searchItem.optionsParams
                    ).find((o) => o.id === generatorId);
                    this.query.push({ searchItemId, generatorId: defaultYearId });
                }
            }
        }
        this._checkComparisonStatus();
        this._notify();
    },

})






















