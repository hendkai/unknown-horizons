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


def get_fife_action_name(action):
	"""Return the action identifier across FIFE getId/getName API variants."""
	for accessor in ('getName', 'getId'):
		method = getattr(action, accessor, None)
		if method is not None:
			return decode_fife_string(method())

	raise AttributeError('FIFE action exposes neither getId() nor getName()')


def decode_fife_string(value):
	"""Return a plain string for FIFE values that may be bytes."""
	if isinstance(value, bytes):
		value = value.decode('utf-8')
	return str(value).replace('\x00', '').strip()


def get_fife_key(fife, *names):
	"""Return the first available FIFE key constant from the given names."""
	for name in names:
		if hasattr(fife.Key, name):
			return getattr(fife.Key, name)
	raise AttributeError('FIFE key exposes none of: {}'.format(', '.join(names)))


def get_fife_digit(fife, keyval):
	"""Return the digit for keyboard/numpad number keys, or None."""
	for digit in range(10):
		for name in ('KP_{}'.format(digit),):
			if getattr(fife.Key, name, None) == keyval:
				return digit
	for zero_name, nine_name in (('NUM_0', 'NUM_9'), ('_0', '_9')):
		zero = getattr(fife.Key, zero_name, None)
		nine = getattr(fife.Key, nine_name, None)
		if zero is not None and nine is not None and zero <= keyval <= nine:
			return int(keyval - zero)
	return None
