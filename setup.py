from setuptools import setup, find_packages


def parse_requirements(filename='requirements.txt'):
    """ load requirements from a pip requirements file. (replacing from pip.req import parse_requirements)"""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name='superape',
    version='1.0.0',
    packages=['monkey', 'monkey.conf', 'monkey.util', 'monkey.monkeyutil'],
    url='',
    license='',
    author='Sean.Yu',
    author_email='Sean Yu (CN) <Sean.Yu@homecredit.cn>',
    description='',
    long_description='',
    include_package_data=True,
    install_requires=parse_requirements(),
)
