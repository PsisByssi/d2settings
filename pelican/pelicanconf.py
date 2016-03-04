#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
THEME = os.path.join(os.getcwd(), '..', '..', 'pelican-bootstrap3')
BOOTSTRAP_THEME = 'cyborg'

AUTHOR = 'Timothy C Eichler'
SITENAME = 'D2SETTINGS'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Berlin'
DATE_FORMATS = {'en':'%d/%m/%Y'}
DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Fork me on Github', 'http://psisbyssi.github.io/d2settings'),
        ('Uncrumpled', 'http://uncrumpled.com'),)

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# MENU SETTINGS
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = True
MENUITEMS = [('Downloads','/pages/downloads.html')]

#GOOGLE
#GOOGLE_ANALYTICS

#TODO TURN OFF AFTER TESTING
LOAD_CONTENT_CACHE = False
