#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import GObject, Gtk, Pango, Gdk
from xng.plugins.base import PopulationFilter, ItemStatus, ProviderItem
from .loadpage import ScLoadingPage
import threading


class ScItemButton(Gtk.FlowBoxChild):
    """ Display an item in a pretty view """

    __gtype_name__ = "ScItemButton"

    item = None
    action_button = None
    name = None

    def __init__(self, appsystem, item):
        Gtk.FlowBoxChild.__init__(self)
        self.item = item
        item_id = item.get_id()

        main_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add(main_box)

        store = item.get_store()

        # Pack the image first
        img = Gtk.Image.new()
        main_box.pack_start(img, False, False, 0)
        appsystem.set_image_from_item(img, item, item.get_store())
        img.set_pixel_size(64)

        stride_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        img.set_margin_end(12)
        main_box.pack_start(stride_box, True, True, 0)

        # Get the title
        name = appsystem.get_name(item_id, item.get_name(), store)
        self.name = name
        label = Gtk.Label(name)
        label.get_style_context().add_class("sc-bold")
        label.set_use_markup(True)
        label.set_margin_bottom(3)
        label.set_property("xalign", 0.0)
        label.set_halign(Gtk.Align.START)
        stride_box.pack_start(label, False, False, 0)

        # Get the summary
        summ = appsystem.get_summary(item_id, item.get_summary(), store)
        if len(summ) > 100:
            summ = "%s…" % summ[0:100]
        summary = Gtk.Label(summ)
        summary.set_use_markup(True)
        summary.set_property("xalign", 0.0)
        summary.set_line_wrap(True)
        summary.set_line_wrap_mode(Pango.WrapMode.WORD)
        summary.set_halign(Gtk.Align.START)
        summary.set_max_width_chars(50)
        stride_box.pack_start(summary, False, False, 0)

        self.get_style_context().add_class("category-item-row")

        if item.has_status(ItemStatus.META_HARDWARE):
            return

        action_name = _("Install")
        action_style = "suggested-action"
        if item.has_status(ItemStatus.INSTALLED):
            action_name = _("Remove")
            action_style = "destructive-action"
        elif item.has_status(ItemStatus.UPDATE_NEEDED):
            action_name = _("Update")

        self.action_button = Gtk.Button.new_with_label(action_name)
        self.action_button.set_halign(Gtk.Align.END)
        self.action_button.set_valign(Gtk.Align.CENTER)
        main_box.pack_end(self.action_button, False, False, 0)
        self.action_button.get_style_context().add_class("flat")

        if item.has_status(ItemStatus.META_ESSENTIAL):
            self.action_button.set_sensitive(False)
        else:
            self.action_button.get_style_context().add_class(action_style)


class ScComponentButton(Gtk.ToggleButton):
    """ Represent components in a category """

    component = None

    def __init__(self, cat):
        Gtk.ToggleButton.__init__(self)
        self.component = cat

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add(box)

        icon = self.component.get_icon_name()

        img = Gtk.Image.new_from_icon_name(
            icon,
            Gtk.IconSize.LARGE_TOOLBAR)
        img.set_margin_end(6)
        img.set_valign(Gtk.Align.CENTER)
        box.pack_start(img, False, False, 0)

        lab = Gtk.Label(self.component.get_name())
        lab.set_halign(Gtk.Align.START)
        lab.set_valign(Gtk.Align.CENTER)
        box.pack_start(lab, True, True, 0)

        self.get_style_context().add_class("group-button")
        self.get_style_context().add_class("flat")


