#!/usr/bin/env python2.7
import gi.repository
gi.require_version('AppStreamGlib', '1.0')
from gi.repository import AppStreamGlib as AS

store = AS.Store()

store.load(AS.StoreLoadFlags.APP_INFO_SYSTEM)

for app in store.get_apps():
    print app.get_comment("C")
    print app.get_name("C")
    pass

app = store.get_app_by_pkgname("libreoffice-writer")
print(app.get_description("C"))
print(app.get_comment("C"))
print app.get_icon_path()
print app.get_name("C")
