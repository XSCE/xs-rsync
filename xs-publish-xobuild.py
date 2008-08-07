#!/usr/bin/python

""" Install an XO build in jffs2-tree format to be served
    via rsync to update the XOs. 

Inspired by bits and pieces of Scott's update-server.

Author: Martin Langhoff <martin@laptop.org>
Copyright: One Laptop per Child
License: GPLv2
"""
from subprocess import call, check_call, Popen, PIPE
import os.path, sys, os, re, tempfile, shutil, stat
from optparse import OptionParser

def main():

    parser = OptionParser(usage='%prog [options] buildfile buildname destdir')
    parser.add_option('-s', '--statedir', dest='statedir',
                      default='/library/xs-rsync/state/')
    parser.add_option('-t', '--tmpdir', dest='tmpdir',
                      default='/library/xs-rsync/tmp/')
    parser.add_option('--onlyfakerootstate', action='store_true', dest='onlyfakeroot',
                      default=False)
    parser.add_option('-f', '--force', action='store_true', dest='force',
                      default=False)
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      default=False)
    (options, paths) = parser.parse_args()

    if (not paths or len(paths) < 3) and not options.onlyfakeroot:
        parser.error('Need at least buildfile, buildname and destdir.')

    if options.onlyfakeroot:
        update_fakerootstate(options)
        exit()

    buildfile = paths[0]
    buildname = paths[1]
    destdir   = paths[2]

    # Some basic checks
    buildfile = os.path.abspath(buildfile)
    if not os.path.exists(buildfile):
        raise RuntimeError('Missing buildfile')
    if not os.path.exists(buildfile + '.md5'):
        raise RuntimeError('Missing MD5 file')
    destdir = os.path.abspath(destdir)
    if not os.path.isdir(destdir):
        raise RuntimeError('Missing destdir')

    # the contents file is a bit more involved
    contentsfile = buildfile
    m = re.match('(.*)-tree.tar.bz2', contentsfile)
    if not m:
        raise RuntimeError('Cannot understand your buildfile name')
    contentsfile = m.group(1) + '.contents'
    if not os.path.exists(contentsfile):
        sys.stdout.write(contentsfile)
        raise RuntimeError('Missing contents file')

    # validate md5 and check contents is valid
    # the md5 file has "local" paths, so
    currentcwd=os.getcwd()
    os.chdir(os.path.dirname(buildfile))
    check_call(['md5sum', '--status', 
                '-c', buildfile + '.md5'])
    os.chdir(currentcwd)

    ##
    ## untar under fakeroot
    ##
    destdir = os.path.join(destdir,buildname,'root')
    if os.path.exists(destdir):
        if options.force:
            check_call(['rm', '-fr', destdir])
        else:
            raise RuntimeError('Destination directory already exists')
    check_call(['mkdir', '-p', destdir])
    tmpstatefile = os.path.join(options.statedir, buildname+".tmp")

    # having the tmpdir in the same partition makes final mv op atomic
    os.environ['TMPDIR'] = options.tmpdir

    basepath = os.path.dirname(sys.argv[0])
    check_call(['flock', tmpstatefile,
                'fakeroot', '-i', tmpstatefile,
                '-s', tmpstatefile, '--',
                os.path.join(basepath, 'xs-unpack-xobuild.sh'),
                destdir, buildfile])
    os.chmod(tmpstatefile, stat.S_IRGRP | stat.S_IROTH| stat.S_IRUSR | stat.S_IWUSR)
    os.rename(tmpstatefile, os.path.join(options.statedir, buildname+'.state'))


    # copy the 'contents' file into place
    destcontent = os.path.join(os.path.dirname(destdir), 'contents')
    shutil.copyfile(contentsfile, destcontent)

    update_fakerootstate(options)

def update_fakerootstate(options):

    ##
    ## Recompose the overall state file atomically
    ##
    #  A very pythonistically verbose way of saying:
    # (cat *.state > .tmpstate) && mv .tmpstate fakeroot.all
    os.environ['TMPDIR'] = options.tmpdir
    (tmpfh, tmpfpath) = tempfile.mkstemp()

    pfind  = Popen(['find', options.statedir, '-type', 'f',
                    '-name', '*.state', '-print0'], stdout=PIPE)
    pxargs = Popen(['xargs', '-0', '--no-run-if-empty', 'cat'],
                   stdin=pfind.stdout,stdout=tmpfh)

    pxargs.communicate()
    pxargs.wait()
    os.fdatasync(tmpfh)
    os.close(tmpfh)

    os.chmod(tmpfpath, stat.S_IRGRP | stat.S_IROTH| stat.S_IRUSR | stat.S_IWUSR)
    os.rename(tmpfpath,
              os.path.join(options.statedir, 'rsyncd.all'))


if __name__ == '__main__': main ()
