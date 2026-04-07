project('athanor',
  version: '0.2.1',
  meson_version: '>= 0.59.0'
)

app_id = 'io.github.athanor_dev.athanor-launcher'

python = import('python')
gnome = import('gnome')
py3 = python.find_installation('python3')
i18n = import('i18n')

prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
pkgdatadir = join_paths(prefix, get_option('datadir'), meson.project_name())
localedir = prefix / get_option('localedir')

po_dir = meson.current_source_dir() / 'po'

# gettext_package = meson.project_name()
# i18n.gettext(gettext_package,
#   args: ['--directory=' + po_dir],
#   preset: 'glib',
#   install: true,
#   install_dir: localedir,
#   data_dirs: po_dir
# )
subdir('po')


blueprint_compiler = find_program('blueprint-compiler')
blueprint_files = [
  'data/ui/page/add_game_page.blp',
  'data/ui/page/game_detail_page.blp',
  'data/ui/page/home_page.blp',
  'data/ui/widget/file_chooser_row.blp',
  'data/ui/widget/game_row.blp',
  'data/ui/window/main_window.blp'
]

blueprints = []
foreach blp : blueprint_files
  blueprints += custom_target(
    blp.underscorify(),
    input: blp,
    output: '@BASENAME@.ui',
    command: [blueprint_compiler, 'compile', '--output', '@OUTPUT@', '@INPUT@']
  )
endforeach

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
conf_py.set_quoted('LOCALE_DIR', localedir)

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



# data/meson.build
i18n.merge_file(
  input: 'data/io.github.athanor_dev.athanor-launcher.desktop.in',
  output: 'io.github.athanor_dev.athanor-launcher.desktop',
  type: 'desktop',
  po_dir: po_dir,
  install: true,
  install_dir: get_option('datadir') / 'applications'
)

i18n.merge_file(
  input: 'data/io.github.athanor_dev.athanor-launcher.metainfo.xml.in',
  output: 'io.github.athanor_dev.athanor-launcher.metainfo.xml',
  type: 'xml',
  po_dir: po_dir,
  install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

# install_data(
#     'data/io.github.athanor_dev.athanor-launcher.desktop',
#     install_dir: join_paths(get_option('datadir'), 'applications')
# )

install_data(
    'data/io.github.athanor_dev.athanor-launcher.svg',
    install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps')
)

# install_data(
#     'data/io.github.athanor_dev.athanor-launcher.metainfo.xml',
#     install_dir: join_paths(get_option('datadir'), 'metainfo')
# )


run_target('run_app',
  command: [
    py3,
    join_paths(meson.current_source_dir(), 'src/athanor/main.py')
  ]
)