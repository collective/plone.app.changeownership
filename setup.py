from setuptools import setup, find_packages
import os

version = '0.3dev'

setup(name='plone.app.changeownership',
      version=version,
      description="Change plone objects ownership",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone change ownership',
      author='Mustapha Benali',
      author_email='mustapha@headnet.dk',
      url='http://svn.plone.org/svn/collective/plone.app.changeownership',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
