# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import os

import pytest
from scripttest import TestFileEnvironment

py2_only = pytest.mark.skipif(sys.version_info[0] >= 3, reason='not working on py3')

@pytest.fixture
def env():
    return TestFileEnvironment(ignore_hidden=False)

import konch


def teardown_function(func):
    konch.reset_config()


def test_format_context():
    context = {
        'my_number': 42,
        'my_func': lambda x: x,
    }
    result = konch.format_context(context)
    assert result == '\n'.join([
        '{0}: {1!r}'.format(key, value)
        for key, value in context.items()
    ])


def test_default_make_banner():
    result = konch.make_banner()
    assert sys.version in result
    assert konch.DEFAULT_BANNER_TEXT in result


def test_make_banner_custom():
    text = 'I want to be the very best'
    result = konch.make_banner(text)
    assert text in result
    assert sys.version in result


def test_make_banner_with_context():
    context = {'foo': 42}
    result = konch.make_banner(context=context)
    assert konch.format_context(context) in result


def test_cfg_defaults():
    assert konch.DEFAULT_OPTIONS['shell'] == konch.AutoShell
    assert konch.DEFAULT_OPTIONS['banner'] == konch.DEFAULT_BANNER_TEXT
    assert konch.DEFAULT_OPTIONS['context'] == {}


def test_config():
    assert konch.cfg == konch.DEFAULT_OPTIONS
    konch.config({
        'banner': 'Foo bar'
    })
    assert konch.cfg['banner'] == 'Foo bar'


def test_reset_config():
    assert konch.cfg == konch.DEFAULT_OPTIONS
    konch.config({
        'banner': 'Foo bar'
    })
    konch.reset_config()
    assert konch.cfg == konch.DEFAULT_OPTIONS


##### Command tests #####


def test_init_creates_config_file(env):
    res = env.run('konch', 'init')
    assert res.returncode == 0
    assert konch.DEFAULT_CONFIG_FILE in res.files_created


def test_init_with_filename(env):
    res = env.run('konch', 'init', 'myconfig')
    assert 'myconfig' in res.files_created


def test_konch_with_no_config_file(env):
    res = env.run('konch', expect_stderr=True)
    assert res.returncode == 0

def test_konch_with_config_file(env):
    env.run('konch', 'init')
    res = env.run('konch', expect_stderr=False)
    assert res.returncode == 0


def test_konch_init_when_config_file_exists(env):
    env.run('konch', 'init')
    res = env.run('konch', 'init', expect_error=True)
    assert 'already exists' in res.stdout
    assert res.returncode == 1


def test_default_banner(env):
    env.run('konch', 'init')
    res = env.run('konch')
    assert konch.DEFAULT_BANNER_TEXT in res.stdout
    assert str(sys.version) in res.stdout


def test_config_file_not_found(env):
    res = env.run('konch', '-f', 'notfound', expect_stderr=True)
    assert 'not found' in res.stderr
    assert res.returncode == 0

TEST_CONFIG = """
import konch

konch.config({
    'banner': 'Test banner'
})
"""


def test_custom_banner(env):
    with open(os.path.join(env.base_path, 'testrc'), 'w') as fp:
        fp.write(TEST_CONFIG)
    res = env.run('konch', '-f', 'testrc')
    assert 'Test banner' in res.stdout


def test_version(env):
    res = env.run('konch', '--version')
    assert konch.__version__ in res.stdout
    res = env.run('konch', '-v')
    assert konch.__version__ in res.stdout
