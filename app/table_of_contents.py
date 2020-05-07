import collections
import contextlib
import json
import yattag

import flask


_Toc = collections.namedtuple('TOC', ['markup'])


def generate(config_string):
    toc = json.loads(config_string)
    print(toc)

    doc, tag, text = yattag.Doc().tagtext()

    issue = toc.get('issue')

    lines = []

    def _traverse_toc(toc_dict):
        with contextlib.ExitStack() as stack:
            title = toc_dict.get('title')
            if title is not None:
                stack.enter_context(tag('ul', style='list-style-type:none;'))
                stack.enter_context(tag('li'))
                stack.enter_context(tag('span', klass='toc-item'))
                page = toc_dict.get('__page')
                if page is not None:
                    stack.enter_context(tag(
                        'a',
                        klass='toc-item',
                        style='text-decoration:none',
                        href=(f'{page}')))
                    """
                            '{{ url_for("single_page", '
                            f'issue_number={issue}, '
                            f'page_number={page}'
                            ') }}')))
                    """
                text(title)

            for subcontents in toc_dict.get('subcontents', []):
                _traverse_toc(subcontents)

    _traverse_toc(toc)

    print(f'generated markup: {doc.getvalue()}')
    return _Toc(markup=flask.Markup(doc.getvalue()))
