#!/bin/bash
#
##
## unpack the jffs2 tree file in a fakeroot
## to preserve all its glory
##
## Author: Martin Langhoff <martin@laptop.org>
##
#
set -e

# Parameters
DESTDIR=$1      # complete dest dir path
BUILDFILE=$2    # tree file

# Very recommended: Set TMPDIR to a tempdir
# on the same partition as DESTDIR
TEMPDIR=$(mktemp -d)

if [ -z "$FAKEROOTKEY" ]; then
    echo $0 MUST run in a fakeroot.
    echo You do NOT want to be creating
    echo random devices on your machine.
    exit 1
fi

if [ -z "$DESTDIR" -o -z "$BUILDFILE" ]; then
    echo Missing a parameter. Usage:
    echo $0 destdir buildfile
    exit 1
fi

# Stop complaining and do the job
if [ ${BUILDFILE:(-8)} = ".tar.bz2" ]; then
    tar -C "$TEMPDIR" --numeric-owner -xpjf "$BUILDFILE"
elif [ ${BUILDFILE:(-9)} = ".tar.lzma" ]; then 
    lzma -cd "$BUILDFILE" | tar -C "$TEMPDIR" --numeric-owner -xp
else
    echo Unknown file format!
    exit 1
fi

#
# Some of the images have odd leftovers around
# so if the image contains a pristine copy, use that.
# Otherwise, clear out the '/versions' directory.
#
if [ -e "$TEMPDIR/versions/pristine" ];then
    PRI=`ls $TEMPDIR/versions/pristine | sort | head -n1`
    if [ -n "$PRI" -a -d "$TEMPDIR/versions/pristine/$PRI" ];then
	mv -T "$TEMPDIR/versions/pristine/$PRI" "$DESTDIR"
	rm -fr "$TEMPDIR"
    else
	rm -fr "$TEMPDIR/versions"
	mv -T "$TEMPDIR" "$DESTDIR"
    fi
else
    rm -fr "$TEMPDIR/versions"
    mv -T "$TEMPDIR" "$DESTDIR"
fi
