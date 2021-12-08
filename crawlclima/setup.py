import os

from setuptools import find_packages, setup
from setuptools_scm import get_version

local = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

version = '0.0.0'

try:
    version = get_version(root='..')
    with open('crawlclima/_version.py', 'w') as f:
        f.write(f"__version__ = '{version}'")
except Exception:
    root_dir = os.path.dirname(__file__)
    if os.path.isfile(f'{root_dir}/crawlclima/_version.py'):
        with open('crawlclima/_version.py', 'r') as f:
            line = f.readline().replace('\n', '')
            version = line[14:]

setup(
    name='crawlclima',
    author='fccoelho',
    author_email='fccoelho@gmail.com',
    url='https://github.com/AlertaDengue/AlertaDengueCaptura.git',
    version=version,
    packages=find_packages(),
    package_data={'': ['*.txt', '*.csv', '*.yml', '*.html']},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GPL V3 License',
        'Operating System :: Linux',
    ],
    install_requires=[
        'click==7.1.1',
        'celery',
        'requests',
        'responses',
        'psycopg2',
        'geojson',
        'python-metar',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'pre-commit',
            'black',
            'isort',
            'flake8',
            'coverage',
            'wheel',
            'setuptools',
            'jupyterlab',
            'docker-compose',
        ]
    },
    description='Rotinas para captura de dados climáticos',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # setup_requires=['setuptools_scm'],
)
