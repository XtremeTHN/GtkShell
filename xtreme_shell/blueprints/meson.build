blueprints = custom_target('blueprints',
  input: files(
    'bar.blp',
    'control.blp',
    'center.blp',
    'script-item.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)