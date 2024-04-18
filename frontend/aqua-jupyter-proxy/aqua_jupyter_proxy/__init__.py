from pathlib import Path


def setup_aqua_proxy():
    return {
        'command': ['python', '/tmp/launch_frontend.py', '{base_url}', '{port}'],
        'timeout': 60,
        'new_browser_tab': True,
        'absolute_url': False,
        'launcher_entry': {
            'title': 'Aqua',
            'icon_path': Path(__file__).parent.absolute() / 'icons' / 'rick_astley.svg'
        }
    }
