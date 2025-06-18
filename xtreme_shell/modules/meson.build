moduledir = pkgdatadir / meson.project_name() / 'modules'

modules_sources = [
    '__init__.py',
    'config.py',
    'constants.py',
    'gobject.py',
    'logger.py',
    'style.py',
    'thread.py',
    'versions.py'
]

install_data(modules_sources, install_dir: moduledir)
subdir('services')