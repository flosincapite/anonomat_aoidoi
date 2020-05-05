import contextlib
import os
import re
import sys
import yaml

from bs4 import BeautifulSoup
import fire


def _generate_toc(issue_directory):
    # TODO: Fill in!
    # Explicit sort here. Subdirs in issue_directory should be of the form
    # <SORT_ORDER_INT>_<NAME>
    result = {}
    section_list = result.setdefault('sections', [])
    for section_dir in sorted(os.listdir(issue_directory)):
        section_dict = {}
        title = re.search(r'^\d+\._(.*)', section_dir).groups()[0]
        # TODO: Add title to section
        current_author = None


class CleanupComponent:
    def clean(self, html_file, output_file=None):

        with open(html_file, 'r') as inp:
            soup = BeautifulSoup(inp.read())

        for node in soup.find_all('p'):
            if node.string:
                node.string.replace_with(re.sub(r'\n', r' ', node.string, re.DOTALL))
            if 'style' in node.attrs:
                del node.attrs['style']

        for node in soup.find_all('i'):
            if node.string:
                node.string.replace_with(re.sub(r'\n', r' ', node.string, re.DOTALL))

        for node in soup.find_all('font'):
            if node.string:
                node.string.replace_with(re.sub(r'\n', r' ', node.string, re.DOTALL))
            node.attrs = {}

        with contextlib.ExitStack() as stack:
            if output_file is None:
                outp = sys.stdout
            else:
                outp = stack.enter_context(open(output_file, 'w'))

            # outp.write(soup.text)
            outp.write(str(soup))


    def fix_toc(self, toc_file, new_toc):
        with open(toc_file, 'r') as inp:
            toc = yaml.load(inp.read())
        for section in toc.get('sections', []):
            for key in ['base_dir', 'cover', 'closing_image']:
                if section.get(key) is not None:
                    section[key] = re.sub(r' ', r'_', section[key])
            for author in section.get('authors', []):
                if author.get('image') is not None:
                    author['image'] = re.sub(r' ', r'_', author['image'])
                for poem in author.get('poems', []):
                    for key in ['contents_html', 'image']:
                        if poem.get(key) is not None:
                            poem[key] = re.sub(r' ', r'_', poem[key])
        with open(new_toc, 'w') as outp:
            yaml.dump(toc, outp)


    def generate_toc(self, issue_directory, toc_file):
        toc_dict = _generate_toc(issue_directory)
        with open(toc_file, 'w') as outp:
            yaml.dump(toc_dict, outp)



if __name__ == '__main__':
    fire.Fire(CleanupComponent)
