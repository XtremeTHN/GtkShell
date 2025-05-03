moduledir = pkgdatadir / meson.project_name() / 'lib'

modules_sources = [
    '__init__.py',
    'debug.py',
    'network.py',
    'logger.py',
    'task.py',
    'constants.py',
    'bluetooth.py',
    'variable.py',
    'utils.py',
    'style.py',
    'versions.py',
    'config.py',
]

install_data(modules_sources, install_dir: moduledir)

subdir('services')