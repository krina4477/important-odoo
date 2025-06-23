/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import { QUARTERS, PERIOD_OPTIONS, QUARTER_OPTIONS, setParam, getSelectedOptions, sortPeriodOptions, getMonthPeriodOptions, getComparisonParams, getSetParam} from "@web/search/utils/dates";
import { Domain } from "@web/core/domain";
import { serializeDate, serializeDateTime } from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";
import { SearchModel } from "@web/search/search_model";
export const DEFAULT_PERIOD = "this_month";
import { clamp } from "@web/core/utils/numbers";

QUARTERS[1] = { description: _t("Q1"), coveredMonths: [4, 5, 6] },
QUARTERS[2] = { description: _t("Q2"), coveredMonths: [7, 8, 9] },
QUARTERS[3] = { description: _t("Q3"), coveredMonths: [10, 11, 12] },
QUARTERS[4] = { description: _t("Q4"), coveredMonths: [1, 2, 3] },

QUARTER_OPTIONS['second_quarter'] = {
        id: "second_quarter",
        groupNumber: 1,
        description: QUARTERS[2].description,
        setParam: { quarter: 2 },
        granularity: "quarter",
    },

QUARTER_OPTIONS['third_quarter'] = {
        id: "third_quarter",
        groupNumber: 1,
        description: QUARTERS[3].description,
        setParam: { quarter: 3 },
        granularity: "quarter",
    },

QUARTER_OPTIONS['fourth_quarter'] = {
        id: "fourth_quarter",
        groupNumber: 1,
        description: QUARTERS[4].description,
        setParam: { quarter: 4 },
        granularity: "quarter",
    },

QUARTER_OPTIONS['first_quarter'] = {
        id: "first_quarter",
        groupNumber: 1,
        description: QUARTERS[1].description,
        setParam: { quarter: 1 },
        granularity: "quarter",
    },

export function getQuarterPeriodOptionsCustom(optionsParams) {
    const { startYear, endYear } = optionsParams;
    const defaultYearId = toGeneratorId("year", clamp(0, startYear, endYear));
    return Object.values(QUARTER_OPTIONS).map((quarter) => ({
        ...quarter,
        defaultYearId,
    }));
}

export function constructDateDomainCustom(
    referenceMoment,
    searchItem,
    selectedOptionIds,
    comparisonOptionId
) {
    let plusParam;
    let selectedOptions;
    if (comparisonOptionId) {
        [plusParam, selectedOptions] = getComparisonParams(
            referenceMoment,
            searchItem,
            selectedOptionIds,
            comparisonOptionId
        );
    } else {
        selectedOptions = getSelectedOptionsCustom(referenceMoment, searchItem, selectedOptionIds);
    }
    if ("withDomain" in selectedOptions) {
        return {
            description: selectedOptions.withDomain[0].description,
            domain: Domain.and([selectedOptions.withDomain[0].domain, searchItem.domain]),
        };
    }
    const yearOptions = selectedOptions.year;
    const otherOptions = [...(selectedOptions.quarter || []), ...(selectedOptions.month || [])];
    sortPeriodOptions(yearOptions);
    sortPeriodOptions(otherOptions);
    const ranges = [];
    const { fieldName, fieldType } = searchItem;
    for (const yearOption of yearOptions) {
        const constructRangeParams = {
            referenceMoment,
            fieldName,
            fieldType,
            plusParam,
        };
        if (otherOptions.length) {
            for (const option of otherOptions) {
                const setParam = Object.assign(
                    {},
                    yearOption.setParam,
                    option ? option.setParam : {}
                );
                const { granularity } = option;
                const range = constructDateRangeCustom(
                    Object.assign({ granularity, setParam }, constructRangeParams)
                );
                ranges.push(range);
            }
        } else {
            const { granularity, setParam } = yearOption;
            const range = constructDateRangeCustom(
                Object.assign({ granularity, setParam }, constructRangeParams)
            );
            ranges.push(range);
        }
    }
    let domain = Domain.combine(
        ranges.map((range) => range.domain),
        "OR"
    );
    domain = Domain.and([domain, searchItem.domain]);
    const description = ranges.map((range) => range.description).join("/");
    return { domain, description };
}

export function getPeriodOptionsCustom(referenceMoment, optionsParams) {
    return [
        ...getMonthPeriodOptionsCustom(referenceMoment, optionsParams),
        ...getQuarterPeriodOptionsCustom(optionsParams),
        ...getYearPeriodOptionsCustom(referenceMoment, optionsParams),
        ...getCustomPeriodOptionsCustom(optionsParams),
    ];
}

