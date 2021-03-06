Name:           xs-rsync
Version:        0.6.6.gf018cff
Release:        1%{?dist}

Summary:        OLPC XS Rsync publishing
Group:          Applications/Archiving
License:        GPLv2
Packager:       Martin Langhoff <martin@laptop.org>
URL:            http://wiki.laptop.org/go/XS-rsync
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  make

Requires:       python
Requires:       rsync
Requires:       xinetd
Requires:       fakeroot
Requires:       fakechroot
Requires:       bash
Requires:       cronie
Requires:       usbmount
Requires:       xs-tools
Requires:       xs-config
Requires:       xz, xz-lzma-compat

%description
XS rsync provides support for publishing resources on the XS via rsync.

The first use of xs-rsync is to offer OS images to run
XO software updates. There are utilities provided for this
task.


%pre
# For static uid/gid mapping, see 
# http://wiki.laptop.org/go/XS_UserManagement
getent group xs-rsync >/dev/null || \
       groupadd -r xs-rsync
getent passwd xs-rsync >/dev/null || \
       useradd -c "XS Rsync" -M  -s /sbin/nologin  \
       -d /library/xs-rsync -r -g xs-rsync xs-rsync

%post
# if the file does not exist, create an empty one
touch /library/xs-rsync/state/rsyncd.all
# Early run to create /etc/xs-rsyncd.conf
if [ ! -e /etc/xs-rsyncd.conf ]; then 
   cp -pr /etc/xs-rsyncd.conf{.in,}
fi

%prep

%setup -q



%build

%install
pwd
ls
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%files
%{_bindir}/xs-publish-xobuild
%{_bindir}/xs-refresh-xobuilds
%{_bindir}/xs-unpack-xobuild
%{_datadir}/%{name}
%{_sysconfdir}/sysconfig/olpc-scripts/setup.d/*
%doc README COPYING
%config(noreplace) %{_sysconfdir}/xs-rsyncd.conf.in
%dir  /library/xs-rsync/xobuilds-packed
%attr(755, xs-rsync, xs-rsync) %dir /library/xs-rsync/pub
%attr(755, xs-rsync, xs-rsync) %dir /library/xs-rsync/pub/builds
%attr(750, xs-rsync, xs-rsync) %dir /library/xs-rsync/state
%attr(750, xs-rsync, xs-rsync) %dir /library/xs-rsync/tmp
%attr(750, xs-rsync, xs-rsync) %dir %{_localstatedir}/run/xs-rsync

%changelog
* Sat Aug 2 2008 Martin Langhoff <martin@laptop.org - 0.1-1
  - This is a git-maintaned package - See the changelog at
  http://dev.laptop.org/git?p=users/martin/xs-rsync;a=log;h=@COMMITID@
(END) 
