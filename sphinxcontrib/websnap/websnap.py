from docutils import nodes
from docutils.parsers.rst import Directive
import os

from sphinx.locale import _

import webpage2html

NAMESPACE = 'websnap'

# http://www.sphinx-doc.org/en/stable/extdev/tutorial.html

class websnap_inline_node(nodes.General, nodes.Element):
    pass

class WebsnapInlineDirective(Directive):
    FORMAT = 'ws-url-%d'
    # see http://www.sphinx-doc.org/en/stable/extdev/markupapi.html#docutils.parsers.rst.Directive
    required_arguments = 2
    final_argument_whitespace = True
    # optional_arguments

    # option_spec
  #  @staticmethod
  #  def check_linkname(name):
  #      if name is None:
  #          raise ValueError(":linkname: option required!")

  #  option_spec = {
  #      'linkname': check_linkname
  #  }

    has_content = False

    def run(self):
        env = self.state.document.settings.env

        target_id = self.FORMAT % env.new_serialno(NAMESPACE)
        target_node = nodes.target('', '', ids=[target_id])

        if not hasattr(env, 'websnap_urls'):
            env.websnap_urls = {}

        url = self.arguments[0]
        linkname = self.arguments[1]

        if url not in env.websnap_urls:
            env.websnap_urls[url] = {
                'docname': env.docname,
                'lineno': self.lineno,
                'url': url,
                'linkname': linkname,
                'target_node': target_node
            }
        return [target_node, websnap_inline_node(url)]



def visit_inline(self, node):
    self.visit_general(node)

def depart_inline(self, node):
    self.visit_general(node)



import json
import random
import io
import sys
from bs4 import BeautifulSoup
import re
import string


class WebpageCache(object):
    def __init__(self, directory, cache_file='.cache'):

        self.directory = directory
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

    def filepath(self, url):
        if url not in self.urlcache:
            title, html = self.download(url)
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
        try:
            print("[*] Downloading webpage: %s" % url)
            sys.stderr = io.StringIO()
            sys.stdout = io.StringIO()
            html = webpage2html.generate(url, verify=False)

            if html.strip() == '':
                raise RuntimeError('Could not resolve URL: %s'.format(url))

            # make a title
            soup = BeautifulSoup(html)
            try:
                title = soup.title.string
            except:
                title = url

            title = re.sub('\S+://+', '', title)
            title = re.sub('www\.', '', title)
            title = re.sub('['+re.escape(string.punctuation)+']+', '-', title)
            title = re.sub('\s+', '_', title)
            return title, html
        finally:
            sys.stderr = eo
            sys.stdout = so

def process_weblinks(app, doctree, fromdocname):
    env = app.builder.env

    if not hasattr(env, 'websnap_urls'):
        return

    if not hasattr(env, 'websnap_page_cache'):
        cache_dir = os.path.join(env.srcdir, env.config.websnap_cache_directory)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        env.websnap_page_cache = WebpageCache(cache_dir)

    cache = env.websnap_page_cache
    urls = env.websnap_urls

    # for url, urlinfo in env.websnap_urls.items():
    #    if url in
    #     print('[*] download url %s' % urlinfo['url'])

    def relpath(url):
        page_path = cache.filepath(url)
        assert page_path.startswith(env.srcdir)

        page_url = page_path[len(env.srcdir):]

        if not page_url.startswith('/'):
            page_url = '/' + page_url
        return page_url



    for node in doctree.traverse(websnap_inline_node):
        content = []
        w_url = node.rawsource
        w_name = urls[w_url]['linkname']

        print("*********", w_name)
        pg = nodes.paragraph()
        
        nref = nodes.reference('', '')
        nref['refuri'] = relpath(w_url)

        nlinkname = nodes.emphasis(_(w_name), _(w_name))
        nref.append(nlinkname)

        pg += nref

        #pg = nodes.raw(
        #        text='<iframe style="width:100%" src="{}"></iframe>'.format(page_url),
        #         #text='<p style="width:100%">{}</p>'.format(page_url),
        #        format='html')

        content.append(pg)

        node.replace_self(content)

def purge_weblinks(app, env, docname):
    if not hasattr(env, 'websnap_urls'):
        return

    urls = env.websnap_urls
    env.websnap_urls = {k: v for k, v in urls.items()
                        if v['docname'] != docname}

def setup(app):
    import os
    print(os.getcwd())
    # configuration parameters
    app.add_config_value('websnap_use_cached', True, 'html')
    app.add_config_value('websnap_cache_directory', '_static/_websnap/', 'html')

    # nodes, and visitors for each markup language
    app.add_node(
        websnap_inline_node,
        html=(visit_inline, depart_inline)
    )

    # register the directives
    app.add_directive('websnap-inline', WebsnapInlineDirective)

    # add event handlers
    app.connect('doctree-resolved', process_weblinks)

    return {'version': '0.0.1'}

# ControlFlow explanation
# - User adds directive to document
# - Directive(*args).run for all directives
#   - returns list of nodes
# - Node visitors are called for each output format
# - Any connected hooks are executed
