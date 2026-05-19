import ast
import types

import pytest


def load_get_enet_architecture():
	with open('setup.py') as f:
		module = ast.parse(f.read())

	selected = [
		node for node in module.body
		if (isinstance(node, ast.Import) and any(alias.name == 'platform' for alias in node.names)) or (
			isinstance(node, ast.FunctionDef) and node.name == 'get_enet_architecture')
	]
	test_module = ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[]))
	compiled = compile(test_module, 'setup.py', 'exec')
	namespace = types.ModuleType('setup_arch_test')
	exec(compiled, namespace.__dict__)
	return namespace.get_enet_architecture


def test_get_enet_architecture_maps_supported_machines():
	get_enet_architecture = load_get_enet_architecture()

	assert get_enet_architecture('x86_64') == 'x64'
	assert get_enet_architecture('AMD64') == 'x64'
	assert get_enet_architecture('arm64') == 'arm64'
	assert get_enet_architecture('aarch64') == 'arm64'
	assert get_enet_architecture('universal2') == 'universal2'


def test_get_enet_architecture_rejects_unknown_machine():
	get_enet_architecture = load_get_enet_architecture()

	with pytest.raises(RuntimeError):
		get_enet_architecture('ppc64')
