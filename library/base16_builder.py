#!/usr/bin/python

# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: base16_builder

short_description: Builds Base16 color schemes and templates

description: Builds and updates Base16 color schemes and templates so that you can install them into config files and render them into your own templates. The module renders scheme templates on the fly so you can use new color schemes that haven't yet been picked up and pre-rendered by the many Base16 template repos.

author:
  - Michael Nussbaum (@mnussbaum)

options:
  scheme:
    description:
      - Set this to the name of a color scheme to only build that one scheme, instead of building all, which is the default
      - Only building a single scheme is much faster then building all
    required: false
    type: string
    default: Build all schemes
  scheme_family:
    description:
      - Set this to the name of a group of schemes that live in a single repo (i.e. a family) to only build that group of schemes
      - If this is unset, and a scheme argument is passed, it's expected the scheme name is present in the scheme family name. E.g. Scheme family "tomorrow" is present in scheme names "tomorrow-night" and "tomorrow"
      - Only set this arg if the scheme family name isn't included in the scheme names. E.g. scheme family "materialtheme" isn't included in scheme name "material-darker"
    required: false
    type: string
    default: Build all schemes
  template:
    description:
      - Set this to the name of a template or a list of template names to only build them instead of building all, which is the default
      - Only building a few templates is much faster then building all
    required: false
    type: list
    default: Build all templates
  cache_dir:
    description:
      - Parent directory to store cloned scheme, template and source data
      - Will be created if it doesn't exist already
      - The default looks for the $XDG_CACHE_DIR env var, then a ~/.cache dir, and falls back to the platform's temp dir if the first two don't exist
    required: false
    type: string
    default: First available of $XDG_CACHE_DIR, $HOME/.cache, or platform derived temp dir
  schemes_source:
    description:
      - Git repo URL or local directory path used to find schemes
      - The source must include a list.yaml file that maps scheme names to scheme repo Git URLs or local directory paths
    required: false
    type: string
    default: https://github.com/chriskempson/base16-schemes-source
  templates_source:
    description:
      - Git repo URL or local directory path used to find templates
      - The source must include a list.yaml file that maps template names to template repo Git URLs or local directory paths
    required: false
    type: string
    default: https://github.com/chriskempson/base16-templates-source
  update:
    description:
      - Clone or pull color scheme and template sources
      - By default will update all schemes and templates, but will repect scheme and template args
      - Build will donwload any missing data, so you never _need_ to call update
    required: false
    type: bool
    default: no
  build:
    description:
      - Set to "no" to disable building of any color schemes or templates
      - Useful to set to "no" when used with update to only download sources
    required: false
    type: bool
    default: yes
"""

EXAMPLES = """
# Build a single color scheme and template and assign it to a variable
- base16_builder:
    scheme: tomorrow-night
    template: shell
  register: base16_schemes

# It helps to print out the registered result once with debug to figure out how
# to access any particular scheme and template. Each Base16 template repo (e.g.
# "shell", "i3") can include multiple template files to render out, so every
# template repo will register their output at a slightly different index path in
# the result object.

- debug:
    var: base16_schemes

# I'll elide the rendered contents for readability, but result will look like this:
#
# "base16_schemes": {
#   "changed": true,
#   "failed": false,
#   "schemes": {
#     "tomorrow-night": {
#       "shell": {
#         "scripts": {
#           "base16-tomorrow-night.sh": "#!/bin/sh\n# base16-shell ..."
#         }
#       },
#       "scheme-variables": {
#         "base00-dec-b": "0.12941176470588237",
#         "base00-dec-g": "0.12156862745098039",
#         "base00-dec-r": "0.11372549019607843",
#         "base00-hex": "1d1f21",
#         "base00-hex-b": "21",
#         "base00-hex-g": "1f",
#         "base00-hex-r": "1d",
#         "base00-rgb-b": "33",
#         "base00-rgb-g": "31",
#         "base00-rgb-r": "29",
#         ...Many more color variables...
#         "scheme-author": "Chris Kempson (http://chriskempson.com)",
#         "scheme-name": "Tomorrow Night",
#         "scheme-slug": "tomorrow-night",
#         "scheme-slug-underscored": "tomorrow_night"
#     }
#   }
# }

