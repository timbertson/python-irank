import re, sys
import db

irank_marker = re.compile("\\[([^]=]+)=([0-5])\\]")

fsenc = sys.getfilesystemencoding()

def version():
	with open(os.path.join(os.path.dirname(__file__), '../VERSION')) as f:
		return f.read().strip()

import os, sys
KEYS = ['rating', 'Mood', 'Softness', 'Nostalgia']
try:
	with open(os.path.expanduser("~/.config/irank/ratings")) as f:
		strip = lambda x: x.strip()
		identity = lambda x: x
		KEYS = filter(identity, map(strip, f.readlines()))
except StandardError:
	print >> sys.stderr, ("Using the default rating keys.\n" +
	    "You can make your own by writing them one line at a time to ~/.config/irank/ratings")

class BaseSong(object):
	def __init__(self, filename):
		self.filename = filename
		try:
			self._open_file(self.filename)
		except ValueError, e:
			raise ValueError("file %s: %s" % (filename, e))
		assert self.file, "Failed to load file: %s" % (filename,)
		self.artist = self._get_artist()
		self.title = self._get_title()
		comment = self._get_comment()
		self.values = Values(comment)
	
	def save(self):
		self._set_comment(self.values.flatten())
		assert self._get_comment() == self.values.flatten(), "Could not save tag!"
		self.file.save()

	def check(self):
		orig_comment = self._get_comment()
		new_comment = 'irank-test-comment'
		self._set_comment(new_comment)
		try:
			actual_comment = self._get_comment()
			return actual_comment == new_comment
		finally:
			self._set_comment(orig_comment)

class MutagenSong(BaseSong):
	DEFAULT_COMMENT = u''
	DEFAULT_LANG='eng'
	DEFAULT_LANG='eng'
	COMMENT_KEY = u"COMM::'%s'" % (DEFAULT_LANG,)
	FALLBACK_KEYS = [
		u"COMM::'XXX'",
		u"COMM:c0:'XXX'",
	]
	
	def _make_comment(self, text):
		import mutagen
		return mutagen.id3.COMM(encoding=3, lang=self.DEFAULT_LANG, desc=u'', text=unicode(text))

	def _tag_value(self, tag):
		if tag is None: return u''
		return tag.text[0]

	def _open_file(self, path):
		import mutagen
		self.file = mutagen.File(path)
		if self.file and not hasattr(self.file, 'tags'):
			self.file.add_tags()

	def _get_comment(self):
		# debugging...
		self._possible_comments = list(filter(lambda item: item[0].startswith('COMM:'), self.file.items()))
		comment = None
		for key in [self.COMMENT_KEY] + self.FALLBACK_KEYS:
			comment = self.file.get(key, None)
			if comment is not None:
				break
		if comment is None:
			comment = self._make_comment(self.DEFAULT_COMMENT)
		return self._tag_value(comment)
	
	def _set_comment(self, comment):
		#self._comment.text = [unicode(comment)]
		self.file[self.COMMENT_KEY] = self._make_comment(comment)
	
	def _get_artist(self):
		tag = self.file.get('TPE1')
		return self._tag_value(tag)
	
	def _get_title(self):
		tag = self.file.get('TIT2')
		return self._tag_value(tag)


#Set the default Song implementation:
Song = MutagenSong

class Values(dict):
	def __init__(self, str=''):
		if str:
			self.__parse(str)

	def __parse(self, comment):
		for match in irank_marker.finditer(comment):
			key, value = match.groups()
			self[key] = int(value)

	def __str__(self):
		summary = []
		for k in KEYS:
			v = self[k]
			line = "%s %s" % self.__format(k,v)
			summary.append(line)
		return "\n".join(summary)
	
	def __format(self, k, v, key_width=None):
		if key_width is None:
			key_width = max(map(len, KEYS)) + 1
		key_str = "%%%ss" % (key_width,) % (k,)
		value_str = "%-5s" % ("*" * v, )
		return key_str, value_str

	def formatted_pairs(self, key_width=None):
		return [self.__format(k,v, key_width) for k,v in self.items()]
	
	def format_line(self, key_width = 1):
		return "   ".join(":".join(pair) for pair in self.formatted_pairs(key_width))

	def __get_real_key(self, key):
		if key in KEYS:
			return key

		for real_key, sanitised_key in zip(KEYS, map(db.sanitise_column_name, KEYS)):
			if key == sanitised_key:
				return real_key
		raise KeyError(key)

	def __setitem__(self, k, v):
		k = self.__get_real_key(k)
		super(type(self), self).__setitem__(k,v)
	
	def __getitem__(self, k):
		k = self.__get_real_key(k)
		return self.get(k,0)
	
	def items(self):
		for k in KEYS:
			yield (k, self[k])
	
	def keys(self):
		return KEYS
	
	def __len__(self):
		return len(KEYS)
	
	def values(self):
		return map(self.__getitem__, KEYS)
	
	def flatten(self):
		items = ["[%s=%s]" % key_val for key_val in self.items() if key_val[1] > 0]
		return "".join(items)


