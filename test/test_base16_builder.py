import json
import os
import re
import shutil
import tempfile

from ansible.compat.tests import unittest
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
try:
    from ansible.compat.tests.mock import ANY, call, patch
except ImportError:
    from mock import ANY, call, patch

from library import base16_builder


def set_module_args(args):
    '''prepare arguments so that they will be picked up during module creation'''
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    '''Exception class to be raised by module.exit_json and caught by the test case'''
    pass


class AnsibleFailJson(Exception):
    '''Exception class to be raised by module.fail_json and caught by the test case'''
    pass


def exit_json(*args, **kwargs):
    '''function to patch over exit_json; package return data into an exception'''
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    '''function to patch over fail_json; package return data into an exception'''
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


SCHEME_NAME = re.compile(r'.*base16-(.*)-scheme$')
TEMPLATE_NAME = re.compile(r'.*base16-(.*)$')


# TODO: Tests on failed git commands


def fake_run_command(command, **kwargs):
    if command and 'git' in command[0]  and command[1] == 'clone':
        if 'schemes-source' in command[2]:
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__),
                    'fixtures',
                    'sources',
                    'schemes',
                ),
                command[3],
            )
        elif 'templates-source' in command[2]:
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__),
                    'fixtures',
                    'sources',
                    'templates',
                ),
                command[3],
            )
        elif SCHEME_NAME.match(command[2]):
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__),
                    'fixtures',
                    'schemes',
                    SCHEME_NAME.match(command[2]).group(1),
                ),
                command[3],
            )
        elif TEMPLATE_NAME.match(command[2]):
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__),
                    'fixtures',
                    'templates',
                    TEMPLATE_NAME.match(command[2]).group(1),
                ),
                command[3],
            )
        else:
            raise ValueError('Unexpected clone: {}'.format(' '.join(command)))

        os.mkdir(os.path.join(command[3], '.git'))
        with open(os.path.join(command[3], '.git', 'config'), 'w') as git_config:
            git_config.write('url = {}'.format(command[2]))

    elif command and git in command[0] and command[1] == 'pull':
        return
    else:
        raise ValueError('Unexpected command: {}'.format(' '.join(command)))


