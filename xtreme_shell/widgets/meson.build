moduledir = pkgdatadir / meson.project_name() / 'widgets'

modules_sources = [
    '__init__.py',
    'images.py',
    'window.py',
    'cava.py',
    'box.py',
]

install_data(modules_sources, install_dir: moduledir)

subdir('bar')
subdir('music')