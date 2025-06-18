from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class ProductWeb(WebsiteSale):
    
    @http.route(['/get/product/files'], type='json', auth="public", website=True)
    def get_product_rec(self, product_id):
        print("*********this is get product rec",product_id)
        product_id = request.env['product.product'].sudo().browse([int(product_id)])
        print("******product_id",product_id.product_3d_image_ids)
        data = {}
        variant = product_id.product_3d_image_ids
        image_url = f'/web/image/product.3d.image/{variant.id}/prod_3d_img'
        data['glb_image_url'] = image_url
        data['variant_id'] = variant.id
        data['variant_name'] = variant.name
        # request.session.glb_image_url = image_url
        # print("---------data",request.session.glb_image_url)
        
        print("********data",data)
        data['product_id'] = product_id.id
        return data
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # data = {}
        # variants = product_id.product_variant_ids
        # print("*********** Product Variants:", variants)

        # # Collect 3D image data
        # for variant in variants:
        #     for image in variant.product_3d_image_ids:
        #         image_url = f'/web/image/product.3d.image/{image.id}/prod_3d_img'
        #         data['glb_image_url'] = image_url
        #         data['product_name'] = variant.name
        #         # data.append({
                #     'variant_id': variant.id,
                #     'product_name': variant.name,
                #     'glb_image_url': image_url,
                # })

        # print("***** variant_image_data:", variant_image_data)
                
        # variant_images = list(product_id.product_3d_image_ids)
        # print("*****variant images",variant_images)
        # image_ids = []
        # if variant_images:
        #     image_ids = variant_images 
        # for rec in image_ids:
        #     print("*****rec._name",rec._name)
        #     if rec._name == 'product.3d.image':
        #         if rec.prod_3d_img:
        #             data['glb_image_url'] = '/web/image/product.3d.image/%s/prod_3d_img' % rec.id
        #             data['product_name'] = product_id.name
    
    
    


#     @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True, readonly=True)
#     def product(self, product, category='', search='', **kwargs):

#         product = product
#         print("***********product page",product)
#         res = super(ProductWeb, self).product(product=product)
        
#         product_id = request.env['product.product'].sudo().browse([product.id])
#         print("******product_id",product_id)
#         variant_images = list(product_id.product_3d_image_ids)
#         print("*****variant images",variant_images)
#         image_ids = []
#         glb_image_url = ''
#         product_name = ''
#         if variant_images:
#             image_ids = variant_images 
#         for rec in image_ids:
#             print("*****rec._name",rec._name)
#             if rec._name == 'product.3d.image':
#                 if rec.prod_3d_img:
#                     glb_image_url = '/web/image/product.3d.image/%s/prod_3d_img' % rec.id
#                     product_name = product_id.name
#         print("********glb_image_url,product_name",glb_image_url,product_name)
        
#         res.qcontext.update({
#                 'glb_image_url': glb_image_url,
#                 'product_name': product_name,
#         })
        
#         return res