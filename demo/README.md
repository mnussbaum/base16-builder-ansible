In this demo I'll:

  1. Change my Base16 color scheme from `twilight` to `unikitty-dark` with Ansible
  2. Source my `~/.zshrc` to pick up my new shell theme
  3. Reload i3 with `$mod+Shift+c` to pick up my new i3 theme
  4. Source my `~/.config/nvim/plugin/colors.vim` file to pick up my new Vim theme

The full Ansible playbook is in the pane above, and my i3 config template is to
the right.

All of this code is available at `https://github.com/mnussbaum/base16-builder-ansible/demo`.
If you want to run the demo yourself, kick it off with:

    $ ansible-playbook colors.yml

The playbook expects you have `ansible-base16-builder`'s dependencies
installed, so you'll need `pystache` and Ansible. See the main project README
for more details.
