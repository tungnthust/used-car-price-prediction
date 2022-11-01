from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read().splitlines()

setup(
    name='used-car-price-prediction',
    version='1.0',
    author='TVT-group',
    description='',
    url='https://github.com/tungnthust/used-car-price-prediction',
    keywords='development, setup, setuptools',
    python_requires='>=3.7',
    install_requires=install_requires
)
