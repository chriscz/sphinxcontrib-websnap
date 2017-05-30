import os
import sys
import re
import io
import random
import string
import json

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.locale import _

from bs4 import BeautifulSoup

from . import webpage2html

__version__ = '0.1.0'

NAMESPACE = 'websnap'

class websnap_url_node(nodes.General, nodes.Element):
    pass

class WebsnapUrlDirective(Directive):
    """
    Sphinx directive
    """
    FORMAT = 'websnap-url-%d'
    required_arguments = 2
    final_argument_whitespace = True
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        if not hasattr(env, 'websnap_urls'):
            env.websnap_urls = {}

        url = self.arguments[0]
        linkname = self.arguments[1]

        target_id = self.FORMAT % env.new_serialno(NAMESPACE)
        target_node = nodes.target('', '', ids=[target_id])

        if url not in env.websnap_urls:
            env.websnap_urls[url] = {
                'url': url,
                'title': linkname,
            }

        node = websnap_url_node()
        node['websnap_url'] = url
        node['websnap_title'] = linkname
        return [target_node, node]


class WebpageCache(object):
    def __init__(self, directory, cache_file='.cache'):
        self.directory = os.path.abspath(directory)
        self.cachepath = os.path.join(directory, cache_file)
        self.urlcache = {}

        if os.path.exists(self.cachepath):
            with open(self.cachepath) as f:
                data = f.read()
                if data:
                    self.urlcache = json.loads(data)

    def write_cache(self):
        with open(self.cachepath, 'w') as f:
            json.dump(self.urlcache, f)

    def sourcerel(self, url, env, make_absolute=True):
        """Return path to the downloaded website, relative to the source directory"""
        page_path = self.filepath(url)
        assert page_path.startswith(env.srcdir)

        page_url = page_path[len(env.srcdir):]

        if make_absolute and not page_url.startswith('/'):
            page_url = '/' + page_url
        return page_url


    def filepath(self, url):
        if url not in self.urlcache:
            title, html = self.download(url)
            # don't like spaces in name
            title = re.sub('\s+', '_', title)
            filename = title + '.html'

            while os.path.exists(os.path.join(self.directory, filename)):
                filename = title + '_' + str(random.randrange(0, 2**32)) + '.html'

            with open(os.path.join(self.directory, filename), 'w') as f:
                f.write(html)

            self.urlcache[url] = filename
            self.write_cache()

        return os.path.join(self.directory, self.urlcache[url])

    def __contains__(self, item):
        return item in self.urlcache

    def download(self, url):
        eo, so = sys.stderr, sys.stdout
        # FIXME actually print out the log somewhere
        log = io.StringIO()
        try:
            print("[*] Downloading webpage: %s" % url)
            sys.stderr = log
            sys.stdout = log
            html = webpage2html.generate(url, verify=False)

            if not html.strip():
                raise RuntimeError('Could not download URL: %s'.format(url))

            # extract_title
            soup = BeautifulSoup(html)
            try:
                title = soup.title.string
            except:
                title = url

            title = re.sub('\S+://+', '', title)
            title = re.sub('www\.', '', title)
            title = re.sub('['+re.escape(string.punctuation)+']+', '-', title)
            return title, html
        finally:
            sys.stderr = eo
            sys.stdout = so

def visit_websnap_url_node(self, node):
    pass

def depart_websnap_url_node(self, node):
    pass

def doctree_resolved(app, doctree, fromdocname):
    env = app.builder.env

    if not hasattr(env, 'websnap_page_cache'):
        cache_dir = os.path.join(env.srcdir, env.config.websnap_cache_directory)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        env.websnap_page_cache = WebpageCache(cache_dir)

    cache = env.websnap_page_cache

    for node in doctree.traverse(websnap_url_node):
        url = node['websnap_url']
        title = node['websnap_title']

        pg = nodes.paragraph()
        nref = nodes.reference('', '')

        # NOTE this cache call is actually where the downloading occurs
        nref['refuri'] = cache.sourcerel(url, env)

        # In a sense the refernce "surrounds" the url title text
        nref.append(nodes.emphasis(_(title), _(title)))

        pg += nref

        node.replace_self(pg)


def setup(app):
    # configuration parameters
    app.add_config_value('websnap_skip_download', False, 'html')
    app.add_config_value('websnap_cache_directory', '_static/_websnap/', 'html')

    # nodes, and visitors for each markup language
    app.add_node(
        websnap_url_node,
        html=(visit_websnap_url_node, depart_websnap_url_node)
    )

    # register the directives
    app.add_directive('websnap-url', WebsnapUrlDirective)
    app.connect('doctree-resolved', doctree_resolved)

    return {'version': __version__}
