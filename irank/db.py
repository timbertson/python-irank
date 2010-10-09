import os
import sqlite3
import irank
import stat
import sys

def populate_db(music_root, db_path = None):
	if db_path is not None:
		if os.path.splitext(db_path)[-1] not in ('.sqlite','.db'):
			raise RuntimeError("not a db file: %s" % (db_path))
		try:
			os.remove(db_path)
		except OSError: pass
	db = sqlite3.connect(db_path or ':memory:')
	db.execute("create table songs (path string, created_at , updated_at, %s);" % (
		", ".join(["%s number" % (key.lower().replace(' ','_'),) for key in irank.KEYS]),))
	add_songs(music_root, db)
	add_diff_metadata(db)
	return db

def add_songs(music_root, db):
	for path, dirs, files in os.walk(music_root):
		for file in files:
			filepath = os.path.join(path, file)
			try:
				song = irank.Song(filepath)
			except StandardError, e:
				print >> sys.stderr, "error processing %s: %s" % (filepath, e)
				import time
				time.sleep(5)
			sql = "insert into songs values (?, ?, ?, %s)" % (", ".join(["?" for k in irank.KEYS]),)
			filestat = os.stat(filepath)
			ctime = filestat[stat.ST_CTIME]
			mtime = filestat[stat.ST_MTIME]
			data = tuple([unicode(filepath, 'UTF-8'), ctime, mtime] + song.values.values())
			db.execute(sql, data)
	db.commit()

def add_diff_metadata(db):
	db.execute("CREATE TABLE diffs (id INTEGER PRIMARY KEY AUTOINCREMENT, path STRING, key STRING, old_val NUMBER, new_val NUMBER);")
	db.commit()

if __name__ == '__main__':
	populate_db(os.path.expanduser("~/Music/Library/TESTING"), '/tmp/irank.db')

