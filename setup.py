from distutils.core import setup

setup(
    name='dhjournal',
    version='1.0',
    packages=['project', 'application', 'application.logic', 'application.utils', 'application.management',
              'application.management.commands', 'application.migrations'],
    url='',
    license='',
    author='Webmaster',
    author_email='wm@wm.wm',
    description='',
    install_requires=['Django==1.8.2', 'pytz==2015.7']
)
