import PyInstaller.__main__ as py
import os
import shutil


def build_client():
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
    ]

    try:
        py.run(args)

    except Exception as e:
        raise RuntimeError("Failed to build client with exception {}".format(e))

    else:
        def mv_dir(path_, dirname):
            try:
                shutil.move(path_, 'dist/client/')
            except FileNotFoundError:
                os.mkdir(os.path.join('dist/client/', dirname))

        shutil.rmtree('build')
        os.remove('client.spec')

        mv_dir('dist/client/_internal/icons', 'icons')
        mv_dir('dist/client/_internal/instances', 'instances')
        mv_dir('dist/client/_internal/logs', 'logs')
        mv_dir('dist/client/_internal/plugins', 'plugins')
        mv_dir('dist/client/_internal/settings', 'settings')
        mv_dir('dist/client/_internal/source', 'source')

        try:
            shutil.rmtree('dist/client/instances/shell_history')
        except FileNotFoundError:
            pass
        os.mkdir('dist/client/instances/shell_history')

        try:
            shutil.rmtree('dist/client/logs')
        except FileNotFoundError:
            pass
        os.mkdir('dist/client/logs')

        shutil.copytree('main/bin/', 'dist/bin/', dirs_exist_ok=True)


if __name__ == "__main__":
    build_client()

