from odoo.osv import expression
import babel.dates
from odoo import api, models, _
# from odoo.tools import (
#     clean_context, config, CountingStream, date_utils, discardattr,
#     DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, frozendict,
#     get_lang, LastOrderedSet, lazy_classproperty, OrderedSet, ormcache,
#     partition, populate, Query, ReversedIterable, split_every, unique,
# )
import datetime
from markupsafe import escape
from odoo.tools import pycompat
from markupsafe import Markup
from collections import OrderedDict
import dateutil
import pytz



class Image(models.AbstractModel):
    _inherit = 'ir.qweb.field.image'
    

    @api.model
    def record_to_html(self, record, field_name, options):
        assert options['tagName'] != 'img',\
            "Oddly enough, the root tag of an image field can not be img. " \
            "That is because the image goes into the tag, or it gets the " \
            "hose again."

        src = src_zoom = None
        if 'zoom' in options and not options.get('zoom') and options.get('type') and options.get('type') == 'image':
            options['zoom'] = 'image_1920'
            
        if options.get('qweb_img_raw_data', False):
            value = record[field_name]
            if value is False:
                return False
            src = self._get_src_data_b64(value, options)
        else:
            src, src_zoom = self._get_src_urls(record, field_name, options)

        aclasses = ['img', 'img-fluid'] if options.get('qweb_img_responsive', True) else ['img']
        aclasses += options.get('class', '').split()
        classes = ' '.join(map(escape, aclasses))

        if options.get('alt-field') and options['alt-field'] in record and record[options['alt-field']]:
            alt = escape(record[options['alt-field']])
        elif options.get('alt'):
            alt = options['alt']
        else:
            alt = escape(record.display_name)

        itemprop = None
        if options.get('itemprop'):
            itemprop = options['itemprop']
        atts = OrderedDict()
        atts["src"] = src
        atts["itemprop"] = itemprop
        atts["class"] = classes
        atts["style"] = options.get('style')
        atts["width"] = options.get('width')
        atts["height"] = options.get('height')
        atts["alt"] = alt
        atts["data-zoom"] = src_zoom and u'1' or None
        atts["data-zoom-image"] = src_zoom
        atts["data-no-post-process"] = options.get('data-no-post-process')

        atts = self.env['ir.qweb']._post_processing_att('img', atts)

        img = ['<img']
        for name, value in atts.items():
            if value:
                img.append(' ')
                img.append(escape(name))
                img.append('="')
                img.append(escape(value))
                img.append('"')
        img.append('/>')

        return Markup(''.join(img))