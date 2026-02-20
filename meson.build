project('athanor',
  version: '0.1.0',
  meson_version: '>= 0.59.0'
)

app_id = 'io.github.athanor_dev.athanor_launcher'

python = import('python')
gnome = import('gnome')
py3 = python.find_installation('python3')

prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
pkgdatadir = join_paths(prefix, get_option('datadir'), meson.project_name())


blueprint_compiler = find_program('blueprint-compiler')
blueprints = custom_target('blueprints',
  input: files('data/ui/main.blp'),
  output: 'main.ui',
  command: [blueprint_compiler, 'compile', '@INPUT@', '--output', '@OUTPUT@'],
)

resources = gnome.compile_resources(
  'athanor',
  'data/athanor.gresource.xml',
  source_dir: [
    'data',
    meson.current_build_dir(),
  ],
  dependencies: blueprints,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir
)

conf_py = configuration_data()
conf_py.set_quoted('APP_ID',app_id)
conf_py.set_quoted('PKGDATADIR', pkgdatadir)
conf_py.set_quoted('NWJS_DIR', '/app/nwjs')
conf_py.set_quoted('RESOURCE_PATH',join_paths(pkgdatadir,'athanor.gresource'))
conf_py.set_quoted('VERSION', meson.project_version())

configure_file(
  input: 'src/athanor/config.py.in',
  output: 'config.py',
  configuration: conf_py,
  install: true,
  install_dir: join_paths(pkgdatadir, 'athanor/')
)

install_subdir(
  'src/athanor',
  install_dir: pkgdatadir,
  exclude_files: [
    'config.py',
    'config.py.in',
    '__pycache__'
  ]
)

conf = configuration_data()
conf.set('PYTHON', py3.full_path())
conf.set('PKGDATADIR', pkgdatadir)

configure_file(
  input: 'data/athanor.in',
  output: 'athanor',
  configuration: conf,
  install: true,
  install_dir: bindir,
  install_mode: 'rwxr-xr-x'
)

install_data(
    'data/io.github.athanor_dev.athanor_launcher.desktop',
    install_dir: join_paths(get_option('datadir'), 'applications')
)

install_data(
    'data/io.github.athanor_dev.athanor_launcher.svg',
    install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps')
)


run_target('run_app',
  command: [
    py3,
    join_paths(meson.current_source_dir(), 'src/athanor/main.py')
  ]
)