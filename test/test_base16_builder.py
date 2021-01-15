import json
from unittest.mock import ANY, call, patch
import os
import re
import shutil
import tempfile
import unittest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


from library import base16_builder


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


SCHEME_NAME = re.compile(r".*base16-(.*)-scheme$")
TEMPLATE_NAME = re.compile(r".*base16-(.*)$")


# TODO: Tests on failed git commands


def fake_run_command(command, **kwargs):
    if command and "git" in command[0] and command[1] == "clone":
        if "schemes-source" in command[2]:
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__), "fixtures", "sources", "schemes"
                ),
                command[3],
            )
        elif "templates-source" in command[2]:
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__), "fixtures", "sources", "templates"
                ),
                command[3],
            )
        elif SCHEME_NAME.match(command[2]):
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__),
                    "fixtures",
                    "schemes",
                    SCHEME_NAME.match(command[2]).group(1),
                ),
                command[3],
            )
        elif TEMPLATE_NAME.match(command[2]):
            shutil.copytree(
                os.path.join(
                    os.path.dirname(__file__),
                    "fixtures",
                    "templates",
                    TEMPLATE_NAME.match(command[2]).group(1),
                ),
                command[3],
            )
        else:
            raise ValueError("Unexpected clone: {}".format(" ".join(command)))

        os.mkdir(os.path.join(command[3], ".git"))
        with open(os.path.join(command[3], ".git", "config"), "w") as git_config:
            git_config.write("url = {}".format(command[2]))

    elif command and git in command[0] and command[1] == "pull":
        return
    else:
        raise ValueError("Unexpected command: {}".format(" ".join(command)))


