#!/usr/bin/env python3

import datetime
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys

import requests
import unidecode
try:
    import colored
except ImportError:
    colored = None

import clap


__version__ = '0.0.1'


filename_ui_choices = (
    os.path.abspath('./ui.json'),
    os.path.expanduser('~/.local/share/pocket/ui.json'),
)
filename_ui = list(filter(os.path.isfile, filename_ui_choices))
if not filename_ui:
    print('error: could not find interface definition')
    exit(1)
filename_ui = filename_ui[0]

model = {}
try:
    with open(filename_ui, 'r') as ifstream: model = json.loads(ifstream.read())
except Exception as e:
    print('error: failed to load interface definition: {}: {}'.format(str(type(e))[8:-2], e))
    exit(1)

args = list(clap.formatter.Formatter(sys.argv[1:]).format())

command = clap.builder.Builder(model).insertHelpCommand().build().get()
parser = clap.parser.Parser(command).feed(args)
checker = clap.checker.RedChecker(parser)


try:
    err = None
    checker.check()
    fail = False
except clap.errors.MissingArgumentError as e:
    print('missing argument for option: {0}'.format(e))
    fail = True
except clap.errors.UnrecognizedOptionError as e:
    print('unrecognized option found: {0}'.format(e))
    fail = True
except clap.errors.ConflictingOptionsError as e:
    print('conflicting options found: {0}'.format(e))
    fail = True
except clap.errors.RequiredOptionNotFoundError as e:
    fail = True
    print('required option not found: {0}'.format(e))
except clap.errors.InvalidOperandRangeError as e:
    print('invalid number of operands: {0}'.format(e))
    fail = True
except clap.errors.UIDesignError as e:
    print('UI has design error: {0}'.format(e))
    fail = True
except clap.errors.AmbiguousCommandError as e:
    name, candidates = str(e).split(': ')
    print("ambiguous shortened command name: '{0}', candidates are: {1}".format(name, candidates))
    print("note: if this is a false positive use '--' operand separator")
    fail = True
except Exception as e:
    print('fatal: unhandled exception: {0}: {1}'.format(str(type(e))[8:-2], e))
    fail, err = True, e
finally:
    if fail: exit(1)
    ui = parser.parse().ui().finalise()


if '--version' in ui:
    print('pocket command line client {0}'.format(__version__))
    exit(0)
if clap.helper.HelpRunner(ui=ui, program=sys.argv[0]).adjust(options=['-h', '--help']).run().displayed(): exit(0)


# Utility functions.
def obtain(dictionary, *path, error=False, default=None):
    found = False
    value = dictionary
    path_length = len(path)-1
    for i, key in enumerate(path):
        if key not in value:
            if error:
                raise KeyError('.'.join(path))
            break
        value = value[key]
        if type(value) is not dict and i < path_length:
            if error:
                raise KeyError('.'.join(path))
            break
        if type(value) is not dict and i == path_length:
            found = True
        if i == path_length:
            found = True
    return (value if found else default)

class Connection:
    """Class representing connection to Jira cloud instance.
    Used to simplify queries.
    """
    def __init__(self, consumer_key, access_token):
        self._domain = 'https://getpocket.com'
        self._consumer_key = consumer_key
        self._access_token = access_token

    # Public helper methods.
    def url(self, url):
        return '{server}{url}'.format(server=self._domain, url=url)

    def headers(self):
        return {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Accept': 'application/json',
        }

    def auth(self, json):
        json['consumer_key'] = self._consumer_key
        json['access_token'] = self._access_token
        return json

    # Public request methods.
    def get(self, url, payload):
        return requests.get(self.url(url), headers=self.headers(), json=self.auth(payload))

    def put(self, url, payload):
        return requests.put(self.url(url), headers=self.headers(), json=self.auth(payload))

    def post(self, url, payload):
        return requests.post(self.url(url), headers=self.headers(), json=self.auth(payload))


settings_choices = (
    os.path.abspath('pocket.json'),
    os.path.expanduser('~/.config/pocket/config.json'),
)
settings_path = list(filter(os.path.isfile, settings_choices))
if not settings_path:
    print('error: pocket settings not found')
    exit(1)
settings_path = settings_path[0]

settings = None
try:
    with open(settings_path) as ifstream:
        settings = json.loads(ifstream.read())
except Exception as e:
    print('error: failed to load pocket settings: {}: {}'.format(str(type(e))[8:-2], e))
    exit(1)

if type(settings) is not dict:
    print('error: settings must be a JSON object')
    exit(1)
if 'consumer_key' not in settings:
    print('error: no consumer_key found in settings')
    exit(1)
if 'access_token' not in settings:
    print('error: no access_token found in settings')
    exit(1)

connection = Connection(settings.get('consumer_key'), settings.get('access_token'))

ui = ui.down()


def commandAdd(ui):
    operands = ui.operands()
    url = operands[0].strip()
    title = ''
    if len(operands) > 1:
        title = operands[1].strip()
    if not url:
        print('error: empty URL')
        exit(1)
    r = connection.post('/v3/add', {
        'url': url,
        'title': title,
    })
    if not r.ok:
        print('error: {}: {}'.format(r.headers.get('X-Error-Code', 0), r.headers.get('X-Error', '')))
        exit(1)


def commandGet(ui):
    r = connection.post('/v3/get', {})
    if not r.ok:
        print('error: {}: {}'.format(r.headers.get('X-Error-Code', 0), r.headers.get('X-Error', '')))
        exit(1)
    payload = {}
    if '--count' in ui:
        payload['count'] = ui.get('--count')
    print(payload)
    response = r.json().get('list', payload)

    if '--grep' in ui:
        # if grep-friendly output has been requested, dump it and
        # exit early
        for _, item in response.items():
            print('{} {}'.format(item.get('resolved_url'), item.get('resolved_title')))
        exit(0)

    # display less-friendly output otherwise
    limit = len(response)-1
    for i, _ in enumerate(response.items()):
        _, item = _
        url_header = 'url {}'.format(item.get('resolved_url', ''))
        if colored:
            url_header = (colored.fg('yellow') + url_header + colored.attr('reset'))
        print(url_header)
        print('Title: {}'.format(item.get('resolved_title', '')))

        display_excerpt = ('--excerpt' in ui and item.get('excerpt'))
        if i < limit or display_excerpt: print()
        if display_excerpt:
            # split after the full stop after sentences
            excerpt_lines = item.get('excerpt', '').split('. ')
            print('.\n'.join(map(lambda s: '    {}'.format(s), map(lambda s: s.strip(), excerpt_lines))))
            if i < limit: print()


def dispatch(ui, *commands, overrides = {}, default_command=''):
    """Semi-automatic command dispatcher.

    Functions passed to `*commands` parameter should be named like `commandFooBarBaz` because
    of command name mangling.
    Example: `foo-bar-baz` is transformed to `FooBarBaz` and handled with `commandFooBarBaz`.

    It is possible to override a command handler by passing it inside the `overrides` parameter.

    This scheme can be effectively used to support command auto-dispatch with minimal manual guidance by
    providing sane defaults and a way of overriding them when needed.
    """
    ui_command = (str(ui) or default_command)
    if not ui_command:
        return
    if ui_command in overrides:
        overrides[ui_command](ui)
    else:
        ui_command = ('command' + ''.join([(s[0].upper() + s[1:]) for s in ui_command.split('-')]))
        for cmd in commands:
            if cmd.__name__ == ui_command:
                cmd(ui)
                break

dispatch(ui,
    commandAdd,
    commandGet,
)
