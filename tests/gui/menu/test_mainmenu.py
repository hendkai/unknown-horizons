# ###################################################
# Copyright (C) 2008-2017 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

from tests.gui import gui_test


@gui_test(timeout=60)
def test_credits(gui):
	"""Test that the credits page shows up."""

	gui.trigger('menu/credits_button')
	gui.trigger('credits_window/okButton')
	assert not gui.find('credits_window')


@gui_test(timeout=60)
def test_help(gui):
	"""Test that the help page shows up."""

	gui.trigger('menu/help_button')
	gui.trigger('help_window/okButton')
	assert not gui.find('help_window')


@gui_test(timeout=60)
def test_settings(gui):
	gui.trigger('menu/settings_button')
	gui.trigger('settings_window/cancelButton')


@gui_test(timeout=60)
def test_settings_resolution_list_is_readable(gui):
	"""The screen-resolution choices must use a high-contrast text style.

	This protects the settings dialog against the macOS/FIFE rendering issue
	where the list entries were present at the widget layer but appeared nearly
	blank in the visible menu.
	"""

	gui.trigger('menu/settings_button')
	resolution_list = gui.find('screen_resolution')
	assert resolution_list.items
	assert resolution_list.font == 'unifont'
	foreground = resolution_list.foreground_color
	selection = resolution_list.selection_color
	assert (foreground.r, foreground.g, foreground.b) == (68, 42, 2)
	assert selection.a <= 32
	assert resolution_list.height >= 90
	gui.trigger('settings_window/cancelButton')
