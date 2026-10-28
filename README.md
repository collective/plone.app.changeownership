# Introduction

plone.app.changeownership as it sounds is a Plone package to change objects ownership.

## Problem

While for a single content you can call the ``/change-owner`` view, there is no way in Plone to transfer **ownership of all objects** owned by an user to a new user. To delete a Plone member in such case is not an option.

## Solution

plone.app.changeownership makes easy to transfer ownership from one or more members to a new member. It also can change content metadata, like *Creators* field.

## Install

The addon is installed via your Plone buildout.

### pip based installation

- `pip install plone.app.changeownership`

### buildout based installation

- Add `plone.app.changeownership` to the list of eggs to install, e.g.:

    ```
    [buildout]
    ...
    eggs =
        ...
        plone.app.changeownership
    ```

- Re-run buildout, e.g. with:

    ```
    $ ./bin/buildout
    ```

You have to install the package from quickinstaller or setup_tool. You will get a configlet in the Plone control panel named "Change Ownership".


## Development

### Package Layout with plone.meta

``` bash
uvx --from plone.meta config-package --no-commit . --branch=current
```

### Linting

``` bash
uvx --with tox-uv tox -r -e lint
```

### Check dependencies

``` bash
uvx --with tox-uv tox -r -e dependencies
```

### Check circular dependencies

``` bash
uvx --with tox-uv tox -r -e circular
```

### Run tests

``` bash
uvx --with tox-uv tox -r -e test
```

## Translate content

```
uvx i18ndude rebuild-pot --pot ./src/plone/app/changeownership/locales/plone.app.changeownership.pot --create plone.app.changeownership ./src/plone/app/changeownership
uvx i18ndude sync --pot ./src/plone/app/changeownership/locales/plone.app.changeownership.pot ./src/plone/app/changeownership/locales/*/LC_MESSAGES/plone.app.changeownership.po
```

## start a local instance

```
uvx cookiecutter -f --no-input --config-file instance.yaml gh:plone/cookiecutter-zope-instance
runwsgi -v instance/etc/zope.ini
```