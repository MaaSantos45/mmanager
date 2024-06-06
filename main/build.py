import PyInstaller.__main__ as py
import os
import shutil
import sys


def check_datas():
    dirpath = f'main/client/'
    for dirname in ['icons', 'instances', 'logs', 'plugins', 'settings', 'source']:
        if not os.path.exists(os.path.join(dirpath, dirname)):
            os.mkdir(os.path.join(dirpath, dirname))


def build_client(name: str):
    args = [
        'main/client/client.py',
        '--noconfirm',
        '--onedir',
        '--windowed',
        '--add-data', 'venv/Lib/site-packages/customtkinter;customtkinter/',
        '--add-data', 'main/client/icons;icons/',
        '--add-data', 'main/client/instances;instances/',
        '--add-data', 'main/client/logs;logs/',
        '--add-data', 'main/client/plugins;plugins/',
        '--add-data', 'main/client/settings;settings/',
        '--add-data', 'main/client/source;source/',
        '--name', name
    ]

    try:
        py.run(args)

    except Exception as e:
        raise RuntimeError("Failed to build client with exception {}".format(e))

    else:
        def mv_dir(path_, dirname):
            try:
                shutil.move(path_, f'dist/{name}/')
            except FileNotFoundError:
                os.mkdir(os.path.join(f'dist/{name}/', dirname))

        shutil.rmtree('build')

        os.remove(f'{name}.spec')

        mv_dir(f'dist/{name}/_internal/icons', 'icons')
        mv_dir(f'dist/{name}/_internal/instances', 'instances')
        mv_dir(f'dist/{name}/_internal/logs', 'logs')
        mv_dir(f'dist/{name}/_internal/plugins', 'plugins')
        mv_dir(f'dist/{name}/_internal/settings', 'settings')
        mv_dir(f'dist/{name}/_internal/source', 'source')

        try:
            shutil.rmtree(f'dist/{name}/instances/shell_history')
        except FileNotFoundError:
            pass
        os.mkdir(f'dist/{name}/instances/shell_history')

        try:
            shutil.rmtree(f'dist/{name}/logs')
        except FileNotFoundError:
            pass
        os.mkdir(f'dist/{name}/logs')

        shutil.copytree('main/bin/', 'dist/bin/', dirs_exist_ok=True)


if __name__ == "__main__":
    output = 'client'
    if len(sys.argv) == 2:
        output = sys.argv[1]
    check_datas()
    build_client(output)

