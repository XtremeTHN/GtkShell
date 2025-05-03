moduledir = pkgdatadir / meson.project_name() / 'widgets' / 'quick'

modules_sources = [
    '__init__.py',
    'settings.py'
]

install_data(modules_sources, install_dir: moduledir)

subdir('buttons')
subdir('scales')