class TestBase16Builder(unittest.TestCase):
    def delete_test_cache_dir(self):
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
        )
        self.mock_module_helper.start()
        self.module = base16_builder
        self.test_cache_dir = os.path.join(
            tempfile.gettempdir(),
            'base16-builder-ansible-test',
        )
        self.delete_test_cache_dir()

    def tearDown(self):
        self.delete_test_cache_dir()

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_builds_a_given_scheme_and_template(self, mock_run_command):
        set_module_args({
            'scheme': 'tomorrow-night',
            'template': 'i3',
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        with open(os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'templates',
            'i3',
            'bar-colors',
            'base16-tomorrow-night.config',
        )) as f:
            i3_tomorrow_night_bar_colors = f.read()
        with open(os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'templates',
            'i3',
            'client-properties',
            'base16-tomorrow-night.config',
        )) as f:
            i3_tomorrow_night_client_properties = f.read()
        with open(os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'templates',
            'i3',
            'colors',
            'base16-tomorrow-night.config',
        )) as f:
            i3_tomorrow_night_colors = f.read()
        with open(os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'templates',
            'i3',
            'themes',
            'base16-tomorrow-night.config',
        )) as f:
            i3_tomorrow_night = f.read()

        self.assertEqual(
            result_args['schemes'],
            {'tomorrow-night': {'i3': {
                'bar-colors': {'base16-tomorrow-night.config': i3_tomorrow_night_bar_colors},
                'colors': {'base16-tomorrow-night.config': i3_tomorrow_night_colors},
                'client-properties': {'base16-tomorrow-night.config': i3_tomorrow_night_client_properties},
                'themes': {'base16-tomorrow-night.config': i3_tomorrow_night},
            }}}
        )

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_builds_all_schemes_in_a_family_if_family_name_is_passed(self, mock_run_command):
        set_module_args({
            'scheme': 'tomorrow',
            'template': 'i3',
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertIn('tomorrow-night', result_args['schemes'])
        self.assertIn('tomorrow', result_args['schemes'])

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_builds_a_scheme_if_family_name_differs_and_is_passed_in(self, mock_run_command):
        set_module_args({
            'scheme': 'material-palenight',
            'scheme_family': 'materialtheme',
            'template': 'i3',
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertIn('material-palenight', result_args['schemes'])

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_builds_nothing_if_build_false_is_passed(self, mock_run_command):
        set_module_args({'build': False})

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args['changed'], False)
        self.assertEqual(result_args['schemes'], {})

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_builds_everything_if_no_scheme_or_template_is_passed(self, mock_run_command):
        set_module_args({'cache_dir': self.test_cache_dir})

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertTrue(len(result_args['schemes'].keys()) > 1)
        self.assertTrue(len(result_args['schemes']['tomorrow-night'].keys()) > 1)

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_update_runs(self, mock_run_command):
        set_module_args({
            'update': True,
            'build': False,
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args['changed'], True)
        self.assertEqual(result_args['schemes'], {})

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_update_runs_with_build(self, mock_run_command):
        set_module_args({
            'update': True,
            'scheme': 'tomorrow-night',
            'template': 'i3',
            'cache_dir': self.test_cache_dir
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(list(result_args['schemes'].keys()), ['tomorrow-night'])
        self.assertEqual(result_args['changed'], True)

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_can_use_template_and_scheme_repos(self, mock_run_command):
        set_module_args({
            'scheme': 'tomorrow-night',
            'template': 'i3',
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()

        set_module_args({
            'scheme': 'tomorrow-night',
            'template': 'i3',
            'schemes_source': 'https://github.com/mnussbaum/base16-schemes-source',
            'templates_source': 'https://github.com/mnussbaum/base16-templates-source',
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args['changed'], True)

        schemes_source = os.path.join(
            self.test_cache_dir,
            'base16-builder-ansible',
            'sources',
            'schemes',
        )
        self.assertTrue(os.path.exists(schemes_source))
        self.assertTrue(call([
            ANY,
            'clone',
            'https://github.com/mnussbaum/base16-schemes-source',
            ANY,
        ], check_rc=True) in mock_run_command.mock_calls)

        templates_source = os.path.join(
            self.test_cache_dir,
            'base16-builder-ansible',
            'sources',
            'templates',
        )
        self.assertTrue(os.path.exists(templates_source))
        self.assertTrue(call([
            ANY,
            'clone',
            'https://github.com/mnussbaum/base16-templates-source',
            ANY,
        ], check_rc=True) in mock_run_command.mock_calls)

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_can_use_template_and_scheme_local_paths(self, mock_run_command):
        set_module_args({
            'scheme': 'local-scheme',
            'template': 'local-template',
            'schemes_source': os.path.join(
                os.path.dirname(__file__),
                'fixtures',
                'sources',
                'schemes',
            ),
            'templates_source': os.path.join(
                os.path.dirname(__file__),
                'fixtures',
                'sources',
                'templates',
            ),
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args['changed'], False)

        self.assertFalse(call([
            ANY,
            'clone',
            ANY,
            ANY,
        ], check_rc=True) in mock_run_command.mock_calls)

        self.assertEqual(
            result_args['schemes'], {
                'local-scheme-night': {'local-template': {
                    'themes': {'base16-local-scheme-night.test': "000000\n00\n00\n00\n0\n0\n0\n0.0\n0.0\n0.0\n"},
                }},
                'local-scheme': {'local-template': {
                    'themes': {'base16-local-scheme.test': "111111\n11\n11\n11\n17\n17\n17\n0.06666666666666667\n0.06666666666666667\n0.06666666666666667\n"},
                }},
            },
        )

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_fails_when_no_schemes_are_found_and_a_scheme_is_passed(self, mock_run_command):
        set_module_args({
            'scheme': 'not-a-real-scheme',
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()

        self.assertEqual(
            result.exception.args[0]['msg'],
            'Failed to build any schemes. Scheme name "not-a-real-scheme" was passed, but didn\'t match any known schemes',
        )

    @patch.object(basic.AnsibleModule, 'run_command', side_effect=fake_run_command)
    def test_module_fails_when_no_templates_are_found_and_a_template_is_passed(self, mock_run_command):
        set_module_args({
            'template': 'not-a-real-template',
            'cache_dir': self.test_cache_dir,
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()

        self.assertEqual(
            result.exception.args[0]['msg'],
            'Failed to build any templates. Template name "not-a-real-template" was passed, but didn\'t match any known templates',
        )
