import os
import sys
import re
import io
import random
import string
import json
from datetime import datetime

import sphinx.util.logging
from docutils import nodes, utils
from docutils.parsers.rst import Directive
from sphinx.locale import _
from sphinx.util.nodes import split_explicit_title

logger = sphinx.util.logging.getLogger(__name__)

from bs4 import BeautifulSoup

from . import webpage2html

__version__ = '0.2.0'

def page_cache(env):
    """Create or return the WebpageCache for this environment"""
    if not hasattr(env, 'websnap_page_cache'):
        cache_dir = os.path.join(env.srcdir, env.config.websnap_cache_directory)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        env.websnap_page_cache = WebpageCache(cache_dir)

    return env.websnap_page_cache

def references(env, value=None):
    """Get the list of nodes that have been created for this environment"""
    if not hasattr(env, 'websnap_references'):
        env.websnap_references = {}
    if value is not None:
        env.websnap_references = value
    return env.websnap_references

class websnap_ref_node(nodes.General, nodes.Element):
    pass

class websnap_download_node(nodes.General, nodes.Element):
    pass

class WebsnapDirective(Directive):
    """
    ::
        .. websnap:: http://www.google.com
                     reference_name
    Sphinx directive that creates a link to an archived website.
    """
    FORMAT = 'websnap-url-%d'
    required_arguments = 2

    final_argument_whitespace = True
    has_content = False

    def run(self):
        env = self.state.document.settings.env

        url = self.arguments[0]
        refname = self.arguments[1]

        if refname in references(env):
            url = references(env)[refname]['url']
            raise ValueError('Reference name `{}` already assigned to URL: {}'.format(refname, url))

        references(env)[refname] = {'docname': env.docname, 'lineno': self.lineno, 'url': url}

        node = websnap_download_node()
        node['websnap_url'] = url
        node['websnap_refname'] = refname

        return [node]

def websnap_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    # type: (unicode, unicode, unicode, int, Inliner, Dict, List[unicode]) -> Tuple[List[nodes.Node], List[nodes.Node]]  # NOQA
    """Role for processing websnap references"""
    env = inliner.document.settings.env
    has_explicit_title, title, target = split_explicit_title(text)

    title = utils.unescape(title)
    target = utils.unescape(target)

    anchor = ''
    anchorindex = target.find('#')
    if anchorindex > 0:
        target, anchor = target[:anchorindex], target[anchorindex:]

    node = websnap_ref_node()
    node['websnap_title'] = title if has_explicit_title else None
    node['websnap_url'] = None
    node['websnap_ref'] = None
    node['websnap_anchor'] = anchor

    node['docname'] = env.docname
    node['lineno'] = lineno

    if re.match(r'^\w+://', target):
        # this is a web target, may need to be download
        node['websnap_url'] = target
    else:
        # this is a reference to an existing downloaded page
        node['websnap_ref'] = target

    # Since references can only be resolved after downloading,
    # we add a faux node here that we will process later
    return [node], []

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
            json.dump(self.urlcache, f, indent=2)

    def sourcerel(self, url, env, make_absolute=True):
        """Return path to the downloaded website, relative to the source directory"""
        page_path = self.snapshot_path(url)
        assert page_path.startswith(env.srcdir)

        page_url = page_path[len(env.srcdir):]

        if make_absolute and not page_url.startswith('/'):
            page_url = '/' + page_url
        return page_url


    def snapshot_path(self, url):
        """Returns the path to the snapshot for the given URL.
           Downloads it if the URL has not been archived"""
        if url not in self.urlcache:
            title, html = self.download(url)
            # don't like spaces in name

            fname = re.sub('\S+://+', '', title or url)
            fname = re.sub('www\.', '', fname)
            fname = re.sub('['+re.escape(string.punctuation)+']+', '-', fname)
            fname = re.sub('\s+', '_', fname)

            filename = fname + '.html'

            while os.path.exists(os.path.join(self.directory, filename)):
                filename = fname + '_' + str(random.randrange(0, 2**32)) + '.html'

            with open(os.path.join(self.directory, filename), 'w') as f:
                f.write(html)

            self.urlcache[url] = {
                'filename': filename,
                'title': title,
                'time': datetime.now().isoformat()
            }
            self.write_cache()

        return os.path.join(self.directory, self.urlcache[url]['filename'])

    def __contains__(self, item):
        return item in self.urlcache

    def download(self, url):
        eo, so = sys.stderr, sys.stdout
        # FIXME actually print out the log somewhere
        log = io.StringIO()
        try:
            logger.info("[*] Downloading webpage: %s" , url)
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
                title = None

            return title, html
        except:
            header = "-"*10 + "websnap.webpage2html log" + "-"*10
            logger.error(header)
            for line in log.getvalue().split('\n'):
                logger.error(line)
            logger.error("-"*len(header))
            raise
        finally:
            sys.stderr = eo
            sys.stdout = so

def visit_websnap_ref_node(self, node):
    pass

def depart_websnap_ref_node(self, node):
    pass
 

def doctree_resolved(app, doctree, fromdocname):
    env = app.builder.env
    cache = page_cache(env)

    warnings = []

    # touch all the urls, so we are sure they are in the cache
    for node in doctree.traverse(websnap_download_node):
        cache.snapshot_path(node['websnap_url'])
        node.parent.remove(node)

    # replace all the references with links
    for node in doctree.traverse(websnap_ref_node):
        if node['websnap_ref']:
            try:
                url = references(env)[node['websnap_ref']]['url']
            except KeyError:
                msg = "[%s::%s] Unresolved websnap reference: %s"
                logger.error(msg, node['docname'], node['lineno'], node['websnap_ref'])
                # FIXME replace with an error node!
                continue
        else:
            url = node['websnap_url']

        path = cache.sourcerel(url, env)

        title = node['websnap_title']

        if title is None:
            # TODO load from the actual website
            title = url

        # In a sense the refernce "surrounds" the url title text
        sn = nodes.inline(title, title)
        rn = nodes.reference('', '', internal=False, refuri=path + node['websnap_anchor'],
                             classes=['websnap-ref'])

        rn += sn
        node.replace_self(rn)

def purge_caches(app, env, docname):
    refs = {k: v for k, v in references(env).items() if v['docname'] != docname}
    references(env, refs)

def setup(app):
    # configuration parameters
    app.add_config_value('websnap_skip_download', False, 'html')
    app.add_config_value('websnap_cache_directory', '_static/_websnap/', 'html')

    # nodes, and visitors for each markup language
    app.add_node(
        websnap_download_node,
        html=(visit_websnap_ref_node, depart_websnap_ref_node)
    )

    # register the directives
    app.add_directive('websnap', WebsnapDirective)
    app.add_role('websnap', websnap_role)

    app.connect('env-purge-doc', purge_caches)
    app.connect('doctree-resolved', doctree_resolved)

    return {'version': __version__}
