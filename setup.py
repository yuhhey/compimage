from distutils.core import setup

setup(name='CompImg',
      version='0.1dev',
      packages=['compimage'],
      author='Yuhhey',
      author_email='atiska1_fejlesztes@yahoo.com',
      packages=['compimage', 'compimage.test'],
      #url='http://pypi.python.org/pypi/TowelStuff/',
      license='LICENSE.txt',
      long_description=open('README.md').read(),
      install_requires([])
)