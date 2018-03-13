ansible-base16-builder
================

This module builds and returns [Base16](https://github.com/chriskempson/base16)
color schemes. Base16 is a framework for generating themes for a wide variety
of applications like Vim, Bash or i3 and color schemes like Tomorrow Night or
Gruvbox.

## Dependencies

Besides Ansible itself, the module's only depedency is
[pystache](https://github.com/defunkt/pystache). You can install it with:

    $ pip install pystache

## Example usages

```yaml
# Build a single color scheme and template and assign it to a variable
- name: Build solarflare for i3
  base16_builder:
    scheme: solarflare
    template: i3
  register: base16_schemes

# It helps to print out the result to figure out how to access any particular
# scheme and template.
# Each base16 template repo (e.g. "i3") can include multiple template files,
# so we need these deeply nested result objects to handle them all
- debug:
    var: base16_schemes

# You can write the generated color schemes to a file or render them into config templates
- copy:
    content: "{{ base16_schemes['solarflare']['i3']['bar-colors']['base16-tomorrow-night.config'] }}"
    dest: /tmp/solarflare-i3-bar-colors.config

# Build every template for the a single color scheme
- name: Build solarflare for every template
  base16_builder:
    scheme: solarflare
  register: base16_schemes

# Build every color scheme for a single template
- name: Build every color scheme for i3
  base16_builder:
    template: i3
  register: base16_schemes

# Build every color scheme for every template
- name: Build every color scheme for every template
  base16_builder: {}
  register: base16_schemes

# Ensure the latest color schemes and templates are downloaded, don't build anything
- name: Update base16 schemes and templates
  base16_builder:
    update: yes
    build: no

# Ensure the latest color schemes and templates are downloaded, build one
- name: Update base16 schemes and templates and build solarflare for i3
  base16_builder:
    update: yes
    scheme: solarflare
    template: i3
  register: base16_schemes

# Ensure the latest color schemes and templates are downloaded, from custom repos
- name: Update base16 schemes and templates from custom repos
  base16_builder:
    update: yes
    build: no
    schemes_source: http://github.com/my_user/my_schemes_sources_fork
    templates_source: http://github.com/my_user/my_templates_sources_fork
```

## Options

```yaml
update:
    description:
        - Refresh color scheme and template sources
    required: false
    type: bool
    default: no
build:
    description:
        - Set to no to not build any color schemes or templates
    required: false
    type: bool
    default: yes
scheme:
    description:
        - Name of a single color scheme to build
    required: false
    type: string
    default: Build all schemes
template:
    description:
        - Name of a single template to build
    required: false
    type: string
    default: Build all templates
data_dir:
    description:
        - Directory to store cloned scheme and template source data
    required: false
    type: string
    default: TODO
schemes_source:
    description:
        - Git repo URL to clone for scheme source data
    required: false
    type: string
    default: https://github.com/chriskempson/base16-schemes-source
templates_source:
    description:
        - Git repo URL to clone for template source data
    required: false
    type: string
    default: https://github.com/chriskempson/base16-templates-source
```

## Developing

This project uses [Pipenv](https://github.com/pypa/pipenv) to install
dependencies. To run the tests:

```bash
pip install --user pipenv
pipenv install
pipenv shell
nose2
```

## To do

* Perf test to decide for/against in memory object retention
* Cache output to local files for reuse?
* Make the tests use fixtures instead of actually cloning repos
