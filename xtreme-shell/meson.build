pkgdatadir = get_option('prefix') / get_option('datadir')
moduledir = pkgdatadir / meson.project_name()

python = import('python')
python_i = python.find_installation('python3', modules: ['gi', 'rich', 'setproctitle'])

dependency('gtk4-layer-shell-0')
dependency('gtk4')
dependency('libadwaita-1')

conf = configuration_data()
conf.set('VERSION', meson.project_version())
conf.set('pkgdatadir', pkgdatadir)

configure_file(
    input: 'xtreme-shell.in',
    output: 'xtreme-shell',
    configuration: conf,
    install: true,
    install_dir: get_option('bindir'),
    install_mode: 'r-xr-xr-x'
)

xtreme_shell_sources = [
    '__init__.py',
    'main.py'
]

install_data(xtreme_shell_sources, install_dir: moduledir)
# install_subdir('style', install_dir: moduledir)

subdir('components')
subdir('modules')
subdir('widgets')
