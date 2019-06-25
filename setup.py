from setuptools import setup

INSTALL_REQUIRES = ['flask', 'sqlalchemy', 'geoalchemy2', 'wtforms', 'Flask-WTF', 'psycopg2-binary']

setup(
    name='volcanoes_api',
    version='',
    packages=['application'],
    url='',
    license='',
    author='hopkina',
    author_email='',
    description='',
    install_requires=INSTALL_REQUIRES,
)
