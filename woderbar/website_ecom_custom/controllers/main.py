# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, http
from odoo.http import request
# from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSaleDelivery):

    # override method for stop creating address of odoo default flow
    def checkout_check_address(self, order):
        # res = super().checkout_check_address(order)
        return False

    def _get_search_order(self, post):
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        return 'name asc'

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        brand_list = request.httprequest.args.getlist('brand')
        brand_values = [[x for x in v.split("-")] for v in brand_list if v]
        brands_ids = {int(v[1]) for v in brand_values}

        domain = []

        # Feature values for domain search
        feature_list = request.httprequest.args.getlist('attrib_feature')
        feature_values = [int(f) for f in feature_list]
        if feature_values:
            domain.append(('feature_id', 'in', feature_values))

        # Categories values for domain search
        category_list = request.httprequest.args.getlist('attrib_category')
        category_values = [int(cat) for cat in category_list]
        if category_values:
            domain.append(('public_categ_ids', 'in', category_values))

        # Vehicle Model values for domain search
        fahrzeug_modell_list = request.httprequest.args.getlist('attrib_fahrzeug_modell')
        fahrzeug_modell_values = fahrzeug_modell_list and [int(cat) for cat in fahrzeug_modell_list  if cat != 'Select Model'] or []
        if fahrzeug_modell_values:
            domain.append(('vehicle_model_id', 'in', fahrzeug_modell_values))

        # Model Year values for domain search

        model_year_list = request.httprequest.args.getlist('attrib_model_year')
        model_year_values = model_year_list and [int(cat) for cat in model_year_list if cat != 'Select Year'] or []
        if model_year_values:
            domain.append(('manufacture_year_id', 'in', model_year_values))

        # Manufacturer Field of the values of Product
        manufacturer_values = [ml[1][0] for ml in request.httprequest.args.lists() if
                               ml[0].startswith('attrib_manufacturer')]
        if manufacturer_values:
            domain.append(('manufacture_name', 'in', manufacturer_values))

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        brands=brand_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list
        if brand_list:
            post['brands'] = brand_list

        Product = request.env['product.template'].with_context(bin_size=True)
        # search_product = .Productsearch(domain, order=self._get_search_order(post))
        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]
        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)
        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        # Search filter values based on depends
        model_year_filter = []
        manufact_year_filter = []
        categ_filter = []
        public_categ_filter = []
        hertesellar_filter = []
        if search_product:
            for att in search_product:
                for public_categ in att.public_categ_ids:
                    public_categ_filter.append(public_categ)

                if att.categ_id and (att.categ_id not in categ_filter):
                    categ_filter.append(att.categ_id )
                if att.vehicle_model_id:
                    for vehicle_id in att.vehicle_model_id:
                        model_year_filter.append(vehicle_id)
                if att.manufacture_year_id:
                    for year_id in att.manufacture_year_id:
                        manufact_year_filter.append(year_id)
                if att.manufacture_name:
                    hertesellar_filter.append(att.manufacture_name)
        values = {
            'search': search,
            'category': category,
            'categ_filter': list(set(categ_filter)) if categ_filter else [],
            'public_categ_filter': list(set(public_categ_filter)) if public_categ_filter else [],
            'model_year_filter': list(set(model_year_filter)) if model_year_filter else [],
            'manufact_year_filter': list(set(manufact_year_filter)) if manufact_year_filter else [],
            'hertesellar_filter': list(set(hertesellar_filter)) if hertesellar_filter else [],
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'feature_values':feature_values,
            'manufacturer_values':manufacturer_values,
            'category_values':category_values,
            'model_year_values':model_year_values,
            'fahrzeug_modell_values':fahrzeug_modell_values

        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    @http.route('/sale/order/update/address', type='json', auth='public')
    def order_update_address(self, order_id, delivery_address_vals, billing_address_vals, same_billing_address):
        order_obj = request.env['sale.order'].sudo().browse(order_id)
        if not order_obj.is_shipping_and_billing_address:
            order_obj.is_shipping_and_billing_address = True
        order_obj.update_shipping_billing_address(delivery_address_vals, billing_address_vals, same_billing_address)
        order_obj.onchange_partner_shipping_id()
        order_obj._compute_tax_id()
        return True

    @http.route()
    def shop_payment(self, **post):
        res = super(WebsiteSaleInherit, self).shop_payment(**post)
        render_values = res.qcontext
        order = request.website.sale_get_order()
        mode = ('edit', 'shipping')
        values, value_billing_val, errors = {}, {}, {}
        same_billing_shipping = False
        order.write({'partner_invoice_id': order.partner_id.id})
        if order.partner_id == order.partner_shipping_id:
            same_billing_shipping = True
        if request.env.user.partner_id == order.partner_id and not request.website.is_public_user():
            values['name'] = order.partner_id.name
            values['street'] = order.partner_id.street
            values['street2'] = order.partner_id.street2
            values['city'] = order.partner_id.city
        # if order.partner_shipping_id:
        #     order.partner_shipping_id.email = order.partner_id.email
        #     order.partner_shipping_id.phone = order.partner_id.phone
        if order.partner_shipping_id:
            order.partner_shipping_id.email = order.partner_id.email
            order.partner_shipping_id.phone = order.partner_id.phone
        if request.env.user.partner_id == order.partner_id and not request.website.is_public_user():
            values['email'] = order.partner_id.email
            values['phone'] = order.partner_id.phone
        can_edit_vat = order.partner_id.sudo().can_edit_vat()
        if not same_billing_shipping and request.env.user.partner_id == order.partner_id and not request.website.is_public_user():
            value_billing_val['name'] = order.partner_shipping_id.name
            value_billing_val['street'] = order.partner_shipping_id.street
            value_billing_val['street2'] = order.partner_shipping_id.street2
            value_billing_val['city'] = order.partner_shipping_id.city
        render_values_address = {
            'website_sale_order': order,
            'partner_id': order.partner_id if request.env.user.partner_id == order.partner_id and not request.website.is_public_user() else False,
            'mode': mode,
            'checkout': values,
            'checkout_billing': value_billing_val,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': post.get('callback'),
            'only_services': order and order.only_services,
            'same_billing_shipping': same_billing_shipping,
        }
        render_values.update(render_values_address)
        render_values.update(self._get_country_related_render_values(post, render_values_address))

        return request.render("website_ecom_custom.payment_wonderbar", render_values)

    @http.route('/shop/cart/paypal_payment', type='json', auth='public', website=True, sitemap=False)
    def shop_paypal_payment(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        acquirers = request.env['payment.acquirer'].sudo().search([('provider','=','paypal')])
        render_values.update({
            'order': render_values['order'].id,
            'paymentacquirer': acquirers.provider,
            'paymentOptionId': acquirers.id,
            'currencyId': render_values['currency'].id,
            'deliveries': render_values['deliveries'].id,
        })
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        mode = ('edit', 'shipping')
        values, value_billing_val, errors = {}, {}, {}
        same_billing_shipping = False
        order.write({'partner_invoice_id': order.partner_id.id})
        if order.partner_id == order.partner_shipping_id:
            same_billing_shipping = True
        values['name'] = order.partner_id.name
        values['street'] = order.partner_id.street
        values['street2'] = order.partner_id.street2
        values['city'] = order.partner_id.city
        if order.partner_shipping_id:
            order.partner_shipping_id.email = order.partner_id.email
            order.partner_shipping_id.phone = order.partner_id.phone
        values['email'] = order.partner_id.email
        values['phone'] = order.partner_id.phone
        can_edit_vat = order.partner_id.can_edit_vat()
        if not same_billing_shipping:
            value_billing_val['name'] = order.partner_shipping_id.name
            value_billing_val['street'] = order.partner_shipping_id.street
            value_billing_val['street2'] = order.partner_shipping_id.street2
            value_billing_val['city'] = order.partner_shipping_id.city
        render_values_address = {
            'website_sale_order': order,
            'partner_id': order.partner_id.id,
            'mode': mode,
            'checkout': values,
            'checkout_billing': value_billing_val,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': post.get('callback'),
            'only_services': order and order.only_services,
            'same_billing_shipping': same_billing_shipping,
        }
        render_values.update(render_values_address)
        render_values.update(self._get_country_related_render_values(post, render_values_address))
        render_values.pop('fees_by_acquirer')
        return render_values
    
    @http.route('/shop/product/paypal_payment', type='json', auth='public', website=True, sitemap=False)
    def product_info_paypal_payment(self, **post):
        order = request.website.product_info_sale_get_order(prod_qty=post['prod_qty'], product_id=post['product_id'])
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        acquirers = request.env['payment.acquirer'].sudo().search([('provider','=','paypal')])
        render_values.update({
            'order': render_values['order'].id,
            'paymentacquirer': acquirers.provider,
            'paymentOptionId': acquirers.id,
            'currencyId': render_values['currency'].id,
            'deliveries': render_values['deliveries'].id,
        })
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        mode = ('edit', 'shipping')
        values, value_billing_val, errors = {}, {}, {}
        same_billing_shipping = False
        order.write({'partner_invoice_id': order.partner_id.id})
        if order.partner_id == order.partner_shipping_id:
            same_billing_shipping = True
        values['name'] = order.partner_id.name
        values['street'] = order.partner_id.street
        values['street2'] = order.partner_id.street2
        values['city'] = order.partner_id.city
        if order.partner_shipping_id:
            order.partner_shipping_id.email = order.partner_id.email
            order.partner_shipping_id.phone = order.partner_id.phone
        values['email'] = order.partner_id.email
        values['phone'] = order.partner_id.phone
        can_edit_vat = order.partner_id.can_edit_vat()
        if not same_billing_shipping:
            value_billing_val['name'] = order.partner_shipping_id.name
            value_billing_val['street'] = order.partner_shipping_id.street
            value_billing_val['street2'] = order.partner_shipping_id.street2
            value_billing_val['city'] = order.partner_shipping_id.city
        render_values_address = {
            'website_sale_order': order,
            'partner_id': order.partner_id.id,
            'mode': mode,
            'checkout': values,
            'checkout_billing': value_billing_val,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': post.get('callback'),
            'only_services': order and order.only_services,
            'same_billing_shipping': same_billing_shipping,
        }
        render_values.update(render_values_address)
        render_values.update(self._get_country_related_render_values(post, render_values_address))
        render_values.pop('fees_by_acquirer')
        return render_values


class RadioSearch(http.Controller):

    @http.route('/find_model_year', type='json', auth="public", website=True, csrf=False)
    def find_model_year(self, manufacturer_value=None, **kw):
        radio_search = request.env['x_radio'].sudo().search([('x_studio_fahrzeug_hersteller', '=', manufacturer_value)])
        Baujahr_list = []
        Baujahr_l = []
        for radio in radio_search:
            for Baujahr in radio.x_studio_many2many_field_F53na:
                if Baujahr.id not in Baujahr_l:
                    Baujahr_l.append(Baujahr.id)
                    Baujahr_list.append((Baujahr.id, Baujahr.x_name))
        return dict(Baujahr=Baujahr_list)

    @http.route('/find_model_name', type='json', auth="public", website=True, csrf=False)
    def find_model_name(self, Fahrzeug_val, Baujahr_val, **kw):
        radio_search = request.env['x_radio'].sudo().search([
            ('x_studio_fahrzeug_hersteller', '=', Fahrzeug_val),
            ('x_studio_many2many_field_F53na', 'in', [int(Baujahr_val)] if Baujahr_val else [])
        ])
        Modell_list = []
        Modell_l = []
        for radio in radio_search:
            for Baujahr in radio.x_studio_many2many_field_VfxZV:
                if Baujahr.id not in Modell_l:
                    Modell_l.append(Baujahr.id)
                    Modell_list.append((Baujahr.id, Baujahr.x_name))
        return dict(Modell=Modell_list)

    @http.route(['/search_radio'], type='http', auth='public', website=True,csrf=False)
    def search_radio(self, **post):
        domain = []

        if post.get('model_year'):
            domain += [('x_studio_many2many_field_F53na', 'in', [int(post.get('model_year'))])]
        if post.get('manufacturer'):
            domain += [('x_studio_fahrzeug_hersteller', '=', post.get('manufacturer'))]
        if post.get('model_name'):
            domain += [('x_studio_many2many_field_VfxZV', 'in', [int(post.get('model_name'))])]

        radio_search = request.env['x_radio'].sudo().search(domain)
        return request.render("website_ecom_custom.search_radio_template", {'radios': radio_search, 'radio_count': len(radio_search)})

    @http.route(['/dab-empfang-wird-kommen-bleibt-das-radio-in-meinem-oldtimer-jetzt-stumm/'], type='http', auth='public', website=True, csrf=False)
    def search_car(self, **post):
        return request.render("website_ecom_custom.classic_car_template")

    @http.route(['/startseite/sendersuchlauf-oldtimer-radio/'], type='http', auth='public', website=True, csrf=False)
    def station_search(self, **post):
        return request.render("website_ecom_custom.classic_station_search_template")

    @http.route(['/product_info'], type='http', auth='public', website=True, csrf=False)
    def product_info_search(self, radio_id):
        radio = request.env['x_radio'].sudo().browse(int(radio_id))
        url = '/product_info/' + slug(radio)
        return request.redirect(url)

    @http.route(['/product_info/<model("x_radio"):radio>'], type='http', auth="public", website=True, sitemap=True)
    def product_radio(self, radio, **kwargs):
        return request.render("website_ecom_custom.product_info_template", {'radio': radio})

    @http.route(['/ersatzteile-fur-dein-radio/warenkorb'], type='http', auth='public', website=True, csrf=False)
    def shop_items(self, **post):
        return request.render("website_ecom_custom.cart_shop_template")

    @http.route(['/startseite/impressum/'], type='http', auth='public', website=True, csrf=False)
    def footer_impressum(self, **post):
        return request.render("website_ecom_custom.footer_impressum_template")

    @http.route(['/ersatzteile-fur-dein-radio/agb/'], type='http', auth='public', website=True, csrf=False)
    def footer_agb(self, **post):
        return request.render("website_ecom_custom.footer_agb_template")

    @http.route(['/startseite/datenschutz/'], type='http', auth='public', website=True, csrf=False)
    def footer_daten(self, **post):
        return request.render("website_ecom_custom.footer_daten_template")

    @http.route(['/startseite/installations-und-bedienungsanleitung/'], type='http', auth='public', website=True, csrf=False)
    def footer_installation(self, **post):
        return request.render("website_ecom_custom.footer_installation_template")

    @http.route(['/contact_us_radio'], type="http", auth='public', website=True, csrf=False)
    def contact_us_radio(self, **post):
        if post.get('email_from'):
            user_id = request.env['res.users'].sudo().browse(request.env.ref('base.user_admin').id)
            mail_id = request.env['mail.mail'].sudo().create({
                "email_from": post.get('email_from'),
                "email_to": user_id.login,
                "subject": "Contact Us",
                "author_id": user_id.partner_id.id,
                "body_html": "<p> Dear " + post.get('name') 
                + ", <br />" 
                + "Email: " + post.get('email_from') 
                + ", <br />" 
                + "Phone: " + post.get('phone')
                + ", <br />" 
                + "Radio type: " + post.get('description') + "</p>",
            })
            mail_id.send()
            return request.redirect('/contactus-thank-you')
        return request.redirect('/')


@http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
def checkout(self, **post):
    order = request.website.sale_get_order()

    redirection = self.checkout_redirection(order)
    if redirection:
        return redirection

    # if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
    #     return request.redirect('/shop/address')

    redirection = self.checkout_check_address(order)
    if redirection:
        return redirection

    values = self.checkout_values(**post)

    if post.get('express'):
        return request.redirect('/shop/confirm_order')

    values.update({'website_sale_order': order})

    # Avoid useless rendering if called in ajax
    if post.get('xhr'):
        return 'ok'
    return request.render("website_sale.checkout", values)

WebsiteSale.checkout = checkout
