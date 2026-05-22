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

import os
import tempfile
from contextlib import contextmanager
from unittest import mock

import yaml

import horizons.i18n as i18n
from horizons.savegamemanager import SavegameManager
from tests.gui import gui_test


class _DictTranslations:
	def __init__(self, translations):
		self._translations = translations

	def gettext(self, message):
		return self._translations.get(message, message)

	def ngettext(self, message1, message2, count):
		message = message1 if count == 1 else message2
		return self.gettext(message)


@contextmanager
def _temporary_translations(translations):
	original_translation = i18n._trans
	i18n._trans = _DictTranslations(translations)
	try:
		yield
	finally:
		i18n._trans = original_translation


@gui_test()
def test_show_menu(gui):
	"""Test that the singleplayer page shows up and closes correctly."""
	gui.trigger('menu/single_button')
	gui.trigger('singleplayermenu/cancel')


def _start_game(gui):
	"""Starts the game from the menu and returns the game options used."""
	with mock.patch('horizons.main.start_singleplayer') as start_mock:
		gui.trigger('singleplayermenu/okay')

		return start_mock.call_args[0][0]


def _assert_text_widgets_not_empty(gui, names):
	for name in names:
		widget = gui.find(name)
		assert widget, 'Missing widget: {}'.format(name)
		assert widget.text.strip(), 'Empty text in widget: {}'.format(name)


@gui_test()
def test_start_scenario(gui):
	"""Test starting a scenario."""
	gui.trigger('menu/single_button')
	gui.trigger('singleplayermenu/scenario')

	# trigger update of scenario infos
	gui.find('maplist').select('tutorial')
	gui.find('uni_langlist').select('English')

	options = _start_game(gui)
	assert options.is_scenario
	assert options.game_identifier.endswith('tutorial_en.yaml')


@gui_test()
def test_start_random_map(gui):
	"""Test starting a new random map."""
	gui.trigger('menu/single_button')
	gui.trigger('singleplayermenu/random')

	# disable pirates and disasters
	gui.trigger('singleplayermenu/lbl_pirates')
	gui.trigger('singleplayermenu/lbl_disasters')

	gui.find('ai_players').select('3')
	gui.find('resource_density_slider').slide(2.0)

	options = _start_game(gui)
	assert not options.is_scenario
	assert not options.pirate_enabled
	assert not options.disasters_enabled
	assert options.trader_enabled
	assert options.ai_players == 3
	assert options.natural_resource_multiplier == 2


@gui_test()
def test_start_map(gui):
	"""Test starting an existing map."""
	gui.trigger('menu/single_button')
	gui.trigger('singleplayermenu/free_maps')

	# trigger update of map info
	gui.find('maplist').select('development')

	gui.find('ai_players').select('1')

	# disable pirates and trader
	gui.trigger('singleplayermenu/lbl_pirates')
	gui.trigger('singleplayermenu/lbl_free_trader')

	options = _start_game(gui)
	assert options.game_identifier.endswith('development.sqlite')
	assert not options.is_scenario
	assert not options.pirate_enabled
	assert not options.trader_enabled
	assert options.disasters_enabled
	assert options.ai_players == 1


@gui_test()
def test_scenario_selection_extra_information(gui):
	"""Selecting a scenario shows additional information."""

	with tempfile.TemporaryDirectory() as tmpdir:
		with mock.patch.object(SavegameManager, 'scenarios_dir', new_callable=mock.PropertyMock) as m:
			m.return_value = tmpdir

			# Create a small temporary scenario
			with open(os.path.join(tmpdir, 'test_en.yaml'), 'w') as f:
				data = {
					'events': [],
					'metadata': {
						'author': 'Tester',
						'description': 'A test',
						'difficulty': 'Impossible',
						'translation_status': 'Something something status'
					}
				}
				yaml.dump(data, f)

			gui.trigger('menu/single_button')
			gui.trigger('singleplayermenu/scenario')

			# trigger update of scenario infos
			gui.find('maplist').select('test')
			gui.find('uni_langlist').select('English')

			assert gui.find('uni_map_author').text == 'Author: Tester'
			assert gui.find('uni_map_difficulty').text == 'Difficulty: Impossible'
			assert gui.find('uni_map_desc').text == 'Description: A test'
			assert gui.find('translation_status').text == 'Something something status'


