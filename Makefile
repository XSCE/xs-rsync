# Installs xs-rsync

# install root
DESTDIR=/

$(DESTDIR):
	mkdir -p $(DESTDIR)

# For developers:


# symbols
PKGNAME = xs-rsync
VERSION =$(shell git describe | sed 's/^v//' | sed 's/-/./g')
RELEASE = 1
COMMITID = $(shell git rev-parse HEAD)
ARCH = noarch

# NOTE: Release is hardcoded in the spec file to 1
NV = $(PKGNAME)-$(VERSION)
NVR = $(NV)-$(RELEASE)
DISTVER=xs11

# rpm target directory
BUILDDIR = $(PWD)/build
TARBALL    = $(BUILDDIR)/SOURCES/$(NV).tar.bz2
SRPM       = $(BUILDDIR)/SRPMS/$(NVR).$(DISTVER).src.rpm
RPM        = $(BUILDDIR)/RPMS/$(ARCH)/$(NVR).$(DISTVER).$(ARCH).rpm


RPMBUILD = rpmbuild \
	--define "_topdir $(BUILDDIR)" \
         --define "dist .$(DISTVER)"

SOURCES: $(TARBALL)
$(TARBALL):
	mkdir -p $(BUILDDIR)/BUILD $(BUILDDIR)/RPMS \
	$(BUILDDIR)/SOURCES $(BUILDDIR)/SPECS $(BUILDDIR)/SRPMS
	mkdir -p $(NV)
	git archive --format=tar --prefix="$(NV)/" HEAD > $(NV).tar
	mkdir -p $(NV)
	echo $(VERSION) > $(NV)/build-version
	tar -rf $(NV).tar $(NV)/build-version
	rm -fr $(NV)
	bzip2 $(NV).tar
	mv $(NV).tar.bz2 $(BUILDDIR)/SOURCES/

SRPM: $(SRPM)
$(SRPM): xs-rsync.spec SOURCES
	$(RPMBUILD) -bs --nodeps $(PKGNAME).spec

xs-rsync.spec: xs-rsync.spec.in
	sed -e 's:@PKGNAME@:$(PKGNAME):g' \
	    -e 's:@VERSION@:$(VERSION):g' \
	    -e 's:@RELEASE@:$(RELEASE):g' \
	    -e 's:@COMMITID@:$(COMMITID):g' \
		< $< > $@

RPM: $(RPM)
$(RPM): SRPM
	$(RPMBUILD) --rebuild $(SRPM)
	rm -fr $(BUILDDIR)/BUILD/$(NV)
	# Tolerate rpmlint errors
	rpmlint $(RPM) || echo "rpmlint errored out but we love you anyway"

publish: SOURCES SRPM
	rsync -e ssh --progress  $(RPM) \
	    xs-dev.laptop.org:/xsrepos/testing/olpc/11/i586/
	rsync -e ssh --progress $(SRPM) \
	    xs-dev.laptop.org:/xsrepos/testing/olpc/11/source/SRPMS/
	rsync -e ssh --progress $(TARBALL) \
	    xs-dev.laptop.org:/xsrepos/testing/olpc/11/source/SOURCES/
	ssh xs-dev.laptop.org sudo createrepo /xsrepos/testing/olpc/11/i586

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

# This forces a rebuild of xs-rsync.spec.in
.PHONY: xs-rsync.spec.in install





