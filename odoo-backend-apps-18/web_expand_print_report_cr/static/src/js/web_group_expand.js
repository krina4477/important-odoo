/** @odoo-module **/
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
// import { session } from '@web/session';
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";
import { download } from "@web/core/network/download";
import { onPatched } from "@odoo/owl";

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        // this.rpc = useService("rpc");
        if (this.props.groupBy.length){
            $(".oe_group_by_expand_buttons").removeClass('o_hidden');
        }

        onPatched(() => {
            if (this.props.groupBy.length){
                $(".oe_group_by_expand_buttons").removeClass('o_hidden');
            }
            else{
                $(".oe_group_by_expand_buttons").addClass('o_hidden');
            }
        });
    },

    expandAllGroups() {
        var layer = this.model.root.groups;
        while (layer.length) {
            if (layer && !layer[0]) {
                break;
            }
            var closed = layer.filter(function (group) {
                return group.isFolded;
            });
            if (closed.length) {
                this._toggleGroups(closed);
                break;
            }
            layer = _.flatten(
                layer.map(function (group) {
                    return group.list.groups;
                }),
                true
            );
        }
    },

    collapseAllGroups() {
        var layer = this.model.root.groups.filter(function (group) {
            return !group.isFolded;
        });
        while (layer.length) {
            var next = _.flatten(
                layer.map(function (group) {
                    if (group.list.groups) {
                        return group.list.groups;
                    }
                }),
                true
            ).filter(function (group) {
                if (typeof group !== "undefined") {
                    return !group.isFolded;
                }
            });

            if (!next.length) {
                this._toggleGroups(layer);
                break;
            }
            layer = next;
        }
    },

    _toggleGroups: function (groups) {
        var self = this;
        if (Object.keys(groups).length != 0) {
            var defs = groups.map(function (group) {
                return self.__owl__.props.Renderer.prototype.toggleGroup(group);
            });
            $.when(...defs).then(
                this._toggleGroups.bind(this, {}, { keepSelection: true, reload: false })
            );
        }
    },

    onClickPrintReport(export_type) {
        var self = this;
        var export_type = export_type.currentTarget.title;

        var header_eles = $(".o_list_renderer > table > thead");
        var header_eles = $(".o_list_renderer > table > thead");

        var header_name_list = [];
        $.each(header_eles, function () {
            var $header_ele = $(this);
            var header_td_elements = $header_ele.find("th");
            $.each(header_td_elements, function () {
                var $header_td = $(this);
                var text = $header_td.text().trim() || "";
                var data_id = $header_td.attr("data-name");
                header_name_list.push({
                    header_name: text.trim(),
                    header_data_id: data_id,
                });
            });
        });

        var data_eles = $(
            ".o_list_renderer >  table > tbody > tr:not(.o_add_record_row)"
        );

        var export_data = [];
        $.each(data_eles, function () {
            var data = [];
            var $data_ele = $(this);
            var is_analysis = false;

            var is_header_group = $(this).hasClass("o_group_header") ? true : false;
            if ($data_ele.text().trim()) {
                var extra_td = 0;
                var group_th_eles = $data_ele.find("th");

                $.each(group_th_eles, function () {
                    var $group_th_ele = $(this);
                    var text = $group_th_ele.text().trim() || "";
                    var is_analysis = true;
                    if ($(this).hasClass("o_group_name")) {
                        var level = $(this).children().children().css("--o-list-group-level")
                        var pixel = (2 + parseInt(level) * 20) + 'px'

                    }
                    var padding_left = $(this).hasClass("o_group_name") ? pixel : '0px';
                    if (text) {
                        if (
                            $group_th_ele.attr("colspan") &&
                            parseInt($group_th_ele.attr("colspan")) > 1
                        ) {
                            data.push({
                                "padding-left": padding_left,
                                group_row: is_header_group,
                                data: text,
                                bold: true,
                                colspan: $group_th_ele.attr("colspan"),
                            });
                        } else {
                            data.push({
                                "padding-left": padding_left,
                                group_row: is_header_group,
                                data: text,
                                bold: true,
                                colspan: 1,
                            });
                        }
                    }
                });

                var data_td_eles = $data_ele.find("td");

                $.each(data_td_eles, function () {
                    var $data_td_ele = $(this);
                    var text = $data_td_ele.text().trim() || "";
                    if ($data_td_ele.hasClass("o_list_record_selector")) {
                        data.push({ data: "", colspan: 1, group_row: false });
                    } else if (
                        $data_td_ele &&
                        $data_td_ele[0].classList.contains("oe_number") &&
                        !$data_td_ele[0].classList.contains("oe_list_field_float_time")
                    ) {
                        var text = text.replace("%", "");
                        var text = formats.parse_value(text, { type: "string" });

                        if (
                            $data_td_ele.attr("colspan") &&
                            parseInt($data_td_ele.attr("colspan")) > 1
                        ) {
                            data.push({
                                group_row: is_header_group,
                                data: text || "",
                                number: true,
                                colspan: $group_th_ele.attr("colspan"),
                            });
                        } else {
                            data.push({
                                group_row: is_header_group,
                                data: text || "",
                                number: true,
                                colspan: 1,
                            });
                        }
                    } else {
                        if (
                            $data_td_ele.attr("colspan") &&
                            parseInt($data_td_ele.attr("colspan")) > 1
                        ) {
                            data.push({
                                group_row: is_header_group,
                                data: text,
                                colspan: $data_td_ele.attr("colspan"),
                            });
                        } else {
                            data.push({ group_row: is_header_group, data: text, colspan: 1 });
                        }
                    }
                });

                var data_length = 0;
                $.each(data, function (dt) {
                    data_length += parseInt(dt.colspan);
                });

                if (data && header_name_list.length > data_length) {
                    var rows_to_add = header_name_list.length - data_length;
                    for (var il = 0; il < rows_to_add; il++) {
                        data.push({ group_row: is_header_group, data: "" });
                    }
                }

                export_data.push(data);
            }
        });

        var footer_eles = $(".o_list_renderer >  table > tfoot > tr");
        $.each(footer_eles, function () {
            var data = [];
            var $footer_ele = $(this);
            var footer_td_eles = $footer_ele.find("td");
            $.each(footer_td_eles, function () {
                var $footer_td_ele = $(this);
                var text = $footer_td_ele.text().trim() || "";
                if (
                    $footer_td_ele &&
                    $footer_td_ele[0].classList.contains("oe_number")
                ) {
                    var text = formats.parse_value(text, { type: "float" });
                    data.push({ data: text || "", bold: true, number: true });
                } else {
                    data.push({ data: text, bold: true });
                }
            });
            export_data.push(data);
        });

        this.env.services.ui.block();
        if (export_type === "Excel") {
            const url =  '/web/export/excel_export';
            const data = {
                data: JSON.stringify({
                    model: self.props.resModel,
                headers: header_name_list,
                rows: export_data,
                })
            }
            this.env.services.ui.unblock();
            return download({ url, data });
        }
        else {
            const activeIds = this.model.root.records.map((datapoint) => datapoint.resId);

            this.orm.call("res.users", "read", [user.userId, ["company_id"]],
            ).then((res) => this.orm.call("res.company", "read", [res[0]["company_id"][0], ["name"]])
            ).then((result) => {
                const url = "/pdf/reports";
                const data = {
                        data: JSON.stringify({
                            uid: user.userId,
                            model: self.props.resModel,
                            headers: header_name_list,
                            rows: export_data,
                            company_name: result[0].name,
                            res_ids: activeIds,
                        }),
                    }
                this.env.services.ui.unblock()
                return download({ url, data });
                });
            };
        }
    },
);
