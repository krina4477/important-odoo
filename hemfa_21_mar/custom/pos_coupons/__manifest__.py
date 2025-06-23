# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name"                  :  "Pos Coupons And Vouchers",
    "summary"               :  """The module allows you to create discount coupons and vouchers in Odoo POS. The voucher code can be used by the customer to obtain discount on orders.Voucher and Coupons|Custom Coupons|Custom Voucher|Custom Voucher and Coupons""",
    "category"              :  "Point of Sale",
    "version"               :  "1.0.4",
    "sequence"              :  1,
    "author"                :  "Webkul Software Pvt. Ltd.",
    "license"               :  "Other proprietary",
    "website"               :  "https://store.webkul.com/OpenERP-POS-Coupons.html",
    "description"           :  """POS coupons & Vouchers
                                Odoo POS coupons
                                POS vouchers
                                Voucher code
                                Coupon code
                                Manage vouchers
                                Discount coupons
                                Discount vouchers
                                Sale vouchers
                                Coupons & vouchers
                                POS discount sale
                                coupon discount
                                Give discount on POS
                                POS discount coupons
                                Odoo POS discount
                                Discount code POS""",
    "live_test_url"         :  "https://odoodemo.webkul.com/?module=pos_coupons&custom_url=/pos/auto",
    "depends"               :   ['point_of_sale', 'wk_coupons'],
    "data"                  :   [
                                    'data/coupon_data_view.xml',
                                    'views/inherited_voucher_history_view.xml',
                                    'views/pos_coupons_view.xml',
                                ],
    "images"                :  ['static/description/Banner.png'],
    "application"           :  True,
    "installable"           :  True,
    "assets"                :   {
                                    'point_of_sale.assets': [
                                        "/pos_coupons/static/src/js/pos_coupon.js",
                                        "/pos_coupons/static/src/css/pos_coupon.css",
                                        "/pos_coupons/static/src/xml/*.xml"
                                    ],
                                },
    "auto_install"          :  False,
    "price"                 :  124,
    "currency"              :  "USD",
    "pre_init_hook"         :  "pre_init_check",
}
