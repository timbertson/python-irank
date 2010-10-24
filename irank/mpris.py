# here lies some code relating to mpris, which should replace the rhytmhbox code at some point
# examples nabbed from http://github.com/mackstann/mpris-remote/blob/master/mpris-remote



import os, sys, re, time, urllib2, dbus

mpris_prefix="org.mpris.MediaPlayer2"
def possible_names():
	return [ name[len(mpris_prefix):] for name in bus.list_names() if org_mpris_re.match(name) ]

# returns first matching player
def get_player():
	names = possible_names()
	if not names:
		print >>sys.stderr, "No MPRIS-compliant player found running."
		raise SystemExit(1)
	return names[0]

bus = dbus.SessionBus()
player_name = os.environ.get('MPRIS_REMOTE_PLAYER', '*')

if player_name == '*':
	player_name = get_player()

root_obj = bus.get_object('org.mpris.%s' % player_name, '/')
player_obj = bus.get_object('org.mpris.%s' % player_name, '/Player')

root = dbus.Interface(root_obj, dbus_interface='org.freedesktop.MediaPlayer')
player = dbus.Interface(player_obj, dbus_interface='org.freedesktop.MediaPlayer')

