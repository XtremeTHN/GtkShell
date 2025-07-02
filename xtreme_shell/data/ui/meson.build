blueprints = custom_target('blueprints',
  input: files(
    'bar.blp',
    'music-label.blp',
    'music-viewer-controls.blp',
    'music-viewer.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)