#!/bin/sh

#for productname, take the lowercased package-name without toplevel-namespace
#Products.Foo  --> foo.po
PRODUCTNAME=plone.app.changeownership   #name po-file

# use lowercase package-name for i18ndomain
I18NDOMAIN=$PRODUCTNAME  # not the same!


# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --create ${I18NDOMAIN} .
i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --merge locales/${PRODUCTNAME}-manual.pot --create ${I18NDOMAIN} .
# Synchronise the resulting .pot with the .po files
i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/*/LC_MESSAGES/${PRODUCTNAME}.po

# Zope3 is lazy so we have to compile the po files ourselves (Plone3.0)
# automatic compilation is fixed since plone3.1
#for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
#    if test -d $lang/LC_MESSAGES; then
#        msgfmt -o $lang/LC_MESSAGES/${PRODUCTNAME}.mo $lang/LC_MESSAGES/${PRODUCTNAME}.po
#    fi
#done
