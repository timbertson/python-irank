package:
	mkzero-gfxmonk -p irank $$(ls -1 | parallel '[ -x {} ] && echo "-p {}"' | grep -E 'irank|rhythmbox') irank.xml

.PHONY: package
