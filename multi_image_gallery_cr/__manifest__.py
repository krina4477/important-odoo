{
    'name': 'Multi-image Gallery',
    'version': '18.0.0.1',
    'summary': '',
    'description': 'Multi-image Gallery with Zoom/360° View in product page',
    'category': '',
    'author': 'Candidroot Pvt.Ltd.',
    'website': 'https://www.candidroot.com/',
    'maintainer': '',
    'sequence': 1,
    'license': 'LGPL-3',
    'depends': ['website_sale', 'website'],
    'data': [
        'security/ir.model.access.csv',
        
        'views/product_image_view.xml',
        'templates/attachment_file.xml',
    ],
    'installable': True,
    'application': True,    
    'assets': {
        'web.assets_frontend': [
            "https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js",
            'multi_image_gallery_cr/static/src/js/on_hover_slider.js',
            'multi_image_gallery_cr/static/src/js/product_glb_img.js',      
            
            'multi_image_gallery_cr/static/src/css/product_glb_img.css',      
        ],
    }
}




# multi_image_gallery_cr