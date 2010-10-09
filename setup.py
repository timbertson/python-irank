#!/usr/bin/env python

from setuptools import *
setup(
	name='irank',
	version='0.1.1',
	author_email='tim3d.junk+irank@gmail.com',
	author='Tim Cuthbertson',
	description="music ranking metadata manager",
	packages = find_packages(exclude=['test', 'test.*']),
	scripts = [
		'irank-edit',
		'_irank-rhythmbox-impl',
		'irank-rhythmbox',
		'nowplaying-rhythmbox',
		'irank-rating-sync'
		'irank-playlists',
	],
	zip_safe=True,
	install_requires=[
		'setuptools',
		#'tagpy', # (best installed as a deb package)
	],
)
