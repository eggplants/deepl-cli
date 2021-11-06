from setuptools import find_packages, setup  # type: ignore

from deepl import __version__

setup(
    name='deepl-cli',
    version=__version__,
    description='DeepL Translator CLI using Selenium',
    description_content_type='',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eggplants/deepl-cli',
    author='eggplants',
    packages=find_packages(),
    python_requires='>=3.5, <3.10',
    include_package_data=True,
    license='MIT',
    install_requires=['pyppeteer'],
    entry_points={
        'console_scripts': [
            'deepl=deepl.main:main'
        ]
    }
)
