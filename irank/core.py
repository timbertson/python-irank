import re

irank_marker = re.compile("\\[([^]=]+)=([0-5])\\]")

KEYS = ['rating', 'Mood', 'Pop', 'Softness', 'Hardcore', 'Nostalgia']

class Song(object):
	def __init__(self, path):
		from tagpy import FileRef
		try:
			self.file = FileRef(path)
		except ValueError, e:
			raise ValueError("file %s: %s" % (path, e))
		self.tags = self.file.tag()
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
			stars = "%6s" % ("*" * v,)
			summary.append(stars + " " + k)
		return "\n".join(summary)
	
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
	
	def values(self):
		return map(self.__getitem__, KEYS)
	
	def flatten(self):
		items = ["[%s=%s]" % key_val for key_val in self.items() if key_val[1] > 0]
		return "".join(items)


