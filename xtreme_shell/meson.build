pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / meson.project_name()

python = import('python')
python_i = python.find_installation('python3', modules: ['gi', 'inotify', 'requests'])

conf = configuration_data()
conf.set('VERSION', meson.project_version())
conf.set('pkgdatadir', pkgdatadir)

configure_file(
    input: 'shell.in',
    output: 'shell',
    configuration: conf,
    install: true,
    install_dir: get_option('bindir'),
    install_mode: 'r-xr-xr-x'
)

shell_sources = [
    '__init__.py',
    'main.py'
]

install_data(shell_sources, install_dir: moduledir)
subdir('lib')
# subdir('style')
subdir('widgets')