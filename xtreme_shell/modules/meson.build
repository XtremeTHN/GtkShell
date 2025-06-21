moduledir = pkgdatadir / meson.project_name() / 'modules'

modules_sources = [
    '__init__.py',
    'config.py',
    'gobject.py',
    'logger.py',
    'style.py',
    'thread.py',
    'versions.py'
]

configure_file(
    input: 'constants.in',
    output: 'constants.py',
    configuration: conf,
    install: true,
    install_dir: moduledir,
    install_mode: 'r--r--r--'
)

install_data(modules_sources, install_dir: moduledir)
subdir('services')