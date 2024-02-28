Introduction
============

plone.app.changeownership as it sounds is a Plone package to change objects
ownership.

Problem
=======

While for a single content you can call the ``/change-owner`` view,
there is no way in Plone to transfer **ownership of all objects** owned by an user
to a new user. To delete a Plone member in such case is not an option. 

Solution
========

plone.app.changeownership makes easy to transfer ownership from one ore more 
members to a new member. It also can change content metadata, like *Creators*
field.

Install
=======

    pip install plone.app.changeownership

You have to install the package from the Add Ons page in Site Setup, or from portal_setup in the ZMI.
You will get a configlet in the Plone control panel named "Change Ownership".

