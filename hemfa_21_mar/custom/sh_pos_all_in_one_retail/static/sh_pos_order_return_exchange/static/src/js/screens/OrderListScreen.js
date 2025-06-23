odoo.define('sh_pos_order_return_exchange.OrderListScreen', function (require, factory) {
    'use strict';

    const OrderListScreen = require('sh_pos_order_list.OrderListScreen')
    const Registries = require("point_of_sale.Registries");

    const ShPosOrderListScreen = (OrderListScreen) =>
        class extends OrderListScreen {
            constructor() {
                super(...arguments);
                this.order_no_return = [];
                this.return_filter = false;
            }

            get_order_by_name(name) {
                var self = this;
                if (self.return_filter) {
                    return _.filter(self.env.pos.db.all_return_order, function (template) {
                        if (template.name.indexOf(name) > -1) {
                            return true;
                        } else if (template['pos_reference'] && template["pos_reference"].indexOf(name) > -1) {
                            return true;
                        } else if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(name) > -1) {
                            return true;
                        } else if (template["date_order"].indexOf(name) > -1) {
                            return true;
                        } else {
                            return false;
                        }
                    });
                } else {
                    return _.filter(self.env.pos.db.all_non_return_order, function (template) {
                        if (template.name.indexOf(name) > -1) {
                            return true;
                        } else if (template['pos_reference'] && template["pos_reference"].indexOf(name) > -1) {
                            return true;
                        } else if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(name) > -1) {
                            return true;
                        } else if (template["date_order"].indexOf(name) > -1) {
                            return true;
                        } else {
                            return false;
                        }
                    });
                }
            }
            get posorderdetail() {
                var self = this;

                if ($('.sh-pos-order-filter') && $('.sh-pos-order-filter').length > 0 && $('.sh-pos-order-filter').val() != "all") {
                    var value = $('.sh-pos-order-filter').val()
                    var templates = _.filter(self.env.pos.db.all_display_order, function (template) {
                        if (template.state == value) {
                            return true;
                        } else {
                            return false
                        }
                    });
                    if (this.state.query && this.state.query.trim() !== "") {
                        var search = this.state.query.trim()
                        var templates = _.filter(templates, function (template) {
                            if (template.name.indexOf(search) > -1) {
                                return true;
                            } else if (template["pos_reference"].indexOf(search) > -1) {
                                return true;
                            } else if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(search) > -1) {
                                return true;
                            } else if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                                return true;
                            } else {
                                return false;
                            }
                        });
                        $(".sh_pagination").pagination("updateItems", Math.ceil(templates.length / self.env.pos.config.sh_how_many_order_per_page));
                        var current_page = $(".sh_pagination").find('.active').text();

                        var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(current_page) - 1);;
                        var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page);
                        templates = templates.slice(showFrom, showTo);

                        return templates
                    } else {
                        $(".sh_pagination").pagination("updateItems", Math.ceil(templates.length / self.env.pos.config.sh_how_many_order_per_page));
                        var current_page = $(".sh_pagination").find('.active').text();

                        var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(current_page) - 1);;
                        var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page);
                        templates = templates.slice(showFrom, showTo);

                        return templates
                    }

                } else {
                    if (this.state.query && this.state.query.trim() !== "") {
                        var templates = this.get_order_by_name(this.state.query.trim());
                        $(".sh_pagination").pagination("updateItems", Math.ceil(templates.length / self.env.pos.config.sh_how_many_order_per_page));
                        var pageNumber = $(".sh_pagination").find('.active').text();
                        var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber) - 1);
                        var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page);
                        templates = templates.slice(showFrom, showTo);
                        return templates;
                    } else {
                        self.order_no_return = [];
                        self.return_order = [];
                        _.each(self.env.pos.db.all_display_order, function (order) {
                            if ((order.is_return_order && order.return_status && order.return_status != "nothing_return") || (!order.is_return_order && !order.is_exchange_order)) {
                                self.order_no_return.push(order);
                            } else {
                                self.return_order.push(order);
                            }
                        });

                        var pageNumber = $(".sh_pagination").find('.active').text();
                        var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber) - 1);
                        var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page);

                        if (!self.return_filter) {
                            self.order_no_return = self.order_no_return.slice(showFrom, showTo);
                            if ($(".sh_pagination") && $(".sh_pagination").length) {

                                $(".sh_pagination").pagination("updateItems", Math.ceil(self.env.pos.db.all_non_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                            }
                            if (this.props.filter_by_partner){
                                const partner_filters =  _.filter(self.env.pos.db.all_display_order, function (template) {
                                    if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(self.props.filter_by_partner) > -1) {
                                        return true;
                                    } else {
                                        return false
                                    }
                                });

                                return partner_filters
                            }else{
                                return self.order_no_return;
                            }
                        } else {
                            self.return_order = self.return_order.slice(showFrom, showTo);
                            if ($(".sh_pagination") && $(".sh_pagination").length) {
                                $(".sh_pagination").pagination("updateItems", Math.ceil(self.env.pos.db.all_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                            }
                            return self.return_order;
                        }
                    }
                }

            }
            back() {
                this.trigger("close-temp-screen");
            }
            exchange_pos_order(event) {
                var self = this;
                self.env.pos.get_order().is_return = false;
                self.env.pos.get_order().is_exchange = true;
                var order_line = [];
                var order_list = [];
                var pos_order_line = [];
                for (let i = 0; i < this.env.pos.db.all_non_return_order.length; i++) {
                    var return_orderline = this.env.pos.db.all_non_return_order[i];
                    var selected_order_id = $(event.currentTarget.closest("tr")).attr("data-order-id")
                    var get_order_id = Number(selected_order_id)
                    if (return_orderline.id === get_order_id) {
                         order_list.push(return_orderline)
                    }

                }
                var order_id = $(event.currentTarget.closest("tr")).attr("data-order-id");
                if (order_id) {
                    order_data = self.env.pos.db.order_by_id[order_id];
                    if (!order_data) {
                        order_id = $(event.currentTarget.closest("tr")).attr("data-order");
                        var order_data = self.env.pos.db.order_by_uid[order_id];
                    }
                    if (!order_data) {
                        order_id = $(event.currentTarget.closest("tr")).attr("data-order");
                        console.log("not order_id",order_id)
                        var order_data = self.env.pos.db.order_by_uid[order_id];
                        console.log("order_data2",order_data)
                    }
                    if (order_data && order_data.lines) {
                        _.each(order_data.lines, function (each_order_line) {
                            var line_data = self.env.pos.db.order_line_by_id[each_order_line];

                            var product = self.env.pos.db.get_product_by_id(line_data.product_id)
                            if (!product){
                                product = self.env.pos.db.get_product_by_id(line_data.product_id[0])
                            }
                            if (line_data && product && !product.sh_product_non_exchangeable) {
                                order_line.push(line_data);
                            }
                        });
                    }
                    else if (order_list && order_list[0]['lines']) {
                        _.each(order_list[0]['lines'], function (each_line_order) {
                            var line_data_check = self.env.pos.db.order_line_by_id[each_line_order];

                            var products = self.env.pos.db.get_product_by_id(line_data_check.product_id)
                            if (!products){
                                products = self.env.pos.db.get_product_by_id(line_data_check.product_id[0])
                            }
                            if (line_data_check && products && !products.sh_product_non_exchangeable) {
                                pos_order_line.push(line_data_check);
                            }
                        });
                    }
                }

                this.env.pos.get_order()['is_exchange'] = true
                if (order_line && order_line.length > 0 ){
                    this.showPopup("ReturnOrderPopup", { lines: order_line, order: order_id });
                }else{
                    this.showPopup("ReturnOrderPopup", { lines: pos_order_line, order: order_list[0].id});
                }
//                if

            }
            return_pos_order(event) {
                var self = this;
                self.env.pos.get_order().is_return = true;
                self.env.pos.get_order().is_exchange = false;
                var order_line = [];
                var order_list = [];
                var pos_order_line = [];
                for (let i = 0; i < this.env.pos.db.all_non_return_order.length; i++) {
                    var return_orderline = this.env.pos.db.all_non_return_order[i];
                    var selected_order_id = $(event.currentTarget.closest("tr")).attr("data-order-id")
                    var get_order_id = Number(selected_order_id)
                    if (return_orderline.id === get_order_id) {
                         order_list.push(return_orderline)
                    }

                }

                var order_id = $(event.currentTarget.closest("tr")).attr("data-order-id");
                if (order_id) {
                    order_data = self.env.pos.db.order_by_id[order_id];
                    if (!order_data) {
                        order_id = $(event.currentTarget.closest("tr")).attr("data-order");
                        var order_data = self.env.pos.db.order_by_uid[order_id];
                    }

                    if (order_data && order_data.lines) {
                        _.each(order_data.lines, function (each_order_line) {
                            var line_data = self.env.pos.db.sh_get_orderline_by_id(each_order_line);
                            var product = self.env.pos.db.get_product_by_id(line_data.product_id)
                            if (!product){
                                product = self.env.pos.db.get_product_by_id(line_data.product_id[0])
                            }
                            if (line_data && !product.sh_product_non_returnable) {
                                order_line.push(line_data);
                            }
                        });
                    }
                     else if (order_list && order_list[0]['lines']) {
                        _.each(order_list[0]['lines'], function (each_line_order) {
                            var line_data_check = self.env.pos.db.order_line_by_id[each_line_order];

                            var products = self.env.pos.db.get_product_by_id(line_data_check.product_id)
                            if (!products){
                                products = self.env.pos.db.get_product_by_id(line_data_check.product_id[0])
                            }
                            if (line_data_check && !products.sh_product_non_returnable) {
                                pos_order_line.push(line_data_check);
                            }
                        });
                    }
                }
                this.env.pos.get_order()['is_return'] = true
                if (order_line && order_line.length > 0 ){

                    this.showPopup("ReturnOrderPopup", { lines: order_line, order: order_id });
                }else{
                       this.showPopup("ReturnOrderPopup", { lines: pos_order_line, order: order_list[0].id});

//                    self.showPopup('ErrorPopup',{
//                        title: self.env._t('Product !'),
//                        body: self.env._t('Not return order line found !')
//                    })
                }
            }
            return_order_filter() {
                var self = this;

                var previous_order = self.env.pos.db.all_order;
                if (!$(".return_order_button").hasClass("highlight")) {
                    self.order_no_return = [];
                    $(".return_order_button").addClass("highlight");

                    self.return_filter = true;
                    $(".sh_pagination").pagination("updateItems", Math.ceil(self.env.pos.db.all_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                    $(".sh_pagination").pagination("selectPage", 1);
                } else {
                    self.return_order = [];
                    $(".return_order_button").removeClass("highlight");
                    self.return_filter = false;

                    $(".sh_pagination").pagination("updateItems", Math.ceil(self.env.pos.db.all_non_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                    $(".sh_pagination").pagination("selectPage", 1);
                }
                self.render();
            }
        };
    Registries.Component.extend(OrderListScreen, ShPosOrderListScreen);

});
