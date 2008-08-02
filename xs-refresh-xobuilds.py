#!/usr/bin/python

""" Add/remove XO builds from the published list
    based on the content of 
    /library/xs-rsync/xobuilds-packed/

    Author: Martin Langhoff <martin@laptop.org>
    Copyright: One Laptop per Child
    License: GPLv2
"""

from subprocess import call, check_call, Popen, PIPE
import os.path, sys, os, re, tempfile, shutil, stat
from optparse import OptionParser

PACKEDDIR='/library/xs-rsync/xobuilds-packed'
BUILDSDIR='/library/xs-rsync/pub/builds'
STATEDIR='/library/xs-rsync/state'
rsyncbaseconfpath = '/etc/xs-rsyncd.conf.in'
rsyncconfpath = '/etc/xs-rsyncd.conf'


buildsbyname = dict()

def main():

    parser = OptionParser(usage='%prog [--force]')
    parser.add_option('-f', '--force', action='store_true', dest='force',
                      default=False)
    (options, Null) = parser.parse_args()

    # Read the current build names into a dict
    direntspacked = os.listdir(PACKEDDIR)
    for dirent in direntspacked:
        # file ending on .name?
        fpath = os.path.join(PACKEDDIR,dirent)
        m = re.match('^(.*)\.name$', dirent)
        if m and os.path.isfile(fpath):
            namefile = open(fpath, 'r')
            name = namefile.readline()
            namefile.close()
            name=name.rstrip()
            buildfn = m.group(1) + '-tree.bz2'
            if not os.path.isfile(os.path.join(PACKEDDIR,buildfn)):
                continue
            buildsbyname[name]     = buildfn
            sys.stdout.write(buildfn + name + "\n")

    # Remove stale builds
    buildremoved = False
    direntspub   = os.listdir(BUILDSDIR)

    for dirent in direntspub:
        fpath = os.path.join(BUILDSDIR,dirent)
        if not os.path.isdir(fpath):
            continue
        if not buildsbyname.has_key(dirent):
            # rm -fr under the xs-rsync user privs
            statefpath = os.path.join(STATEDIR, dirent+'.state')
            if os.path.exists(statefpath):
                check_call(['sudo', '-u', 'xs-rsync',
                            'rm', '-fr', fpath, statefpath ])
            buildremoved = True

    # Remove stale state files
    direntspub   = os.listdir(STATEDIR)
    for dirent in direntspub:
        fpath = os.path.join(STATEDIR,dirent)
        if not os.path.isfile(fpath):
            continue
        m = re.match('^(.*)\.state$', dirent)
        if m:
            bname = m.group(1)
            if buildsbyname.has_key(bname):
                continue
            # rm under the xs-rsync user privs
            check_call(['sudo', '-u', 'xs-rsync',
                        'rm', fpath ])
            buildremoved = True

    # Add / refresh builds
    buildadded = False
    for buildname in buildsbyname.keys():
        bpath = os.path.join(BUILDSDIR,buildname)
        ppath = os.path.join(PACKEDDIR,buildsbyname[buildname])
        if options.force or not os.path.exists(bpath):
            installcmd = [ 'sudo', '-u', 'xs-rsync',
                           os.path.join(os.path.dirname(sys.argv[0]), 'xs-publish-xobuild.py') ]
            if options.force:
                installcmd.append('-f')
            installcmd.append(ppath)
            installcmd.append(buildname)
            installcmd.append(BUILDSDIR)
            check_call(installcmd)
            buildadded = True

    # Check - we might need to rebuild
    # the state file -
    if buildremoved and not buildadded:
        installcmd = [ 'sudo', '-u', 'xs-rsync',
                       os.path.join(os.path.dirname(sys.argv[0]), 'xs-publish-xobuild.py'),
                       '--onlyfakerootstate']
        check_call(installcmd)

    # Update rsyncd conf - if anything changed!
    # being careful to do an atomic replacement
    if buildadded or buildremoved:
        (tmpfh, tmpfname) = tempfile.mkstemp('tmp', '.xs-rsync')
        templ = open(rsyncbaseconfpath, 'r')
        while True:
            buf = templ.read(4096)
            if not buf:
                break
            os.write(tmpfh, buf)
        for buildname in buildsbyname.keys():
            os.write(tmpfh, "[build-%s]\n" % (buildname) )
            os.write(tmpfh, 'path = ' + os.path.join(BUILDSDIR, buildname) +"\n"  )
            os.write(tmpfh, "read only = yes \n\n");
        os.close(tmpfh)
        # Why would you say 644, when you can be
        # very verbose with cryptic constants? Why?
        os.chmod(tmpfname, stat.S_IRGRP | stat.S_IROTH| stat.S_IRUSR | stat.S_IWUSR)

        # /tmp may be on a different FS, we cannot use os.rename()
        check_call(['mv', tmpfname, rsyncconfpath])


if __name__ == '__main__': main ()
