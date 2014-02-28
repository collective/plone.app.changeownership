Introduction
============

plone.app.changeownership as it sounds is a plone package to change objects
ownership.

Problem
=======

There is no way in plone to transfer ownership of all objects owned by an user
to a new user. To delete a plone member in such case is not an option. 


Solution
========

plone.app.changeownership makes easy to transfer ownership from one ore more 
members to a new member. It also can change content metadata, like *Creators*
field.


Install
=======

See docs/INSTALL.txt for a buildout configuration.

You have to install the package from quickinstaller or setup_tool. You will get
a configlet in the plone control panel named "Change Ownership"



