#
# spec file for package acct
#
# Copyright (c) 2021 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           acct
Version:        6.6.4
Release:        4.6
Summary:        User-Specific Process Accounting
License:        GPL-2.0-or-later
Group:          System/Base
URL:            https://www.gnu.org/software/acct/
Source:         https://ftp.gnu.org/gnu/acct/%{name}-%{version}.tar.gz
Source1:        acct.service
Source2:        logrotate.acct
Source3:        https://ftp.gnu.org/gnu/acct/%{name}-%{version}.tar.gz.sig
Source4:        http://savannah.gnu.org/project/memberlist-gpgkeys.php?group=acct&download=1#/acct.keyring
Patch0:         acct-6.6.2-hz.patch
#BuildRequires:  makeinfo
#BuildRequires:  systemd-rpm-macros
Requires:       logrotate
#Requires(post): %{install_info_prereq}
#Requires(postun): %{install_info_prereq}
%{?systemd_ordering}

%description
This package contains the programs necessary for user-specific process
accounting: sa, accton, and lastcomm.

%prep
%setup -q
%patch0

%build
%configure
make %{?_smp_mflags}

%install
install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -d -m 755 %{buildroot}/%{_unitdir}
install -d -m 755 %{buildroot}%{_localstatedir}/account/
install -d -m 755 %{buildroot}%{_libexecdir}/account
install -d -m 755 %{buildroot}%{_sbindir}
install -d -m 755 %{buildroot}%{_bindir}
%make_install

install -m 644 %{SOURCE1} %{buildroot}/%{_unitdir}/acct.service
ln -sf service %{buildroot}%{_sbindir}/rcacct

install -m 644 %{SOURCE2}  %{buildroot}%{_sysconfdir}/logrotate.d/acct
mkdir -p %{buildroot}%{_localstatedir}/log/account
touch %{buildroot}%{_localstatedir}/log/account/pacct

rm -f %{buildroot}%{_bindir}/last
rm -f %{buildroot}/%{_mandir}/man1/last.1*

%pre
%service_add_pre acct.service

%post
%install_info --info-dir=%{_infodir} %{_infodir}/accounting.info
%service_add_post acct.service

%preun
%install_info_delete --info-dir=%{_infodir} %{_infodir}/accounting.info
%service_del_preun acct.service

%postun
%service_del_postun acct.service

%files
%doc README NEWS
%{_infodir}/accounting.info
%{_infodir}/dir
%{_mandir}/man1/ac.1
%{_mandir}/man1/lastcomm.1
%{_mandir}/man8/accton.8
%{_mandir}/man8/dump-acct.8
%{_mandir}/man8/dump-utmp.8
%{_mandir}/man8/sa.8
%config %{_sysconfdir}/logrotate.d/acct
%dir %{_localstatedir}/log/account
%{_localstatedir}/log/account/pacct
%{_bindir}/ac
%{_bindir}/lastcomm
%{_sbindir}/accton
%{_sbindir}/dump-acct
%{_sbindir}/dump-utmp
%{_sbindir}/rcacct
%{_sbindir}/sa

/%{_unitdir}/acct.service

%changelog
* Tue Jul 27 2021 Johannes Segitz <jsegitz@suse.com>
- Added hardening to systemd service(s). Modified:
  * acct.service
* Sun Mar 17 2019 Jan Engelhardt <jengelh@inai.de>
- Reduce %%systemd_requires to %%systemd_ordering: %%service_*
  can handle the absence.
