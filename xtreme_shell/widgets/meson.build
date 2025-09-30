moduledir = pkgdatadir / meson.project_name() / 'widgets'

modules_sources = [
    '__init__.py',
    'cava.py'
]

install_data(modules_sources, install_dir: moduledir)

subdir('bar')
subdir('icons')
subdir('control')
subdir('applications')
subdir('notifications')