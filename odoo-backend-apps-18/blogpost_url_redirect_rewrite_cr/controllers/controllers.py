# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo import http, fields, tools
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request

from odoo.tools import sql


class MyController(WebsiteBlog):

    @http.route([
        '''/blog/<model("blog.blog"):blog>/<model("blog.post", "[('blog_id','=',blog.id)]"):blog_post>''',
        '/page/<string:name>',
    ], type='http', auth="public", website=True, sitemap=True)
    def blog_post(self, name='',blog=None, blog_post=None, tag_id=None, page=1, enable_editor=None, **post):
        path = request.httprequest.path
        slug = request.env['ir.http']._slug
        if path.startswith('/blog'):
            redirect_id = request.env['website.seo.redirection'].search([('origin', '=', path)])
            if redirect_id.origin:
                return request.redirect(redirect_id.destination)
        # try:
        redirect_id = request.env['website.seo.redirection'].search([('destination', '=', "/page/"+name)])

        if redirect_id:
            blog_id = redirect_id.origin.split('/')[2].split('-')[-1]
            blog_post_id = redirect_id.origin.split('/')[-1].split('-')[-1]
            if blog_id and blog_post_id:
                blog = request.env['blog.blog'].browse(int(blog_id))
                blog_post = request.env['blog.post'].browse(int(blog_post_id))
                if not blog_post and not blog:
                    raise

        BlogPost = request.env['blog.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        domain = request.website.website_domain()
        blogs = blog.search(domain, order="create_date, id asc")

        tag = None
        if tag_id:
            tag = request.env['blog.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin,
                            date_end=date_end)

        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/blog/%s/%s" % (slug(blog_post.blog_id), slug(blog_post)), code=301)

        tags = request.env['blog.tag'].search([])

        # Find next Post
        blog_post_domain = [('blog_id', '=', blog.id)]
        if not request.env.user.has_group('website.group_website_designer'):
            blog_post_domain += [('post_date', '<=', fields.Datetime.now())]

        all_post = BlogPost.search(blog_post_domain)

        if blog_post not in all_post:
            return request.redirect("/blog/%s" % (slug(blog_post.blog_id)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blogs': blogs,
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'date': date_begin,
            'blog_url': blog_url,
        }
        response = request.render("website_blog.blog_post_complete", values)

        if blog_post.id not in request.session.get('posts_viewed', []):
            if sql.increment_fields_skiplock(blog_post, 'visits'):
                if not request.session.get('posts_viewed'):
                    request.session['posts_viewed'] = []
                request.session['posts_viewed'].append(blog_post.id)
                request.session.modified = True
        return response
