# ###################################################
# Copyright (C) 2008-2017 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ###################################################

from fife.extensions.pychan.widgets import Label, VBox

from horizons.util.python.callback import Callback


class ReadableListBox(VBox):
	"""Simple label-backed list selector for settings dialogs.

	FIFE's native ListBox can render its item text invisibly on some macOS/SDL
	combinations even though the items exist in the widget model. This widget keeps
	the same data API used by SettingsDialog (setInitialData, setData, getData) but
	renders the choices as normal Labels, which are reliable in the book-style UI.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.accepts_initial_data = True
		self._realSetInitialData = self._set_items
		self.accepts_data = True
		self._realSetData = self._set_selected
		self._realGetData = self._get_selected
		self.items = []
		self.selected = 0

	def _set_items(self, items):
		self.items = list(items)
		if self.selected >= len(self.items):
			self.selected = 0
		self._rebuild_labels()

	def _set_selected(self, index):
		self.selected = int(index)
		self._rebuild_labels()

	def _get_selected(self):
		return self.selected

	def _select(self, index):
		self.setData(index)

	def _rebuild_labels(self):
		self.removeAllChildren()
		for index, item in enumerate(self.items):
			prefix = '✓ ' if index == self.selected else '  '
			label = Label(
				text='{}{}'.format(prefix, item),
				font=self.font,
				foreground_color=self.foreground_color,
				min_size=(self.min_size[0], 20),
				max_size=(self.max_size[0], 20),
			)
			label.capture(Callback(self._select, index), event_name='mouseClicked')
			self.addChild(label)
