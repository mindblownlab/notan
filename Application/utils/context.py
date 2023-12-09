import os
import json

project = None
context = None

if 'MB_CONTEXT' in os.environ.keys():
    if os.environ['MB_CONTEXT']:
        context = dict(json.loads(os.environ['MB_CONTEXT'])) or None

if 'MB_PROJECT' in os.environ.keys():
    if os.environ['MB_PROJECT']:
        project = dict(json.loads(os.environ['MB_PROJECT'])) or None


def get_context():
    if 'MB_CONTEXT' in os.environ.keys():
        if os.environ['MB_CONTEXT']:
            return dict(json.loads(os.environ['MB_CONTEXT'])) or None


def get_project():
    if 'MB_PROJECT' in os.environ.keys():
        if os.environ['MB_PROJECT']:
            return dict(json.loads(os.environ['MB_PROJECT'])) or None
