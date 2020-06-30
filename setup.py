import scenario
from setuptools import setup, find_packages


setup(
    name='Scenario',
    version=scenario.__version__,
    author=scenario.__author__,
    author_email='luaviskang@gmail.com',
    description='Server scenario testing tool',
    packages=find_packages(),
    package_dir={
        '': '.'
    },
    install_requires=[
        'requests==2.23.0',
        'tqdm==4.46.1',
    ],
)
