from setuptools import find_packages, setup

with open('README.md', 'r') as fh:
    long_description = fh.read()


def read(filename):
    return [req.strip() for req in open(filename).readlines()]


setup(
    name='Downloader_app',
    version='0.2.0',
    author='fccoelho',
    author_email='fccoelho@gmail.com',
    url='https://github.com/AlertaDengue/AlertaDengueCaptura.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GPL V3 License',
        'Operating System :: Linux',
    ],
    python_requires='>=3.7',
)
