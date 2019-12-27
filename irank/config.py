from optparse import OptionParser
import os, sys, logging
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
		self.add_option('-c', '--config', help='config file (%default)', default=config_file('playlists'))
		self.add_option('-v', '--verbose', action='store_true')
	
	def parse_args(self, *args):
		opts, args = OptionParser.parse_args(self, *args)
		if not hasattr(opts, 'android'):
			opts.android = self.__default('android')
		for path_attr in ('irank', 'music'):
			try:
				setattr(opts, path_attr, os.path.expanduser(getattr(opts, path_attr)))
			except AttributeError: pass
		level = logging.DEBUG if opts.verbose else logging.INFO
		logging.basicConfig(stream=sys.stderr, level=level, format="%(message)s")
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
				return list(yaml.safe_load_all(f))[0]
		except OSError:
			return {}

class IrankApp(object):
	def __init__(self, opts):
		self.opts = opts
	
	@property
	def db_path(self):
		return getattr(self.opts, 'db_path', os.path.join(self.base_path, "irank.sqlite"))

	@property
	def base_path(self):
		return os.path.expanduser(self.opts.irank)
	
	@property
	def playlist_rules(self):
		with open(os.path.expanduser(self.opts.config)) as input_file:
			return yaml.safe_load(input_file)
	
	@property
	def db(self):
		from irank import db
		return db.load(self.db_path)

	def songs_for(self, playlist_name, db=None, relative=False):
		db = db or self.db
		condition = self.playlist_rules[playlist_name]
		src = os.path.expanduser(self.opts.music)
		for filepath, in db.execute('select path from songs where %s' % (condition,)):
			if relative:
				if filepath.startswith(src):
					filepath = filepath[len(src) + len(os.path.sep):]
			yield filepath
