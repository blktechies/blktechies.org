# -*- coding: utf-8 -*-
from lxml.html import fragment_fromstring
from lxml.html.clean import Cleaner, autolink


class HTMLCleaner(object):
    def clean_html(self, html):
        cleaner = Cleaner(scripts=True, style=True,
                                         embedded=True, page_structure=True,
                                         frames=True, add_nofollow=True,
                                         forms=True, annoying_tags=True)
        cleaner.allow_tags = set(cleaner.allow_tags or ()) | set(('p', 'br'))
        cleaner.kill_tags = set(cleaner.kill_tags or ()) | set(('img', 'style', 'script', 'link', 'head'))
        html = cleaner.clean_html(html)
        return html

    def clean_all(self, html_fragments):
        return tuple(self.clean_html(html) for html in html_fragments)

    def strip_tags(self, html):
        kill_tags = set(['object', 'embed', 'applet', 'iframe', 'audio',
                         'video', 'svg', 'script', 'code'])
        cleaner = Cleaner(allow_tags=[None],
                                         remove_unknown_tags=False,
                                         kill_tags=kill_tags)
        tree = fragment_fromstring(html, create_parent=True)
        tree = cleaner.clean_html(tree)
        return tree.text_content()

    def autolink_html(self, html):
        tree = fragment_fromstring(html, create_parent=True)
        autolink(tree)

html_cleaner = HTMLCleaner()
