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

import pytest

from horizons.util.fife_compat import get_fife_action_name


class ActionWithId:
	def getId(self):
		return 'idle_as_lumberjack_barrack0'


class ActionWithName:
	def getName(self):
		return 'idle_as_lumberjack_barrack0'


class ActionWithoutName:
	pass


def test_get_fife_action_name_uses_get_id():
	assert get_fife_action_name(ActionWithId()) == 'idle_as_lumberjack_barrack0'


def test_get_fife_action_name_falls_back_to_get_name():
	assert get_fife_action_name(ActionWithName()) == 'idle_as_lumberjack_barrack0'


def test_get_fife_action_name_fails_without_supported_accessor():
	with pytest.raises(AttributeError):
		get_fife_action_name(ActionWithoutName())
