import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crawlclima",
    version="0.1.0",
    author="fccoelho",
    author_email="fccoelho@gmail.com",
    description="Rotinas para captura de dados climáticos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlertaDengue/AlertaDengueCaptura.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL V3 License",
        "Operating System :: Linux",
    ],
    python_requires='>=3.7',
)
