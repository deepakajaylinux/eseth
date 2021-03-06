# -*- coding: utf-8 -*-
"""A role to easily make links to your dotfiles on BitBucket or GitHub."""
VERSION = 0.1
AUTHOR = 'Seth House <seth@eseth.com>'

import os
import re

from docutils import nodes, utils
from docutils.parsers.rst import roles

from sphinx.util import caption_ref_re

re_rcfile = re.compile(r'^'\
        '(?P<rcfile>[\w._-]*)'\
        '(@(?P<revhash>[\w]*))?'\
        '(#(?P<linenr>[0-9]*))?$')

def rcfile_role(role, rawtext, text, lineno, inliner,
        options={}, content=[]):
    """Shortcut to return the URL of an *rc file, optionally of a specific
    version and on a specific line.

    Usage::

        I have written a function that does FOO, see :rc:`line 32 of my barrc
        <barrc@b1e8bfc81b0a#32>` for the implementation.

        View my latest :rc:`vimrc`.

        View line 32 of my latest :rc:`vimrc#32`.

        :rc:`See all my dotfiles. <*>`
    
    """
    env = inliner.document.settings.env

    # Is this a Sphinx-style ref?
    brace = text.find('<')
    if brace != -1:
        m = caption_ref_re.match(text)
        if m:
            target = m.group(2)
            title = m.group(1)
        else:
            # fallback: everything after '<' is the target
            target = text[brace+1:]
            title = text[:brace]

    if target == '*':
        uri = env.config['rc_main'] or env.config['rc_url']
    else:
        # Parse arguments for the rc file like rev and line number
        rc_string = re_rcfile.search(target)

        # We didn't get at least a filename, return an error
        if not rc_string:
            msg = inliner.reporter.error(
                'Could not parse rc file string.'
                '"%s" is invalid.' % text, line=lineno)
            prb = inliner.problematic(rawtext, rawtext, msg)
            return [prb], [msg]

        # Get a dict of any params passed for the rc file and build the url
        tokens = rc_string.groupdict()

        uri = '%s/%s/%s' % (
                env.config['rc_url'],
                tokens.get('revhash') or env.config['rc_head'],
                tokens['rcfile'])

        if tokens.get('linenr'):
            uri += env.config['rc_linenr'] % tokens

    # Build the actual rST node and return it
    node = nodes.reference(rawtext, title, refuri=uri, **options)
    return [node], []

def setup(app):
    try:
        user = os.getlogin()
    except OSError:
        user = os.getenv('USER')

    # bitbucket
    # app.add_config_value('rc_main', None, True)
    # app.add_config_value('rc_url',
            # 'http://bitbucket.org/%s/dotfiles/src/' % user or 'username', True)
    # app.add_config_value('rc_head', 'tip', True)
    # app.add_config_value('rc_linenr', '#cl-%(linenr)s', True)

    # github
    app.add_config_value('rc_main', 
        'http://github.com/%s/dotfiles/tree/master' % user or 'username', True)
    app.add_config_value('rc_url',
        'http://github.com/%s/dotfiles/blob' % user or 'username', True)
    app.add_config_value('rc_head', 'master', True)
    app.add_config_value('rc_linenr', '#L%(linenr)s', True)


roles.register_local_role('rc', rcfile_role)
