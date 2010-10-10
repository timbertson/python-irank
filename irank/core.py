import re

irank_marker = re.compile("\\[([^]=]+)=([0-5])\\]")

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

class Song(object):
	def __init__(self, path):
		from tagpy import FileRef
		try:
			self.file = FileRef(path)
		except ValueError, e:
			raise ValueError("file %s: %s" % (path, e))
		self.tags = self.file.tag()
		self.artist = self.tags.artist
		self.title = self.tags.title
		self.values = Values(self.tags.comment)
	
	def save(self):
		self.tags.comment = self.values.flatten()
		self.file.save()

class Values(dict):
	def __init__(self, str=''):
		if str:
			self._parse(str)

	def _parse(self, comment):
		for match in irank_marker.finditer(comment):
			key, value = match.groups()
			self[key] = int(value)

	def __str__(self):
		summary = []
		for k in KEYS:
			v = self[k]
			line = "%s %s" % self._format(k,v)
			summary.append(line)
		return "\n".join(summary)
	
	def _format(self, k, v):
		key_str = "%15s" % (k,)
		value_str = "%-5s" % ("*" * v, )
		return key_str, value_str

	def formatted_pairs(self):
		return [self._format(k,v) for k,v in self.items()]
	
	def __setitem__(self, k, v):
		if not k in KEYS:
			raise KeyError(k)
		super(type(self), self).__setitem__(k,v)
	
	def __getitem__(self, k):
		if not k in KEYS:
			raise KeyError(k)
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


