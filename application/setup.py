from setuptools import setup

setup(name='dhjournal',
      version='1.0',
      description='OpenShift App',
      author='Vasily Nesterov',
      author_email='da3x11@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      packages=[
          'application',
          'application.logic',
          'application.management',
          'application.management.commands',
          'application.migrations',
          'application.utils'
      ],
      install_requires=['Django==1.8.2', 'pytz==2015.7'],
)

