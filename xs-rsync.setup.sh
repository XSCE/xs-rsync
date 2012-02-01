#!/bin/bash
DATADIR=/usr/share/xs-rsync

ln -sf $DATADIR/usbmount-50-xs-rsync-installcontent /etc/usbmount/mount.d/50-xs-rsync-installcontent
ln -sf $DATADIR/crond-xs-rsync.conf /etc/cron.d/xs-rsync
ln -sf $DATADIR/xinetd-xs-rsyncd.conf /etc/xinetd.d/xs-rsyncd

service xinetd condrestart
