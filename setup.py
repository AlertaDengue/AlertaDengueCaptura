from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


def read(filename):
    return [req.strip() for req in open(filename).readlines()]


setup(
    name="crawlclima",
    version="0.1.0",
    author="fccoelho",
    author_email="fccoelho@gmail.com",
    description="Rotinas para captura de dados climáticos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlertaDengue/AlertaDengueCaptura.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL V3 License",
        "Operating System :: Linux",
    ],
    python_requires='>=3.7',
    install_requires=read("requirements.txt"),
    extras_require={'develop': read("requirements-dev.txt")},
)
