# Installs xs-rsync

# install root
DESTDIR=/

$(DESTDIR):
	mkdir -p $(DESTDIR)

install:
	install -D -d $(DESTDIR)/usr/bin
	install -D xs-refresh-xobuilds $(DESTDIR)/usr/bin
	install -D xs-publish-xobuild $(DESTDIR)/usr/bin
	install -D xs-unpack-xobuild $(DESTDIR)/usr/bin

	install -D -m 644 rsyncd.conf.in     $(DESTDIR)/etc/xs-rsyncd.conf.in

	install -D -d $(DESTDIR)/usr/share/xs-rsync
	install -m 755 usbmount-50-xs-rsync-installcontent $(DESTDIR)/usr/share/xs-rsync
	install -m 644 crond-xs-rsync.conf $(DESTDIR)/usr/share/xs-rsync
	install -m 644 xinetd-xs-rsyncd.conf $(DESTDIR)/usr/share/xs-rsync

	# root owned
	install -D -d $(DESTDIR)/library/xs-rsync
	install -D -d $(DESTDIR)/library/xs-rsync/xobuilds-packed
	# xs-rsync owned - set in the spec file
	install -D -d $(DESTDIR)/library/xs-rsync/pub
	install -D -d $(DESTDIR)/library/xs-rsync/pub/builds
	install -D -d $(DESTDIR)/library/xs-rsync/state
	install -D -d $(DESTDIR)/library/xs-rsync/tmp
	install -D -d $(DESTDIR)/var/run/xs-rsync

	install -D -m 755 xs-rsync.setup.sh $(DESTDIR)/etc/sysconfig/olpc-scripts/setup.d/xs-rsync
