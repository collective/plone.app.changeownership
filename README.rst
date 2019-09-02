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

The addon is installed via your Plone buildout.

* Add ``plone.app.changeownership`` to the list of eggs to install, e.g.: ::

    [buildout]
    ...
    eggs =
        ...
        plone.app.changeownership

* Re-run buildout, e.g. with: ::

    $ ./bin/buildout

You have to install the package from quickinstaller or setup_tool. You will get
a configlet in the Plone control panel named "Change Ownership".