* Tue Sep 19 2017 kstreitova@suse.com
- acct.service: fix chmod command call to use an absolute path
  [bsc#1053528]
* Mon Jul 10 2017 astieger@suse.com
- update to 6.6.4:
  * Added --pid to 'lastcomm'.
* Thu Apr 13 2017 kstreitova@suse.com
- remove acct-info.patch that is no longer needed (fixed upstream
  in version 6.6.3)
- note: acct-6.6.2-hz.patch was not accepted upstream as it might
  break support for the HP alpha platform
* Thu Apr  6 2017 mpluskal@suse.com
- Update to version 6.6.3:
  * Fixed manuals.
- Refresh patches:
  * acct-6.6.2-hz.patch
  * acct-info.patch
- Drop no longer needed:
  * acct-ac.patch
  * acct-timestamp.patch
* Wed Mar 29 2017 kstreitova@suse.com
- cleanup with spec-cleaner
- get rid of %%{name} and %%{version} macros from the patch names
* Wed Jul 13 2016 kstreitova@suse.com
- remove syslog.target from acct.service file [bsc#983938]
* Fri Mar  4 2016 olaf@aepfle.de
- Remove timestamp from info file
  acct-timestamp.patch
* Thu Jul  2 2015 tchvatal@suse.com
- The previous commit ghosted the log file, but we need it empty
  and present to start with, so unghost it
* Mon Jun 22 2015 tchvatal@suse.com
- Use just /var/log/account/pacct file and remove the tmpfiles creation
  completely
* Mon Jun 22 2015 tchvatal@suse.com
- Use try-restart not restart on logrotate update, otherwise we could
  suprisingly start the service for user, which is not desired
- Cleanup with spec-cleaner
- Use tmpfiles creation instead of hand-written shell script
* Sun May 17 2015 meissner@suse.com
- install deinstall needs to be in preun
* Sun Mar  1 2015 p.drouand@gmail.com
- Fixthe log path in service and logrotate files; fix bnc#915654
* Fri Dec 19 2014 p.drouand@gmail.com
- Add back .keyring and .sig files; OBS verify them too
* Sat Dec 13 2014 p.drouand@gmail.com
- Update to version 6.6.2
  + Link with -lm.
  + Fix texi.
  + The rest of fixes from 6.5.5 to 6.6.1.
- Update Url to new project home
- Use download Url
- Remove dependency on gpg-offline and keyring files; let OBS handle
  source verification
- Adapt acct-hz.patch to upstream changes
  > acct-6.6.2-hz.patch
* Thu Aug 28 2014 vcizek@suse.com
- fixed libexec path in acct.service (bnc#893980)
* Mon Mar 17 2014 werner@suse.de
- cleanup of acct
  * Add install section in service unit (bnc#867138)
  * Add a simple script to create pacct file
* Sat Dec 21 2013 vcizek@suse.com
- update to 6.6.1
  * Fixed vulnabilities, due to autmake. Thanks to Karl Berry
    for pointing this out.
  * Update gnulib to latest git.
- dropped acct-stdio.h.patch (upstream)
- add gpg verification
* Sat Oct 19 2013 p.drouand@gmail.com
- Remove useless %%inserv_prereq and fillup_prereq macro; acct package
  doesn't contain neither sysvinit script and sysconfig file
* Thu Jun  6 2013 schuetzm@gmx.net
- Converted rc file to systemd unit file.
- Fixed a bug where the accounting file wasn't reopened after
  logrotate, because force-reload isn't implemented.
* Fri Apr 26 2013 mmeister@suse.com
- Added makeinfo BuildRequire to fix build with new automake
* Sat Jan 12 2013 coolo@suse.com
- remove suse_update_config
* Wed Sep  5 2012 vcizek@suse.com
- drop useless acct-axp.patch
* Sun Jul 22 2012 aj@suse.de
- Fix build with missing gets declaration (glibc 2.16)
* Mon Jan 23 2012 bart.vanassche@gmail.com
- switch from acct-6.3.5 to acct-6.5.5. From the upstream acct ChangeLog:
  * Fix potential buffer-overflows.
  * UNIX 98 pty support.
  * Add Linux multiformat support.
  * lastcomm.c: integrated patch from Paul Jones which adds
  paging and swapping support to lastcomm and sa
* Tue Oct  4 2011 uli@suse.com
- cross-build fix: use %%__cc, %%__cxx macros
* Fri Sep 30 2011 coolo@suse.com
- add libtool as buildrequire to make the spec file more reliable
* Sat Sep 17 2011 jengelh@medozas.de
- Remove redundant tags/sections from specfile
- Use %%_smp_mflags for parallel build
* Thu Mar  3 2011 lchiquitto@novell.com
- fix initscript's force-reload action to reload the service only
  if it is running [bnc#667437]
* Wed Dec 23 2009 coolo@novell.com
- remove the moblin hack that fixes something not in this package
* Fri Nov  6 2009 gregkh@suse.de
- fix mode on /etc/logrotate.d/acct to not be executable.
* Wed Nov  4 2009 gregkh@suse.de
- do not enable acct to start automatically on Moblin.  We don't
  want to access the disk every 15 seconds or so for no reason at
  all on laptops.
* Wed Feb 14 2007 mkudlvasr@suse.cz
- fixed ahz value problems [#244186]
* Tue Sep  5 2006 anosek@suse.cz
- fixed compiler warning: old-style function definition
  [#203115] (warning.patch)
* Tue Aug 22 2006 postadal@suse.cz
- define HZ as sysconf(_SC_CLK_TCK) if undefined
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Tue Oct  5 2004 postadal@suse.cz
- fixed 64bit problem in printing time [#42969]
* Mon Oct  4 2004 postadal@suse.cz
- fixed to work with acct v3 format which the new kernel uses [#46768]
* Thu Feb 12 2004 ro@suse.de
- fix owner/group for var/account/pacct
* Thu Feb 12 2004 postadal@suse.cz
-added norootforbuild flag to the spec file
* Tue Aug 26 2003 postadal@suse.cz
- use new stop_on_removal/restart_on_upate macros
* Sun May 25 2003 ro@suse.de
- remove unpackaged files from buildroot
* Thu Apr 24 2003 ro@suse.de
- merge postuns
* Thu Apr 24 2003 ro@suse.de
- fix install_info --delete call and move from preun to postun
* Tue Feb 25 2003 postadal@suse.cz
- used install-info macros
- fixed accounting.info (dir entry)
* Mon Sep  9 2002 ro@suse.de
- added logrotate configuration
* Fri Aug 16 2002 postadal@suse.cz
- added %%insserv_prereq, %%fillup_prereq and fileutils
  to PreReq [#17787]
* Wed Aug 14 2002 poeml@suse.de
- fix comment in rc.script
* Tue Apr  2 2002 postadal@suse.cz
- fixed to compile with autoconf-2.53
* Mon Feb 25 2002 postadal@suse.cz
- modified copyright in /etc/init.d/acct
* Tue Jan 15 2002 egmont@suselinux.hu
- removed colons from startup/shutdown messages
* Sun Jan 13 2002 ro@suse.de
- removed START_ACCT
* Wed Nov 14 2001 ro@suse.de
- don't call automake for now
* Wed Aug  8 2001 cihlar@suse.cz
- fixed to compile on axp
* Tue Aug  7 2001 cihlar@suse.cz
- fixed stop and status part of init script
- moved rc.acct and rc.config.acct from patch
* Mon Jun 25 2001 pblaha@suse.cz
- rewrite init script to conform LSB
* Wed Dec 13 2000 smid@suse.cz
- rcacct link added
* Tue Nov 28 2000 ro@suse.de
- startscript to etc/init.d
* Thu Nov  2 2000 smid@suse.cz
- fix ugly bug in startup scripts
* Tue Aug 29 2000 smid@suse.cz
- sources => bzip2
- spec cleanup
* Wed Jun  7 2000 cihlar@suse.cz
- Copyright tag fixed
* Fri Apr  7 2000 smid@suse.cz
- upgrade to 6.3.5
- buildroot added
* Sun Feb 20 2000 garloff@suse.de
- Create /var/account/pacct in script if non-existing
* Thu Feb 17 2000 kukuk@suse.de
- Fix configure options
* Tue Feb 15 2000 kukuk@suse.de
- Fill in group tag
* Thu Jan 20 2000 kukuk@suse.de
- Move /usr/{man,info} -> /usr/share/{man,info}
* Mon Sep 13 1999 bs@suse.de
- ran old prepare_spec on spec file to switch to new prepare_spec.
* Wed Apr  7 1999 kukuk@suse.de
- With glibc 2, include linux/acct.h, not sys/acct.h
* Tue Dec 29 1998 tmg@suse.de
- fixed several bugs in init script ;)
* Sat Dec 12 1998 bs@suse.de
- made absolute path in %%post to relative path
* Tue Dec  8 1998 ro@suse.de
- updated init script
* Sun Oct 18 1998 tmg@suse.de
- initial revision