class TestBase16Builder(unittest.TestCase):
    def delete_test_cache_dir(self):
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
        )
        self.mock_module_helper.start()
        self.module = base16_builder
        self.test_cache_dir = os.path.join(
            tempfile.gettempdir(), "base16-builder-ansible-test"
        )
        self.delete_test_cache_dir()

    def tearDown(self):
        self.delete_test_cache_dir()

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_builds_a_given_scheme_and_template(self, mock_run_command):
        set_module_args(
            {
                "scheme": "tomorrow-night",
                "template": "i3",
                "cache_dir": self.test_cache_dir,
            }
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        with open(
            os.path.join(
                os.path.dirname(__file__),
                "fixtures",
                "templates",
                "i3",
                "bar-colors",
                "base16-tomorrow-night.config",
            )
        ) as f:
            i3_tomorrow_night_bar_colors = f.read()
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "fixtures",
                "templates",
                "i3",
                "client-properties",
                "base16-tomorrow-night.config",
            )
        ) as f:
            i3_tomorrow_night_client_properties = f.read()
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "fixtures",
                "templates",
                "i3",
                "colors",
                "base16-tomorrow-night.config",
            )
        ) as f:
            i3_tomorrow_night_colors = f.read()
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "fixtures",
                "templates",
                "i3",
                "themes",
                "base16-tomorrow-night.config",
            )
        ) as f:
            i3_tomorrow_night = f.read()

        self.assertEqual(
            result_args["schemes"],
            {
                "tomorrow-night": {
                    "i3": {
                        "bar-colors": {
                            "base16-tomorrow-night.config": i3_tomorrow_night_bar_colors
                        },
                        "colors": {
                            "base16-tomorrow-night.config": i3_tomorrow_night_colors
                        },
                        "client-properties": {
                            "base16-tomorrow-night.config": i3_tomorrow_night_client_properties
                        },
                        "themes": {"base16-tomorrow-night.config": i3_tomorrow_night},
                    },
                    "scheme-variables": {
                        "base00-dec-b": "0.12941176470588237",
                        "base00-dec-g": "0.12156862745098039",
                        "base00-dec-r": "0.11372549019607843",
                        "base00-hex": "1d1f21",
                        "base00-hex-bgr": "211f1d",
                        "base00-hex-b": "21",
                        "base00-hex-g": "1f",
                        "base00-hex-r": "1d",
                        "base00-rgb-b": "33",
                        "base00-rgb-g": "31",
                        "base00-rgb-r": "29",
                        "base01-dec-b": "0.1803921568627451",
                        "base01-dec-g": "0.16470588235294117",
                        "base01-dec-r": "0.1568627450980392",
                        "base01-hex": "282a2e",
                        "base01-hex-bgr": "2e2a28",
                        "base01-hex-b": "2e",
                        "base01-hex-g": "2a",
                        "base01-hex-r": "28",
                        "base01-rgb-b": "46",
                        "base01-rgb-g": "42",
                        "base01-rgb-r": "40",
                        "base02-dec-b": "0.2549019607843137",
                        "base02-dec-g": "0.23137254901960785",
                        "base02-dec-r": "0.21568627450980393",
                        "base02-hex": "373b41",
                        "base02-hex-bgr": "413b37",
                        "base02-hex-b": "41",
                        "base02-hex-g": "3b",
                        "base02-hex-r": "37",
                        "base02-rgb-b": "65",
                        "base02-rgb-g": "59",
                        "base02-rgb-r": "55",
                        "base03-dec-b": "0.5882352941176471",
                        "base03-dec-g": "0.596078431372549",
                        "base03-dec-r": "0.5882352941176471",
                        "base03-hex": "969896",
                        "base03-hex-bgr": "969896",
                        "base03-hex-b": "96",
                        "base03-hex-g": "98",
                        "base03-hex-r": "96",
                        "base03-rgb-b": "150",
                        "base03-rgb-g": "152",
                        "base03-rgb-r": "150",
                        "base04-dec-b": "0.7058823529411765",
                        "base04-dec-g": "0.7176470588235294",
                        "base04-dec-r": "0.7058823529411765",
                        "base04-hex": "b4b7b4",
                        "base04-hex-bgr": "b4b7b4",
                        "base04-hex-b": "b4",
                        "base04-hex-g": "b7",
                        "base04-hex-r": "b4",
                        "base04-rgb-b": "180",
                        "base04-rgb-g": "183",
                        "base04-rgb-r": "180",
                        "base05-dec-b": "0.7764705882352941",
                        "base05-dec-g": "0.7843137254901961",
                        "base05-dec-r": "0.7725490196078432",
                        "base05-hex": "c5c8c6",
                        "base05-hex-bgr": "c6c8c5",
                        "base05-hex-b": "c6",
                        "base05-hex-g": "c8",
                        "base05-hex-r": "c5",
                        "base05-rgb-b": "198",
                        "base05-rgb-g": "200",
                        "base05-rgb-r": "197",
                        "base06-dec-b": "0.8784313725490196",
                        "base06-dec-g": "0.8784313725490196",
                        "base06-dec-r": "0.8784313725490196",
                        "base06-hex": "e0e0e0",
                        "base06-hex-bgr": "e0e0e0",
                        "base06-hex-b": "e0",
                        "base06-hex-g": "e0",
                        "base06-hex-r": "e0",
                        "base06-rgb-b": "224",
                        "base06-rgb-g": "224",
                        "base06-rgb-r": "224",
                        "base07-dec-b": "1.0",
                        "base07-dec-g": "1.0",
                        "base07-dec-r": "1.0",
                        "base07-hex": "ffffff",
                        "base07-hex-bgr": "ffffff",
                        "base07-hex-b": "ff",
                        "base07-hex-g": "ff",
                        "base07-hex-r": "ff",
                        "base07-rgb-b": "255",
                        "base07-rgb-g": "255",
                        "base07-rgb-r": "255",
                        "base08-dec-b": "0.4",
                        "base08-dec-g": "0.4",
                        "base08-dec-r": "0.8",
                        "base08-hex": "cc6666",
                        "base08-hex-bgr": "6666cc",
                        "base08-hex-b": "66",
                        "base08-hex-g": "66",
                        "base08-hex-r": "cc",
                        "base08-rgb-b": "102",
                        "base08-rgb-g": "102",
                        "base08-rgb-r": "204",
                        "base09-dec-b": "0.37254901960784315",
                        "base09-dec-g": "0.5764705882352941",
                        "base09-dec-r": "0.8705882352941177",
                        "base09-hex": "de935f",
                        "base09-hex-bgr": "5f93de",
                        "base09-hex-b": "5f",
                        "base09-hex-g": "93",
                        "base09-hex-r": "de",
                        "base09-rgb-b": "95",
                        "base09-rgb-g": "147",
                        "base09-rgb-r": "222",
                        "base0A-dec-b": "0.4549019607843137",
                        "base0A-dec-g": "0.7764705882352941",
                        "base0A-dec-r": "0.9411764705882353",
                        "base0A-hex": "f0c674",
                        "base0A-hex-bgr": "74c6f0",
                        "base0A-hex-b": "74",
                        "base0A-hex-g": "c6",
                        "base0A-hex-r": "f0",
                        "base0A-rgb-b": "116",
                        "base0A-rgb-g": "198",
                        "base0A-rgb-r": "240",
                        "base0B-dec-b": "0.40784313725490196",
                        "base0B-dec-g": "0.7411764705882353",
                        "base0B-dec-r": "0.7098039215686275",
                        "base0B-hex": "b5bd68",
                        "base0B-hex-bgr": "68bdb5",
                        "base0B-hex-b": "68",
                        "base0B-hex-g": "bd",
                        "base0B-hex-r": "b5",
                        "base0B-rgb-b": "104",
                        "base0B-rgb-g": "189",
                        "base0B-rgb-r": "181",
                        "base0C-dec-b": "0.7176470588235294",
                        "base0C-dec-g": "0.7450980392156863",
                        "base0C-dec-r": "0.5411764705882353",
                        "base0C-hex": "8abeb7",
                        "base0C-hex-bgr": "b7be8a",
                        "base0C-hex-b": "b7",
                        "base0C-hex-g": "be",
                        "base0C-hex-r": "8a",
                        "base0C-rgb-b": "183",
                        "base0C-rgb-g": "190",
                        "base0C-rgb-r": "138",
                        "base0D-dec-b": "0.7450980392156863",
                        "base0D-dec-g": "0.6352941176470588",
                        "base0D-dec-r": "0.5058823529411764",
                        "base0D-hex": "81a2be",
                        "base0D-hex-bgr": "bea281",
                        "base0D-hex-b": "be",
                        "base0D-hex-g": "a2",
                        "base0D-hex-r": "81",
                        "base0D-rgb-b": "190",
                        "base0D-rgb-g": "162",
                        "base0D-rgb-r": "129",
                        "base0E-dec-b": "0.7333333333333333",
                        "base0E-dec-g": "0.5803921568627451",
                        "base0E-dec-r": "0.6980392156862745",
                        "base0E-hex": "b294bb",
                        "base0E-hex-bgr": "bb94b2",
                        "base0E-hex-b": "bb",
                        "base0E-hex-g": "94",
                        "base0E-hex-r": "b2",
                        "base0E-rgb-b": "187",
                        "base0E-rgb-g": "148",
                        "base0E-rgb-r": "178",
                        "base0F-dec-b": "0.35294117647058826",
                        "base0F-dec-g": "0.40784313725490196",
                        "base0F-dec-r": "0.6392156862745098",
                        "base0F-hex": "a3685a",
                        "base0F-hex-bgr": "5a68a3",
                        "base0F-hex-b": "5a",
                        "base0F-hex-g": "68",
                        "base0F-hex-r": "a3",
                        "base0F-rgb-b": "90",
                        "base0F-rgb-g": "104",
                        "base0F-rgb-r": "163",
                        "scheme-author": "Chris Kempson (http://chriskempson.com)",
                        "scheme-name": "Tomorrow Night",
                        "scheme-slug": "tomorrow-night",
                        "scheme-slug-underscored": "tomorrow_night",
                    },
                }
            },
        )

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_builds_all_schemes_in_a_family_if_family_name_is_passed(
        self, mock_run_command
    ):
        set_module_args(
            {"scheme": "tomorrow", "template": "i3", "cache_dir": self.test_cache_dir}
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertIn("tomorrow-night", result_args["schemes"])
        self.assertIn("tomorrow", result_args["schemes"])

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_builds_a_scheme_if_family_name_differs_and_is_passed_in(
        self, mock_run_command
    ):
        set_module_args(
            {
                "scheme": "material-palenight",
                "scheme_family": "materialtheme",
                "template": "i3",
                "cache_dir": self.test_cache_dir,
            }
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertIn("material-palenight", result_args["schemes"])

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_builds_nothing_if_build_false_is_passed(self, mock_run_command):
        set_module_args({"build": False})

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args["changed"], False)
        self.assertEqual(result_args["schemes"], {})

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_builds_everything_if_no_scheme_or_template_is_passed(
        self, mock_run_command
    ):
        set_module_args({"cache_dir": self.test_cache_dir})

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertTrue(len(result_args["schemes"].keys()) > 1)
        self.assertTrue(len(result_args["schemes"]["tomorrow-night"].keys()) > 1)

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_update_runs(self, mock_run_command):
        set_module_args(
            {"update": True, "build": False, "cache_dir": self.test_cache_dir}
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args["changed"], True)
        self.assertEqual(result_args["schemes"], {})

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_update_runs_with_build(self, mock_run_command):
        set_module_args(
            {
                "update": True,
                "scheme": "tomorrow-night",
                "template": "i3",
                "cache_dir": self.test_cache_dir,
            }
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(list(result_args["schemes"].keys()), ["tomorrow-night"])
        self.assertEqual(result_args["changed"], True)

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_update_can_use_template_and_scheme(self, mock_run_command):
        set_module_args(
            {
                "update": True,
                "build": False,
                "scheme": "",
                "template": "",
                "cache_dir": self.test_cache_dir,
            }
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(
            [
                call(
                    [
                        ANY,
                        "clone",
                        "https://github.com/chriskempson/base16-schemes-source",
                        ANY,
                    ],
                    check_rc=True,
                ),
                call(
                    [
                        ANY,
                        "clone",
                        "https://github.com/chriskempson/base16-templates-source",
                        ANY,
                    ],
                    check_rc=True,
                ),
            ],
            mock_run_command.mock_calls,
        )

        self.assertEqual(list(result_args["schemes"].keys()), [])
        self.assertTrue(result_args["changed"])

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_can_use_template_and_scheme_repos(self, mock_run_command):
        set_module_args({"scheme": "tomorrow-night", "template": "i3"})

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()

        set_module_args(
            {
                "scheme": "tomorrow-night",
                "template": "i3",
                "schemes_source": "https://github.com/mnussbaum/base16-schemes-source",
                "templates_source": "https://github.com/mnussbaum/base16-templates-source",
                "cache_dir": self.test_cache_dir,
            }
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args["changed"], True)

        schemes_source = os.path.join(
            self.test_cache_dir, "base16-builder-ansible", "sources", "schemes"
        )
        self.assertTrue(os.path.exists(schemes_source))
        self.assertTrue(
            call(
                [
                    ANY,
                    "clone",
                    "https://github.com/mnussbaum/base16-schemes-source",
                    ANY,
                ],
                check_rc=True,
            )
            in mock_run_command.mock_calls
        )

        templates_source = os.path.join(
            self.test_cache_dir, "base16-builder-ansible", "sources", "templates"
        )
        self.assertTrue(os.path.exists(templates_source))
        self.assertTrue(
            call(
                [
                    ANY,
                    "clone",
                    "https://github.com/mnussbaum/base16-templates-source",
                    ANY,
                ],
                check_rc=True,
            )
            in mock_run_command.mock_calls
        )

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_can_use_template_and_scheme_local_paths(self, mock_run_command):
        set_module_args(
            {
                "scheme": "local-scheme",
                "template": "local-template",
                "schemes_source": os.path.join(
                    os.path.dirname(__file__), "fixtures", "sources", "schemes"
                ),
                "templates_source": os.path.join(
                    os.path.dirname(__file__), "fixtures", "sources", "templates"
                ),
                "cache_dir": self.test_cache_dir,
            }
        )

        with self.assertRaises(AnsibleExitJson) as result:
            base16_builder.main()
        result_args = result.exception.args[0]

        self.assertEqual(result_args["changed"], False)

        self.assertFalse(
            call([ANY, "clone", ANY, ANY], check_rc=True) in mock_run_command.mock_calls
        )

        self.assertEqual(
            result_args["schemes"],
            {
                "local-scheme-night": {
                    "local-template": {
                        "themes": {
                            "base16-local-scheme-night.test": "000000\n00\n00\n00\n0\n0\n0\n0.0\n0.0\n0.0\n"
                        }
                    },
                    "scheme-variables": ANY,
                },
                "local-scheme": {
                    "local-template": {
                        "themes": {
                            "base16-local-scheme.test": "111111\n11\n11\n11\n17\n17\n17\n0.06666666666666667\n0.06666666666666667\n0.06666666666666667\n"
                        }
                    },
                    "scheme-variables": ANY,
                },
            },
        )

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_fails_when_no_schemes_are_found_and_a_scheme_is_passed(
        self, mock_run_command
    ):
        set_module_args(
            {"scheme": "not-a-real-scheme", "cache_dir": self.test_cache_dir}
        )

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()

        self.assertEqual(
            result.exception.args[0]["msg"],
            'Failed to build any schemes. Scheme name "not-a-real-scheme" was passed, but didn\'t match any known schemes',
        )

    @patch.object(basic.AnsibleModule, "run_command", side_effect=fake_run_command)
    def test_module_fails_when_no_templates_are_found_and_a_template_is_passed(
        self, mock_run_command
    ):
        set_module_args(
            {"template": "not-a-real-template", "cache_dir": self.test_cache_dir}
        )

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()

        self.assertEqual(
            result.exception.args[0]["msg"],
            'Failed to build any templates. Template names [\'not-a-real-template\'] were passed, but didn\'t match any known templates',
        )
