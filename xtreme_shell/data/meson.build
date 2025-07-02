gnome = import('gnome')

moduledir = pkgdatadir / meson.project_name() / 'data'

install_subdir('styles', install_dir: moduledir)
subdir('ui')

gnome.compile_resources(
    'xtreme-shell',
    'xtreme-shell.gresource.xml',
    gresource_bundle: true,
    dependencies: blueprints,
    install: true,
    install_dir: moduledir
)