# You can write the generated color schemes to a file or render them into your
# own templates
- copy:
    content: "{{ base16_schemes['schemes']['tomorrow-night']['shell']['scripts']['base16-tomorrow-night.sh'] }}"
    dest: /my/bash/profile/dir/tomorrow-night-shell.sh

# Build every template for a single color scheme
- base16_builder:
    scheme: tomorrow-night
  register: base16_schemes

# Build every color scheme for a single template
- base16_builder:
    template: shell
  register: base16_schemes

# Build every color scheme for a few select templates
- base16_builder:
    template:
      - shell
      - i3
      - qutebrowser
  register: base16_schemes

# Build every color scheme for every template
- base16_builder: {}
  register: base16_schemes

# Download latest color scheme and template source files, but don't build anything
- base16_builder:
    update: yes
    build: no

# Download updates for and rebuild a single template and scheme
- base16_builder:
    update: yes
    scheme: tomorrow-night
    template: shell
  register: base16_schemes

# If you make your own Base16 color scheme and want to reference it before it's
# pulled into the master list of schemes you can fork the master list, add a
# reference to your scheme, and then use your list fork as the schemes source
# arg here. The same applies to new template repos and the master template
# list. Those master lists are available at:
#
#   https://github.com/chriskempson/base16-schemes-source
#   https://github.com/chriskempson/base16-templates-source
#
- base16_builder:
    scheme: my-brand-new-color-scheme
    template: shell
    schemes_source: http://github.com/my-user/my-schemes-source-fork
    templates_source: http://github.com/my-user/my-templates-source-fork
"""

RETURN = """
schemes:
  description: A dict of color schemes mapped to nested dicts of rendered templates. One special template is also rendered for every color scheme called "scheme-variables". This contains the raw base16 color variables used for that scheme. These can be useful for rendering Ansible templates with individual color codes.
  type: dict
  sample:
    schemes:
      tomorrow-night:
        scheme-variables:
          scheme-author: "Chris Kempson (http://chriskempson.com)"
          scheme-name: "Tomorrow Night"
          scheme-slug: "tomorrow-night",
          scheme-slug-underscored: "tomorrow_night",
          base00-dec-b: "0.12941176470588237"
          base00-dec-g: "0.12156862745098039"
          base00-dec-r: "0.11372549019607843"
          base00-hex: "1d1f21"
          base00-hex-b: "21"
          base00-hex-g: "1f"
          base00-hex-r: "1d"
          base00-rgb-b: "33"
          base00-rgb-g: "31"
          base00-rgb-r: "29"
          ...Many more colors variables...
        shell:
          scripts:
            base16-tomorrow-night.sh: "#!/bin/sh\n# base16-shell ..."
        vim:
          colors:
            base16-tomorrow-night.colors: "\" vi:syntax=vim\n\n\" base16-vim ..."
      gruvbox-light-soft:
        scheme-variables:
          ...Color variables...
        shell:
          scripts:
            base16-gruvbox-light-soft.sh: "#!/bin/sh\n# base16-shell ..."
        vim:
          colors:
            base16-gruvbox-light-soft.colors: "\" vi:syntax=vim\n\n\" base16-vim ..."
      gruvbox-dark-medium:
        scheme-variables:
          ...Color variables...
        shell:
          scripts:
            base16-gruvbox-dark-medium.sh: "#!/bin/sh\n# base16-shell ..."
        vim:
          colors:
            base16-gruvbox-dark-medium.colors: "\" vi:syntax=vim\n\n\" base16-vim ..."
