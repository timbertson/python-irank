import re


irank_marker = re.compile("\\[([^]=]+)=([0-5])\\]")

KEYS = ['rating', 'Mood', 'Pop', 'Softness', 'Hardcore', 'Nostalgia']

class Values(dict):
	def __str__(self):
		summary = []
		for k in KEYS:
			v = self.get(k, 0)
			stars = "%6s" % ("*" * v,)
			summary.append(stars + " " + k)
		return "\n".join(summary)
	
def parse(comment):
	values = Values()
	for match in irank_marker.finditer(comment):
		key, value = match.groups()
		values[key] = int(value)
	return values

def flatten(values):
	key_val_pairs = [(k, values.get(k,0)) for k in KEYS] # (note: sorted according to KEYS order)
	items = ["[%s=%s]" % key_val for key_val in key_val_pairs if key_val[1] > 0]
	return "".join(items)
