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

from fife.extensions import pychan
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
		self._labels = []

	def _set_items(self, items):
		items = list(items)
		if items == self.items and len(self._labels) == len(self.items):
			if self.selected >= len(self.items):
				self.selected = 0
			self._update_labels()
			return
		self.items = items
		if self.selected >= len(self.items):
			self.selected = 0
		self._rebuild_labels()

	def _set_selected(self, index):
		self.selected = int(index)
		if self.selected >= len(self.items):
			self.selected = 0
		self._update_labels()

	def _get_selected(self):
		return self.selected

	def _select(self, index):
		self.setData(index)
		self._emit_action()

	def select(self, value):
		self._select(self.items.index(value))

	@property
	def selected_item(self):
		if 0 <= self.selected < len(self.items):
			return self.items[self.selected]
		return None

	def _emit_action(self):
		callbacks = self.event_mapper.callbacks.get('default', {})
		callback = callbacks.get('action')
		if callback is not None:
			pychan.tools.applyOnlySuitable(callback, widget=self)

	def _rebuild_labels(self):
		self.removeAllChildren()
		self._labels = []
		for index, item in enumerate(self.items):
			label = Label(
				text=self._format_item(index),
				font=self.font,
				foreground_color=self.foreground_color,
				min_size=(self.min_size[0], 20),
				max_size=(self.max_size[0], 20),
			)
			label.capture(Callback(self._select, index), event_name='mouseClicked')
			self.addChild(label)
			self._labels.append(label)

	def _update_labels(self):
		for index, label in enumerate(self._labels):
			label.text = self._format_item(index)

	def _format_item(self, index):
		prefix = '> ' if index == self.selected else '  '
		item = self.items[index]
		if isinstance(item, bytes):
			item = item.decode('utf-8', 'replace')
		item = str(item).replace('\x00', '').strip()
		return '{}{}'.format(prefix, item)
