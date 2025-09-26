pkgdatadir = get_option('prefix') / get_option('datadir')
moduledir = pkgdatadir / meson.project_name()

gnome = import('gnome')

python = import('python')
python_i = python.find_installation('python3', modules: ['gi'])

subdir('blueprints')

gnome.compile_resources(
    'xtreme-shell',
    'xtreme-shell.gresource.xml',
    gresource_bundle: true,
    dependencies: blueprints,
    install: true,
    install_dir: moduledir
)

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

xtreme_shell_sources = [
    '__init__.py',
    'main.py'
]

install_data(xtreme_shell_sources, install_dir: moduledir)
install_subdir('scss', install_dir: moduledir)
install_subdir('icons', install_dir: moduledir)

subdir('modules')
subdir('widgets')