"""

import os
import shutil
import tempfile
import yaml

from ansible.module_utils.basic import AnsibleModule

PYSTACHE_ERR = None
try:
    import pystache
except (ImportError, ModuleNotFoundError) as err:
    PYSTACHE_ERR = err


def open_yaml(path):
    with open(path) as yaml_file:
        return yaml.safe_load(yaml_file)


class GitRepo(object):
    def __init__(self, builder, url_or_local_path, clone_dest):
        self.builder = builder
        self.module = builder.module
        self.git_path = self.module.get_bin_path("git", True)

        if os.path.exists(url_or_local_path):
            self.path = url_or_local_path
            self.local_repo = True
        else:
            self.local_repo = False
            self.url = url_or_local_path
            self.path = clone_dest

        self.git_config_path = os.path.join(self.path, ".git", "config")

    def clone_or_pull(self):
        if self.local_repo:
            return

        if not self.clone_if_missing():
            self.builder.result["changed"] = True
            if self.module.check_mode:
                return

            self.module.run_command(
                [self.git_path, "pull"], cwd=self.path, check_rc=True
            )

    def clone_if_missing(self):
        if self.local_repo:
            return

        if not os.path.exists(os.path.dirname(self.path)):
            self.builder.result["changed"] = True
            if self.module.check_mode:
                return

            os.makedirs(os.path.dirname(self.path))

        if self._repo_at_path():
            return False

        self.builder.result["changed"] = True
        if self.module.check_mode:
            return

        # If a different repo is at the given path, replace it
        if os.path.exists(self.git_config_path):
            shutil.rmtree(self.path)

        self.module.run_command(
            [self.git_path, "clone", self.url, self.path], check_rc=True
        )

        return True

    def _repo_at_path(self):
        """
        This is a very rough heuristic to tell if there's a git repo at the
        path that points to the same repo URL we were given. It would be better
        to parse the file, but that would pull in another dependency :/
        """
        if not os.path.exists(self.git_config_path):
            return False

        with open(self.git_config_path) as git_config:
            if "url = {}".format(self.url) in git_config.read():
                return True

        return False


class Base16SourceRepo(object):
    def __init__(self, builder, source_repo_class):
        self.builder = builder
        self.module = builder.module
        self.source_repo_class = source_repo_class
        self.source_type = source_repo_class.source_type
        self.git_repo = GitRepo(
            builder,
            self.module.params["{}_source".format(self.source_type)],
            os.path.join(
                self.module.params["cache_dir"],
                "base16-builder-ansible",
                "sources",
                self.source_type,
            ),
        )

    def _source_repos(self):
        for (source_family, source_url) in open_yaml(
            os.path.join(self.git_repo.path, "list.yaml")
        ).items():
            # Not sure if caching this value would be good or not
            yield self.source_repo_class(
                self.builder,
                source_family,
                source_url,
                os.path.join(
                    self.module.params["cache_dir"],
                    "base16-builder-ansible",
                    self.source_type,
                    source_family,
                ),
            )

    def sources(self):
        self.git_repo.clone_if_missing()
        for source_repo in self._source_repos():
            for source in source_repo.sources():
                yield source

    def update(self):
        self.git_repo.clone_or_pull()
        for source_repo in self._source_repos():
            source_repo.clone_or_pull()


class Scheme(object):
    def __init__(self, path):
        self.path = path
        self.data = {}
        self._slug = None

        self.base16_vars = {
            "scheme-author": self._data()["author"],
            "scheme-name": self._data()["scheme"],
            "scheme-slug": self.slug(),
            "scheme-slug-underscored": self.slug().replace("-", "_"),
        }
        self.computed_bases = False

    def _data(self):
        if self.data:
            return self.data

        self.data = open_yaml(self.path)
        return self.data

    def slug(self):
        if self._slug:
            return self._slug

        self._slug = (
            os.path.splitext(os.path.basename(self.path))[0].lower().replace(" ", " ")
        )

        return self._slug

    def base16_variables(self):
        if self.computed_bases:
            return self.base16_vars

        for base in ["{:02X}".format(i) for i in range(16)]:
            base_key = "base{}".format(base)
            base_hex_key = "{}-hex".format(base_key)
            base_hex_r = self._data()[base_key][0:2]
            base_hex_g = self._data()[base_key][2:4]
            base_hex_b = self._data()[base_key][4:6]
            self.base16_vars.update(
                {
                    base_hex_key: self._data()[base_key],
                    "{}-r".format(base_hex_key): base_hex_r,
                    "{}-g".format(base_hex_key): base_hex_g,
                    "{}-b".format(base_hex_key): base_hex_b,
                    "{}-hex-bgr".format(base_key): "{}{}{}".format(
                        base_hex_b,
                        base_hex_g,
                        base_hex_r,
                    ),
                }
            )
            self.base16_vars.update(
                {
                    "{}-rgb-r".format(base_key): str(
                        int(self.base16_vars[base_hex_key + "-r"], 16)
                    ),
                    "{}-rgb-g".format(base_key): str(
                        int(self.base16_vars[base_hex_key + "-g"], 16)
                    ),
                    "{}-rgb-b".format(base_key): str(
                        int(self.base16_vars[base_hex_key + "-b"], 16)
                    ),
                    "{}-dec-r".format(base_key): str(
                        int(self.base16_vars[base_hex_key + "-r"], 16) / 255
                    ),
                    "{}-dec-g".format(base_key): str(
                        int(self.base16_vars[base_hex_key + "-g"], 16) / 255
                    ),
                    "{}-dec-b".format(base_key): str(
                        int(self.base16_vars[base_hex_key + "-b"], 16) / 255
                    ),
                }
            )

        self.computed_bases = True
        return self.base16_vars


class SchemeRepo(object):
    source_type = "schemes"

    def __init__(self, builder, name, source_url_or_local_path, clone_dest):
        self.builder = builder
        self.module = builder.module
        self.name = name
        self.git_repo = GitRepo(self.builder, source_url_or_local_path, clone_dest)

    def sources(self):
        # Only clone and yield scheme repos that could contain the requested
        # scheme. We still need to do an exact comparison with the scheme slug
        # to only yield a single requested scheme though.
        if not self._matches_params():
            return

        self.git_repo.clone_if_missing()

        for path in os.listdir(self.git_repo.path):
            if os.path.splitext(path)[1] in [".yaml", ".yml"]:
                # Cache schemes here?
                scheme = Scheme(os.path.join(self.git_repo.path, path))
                module_scheme_arg = self.module.params.get("scheme")
                if (
                    module_scheme_arg is not None
                    and module_scheme_arg not in scheme.slug()
                ):
                    continue

                yield scheme

    def clone_or_pull(self):
        if not self._matches_params():
            return

        self.git_repo.clone_or_pull()

    def _matches_params(self):
        module_scheme_arg = self.module.params.get("scheme")
        module_scheme_family_arg = (
            self.module.params.get("scheme_family") or module_scheme_arg
        )
        if module_scheme_family_arg is None:
            return True

        return self.name in module_scheme_family_arg


class Template(object):
    def __init__(self, family, path, config):
        self.family = family
        self.path = path
        self.config = config
        self.renderer = pystache.Renderer(search_dirs=os.path.dirname(self.path))

    def build(self, scheme):
        # The base16 spec calls for the file to be written to
        # os.path.join(
        #     os.path.dirname(self.path),
        #     self.config['output'],
        #     'base16-{}.{}'.format(scheme.slug(), self.config['extension']),
        # )
        return {
            "output_dir": self.config["output"],
            "output_file_name": "base16-{}{}".format(
                scheme.slug(), self.config["extension"]
            ),
            "output": self.renderer.render_path(self.path, scheme.base16_variables()),
        }


class TemplateRepo(object):
    source_type = "templates"

    def __init__(self, builder, name, url_or_local_path, clone_dest):
        self.builder = builder
        self.module = builder.module
        self.name = name
        self.git_repo = GitRepo(self.builder, url_or_local_path, clone_dest)
        self.templates_dir = os.path.join(self.git_repo.path, "templates")

    def sources(self):
        if not self._matches_params():
            return

        self.git_repo.clone_if_missing()

        for path in os.listdir(self.templates_dir):
            (file_name, file_ext) = os.path.splitext(path)
            if file_name != "config" or file_ext not in [".yaml", ".yml"]:
                continue

            for template_name, template_config in open_yaml(
                os.path.join(self.templates_dir, path)
            ).items():
                # Cache here?
                yield Template(
                    self.name,
                    os.path.join(
                        self.templates_dir, "{}.mustache".format(template_name)
                    ),
                    template_config,
                )

    def clone_or_pull(self):
        if not self._matches_params():
            return

        self.git_repo.clone_or_pull()

    def _matches_params(self):
        module_template_arg = self.module.params.get("template")
        if module_template_arg is None:
            return True

        return self.name in module_template_arg


class Base16Builder(object):
    def __init__(self, module):
        self.module = module

        self.schemes_repo = Base16SourceRepo(self, SchemeRepo)
        self.templates_repo = Base16SourceRepo(self, TemplateRepo)

        self.result = dict(changed=False, schemes=dict())

    def run(self):
        if PYSTACHE_ERR:
            self.module.fail_json(
                msg="Failed to import pystache. Type `pip install pystache` - {}".format(
                    PYSTACHE_ERR
                ),
                **self.result
            )

        if self.module.params["update"]:
            self.schemes_repo.update()
            self.templates_repo.update()

        if not self.module.params["build"]:
            self.module.exit_json(**self.result)

        for scheme in self.schemes_repo.sources():
            scheme_result = {}
            self.result["schemes"][scheme.slug()] = scheme_result

            scheme_result["scheme-variables"] = scheme.base16_variables()

            for template in self.templates_repo.sources():
                build_result = template.build(scheme)
                if not scheme_result.get(template.family):
                    scheme_result[template.family] = {}

                template_family_result = scheme_result[template.family]

                if not template_family_result.get(build_result["output_dir"]):
                    template_family_result[build_result["output_dir"]] = {}

                template_result = template_family_result[build_result["output_dir"]]
                template_result[build_result["output_file_name"]] = build_result[
                    "output"
                ]

            if len(scheme_result) == 1 and self.module.params["template"]:
                failure_msg = "Failed to build any templates."
                if self.module.params["template"]:
                    failure_msg = '{} Template names {} were passed, but didn\'t match any known templates'.format(
                        failure_msg, self.module.params["template"]
                    )

                self.module.fail_json(msg=failure_msg, **self.result)

        if not self.result["schemes"]:
            failure_msg = "Failed to build any schemes."
            if self.module.params["scheme"]:
                failure_msg = '{} Scheme name "{}" was passed, but didn\'t match any known schemes'.format(
                    failure_msg, self.module.params["scheme"]
                )

            self.module.fail_json(msg=failure_msg, **self.result)

        self.module.exit_json(**self.result)


def main():
    if "XDG_CACHE_DIR" in os.environ.keys():
        default_cache_dir = os.environ["XDG_CACHE_DIR"]
    elif os.path.exists(os.path.join(os.path.expanduser("~"), ".cache")):
        default_cache_dir = os.path.join(os.path.expanduser("~"), ".cache")
    else:
        default_cache_dir = tempfile.gettempdir()

    module = AnsibleModule(
        argument_spec=dict(
            update=dict(type="bool", required=False, default=False),
            build=dict(type="bool", required=False, default=True),
            scheme=dict(type="str", required=False),
            scheme_family=dict(type="str", required=False),
            template=dict(type="list", required=False),
            cache_dir=dict(type="str", required=False, default=default_cache_dir),
            schemes_source=dict(
                type="str",
                required=False,
                default="https://github.com/chriskempson/base16-schemes-source",
            ),
            templates_source=dict(
                type="str",
                required=False,
                default="https://github.com/chriskempson/base16-templates-source",
            ),
        ),
        supports_check_mode=True,
    )

    return Base16Builder(module).run()


if __name__ == "__main__":
    main()
