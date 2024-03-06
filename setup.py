from setuptools import setup, find_packages
import os

version = '1.1.dev0'

tests_require = [
    'plone.app.testing',
    'plone.app.robotframework',  # undeclared dependency of plone.app.event
]

setup(name='plone.app.changeownership',
      version=version,
      description="Change Plone objects ownership",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      # Get more strings from https://pypi.org/classifiers/
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        ],
      keywords='plone change ownership',
      author='Mustapha Benali',
      author_email='mustapha@headnet.dk',
      url='http://plone.org/products/plone.app.changeownership',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
