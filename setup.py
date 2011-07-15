#!/usr/bin/env python

#NOTE: this file is deprecated - you should use the 0install feed (irank.xml)

from setuptools import *
setup(
	name='irank',
	version='0.3',
	author_email='tim3d.junk+irank@gmail.com',
	author='Tim Cuthbertson',
	description="music ranking metadata manager",
	packages = find_packages(exclude=['test', 'test.*']),
	scripts = [
		'irank-edit',
		'_irank-rhythmbox-impl',
		'irank-rhythmbox',
		'nowplaying-rhythmbox',
		'irank-rating-sync',
		'irank-playlists',
		'irank-ls',
	],
	zip_safe=True,
	install_requires=[
		'setuptools',
		#'tagpy', # (best installed as a deb package)
	],
)
