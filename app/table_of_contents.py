import collections
import contextlib
import json
import yattag

import flask


_Toc = collections.namedtuple('TOC', ['markup', 'toc_page'])
    
    
def _traverse_toc(toc_dict, issue, doc=None, tag=None, text=None):
    if doc is None:
        doc, tag, text = yattag.Doc().tagtext()

    with contextlib.ExitStack() as stack:
        title = toc_dict.get('title')
        if title is not None:
            toc_title = toc_dict.get('sequence_title', title)
            stack.enter_context(tag('ul', style='list-style-type:none;'))
            stack.enter_context(tag('li'))
            stack.enter_context(tag('span', klass='toc-item'))
            page = toc_dict.get('__page')
            if page is not None:
                stack.enter_context(tag(
                    'a',
                    klass='toc-item',
                    style='text-decoration:none',
                    href=(f'/viewer/{issue}/{page}')))
            text(toc_title)

        for subcontents in toc_dict.get('subcontents', []):
            _ = _traverse_toc(subcontents, issue, doc, tag, text)

    return doc


def generate(config_string):
    toc = json.loads(config_string)

    html_doc = _traverse_toc(toc, toc['issue'])

    toc_page = toc.get('toc_page')
    return _Toc(markup=flask.Markup(html_doc.getvalue()), toc_page=toc_page)
