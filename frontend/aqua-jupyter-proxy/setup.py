import setuptools


setuptools.setup(
    name='aqua-jupyter-proxy',
    author='Kimbo Chen',
    packages=setuptools.find_packages(),
    install_requires=[
        'jupyter-server-proxy>=1.5.0',
        'gradio',
        'requests'
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'aqua = aqua_jupyter_proxy:setup_aqua_proxy'
        ]
    },
    package_data={
        'aqua_jupyter_proxy': ['icons/rick_astley.svg'],
    }
)
