from optparse import OptionParser
import os, sys
import yaml

def realpath(p):
	return os.path.abspath(os.path.expanduser(p))

def config_file(name): return realpath("~/.config/irank/" + name)

PATHS_CONFIG = config_file("paths")

class IrankOptionParser(OptionParser):
	def __init__(self, *args):
		OptionParser.__init__(self, *args)
		self.__custom_paths = self.__get_custom_paths()
		self.add_option('--music', help='input (music) directory', **self.__default_d('music'))
		self.add_option('--irank', help='output (irank playlist) directory', **self.__default_d('irank'))
		self.add_option('-v', '--verbose', action='store_true')
	
	def parse_args(self, *args):
		opts, args = OptionParser.parse_args(self, *args)
		if not hasattr(opts, 'android'):
			opts.android = self.__default('android')
		return (opts, args)
	
	def __default(self, name):
		return self.__custom_paths.get(name, None)
	
	def __default_d(self, name):
		value = self.__default(name)
		if value is None: return {}
		return dict(default=value)

	def __get_custom_paths(self):
		try:
			with open(PATHS_CONFIG) as f:
				return list(yaml.load_all(f))[0]
		except OSError:
			return {}