class ScCategoriesView(Gtk.Box):
    """ Transitioned from Home view to show a category """

    __gtype_name__ = "ScCategoriesView"

    __gsignals__ = {
        'item-selected': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                          (ProviderItem,))
    }

    context = None
    category = None

    item_scroller = None
    item_list = None

    item_first = None
    load_page = None

    software_label = None

    def get_page_name(self):
        if not self.category:
            return "Categories"
        return self.category.get_name()

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context
        self.item_first = None

        self.layout_constraint = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.pack_start(self.layout_constraint, True, True, 0)
        self.layout_constraint.set_margin_start(40)
        self.layout_constraint.set_margin_top(40)
        self.layout_constraint.set_margin_bottom(40)

        # Mark the Categories view
        lab = Gtk.Label(_("Components"))
        lab.get_style_context().add_class("sc-big")
        lab.set_margin_bottom(12)
        lab.set_halign(Gtk.Align.START)
        lab.set_use_markup(True)
        self.layout_constraint.pack_start(lab, False, False, 0)

        self.components = Gtk.FlowBox()
        self.components.set_selection_mode(Gtk.SelectionMode.NONE)
        self.layout_constraint.pack_start(self.components, False, False, 0)
        self.components.set_margin_bottom(22)
        self.components.set_margin_end(40)

        # Mark the Categories view
        lab = Gtk.Label(_("Software"))
        self.software_label = lab
        lab.get_style_context().add_class("sc-big")
        lab.set_margin_bottom(12)
        lab.set_halign(Gtk.Align.START)
        lab.set_use_markup(True)
        self.layout_constraint.pack_start(lab, False, False, 0)

        # Allow switching to inline loading view
        self.stack = Gtk.Stack.new()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_homogeneous(False)
        self.layout_constraint.pack_start(self.stack, True, True, 0)
        self.loading = ScLoadingPage()
        self.stack.add_named(self.loading, "loading")

        # no items found, TODO: Allow repo manipulation
        self.no_items_found = Gtk.Label("<big>{}</big>".format(
            _("No software was found")))
        self.no_items_found.set_valign(Gtk.Align.CENTER)
        self.no_items_found.set_halign(Gtk.Align.CENTER)
        self.no_items_found.get_style_context().add_class("dim-label")
        self.no_items_found.show_all()
        self.no_items_found.set_use_markup(True)
        self.stack.add_named(self.no_items_found, "no-items-found")

        # Build main item view
        self.item_view = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.stack.add_named(self.item_view, "items")

        self.item_scroller = Gtk.ScrolledWindow.new(None, None)
        self.item_scroller.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.item_scroller.set_overlay_scrolling(False)
        self.item_list = Gtk.FlowBox.new()
        self.item_list.set_sort_func(self.sort_categories)
        self.item_list.set_activate_on_single_click(True)
        self.item_list.connect('child-activated', self.item_activated)
        self.item_list.set_row_spacing(12)
        self.item_list.set_column_spacing(12)
        self.item_list.set_homogeneous(True)
        self.item_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.item_scroller.add(self.item_list)
        self.item_list.set_margin_end(20)
        self.item_list.set_valign(Gtk.Align.START)
        self.item_view.pack_start(self.item_scroller, True, True, 0)

        self.show_all()

    def sort_categories(self, catA, catB):
        return cmp(catA.name.lower(), catB.name.lower())

    def item_activated(self, box, child, udata=None):
        """ An item in the component listing is being interacted with """
        if not child:
            return
        self.emit_selected_item(child.item)

    def emit_selected_item(self, item):
        """ Pass our item selection back up to the main window """
        self.emit('item-selected', item)

    def set_category(self, category):
        """ Set the root level category """
        if category == self.category:
            return
        self.category = category
        software_label = category.get_software_label()
        if not software_label:
            software_label = _("Software")
        self.software_label.set_text(software_label)

        # Clear out the old categories
        self.item_first = None
        for sproglet in self.components.get_children():
            self.components.remove(sproglet)

        # Add all the new components
        children = self.category.get_children()
        for component in children:
            self.add_component(component)

        if not children:
            self.stack.set_visible_child_name("no-items-found")

        # Begin selection of the first item
        if not self.item_first:
            return
        self.item_first.set_active(True)

    def add_component(self, component):
        """ Add a new component to the view for the toplevel parent """
        button = ScComponentButton(component)
        button.show_all()
        button.connect('clicked', self.component_clicked)
        self.components.add(button)
        if not self.item_first:
            self.item_first = button

    def component_clicked(self, btn, udata=None):
        """ A component has been selected, so transition to it """
        if not btn.get_active():
            return
        self.select_component(btn.component)
        for sproglet in self.components.get_children():
            child = sproglet.get_child()
            if child == btn:
                continue
            child.set_active(False)
        btn.set_active(True)

    def item_clicked(self, btn, udata=None):
        """ An item has been selected, ask main view to show it """
        self.emit_selected_item(btn.item)

    def select_component(self, component):
        """ Activate the current component """
        print("Component: {}".format(component.get_id()))

        # Move into busy state
        self.begin_busy()

        # Force UI to update itself before loading.
        while (Gtk.events_pending()):
            Gtk.main_iteration()

        # Populate storage in a thread now
        thre = threading.Thread(target=self.build_component, args=(component,))
        thre.start()

    def begin_busy(self):
        """ This view is now busy """
        self.context.set_window_busy(True)
        self.components.set_sensitive(False)
        self.loading.set_message()  # Randomise the message
        self.stack.set_visible_child_name("loading")

    def end_busy(self):
        """ This view is now ready """
        self.context.set_window_busy(False)
        self.components.set_sensitive(True)
        self.stack.set_visible_child_name("items")

    def build_component(self, component):
        """ Begin building the component in a thread """

        # Clear out the old items
        Gdk.threads_enter()
        for sproglet in self.item_list.get_children():
            self.item_list.remove(sproglet)
        Gdk.threads_leave()

        for plugin in self.context.plugins:
            plugin.populate_storage(self,
                                    PopulationFilter.CATEGORY,
                                    component)

        GObject.idle_add(self.reset_scroller)

    def reset_scroller(self):
        """ Called back on idle loop to reset scroll position """
        # Reset scroll policy now
        policy = self.item_scroller.get_vadjustment()
        policy.set_value(0)
        policy = self.item_scroller.get_hadjustment()
        policy.set_value(0)

        self.end_busy()
        return False

    def add_item(self, id, item, popfilter):
        """ Adding new item.. """
        Gdk.threads_enter()
        wid = ScItemButton(self.context.appsystem, item)
        self.item_list.add(wid)
        wid.show_all()
        Gdk.threads_leave()
