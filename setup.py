from setuptools import find_packages, setup

"""Update:
(change version,)
sudo rm -rf build dist *.egg-info
python setup.py sdist bdist_wheel
python -m twine upload --repository pypi dist/*
"""

setup(
    name='deepl-cli',
    version='0.0.11',
    description='DeepL Translator CLI using Selenium',
    description_content_type='',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eggplants/deepl-cli',
    author='eggplants',
    packages=find_packages(),
    python_requires='>=3.0',
    include_package_data=True,
    license='MIT',
    install_requires=['pyppeteer'],
    entry_points={
        'console_scripts': [
            'deepl=deepl.main:main'
        ]
    }
)