function getYearPeriodOptionsCustom(referenceMoment, optionsParams) {
    const { startYear, endYear } = optionsParams;
    return [...Array(endYear - startYear + 1).keys()]
        .map((i) => {
            const offset = startYear + i;
            const date = referenceMoment.plus({ years: offset });
            return {
                id: toGeneratorId("year", offset),
                description: date.toFormat("yyyy"),
                granularity: "year",
                groupNumber: 2,
                plusParam: { years: offset },
            };
        })
        .reverse();
}

function getCustomPeriodOptionsCustom(optionsParams) {
    const { customOptions } = optionsParams;
    return customOptions.map((option) => ({
        id: option.id,
        description: option.description,
        granularity: "withDomain",
        groupNumber: 3,
        domain: option.domain,
    }));
}

function getMonthPeriodOptionsCustom(referenceMoment, optionsParams) {
    const { startYear, endYear, startMonth, endMonth } = optionsParams;
    return [...Array(endMonth - startMonth + 1).keys()]
        .map((i) => {
            const monthOffset = startMonth + i;
            const date = referenceMoment.plus({
                months: monthOffset,
                years: clamp(0, startYear, endYear),
            });
            const yearOffset = date.year - referenceMoment.year;
            return {
                id: toGeneratorId("month", monthOffset),
                defaultYearId: toGeneratorId("year", clamp(yearOffset, startYear, endYear)),
                description: date.toFormat("MMMM"),
                granularity: "month",
                groupNumber: 1,
                plusParam: { months: monthOffset },
            };
        })
        .reverse();
}

export function toGeneratorId(unit, offset) {
    if (!offset) {
        return unit;
    }
    const sep = offset > 0 ? "+" : "-";
    const val = Math.abs(offset);
    return `${unit}${sep}${val}`;
}

function constructDateRangeCustom(params) {
    const { referenceMoment, fieldName, fieldType, granularity, setParam, plusParam } = params;
    if ("quarter" in setParam) {
        // Luxon does not consider quarter key in setParam (like moment did)
        setParam.month = QUARTERS[setParam.quarter].coveredMonths[0];
        delete setParam.quarter;
    }
    const date = referenceMoment.set(setParam).plus(plusParam || {});
    // compute domain
    const leftDate = date.startOf(granularity);
    const rightDate = date.endOf(granularity);
    let leftBound;
    let rightBound;
    if (fieldType === "date") {
        leftBound = serializeDate(leftDate);
        rightBound = serializeDate(rightDate);
    } else {
        leftBound = serializeDateTime(leftDate);
        rightBound = serializeDateTime(rightDate);
    }
    const domain = new Domain(["&", [fieldName, ">=", leftBound], [fieldName, "<=", rightBound]]);
    // compute description
    const descriptions = [date.toFormat("yyyy")];
    const method = localization.direction === "rtl" ? "push" : "unshift";
    if (granularity === "month") {
        descriptions[method](date.toFormat("MMMM"));
    } else if (granularity === "quarter") {
        if ( 4 <= date.c.month && date.c.month <= 6 ){
            var quarter = 1
        }
        else if ( 7 <= date.c.month && date.c.month <= 9 ){
            var quarter = 2
        }
        else if ( 10 <= date.c.month && date.c.month <= 12 ){
            var quarter = 3
        }
        else if ( 1 <= date.c.month && date.c.month <= 3 ){
            var quarter = 4
        }
        else {
            var quarter = date.quarter
        }
        descriptions[method](QUARTERS[quarter].description.toString());
    }
    const description = descriptions.join(" ");
    return { domain, description };
}

function getSelectedOptionsCustom(referenceMoment, searchItem, selectedOptionIds) {
    const selectedOptions = { year: [] };
    const periodOptions = getPeriodOptionsCustom(referenceMoment, searchItem.optionsParams);
    for (const optionId of selectedOptionIds) {
        const option = periodOptions.find((option) => option.id === optionId);
        const granularity = option.granularity;
        if (!selectedOptions[granularity]) {
            selectedOptions[granularity] = [];
        }
        if (option.domain) {
            selectedOptions[granularity].push(pick(option, "domain", "description"));
        } else {
            const setParam = getSetParam(option, referenceMoment);
            selectedOptions[granularity].push({ granularity, setParam });
        }
    }
    return selectedOptions;
}