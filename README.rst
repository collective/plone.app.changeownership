Introduction
============

plone.app.changeownership as it sounds is a Plone package to change objects
ownership.

IMPORTANT: This version was used only on Plone.org to change the ownership of FoundationMember objects, in Sept. 2016. As of June 25, 2017, it is no longer needed on Plone.org.

Problem
=======

While for a single content you can call the ``/ownership_form`` view,
there is no way in Plone to transfer **ownership of all objects** owned by an user
to a new user. To delete a Plone member in such case is not an option. 

Solution
========

plone.app.changeownership makes easy to transfer ownership from one ore more 
members to a new member. It also can change content metadata, like *Creators*
field.

Install
=======

See docs/INSTALL.txt for a buildout configuration.

You have to install the package from quickinstaller or setup_tool. You will get
a configlet in the Plone control panel named "Change Ownership".

