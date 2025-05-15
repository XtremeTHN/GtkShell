moduledir = pkgdatadir / meson.project_name() / 'lib'

modules_sources = [
    '__init__.py',
    'debug.py',
    'network.py',
    'logger.py',
    'task.py',
    'loader.py',
    'bluetooth.py',
    'variable.py',
    'utils.py',
    'style.py',
    'versions.py',
    'config.py',
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
