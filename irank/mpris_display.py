import irank
from irank import mpris
import sys
import os
import subprocess
import logging
import gobject

def run_with_current_track(player, process_name, next_song=False):
	subprocess.check_call([process_name, player.track])
	if(next_song):
		player.next()

def edit_loop(player):
	while True:
		line = None
		try:
			line = input().strip()
			logging.debug('saw input: %r', line)
		except EOFError: break
		if line == 'd':
			run_with_current_track(player, 'irank-delete', False)
		elif line == 'k':
			run_with_current_track(player, 'irank-keep', True)
		elif line in ('a','y'):
			run_with_current_track(player, 'irank-discard', True)
		elif not line:
			clear()
			# just running the function should work, but curses gets in a funny state sometimes...
			run_with_current_track(player, 'irank-edit', False)
			display_song(player.track)

def clear():
	os.system("clear")

def display_song(current_song):
	logging.debug('displaying current song')
	clear()
	if not current_song: return
	print(os.path.basename(current_song))
	print()
	try:
		print(irank.Song(current_song).values)
	except Exception as e:
		print(e)

def display_loop(player):
	player.each_track(display_song)
	loop = gobject.MainLoop()
	try:
		loop.run()
	except KeyboardInterrupt:
		sys.exit(1)

if __name__ == '__main__':
	display_loop(mpris.Player())
