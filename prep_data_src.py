import json
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

import requests
import yaml


def update_website(file_path, url):
    data_src = requests.get(f'https://r.jina.ai/{url}')
    with open(file_path, 'w') as f:
        f.write(data_src.text)


def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    data_srcs = cfg['data_srcs']

    save_path = Path(data_srcs['save_path'])
    save_path.mkdir(exist_ok=True)

    for name, url in data_srcs['websites'].items():
        doc_src_path = save_path / f'{name}.md'
        if not doc_src_path.exists():
            update_website(doc_src_path, save_path)

    for pdf_path in Path(data_srcs["pdf_dir"]).glob('*.pdf'):
        if not (save_path / pdf_path.stem).exists():
            subprocess.run(
                f'DEFAULT_LANG="en" marker_single {pdf_path} {save_path}',
                shell=True, executable='/bin/bash'
            )

    with open(save_path / 'doc_src_paths.json', 'w') as f:
        doc_src_paths = list(map(str, save_path.rglob('*.md')))
        json.dump(doc_src_paths, f, indent=2)


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-w', '--update-website', action='store_true')
    parser.add_argument('-f', '--config')
    parser.add_argument('--file-path')
    parser.add_argument('--url')
    parser.add_argument('--save-path')

    args = parser.parse_args()

    if args.update_website:
        update_website(args.file_path, args.url)
    else:
        main(args.config)
