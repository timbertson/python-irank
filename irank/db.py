import os
import sqlite3
import irank
import stat
import sys
import re

def sanitise_column_name(s):
	return re.sub('[^a-zA-Z]', '_', s)

def populate_db(music_root, db_path = None):
	if db_path is not None:
		if os.path.splitext(db_path)[-1] not in ('.sqlite','.db'):
			raise RuntimeError("not a db file: %s" % (db_path))
		try:
			os.remove(db_path)
		except OSError: pass
	db = sqlite3.connect(db_path or ':memory:')

	key_cols = map(sanitise_column_name, irank.KEYS)
	songs_definition = "create table songs (path string PRIMARY KEY, artist string, title string, created_at , updated_at, %s);"
	updates_definition = "create table updates (path string PRIMARY KEY, %s);"

	custom_columns = ", ".join(["%s number" % (column,) for column in key_cols])

	for definition in (songs_definition, updates_definition):
		db.execute(definition % (custom_columns,))

	add_songs(music_root, db)
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
				continue
			sql = "insert into songs values (?, ?, ?, ?, ?, %s)" % (", ".join(["?" for k in irank.KEYS]),)
			filestat = os.stat(filepath)
			ctime = filestat[stat.ST_CTIME]
			mtime = filestat[stat.ST_MTIME]
			data = tuple([unicode(filepath, 'UTF-8'), song.artist, song.title, ctime, mtime] + song.values.values())
			db.execute(sql, data)
	db.commit()

if __name__ == '__main__':
	populate_db(os.path.expanduser("~/Music/Library/TESTING"), '/tmp/irank.db')

