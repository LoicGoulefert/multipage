from setuptools import setup


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="multipage",
    version="0.1.0",
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Loïc Goulefert",
    url="",
    license=license,
    packages=["multipage"],
    install_requires=[
        'click',
        'vpype',
    ],
    entry_points='''
            [vpype.plugins]
            multipage=multipage.multipage:multipage
        ''',
)
