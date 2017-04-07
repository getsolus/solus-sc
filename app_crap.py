#!/usr/bin/env python2.7
import gi.repository
gi.require_version('AppStreamGlib', '1.0')
from gi.repository import AppStreamGlib as AS

store = AS.Store()

store.load(AS.StoreLoadFlags.APP_INFO_SYSTEM)

def test_markup(desc):
    m = AS.markup_convert_simple(desc)
    return m

app = store.get_app_by_pkgname("pitivi")

desc = app.get_description("C")
print test_markup(desc)
