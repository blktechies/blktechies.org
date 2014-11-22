from lxml.html.clean import Cleaner

def clean_html(html):
    cleaner = Cleaner(scripts=True, style=True, embedded=True, page_structure=True, frames=True,
                      add_nofollow=True, forms=True, annoying_tags=True)
    cleaner.remove_tags = set(cleaner.remove_tags or ()) | set(('span', 'div', 'table', 'tr', 'td', 'body', 'html', 'meta',))
    cleaner.kill_tags = set(cleaner.kill_tags or ()) | set(('img', 'style', 'script', 'link', 'head'))

    html = cleaner.clean_html(html)
    return html
