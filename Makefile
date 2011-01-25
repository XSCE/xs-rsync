# Installs xs-rsync

# install root
DESTDIR=/

$(DESTDIR):
	mkdir -p $(DESTDIR)

install:
	install -D -d $(DESTDIR)/usr/bin
	install -D xs-refresh-xobuilds.py $(DESTDIR)/usr/bin
	install -D xs-publish-xobuild.py $(DESTDIR)/usr/bin
	install -D xs-unpack-xobuild.sh $(DESTDIR)/usr/bin

	install -D -m 644 rsyncd.conf.in     $(DESTDIR)/etc/xs-rsyncd.conf.in
	install -D -m 644 xinetd-xs-rsyncd.conf $(DESTDIR)/etc/xinetd.d/xs-rsyncd
	install -D -m 644 crond-xs-rsync.conf   $(DESTDIR)/etc/cron.d/xs-rsync

	install -D -m 755 usbmount-50-xs-rsync-installcontent $(DESTDIR)/etc/usbmount/mount.d/50-xs-rsync-installcontent

	# root owned
	install -D -d $(DESTDIR)/library/xs-rsync
	install -D -d $(DESTDIR)/library/xs-rsync/xobuilds-packed
	# xs-rsync owned - set in the spec file
	install -D -d $(DESTDIR)/library/xs-rsync/pub
	install -D -d $(DESTDIR)/library/xs-rsync/pub/builds
	install -D -d $(DESTDIR)/library/xs-rsync/state
	install -D -d $(DESTDIR)/library/xs-rsync/tmp
	install -D -d $(DESTDIR)/var/run/xs-rsync






