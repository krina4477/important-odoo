odoo.define("hemfa_pos_attributes_values_viewer.OrderListScreen", function(require) {
    "use strict";
    const OrderListScreen = require("point_of_sale.PosComponent");
    const {patch} = require('web.utils');
    var session = require('web.session');

    patch(OrderListScreen.prototype, 'hemfa_pos_attributes_values_viewer/static/src/js/OrderListScreen.js', {
        onMounted() {
            var self = this;
            if (this.props.filter_by_partner) {
                $('.sh_pos_order_search').val(self.props.filter_by_partner);
                $('.sh_pos_order_search')[0].disabled = true;
            }
            $(".sh_pagination").pagination({
                pages: Math.ceil(self.env.pos.order_length / self.env.pos.config.sh_how_many_order_per_page),
                displayedPages: 1,
                edges: 1,
                cssStyle: "light-theme",
                showPageNumbers: false,
                showNavigator: true,
                onPageClick: function(pageNumber) {
                    try {
                        let context = Object(session.user_context);
                        context.with_attributes = true;
                        self.env.services.rpc({
                            model: "pos.order",
                            method: "search_order",
                            args: [self.env.pos.config, pageNumber + 1],
                            kwargs: {context:context }
                        }).then(function(orders) {
                            if (orders) {
                                if (orders["order"].length == 0) {
                                    $($(".next").parent()).addClass("disabled");
                                    $(".next").replaceWith(function() {
                                        $("<span class='current next'>Next</span>");
                                    });
                                }
                            }
                        })
                        self.env.services.rpc({
                            model: "pos.order",
                            method: "search_order",
                            args: [self.env.pos.config, pageNumber],
                            kwargs: {context:context }
                        }).then(async function(orders) {
                            self.env.pos.db.all_order = [];
                            self.env.pos.db.temp_order_by_id = {}
                            if (orders) {
                                if (orders["order"]) {
                                    self.env.pos.db.all_orders(orders["order"]);
                                }
                                if (orders["order_line"]) {
                                    self.env.pos.db.all_orders_line(orders["order_line"]);
                                }
                            }
                            self.all_order = self.env.pos.db.all_order;
                            self.render();
                        }).catch(function(reason) {
                            var templates = self.env.pos.db.all_display_order
                            $(".sh_pagination").pagination("updateItems", Math.ceil(templates.length / self.env.pos.config.sh_how_many_order_per_page));
                            var current_page = $(".sh_pagination").find('.active').text();
                            var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(current_page) - 1);
                            var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page);
                            templates = templates.slice(showFrom, showTo);
                            self.env.pos.db.all_order = templates
                            self.render();
                        })
                    } catch (error) {
                        console.log('error -> ', error)
                    }
                },
            });
            if (this.env.pos.db.all_order.length > 0) {
                var today = new Date();
                var dd = today.getDate();
                var mm = today.getMonth() + 1;
                var yyyy = today.getFullYear();
                var today_date = yyyy + "-" + mm + "-" + dd;
                if (this.env.pos.config.sh_load_order_by == "day_wise") {
                    if (this.env.pos.config.sh_day_wise_option == "current_day") {
                        this.env.pos.db.all_order = this.env.pos.get_current_day_order(this.env.pos.db.all_order);
                    } else if (this.env.pos.config.sh_day_wise_option == "last_no_day") {
                        if (this.env.pos.config.sh_last_no_days != 0) {
                            this.env.pos.db.all_order = this.env.pos.get_last_day_order(this.env.pos.db.all_order);
                        }
                    }
                } else if (this.env.pos.config.sh_load_order_by == "session_wise") {
                    if (this.env.pos.config.sh_session_wise_option == "current_session") {
                        this.env.pos.db.all_order = this.env.pos.get_current_session_order(this.env.pos.db.all_order);
                    } else if (this.env.pos.config.sh_session_wise_option == "last_no_session") {
                        if (this.env.pos.config.sh_last_no_session != 0) {
                            this.env.pos.db.all_order = this.env.pos.get_last_session_order(this.env.pos.db.all_order);
                        }
                    }
                }
            }
            $(".sh_pagination").pagination("selectPage", 1);
        }
    });
});