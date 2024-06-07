import os


def setup_dirs(path_to_change):
    try:
        os.chdir(path_to_change)
    except Exception as e:
        raise NotADirectoryError(f"Dir Path:{path_to_change} unable by: {e}")

    dir_path = '.'

    for dirname in ['icons', 'instances', 'logs', 'plugins', 'settings', 'source']:
        if not os.path.exists(os.path.join(dir_path, dirname)):
            os.mkdir(os.path.join(dir_path, dirname))

        if dirname == 'instances':
            if not os.path.exists(os.path.join(os.path.join(dir_path, 'instances'), 'shell_history')):
                os.mkdir(os.path.join(os.path.join(dir_path, 'instances'), 'shell_history'))

            if not os.path.exists(os.path.join(os.path.join(dir_path, 'instances'), 'files')):
                os.mkdir(os.path.join(os.path.join(dir_path, 'instances'), 'files'))
        elif dirname == 'settings':
            standard = {'apparence': 'System', 'color_theme': 'dark-blue', 'connections': ''}
            for file in ['apparence', 'color_theme', 'connections']:
                if not os.path.exists(os.path.join(os.path.join(dir_path, dirname), file)):
                    with open(os.path.join(os.path.join(dir_path, dirname), file), 'w') as f:
                        f.write(standard[file])
        elif dirname == 'source':
            try:
                os.mkdir(os.path.join(os.path.join(dir_path, dirname), 'dist'))
            except FileExistsError:
                pass

            try:
                os.mkdir(os.path.join(os.path.join(dir_path, dirname), 'config'))
            except FileExistsError:
                pass

            lines = [
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n',
                '<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">\n',
                '  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">\n',
                '    <security>\n',
                '      <requestedPrivileges>\n',
                '        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>\n',
                '      </requestedPrivileges>\n',
                '    </security>\n',
                '  </trustInfo>\n',
                '</assembly>\n',
            ]
            if not os.path.exists(os.path.join(os.path.join(os.path.join(dir_path, dirname), 'config'), 'manifest.xml')):
                with open(os.path.join(os.path.join(os.path.join(dir_path, dirname), 'config'), 'manifest.xml'), 'w') as manifest:
                    for line in lines:
                        manifest.write(line)