@gui_test()
def test_singleplayer_menu_visible_labels_are_populated(gui):
	"""The new-game flow keeps visible labels populated while switching modes."""
	gui.trigger('menu/single_button')

	_assert_text_widgets_not_empty(gui, [
		'singleplayermenu/headline',
		'singleplayermenu/scenario',
		'singleplayermenu/random',
		'singleplayermenu/free_maps',
		'player_label',
		'color_label',
		'ai_players_label',
		'choose_map_lbl',
		'select_lang_lbl',
	])

	gui.find('maplist').select('tutorial')
	gui.find('uni_langlist').select('English')
	_assert_text_widgets_not_empty(gui, [
		'uni_map_author',
		'uni_map_difficulty',
		'uni_map_desc',
	])

	gui.trigger('singleplayermenu/random')
	_assert_text_widgets_not_empty(gui, [
		'headline_map_settings_lbl',
		'seed_string_lbl',
		'map_size_lbl',
		'water_percent_lbl',
		'max_island_size_lbl',
		'preferred_island_size_lbl',
		'island_size_deviation_lbl',
		'headline_game_settings_lbl',
		'resource_density_lbl',
		'lbl_free_trader',
		'lbl_pirates',
		'lbl_disasters',
	])

	gui.trigger('singleplayermenu/free_maps')
	gui.find('maplist').select('development')
	_assert_text_widgets_not_empty(gui, [
		'headline_choose_map_lbl',
		'recommended_number_of_players_lbl',
		'headline_game_settings_lbl',
		'resource_density_lbl',
		'lbl_free_trader',
		'lbl_pirates',
		'lbl_disasters',
	])


@gui_test()
def test_singleplayer_menu_visible_labels_are_populated_in_german(gui):
	"""The rendered new-game flow stays populated when gettext returns German."""
	with _temporary_translations({
		'Generating preview…': 'Vorschau wird erzeugt…',
		'An unknown error occurred while generating the map preview':
			'Beim Erzeugen der Kartenvorschau ist ein unbekannter Fehler aufgetreten',
	}):
		gui.trigger('menu/single_button')

		_assert_text_widgets_not_empty(gui, [
			'singleplayermenu/headline',
			'singleplayermenu/scenario',
			'singleplayermenu/random',
			'singleplayermenu/free_maps',
			'player_label',
			'color_label',
			'ai_players_label',
			'choose_map_lbl',
			'select_lang_lbl',
		])

		gui.find('maplist').select('tutorial')
		gui.find('uni_langlist').select('English')
		_assert_text_widgets_not_empty(gui, [
			'uni_map_author',
			'uni_map_difficulty',
			'uni_map_desc',
		])

		gui.trigger('singleplayermenu/random')
		_assert_text_widgets_not_empty(gui, [
			'headline_map_settings_lbl',
			'seed_string_lbl',
			'map_size_lbl',
			'water_percent_lbl',
			'max_island_size_lbl',
			'preferred_island_size_lbl',
			'island_size_deviation_lbl',
			'headline_game_settings_lbl',
			'resource_density_lbl',
			'lbl_free_trader',
			'lbl_pirates',
			'lbl_disasters',
			'map_preview_status_label',
		])
		assert gui.find('map_preview_status_label').text == 'Vorschau wird erzeugt…'

		gui.trigger('singleplayermenu/free_maps')
		gui.find('maplist').select('development')
		_assert_text_widgets_not_empty(gui, [
			'headline_choose_map_lbl',
			'recommended_number_of_players_lbl',
			'headline_game_settings_lbl',
			'resource_density_lbl',
			'lbl_free_trader',
			'lbl_pirates',
			'lbl_disasters',
		])
