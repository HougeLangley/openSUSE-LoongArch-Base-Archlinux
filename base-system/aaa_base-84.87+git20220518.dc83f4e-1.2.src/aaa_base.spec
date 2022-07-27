#
# spec file for package aaa_base
#
# Copyright (c) 2022 SUSE LLC
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
# icecream 0


#Compat macro for new _fillupdir macro introduced in Nov 2017
%if ! %{defined _fillupdir}
  %define _fillupdir /var/adm/fillup-templates
%endif

%if 0%{?_build_in_place}
%define git_version %(git log '-n1' '--date=format:%Y%m%d' '--no-show-signature' "--pretty=format:+git%cd.%h")
BuildRequires:  git-core
%else
# this is required for obs' source validator. It's
# 20-files-present-and-referenced ignores all conditionals. So the
# definition of git_version actually happens always.
%define git_version %{nil}
%endif

Name:           aaa_base
Version:        84.87+git20220518.dc83f4e%{git_version}
Release:        1.2
Summary:        openSUSE Base Package
License:        GPL-2.0-or-later
Group:          System/Fhs
URL:            https://github.com/openSUSE/aaa_base
Source:         aaa_base-%{version}.tar
Source1:        README.packaging.txt
Source99:       aaa_base-rpmlintrc
Requires:       /bin/mktemp
Requires:       /usr/bin/cat
Requires:       /usr/bin/date
Requires:       /usr/bin/grep
Requires:       /usr/bin/mv
Requires:       /usr/bin/sed
Requires:       /usr/bin/tput
Requires:       /usr/bin/xz
Requires:       distribution-release
Requires:       filesystem
Requires(pre):  /usr/bin/rm
Requires(pre):  (glibc >= 2.30 if glibc)
Requires(post): fillup /usr/bin/chmod /usr/bin/chown
Recommends:     aaa_base-extras
Recommends:     iproute2
Recommends:     iputils
Recommends:     logrotate
Recommends:     netcfg
Recommends:     udev
# do not require systemd - aaa_base is in the build environment and we don't
# want to pull in tons of dependencies
Conflicts:      sysvinit-init

# run osc service mr to recreate

%description
This package installs several important configuration files and central scripts.

%package extras
Summary:        SUSE Linux Base Package (recommended part)
Group:          System/Fhs
Requires:       %{name} = %{version}
Requires:       /usr/bin/find
Requires:       cpio
Requires(post): fillup
Provides:       aaa_base:/etc/DIR_COLORS

%description extras
The parts of aaa_base that should be installed by default but are not
strictly required to run a system. (bash completions and convenience hacks).

%package malloccheck
Summary:        SUSE Linux Base Package (malloc checking)
Group:          System/Fhs
Requires:       %{name} = %{version}

%description malloccheck
This package sets environment variables that enable stricter
malloc checks to catch potential heap corruptions. It's not
installed by default as it may degrade performance.

%package wsl
Summary:        SUSE Linux Base Package (Windows Subsystem for Linux)
Group:          System/Fhs
Requires:       %{name} = %{version}

%description wsl
This package includes some special settings needed on Windows Subsystem
for Linux. It should only be installed on WSL and not on regular Linux
systems.

%prep
%setup -q

%build
%make_build CFLAGS="%{optflags}" CC="%{__cc}"

%install
%make_install
mkdir -p %{buildroot}/etc/sysctl.d
case "$RPM_ARCH" in
	s390*) ;;
	*) rm -f %{buildroot}/usr/lib/sysctl.d/50-default-s390.conf ;;
esac
#
# make sure it does not creep in again
test -d %{buildroot}/root/.gnupg && exit 1
# TODO: get rid of that at some point in the future
mkdir -p %{buildroot}/etc/init.d
for i in boot.local after.local ; do
  install -m 755 /dev/null %{buildroot}/etc/init.d/$i
done
#
install -d -m 755 %buildroot%{_libexecdir}/initscripts/legacy-actions
# keep as ghost for migration
touch %buildroot/etc/inittab

# Backup directories
install -d -m 755 %{buildroot}/var/adm/backup/{rpmdb,sysconfig}

mkdir -p %{buildroot}%{_fillupdir}
%if "%{_fillupdir}" != "/var/adm/fillup-templates"
  for f in %{buildroot}/var/adm/fillup-templates/* ; do
    test -e "$f" || continue
    mv $f %{buildroot}%{_fillupdir}/
  done
  rm -vrf %{buildroot}/var/adm/fillup-templates
%endif
%if "%{_fillupdir}" != "/usr/share/fillup-templates"
  for f in %{buildroot}/usr/share/fillup-templates/* ; do
    test -e "$f" || continue
    mv $f %{buildroot}%{_fillupdir}/
  done
  rm -vrf %{buildroot}/usr/share/fillup-templates
%endif

%pre -f aaa_base.pre

%post -f aaa_base.post

%pre extras
%service_add_pre backup-rpmdb.service backup-rpmdb.timer backup-sysconfig.service backup-sysconfig.timer check-battery.service check-battery.timer

%post extras
%fillup_only -n backup
%service_add_post backup-rpmdb.service backup-rpmdb.timer backup-sysconfig.service backup-sysconfig.timer check-battery.service check-battery.timer

%preun extras
%service_del_preun backup-rpmdb.service backup-rpmdb.timer backup-sysconfig.service backup-sysconfig.timer check-battery.service check-battery.timer

%postun extras
%service_del_postun backup-rpmdb.service backup-rpmdb.timer backup-sysconfig.service backup-sysconfig.timer check-battery.service check-battery.timer

%files
%license COPYING
%config(noreplace) /etc/DIR_COLORS
%config(noreplace) /etc/sysctl.conf
%config /etc/bash.bashrc
%config /etc/csh.cshrc
%config /etc/csh.login
%config /etc/inputrc
%config /etc/inputrc.keys
%config /etc/mime.types
%config /etc/profile
/usr/etc/profile.d/alljava.csh
/usr/etc/profile.d/alljava.sh
/usr/etc/profile.d/lang.csh
/usr/etc/profile.d/lang.sh
/usr/etc/profile.d/profile.csh
/usr/etc/profile.d/profile.sh
/usr/etc/profile.d/xdg-environment.csh
/usr/etc/profile.d/xdg-environment.sh
/usr/etc/profile.d/alias.ash
/usr/etc/profile.d/alias.bash
/usr/etc/profile.d/alias.tcsh
/usr/etc/profile.d/ls.tcsh
/usr/etc/profile.d/ls.bash
/usr/etc/profile.d/ls.zsh
%config /etc/shells
%ghost %dir /etc/init.d
%ghost %config(noreplace) /etc/init.d/boot.local
%ghost %config(noreplace) /etc/init.d/after.local
%ghost %config /etc/inittab
# don't forget to also change aaa_base.post, boot.cleanup
# and /etc/permissions!
%ghost %attr(0644,root,root) %verify(not md5 size mtime) /var/log/lastlog
/usr/bin/get_kernel_version
/usr/sbin/refresh_initrd
/usr/sbin/service
/usr/sbin/smart_agetty
/usr/bin/filesize
/usr/bin/old
/usr/bin/rpmlocate
/usr/bin/safe-rm
/usr/bin/safe-rmdir
/usr/sbin/sysconf_addword
/usr/share/man/man1/smart_agetty.1
/usr/share/man/man5/defaultdomain.5
/usr/share/man/man8/safe-rm.8
/usr/share/man/man8/safe-rmdir.8
/usr/share/man/man8/service.8
/usr/lib/sysctl.d/50-default.conf
/usr/lib/sysctl.d/51-network.conf
/usr/lib/sysctl.d/52-yama.conf
%dir %{_libexecdir}/initscripts
%dir %{_libexecdir}/initscripts/legacy-actions
%{_fillupdir}/sysconfig.language
%{_fillupdir}/sysconfig.proxy
%{_fillupdir}/sysconfig.windowmanager

%files extras
/etc/skel/.emacs
/etc/skel/.inputrc
%dir /usr/lib/base-scripts
/usr/etc/profile.d/complete.bash
/usr/lib/base-scripts/backup-rpmdb
/usr/lib/base-scripts/backup-sysconfig
/usr/lib/base-scripts/check-battery
/usr/lib/systemd/system/backup-rpmdb.service
/usr/lib/systemd/system/backup-rpmdb.timer
/usr/lib/systemd/system/backup-sysconfig.service
/usr/lib/systemd/system/backup-sysconfig.timer
/usr/lib/systemd/system/check-battery.service
/usr/lib/systemd/system/check-battery.timer
/usr/share/man/man8/resolv+.8
/var/adm/backup/rpmdb
/var/adm/backup/sysconfig
%{_fillupdir}/sysconfig.backup

%files malloccheck
/usr/etc/profile.d/malloc-debug.sh
/usr/etc/profile.d/malloc-debug.csh

%files wsl
/usr/etc/profile.d/wsl.csh
/usr/etc/profile.d/wsl.sh

%changelog
* Wed May 18 2022 werner@suse.de
- Update to version 84.87+git20220518.dc83f4e:
  * Also in /etc/profile, rootsh is not restricted
* Wed May 18 2022 werner@suse.de
- Update to version 84.87+git20220518.78b2a0b:
  * The wrapper rootsh is not a restricted shell
* Tue Apr 19 2022 lnussel@suse.de
- Update to version 84.87+git20220419.bf51b75:
  * add Yama LSM sysctl setting and description
  * Stop lowering the inotify limit
  * move DIR_COLORS to where ls.bash is
* Mon Apr 11 2022 lnussel@suse.de
- Update to version 84.87+git20220411.adfb912:
  * move bash completion back to -extras (bsc#1187213)
* Thu Mar 24 2022 dmueller@suse.com
- Update to version 84.87+git20220324.fca4619:
  * No completion in restricted bash
  * No longer install /usr/lib/restricted/bin/hostname => /bin/hostname symlink
* Mon Mar 21 2022 lnussel@suse.de
- Update to version 84.87+git20220321.f60f2de:
  * order header in the way spec-cleaner wants it
  * move changes from package to git
  * merge audio files highlighting fixes from coreutils 9
  * Update from coreutils 9
  * Make source validator happy
* Mon Mar 21 2022 lnussel@suse.de
- Update to version 84.87+git20220321.5a5cb79:
  * DIR_COLORS: lz support
  * DIR_COLORS: zstd support
* Mon Feb 21 2022 lnussel@suse.de
- Update to version 84.87+git20220221.b62a2cf:
  * package: Require new enough version of glibc
  * package: build in place support
  * drop /etc/ttytype (boo#1191923)
* Sat Dec 11 2021 dleuenberger@suse.com
- Update to version 84.87+git20211206.de24bdf:
  * Add "rpm" make target
  * Remove legacy usrmerged sections
  * Add rpmlintrc and README from OBS too
  * Fix osc service instructions
  * Add obs workflow for git integration
  * Adopt upstream way of setting rp_filter and promote_secondaries
  * Don't fail if net.ipv4.ping_group_range can't be set
  * add spec file
* Thu Nov 25 2021 Dr. Werner Fink <werner@suse.de>
- Clear term.sh and term.csh also from file list
* Wed Nov 24 2021 werner@suse.de
- Update to version 84.87+git20211124.5486aad:
  * Remove term.sh and term.csh: no COLORTERM anymore
    Avoid changing COLORTERM variable in urxvt (boo#1190833)
* Tue Nov  2 2021 ro@suse.de
- Update to version 84.87+git20211102.80d7177:
  * Add $HOME/.local/bin to PATH, if it exists (bsc#1192248)
  * Avoid tcsh undefined LANG variable (boo#1190142)
* Mon Aug 23 2021 kukuk@suse.com
- Update to version 84.87+git20210823.4c98889:
  * Remove /etc/hushlogins
* Thu Aug 19 2021 lnussel@suse.de
- Update to version 84.87+git20210819.b55340d:
  * Rework locale checks for better support of ssh
  * Update mime types from apache
  * Better support of Midnight Commander color skins (boo#1188862)
* Wed Jul 28 2021 kukuk@suse.com
- Update to version 84.87+git20210727.b447649:
  * Move /etc/profile.d/* to /usr/etc/profile.d/
* Tue Jun 22 2021 Dominique Leuenberger <dimstar@opensuse.org>
- Switch back to using tar_scm in _service file: with aaa_base
  being part of the distro bootstrap (ring0) we want to have the
  build deps as lean as possible. Buildtime services equals to
  build deps.
* Wed Jun 16 2021 lnussel@suse.de
- Update to version 84.87+git20210616.9cf42ff:
  * add media type application/wasm (boo#1187387)
  * Remove legacy links in /sbin
  * Fix profile.csh to really set http proxies
* Tue Jun  1 2021 werner@suse.de
- Update to version 84.87+git20210601.8cb043f:
  * Use shell builtins for $HOSTTYPE and others (boo#1186296)
* Wed Mar 17 2021 ro@suse.de
- Update to version 84.87+git20210317.2c04190:
  * Don't rely on external dirname utility, but use ${d:h} tcsh expression.
  * Enable locking feature of tcsh history file handling
  * Add tcsh xd alias as well.
  * Add ash xd() function as well.
  * Add new function xd() "jump to the directory of a file"
* Mon Mar  8 2021 ro@suse.de
- Update to version 84.87+git20210308.d7a7d3a:
  * excluding new kernel string in version search
  * Fixing possible resource leak. Found by running ccpcheck on the source code.
  * Comment out 8-bit C1 conflicting with UTF-8 in /etc/inputrc
  * Fix keyseq specifications in /etc/inputrc{,.keys}
* Mon Nov 23 2020 Ludwig Nussel <lnussel@suse.de>
- clean up rpmlintrc. Add filter for deprecated init scripts. We'll have to
  keep them around for a while until systemd takes over ownership.
- Update to version 84.87+git20201123.4f16b16:
  * mark /etc/init.d/{boot,after}.local as %%config(noreplace) (boo#1179097)
  * Avoid semicolon within (t)csh login script on S/390
* Thu Oct 29 2020 Ludwig Nussel <lnussel@suse.de>
- prepare usrmerge (boo#1029961)
* Fri Sep 18 2020 dleuenberger@suse.com
- Update to version 84.87+git20200918.331aa2f:
  * sysctl.d/50-default.conf: fix ping_group_range syntax error
  * alias.bash check if ip command knows color=auto (jsc#SLE-7679)
* Wed Sep  9 2020 Ludwig Nussel <lnussel@suse.de>
- Update to version 84.87+git20200909.ee4a72c:
  * /etc/profile.d/xdg-environment.{sh,csh}: Added /usr/etc/xdg to $XDG_CONFIG_DIRS
  * sysctl.d/50-default.conf: allow everybody to create IPPROTO_ICMP sockets (bsc#1174504)
* Tue Aug 18 2020 ro@suse.de
- Update to version 84.87+git20200818.b9dd70f:
  * backup-rpmdb: exit if zypp.pid is there and running
    (bug#1161239)
* Tue Aug 18 2020 ro@suse.de
- Update to version 84.87+git20200818.5220a5f:
  * profile and csh.login: on s390x set TERM to dumb on serial console
  * etc/profile add some missing ;; in case esac statements
  * refresh_initrd call modprobe as /sbin/modprobe (bug#1011548)
  * DIR_COLORS: merge TERM entries with list from (bug#1006973)
  * sort TERM entries in etc/DIR_COLORS
  * DIR_COLORS add TERM rxvt-unicode-256color (bug#1006973)
  * Rename path() to _path() to avoid using a general name.
* Wed Aug 12 2020 Dr. Werner Fink <werner@suse.de>
- Let's own /etc/init.d/ as it is gone from package filesystem
* Tue Aug  4 2020 Thorsten Kukuk <kukuk@suse.com>
- Don't create/ship halt.local, systemd support for it was dropped.
* Tue Aug  4 2020 werner@suse.de
- Update to version 84.87+git20200804.d7fb210:
  * bashrc: fix bash: -s: command not found
* Tue Aug  4 2020 werner@suse.de
- Update to version 84.87+git20200804.00680c3:
  * Add proper quoting to last change
  * add screen.xterm-256color to DIR_COLORS
* Wed Jul  8 2020 ro@suse.de
- Update to version 84.87+git20200708.f5e90d7:
  * check for Packages.db and use this instead of Packages
    (boo#1171762)
  * Add also support for /usr/etc/profile.d for tcsh
  * Do add some support for /usr/etc/profile.d
* Tue Jun 16 2020 Dominique Leuenberger <dimstar@opensuse.org>
- Properly adjust usr/bin/service to look for legacy-action
  initscripts in %%{_libexecdir}/initscripts/legacy-action, no
  matter what the value of %%{_libexecdir} is (planned to change
  from /usr/lib to /usr/libexec)
* Wed May 13 2020 Ludwig Nussel <lnussel@suse.de>
- move shell aliases back to main package. They don't cost anything
  and it's just too annoying to not have them
* Thu May  7 2020 lnussel@suse.de
- Update to version 84.87+git20200507.e2243a4:
  * handle non-existing /etc/nsswitch.conf
  * set SYSTEMD_OFFLINE=1 if there's no systemd
  * Better support of Midnight Commander (bsc#1170527)
  * improve sysconf_addword: remove/cleanup spaces while adding/removing flags/modules
* Thu May  7 2020 werner@suse.de
- Better support of Midnight Commander (bsc#1170527)
* Tue Mar 31 2020 Michal Suchanek <msuchanek@suse.com>
- Require xz (boo#1162581).
* Tue Mar 24 2020 lnussel@suse.de
- Update to version 84.87+git20200312.411a96b:
  * get_kernel_version: support xz compressed kernel (boo#1162581).
* Mon Feb 24 2020 kukuk@suse.com
- Update to version 84.87+git20200224.7105b32:
  * Add usrfiles for protocols and rpc, too
* Mon Feb 24 2020 ro@suse.com
- Update to version 84.87+git20200224.bb11f02:
  * change feedback url from http://www.suse.de/feedback to
    https://github.com/openSUSE/aaa_base/issues
  * added "-h"/"--help" to "old" command (from Bernhard Lang)
* Fri Feb  7 2020 ro@suse.com
- Update to version 84.87+git20200207.27e2c61:
  * change rp_filter to 2 to follow the current default (bsc#1160735)
* Thu Feb  6 2020 ro@suse.com
- Update to version 84.87+git20200206.ed897a1:
  * get_kernel_version: fix for current kernel on s390x (from azouhr)
* Thu Feb  6 2020 kukuk@suse.com
- Update to version 84.87+git20200206.8d74b0b:
  * Fix services entry in /etc/nsswitch.conf [bsc#1162916]
- Make sure glibc is recent enough else nsswitch.conf update
  will fail
* Tue Jan 28 2020 kukuk@suse.com
- Adjust Requires/Requires(pre)/Requires(post)
- Update to version 84.87+git20200128.8a17290:
  * Move chkconfig to insserv-compat, as most functionality isn't supported anymore since we have different solutions with systemd.
  * Remove /usr/bin/mkinfodir, not used anywhere anymore
* Thu Jan 16 2020 ro@suse.com
- Update to version 84.87+git20200116.59482ba:
  * drop dev.cdrom.autoclose = 0 from sysctl config (bsc#1160970)
  * Call binaries in /usr only, /bin is legacy
* Wed Jan  8 2020 ro@suse.com
- Update to version 84.87+git20200108.0da43d3:
  * generalize testing for JVMs when creating the java path
    to support sapjvm and others (boo#1157794)
* Fri Dec  6 2019 kukuk@suse.com
- Update to version 84.87+git20191206.1cb88e3:
  * Add support for lesskey.bin in /usr/etc
  * Do last change also for tcsh
  * Not all XTerm based emulators do have an terminfo entry
* Wed Nov 20 2019 ro@suse.com
- Update to version 84.87+git20191120.98f1524:
  * merged PR 65
  * dash fixes
  * handle /usr/etc/login.defs for wsl
* Thu Oct 17 2019 werner@suse.de
- Update to version 84.87+git20191017.bf0a315:
  * Use short TERM name rxvt for rxvt-unicode and rxvt-unicode-256-color
* Thu Oct 17 2019 werner@suse.de
- Update to version 84.87+git20191017.14003c1:
  * Use official key binding functions in inputrc
    that is replace up-history with previous-history, down-history with
    next-history and backward-delete-word with backward-kill-word
    (bsc#1084934).  Add some missed key escape sequences for urxvt-unicode
    terminal as well (boo#1007715).
* Wed Oct 16 2019 ro@suse.com
- Update to version 84.87+git20191016.80d1420:
  * backup-sysconfig: fall back top cpio if tar is not available
    (bsc#1089299)
  * backup-rpmdb: check if rpm database is okay before backup to
    avoid overwriting good backups with corrupt ones (bsc#1079861)
  * service: check if there is a second argument before using it
    (bsc#1051143)
* Mon Oct 14 2019 ro@suse.com
- Update to version 84.87+git20191014.52dc403:
  * also add color alias for ip command, jira#sle-9880, bsc#1153943
* Thu Oct 10 2019 ro@suse.com
- Update to version 84.87+git20191010.b20083a:
  * check if variables can be set before modifying them
    to avoid warnings on login with a restricted shell
    (bsc#1138869)
* Wed Oct  9 2019 ro@suse.com
- Update to version 84.87+git20191009.4c2bd8e:
  * Add s390x compressed kernel support (bsc#1151023)
  * Fix LC_NAME and LC_ADDRESS in sh.ssh
  * fix string test to arithmetic test in /etc/profile.d/wsl.sh
* Thu Aug 22 2019 ro@suse.com
- Update to version 84.87+git20190822.82a17f1:
  * add sysctl.d/51-network.conf to tighten network security a bit
    see also (boo#1146866) (jira#SLE-9132)
* Thu Jul 25 2019 Fabian Vogt <fvogt@suse.com>
- Drop /bin/login requirement
* Thu Jul 18 2019 ro@suse.com
- Update to version 84.87+git20190718.ce933cb:
  * Make systemd detection cgroup oblivious (bsc#1140647)
* Wed Jun 12 2019 Dirk Mueller <dmueller@suse.com>
- stop using insecure protocols in _service file
* Thu Apr 18 2019 kukuk@suse.com
- Update to version 84.87+git20190418.d83e9d6:
  * convert_sysctl isn't needed anymore
* Thu Apr 18 2019 kukuk@suse.com
- Update to version 84.87+git20190418.f488c70:
  * Remove sysconfig/sysctl to sysctl.conf merge, there is no active
    distribution anymore from which we support an update with this.
* Thu Apr 18 2019 kukuk@suse.com
- Update to version 84.87+git20190418.155e7f0:
  * Remove sysconfig/cron to tmpfiles, we don't support upgrade from
    such old distributions to Factory anymore.
  * /etc/sysconfig/boot and /etc/sysconfig/shutdown don't exist anymore,
    no need to remove single variables from it.
  * Remove obsolete code for /etc/psdevtab and YaST
* Thu Apr 18 2019 kukuk@suse.de
- Remove over 12 year old compat provides
- Remove BuildRequires for net-tools, the code was removed and this
  package does not contain the wanted tool anymore
- Replace net-tools with successors in Recommends
* Thu Apr 18 2019 kukuk@suse.com
- Update to version 84.87+git20190418.a543e8e:
  * Remove rc.splash and rc.status, now part of insserv-compat [bsc#1132738]
* Fri Apr  5 2019 ro@suse.com
- Update to version 84.87+git20190404.8684de3:
  * Add two Scheme/LISP based shells to /etc/shells
  * /etc/profile does not work in AppArmor-confined containers (bsc#1096191)
* Thu Mar  7 2019 ro@suse.de
- Update to version 84.87+git20190307.00d332a:
  * update logic for JRE_HOME env variable (bsc#1128246)
* Wed Jan  9 2019 opensuse-packaging@opensuse.org
- Update to version 84.87+git20190109.b66cf03:
  * Restore old position of ssh/sudo source of profile
    for bug bsc#1118364 but hopefully do not reintroduce
    bug boo#1088524
* Mon Dec 10 2018 werner@suse.de
- Update to version 84.87+git20181210.841bf8f:
  * Set HISTTIMEFORMAT and HISTCONTROL only if unset (boo#1112653)
* Tue Nov 13 2018 ro@suse.de
- Update to version 84.87+git20181113.08d4125:
  * Sync x-genesis-rom extensions with freedesktop DB
  * test for /applications before adding data dir
    (bsc#1095969)
  * Clean up the no_proxy value: not all clients ignore spaces
    (bsc#1089796)
  * Add option --version to /sbin/service
* Wed Nov  7 2018 opensuse-packaging@opensuse.org
- Update to version 84.87+git20181107.f39a8d1:
  * Readline: Do not miss common mappings for vi
  * Readline: Use overwrite-mode on Insert key
  * Avoid `ls' command in alljava shell scriptlets
  * bashrc: Change =~ test to globs. Fixes mkshrc.
  * Update README (#55)
* Mon Apr  9 2018 werner@suse.de
- Update to version 84.87+git20180409.04c9dae:
  * In bash.bashrc move ssh/sudo source of profile to avoid removing
    the `is' variable before last use (boo#1088524).
  * Avoid the shell code checker stumble over `function' keys word
    in ls.bash (git#54).
* Thu Feb 22 2018 fvogt@suse.com
- Use %%license (boo#1082318)
* Thu Feb  8 2018 opensuse-packaging@opensuse.org
- Update to version 84.87+git20180208.8eeab90:
  * Don't call fillup for removed sysconfig.news
  * Adjust path for script converting sysctl config
  * For ksh use builtin keyword 'function' to make sure that the
    keyword 'typeset' really set the variable IFS to be local within
    the function _ls.
* Mon Feb  5 2018 kukuk@suse.de
- Update to version 84.87+git20180205.2d2832f:
  * Move /lib/aaa_base/convert_sysctl to /usr/lib/base-scripts/convert_sysctl
    to cleanup filesystem.
  * Don't create /etc/init.d/{boot.local,after.local,halt.local} in
    aaa_base.pre section.
  * Remove dead code from pre/post install sections.
* Mon Feb  5 2018 kukuk@suse.de
- Add /var/adm/backup subdirectories to aaa_base-extras, they are
  only needed by this package.
* Sun Feb  4 2018 kukuk@suse.de
- Update to version 84.87+git20180204.875cba8:
  * Move sysconfig.backup into extra subpackage, where all the
    scripts using it are, too.
  * Create systemd timer for the cron.daily scripts for backup-rpmdb,
    backup-sysconfig and check-battery. Move scripts to
    /usr/lib/base-scripts.
  * Remove suse.de-cron-local. If somebody really still has a
    /root/cron.daily.local file, he can move it to /etc/cron.daily.
  * Don't modify data in root's home directory
  * Don't create userdel.local, this isn't in use since many years
* Tue Jan 30 2018 kukuk@suse.de
- Update to version 84.87+git20180130.ae1f262:
  * Really remove /usr/sbin/Check, obsolete since 8 years
  * Remove ChangeSymlinks, 90%% are obsolete, the rest is dangerous
  * Remove 14 year old outdated documentation and dummy scripts for
    Java
* Tue Jan 30 2018 kukuk@suse.de
- Update to version 84.87+git20180130.36ea161:
  * Remove obsolete/outdated manual pages (route.conf.5,init.d.7,
    quick_halt.8)
* Tue Dec  5 2017 kukuk@suse.de
- Cleanup PreReq and move some parts to Requires(post), so that
  we can deinstall them if we no longer need them
* Fri Dec  1 2017 opensuse-packaging@opensuse.org
- Update to version 84.87+git20171201.65000be:
  * Revert changes on sysconfig language and make lang.(c)sh
    to use sysconfig language as fallback or better use
    locale.conf as default. See discussion in bsc#1069971
    and FATE#319454 as well
* Thu Nov 30 2017 opensuse-packaging@opensuse.org
- Update to version 84.87+git20171130.974ac5c:
  * Better parsing of sh variable settings in lang.csh
* Wed Nov 29 2017 opensuse-packaging@opensuse.org
- Update to version 84.87+git20171129.a45b936:
  * Remove RC_* variables from language sysconf template
    (bsc#1069971 as well as FATE#319454)
* Tue Nov 28 2017 opensuse-packaging@opensuse.org
- Update to version 84.87+git20171128.945b960:
  * lang.(c)sh: catch if ROOT_USES_LANG becomes not set
* Tue Nov 28 2017 opensuse-packaging@opensuse.org
- Update to version 84.87+git20171128.aa232d3:
  * Add wsl specific code to profile.d/wsl.csh
  * move wsl specific code from profile into profile.d/wsl.sh
  * Remove obsolete "make package"
* Tue Nov 28 2017 opensuse-packaging@opensuse.org
- Update to version 84.87+git20171128.a6752e8:
  * lang.(c)sh: handle locale.conf if sysconfig does not
* Tue Nov 28 2017 werner@suse.de
- lang.(c)sh: handle locale.conf if sysconfig does not provide
  default locale (bsc#1069971, FATE#319454)
* Tue Nov 28 2017 lnussel@suse.de
- Update to version 84.87+git20171128.17ae554:
  * Check for /proc/version before using it
  * Remove legacy code for /proc/iSeries
  * Move fillup-templates to /usr/share (boo#1069468)
* Mon Nov 27 2017 dimstar@opensuse.org
- Fix installation of fillup-templates.
* Thu Nov 23 2017 rbrown@suse.com
- Replace references to /var/adm/fillup-templates with new
  %%_fillupdir macro (boo#1069468)
* Mon Nov 20 2017 lnussel@suse.de
- use TW versioning, 13.2 is misleading
- Update to version 84.87+git20171120.d36b8b1:
  * Fix double sourcing of /etc/bash_completion.d
  * create wsl.sh in /etc/profile.d to set umask in WSL
  * Add support for /usr/bin/fish (boo#1068840)
  * Get mixed use case of service wrapper script straight (bsc#1040613)
* Wed Aug 30 2017 kukuk@suse.de
- Update to version 13.2+git20170828.8f12a9e:
  * profile: don't override PATH in WSL
  * Remove passwd, group and shadow files. Remove %%ghost entry for
    /run/utmp, /var/log/wtmp and /var/log/btmp, systemd is taking
    care of them
  * Remove run/utmp, too.
* Sun Aug 20 2017 vuntz@opensuse.org
- Update to version 13.2+git20170814.cc9e34e:
  * Unset id in csh.cshrc instead of profile.csh (bsc#1049577)
  * Restore the is variable within /etc/profile
* Mon Jul 31 2017 lnussel@suse.de
- Update to version 13.2+git20170731.c10ca77:
  * Fix csh.cshrc as tcsh does not handle stderr
  * Do not set alias cwdcmd for experts (boo#1045889)
  * unset unused variables on profile files (bsc#1049577)
  * Deprecate DEFAULT_WM in sysconfig.windowmanager
* Mon Jun 19 2017 werner@suse.de
- Fix csh.cshrc as tcsh does not handle stderr messages within {}
  well (boo#1044876)
* Mon Jun 12 2017 werner@suse.de
- Fix copy+paste error in /etc/csh.login boo#1043560
* Fri Jun  2 2017 werner@suse.de
- Support changing PS1 even for mksh and user root (bsc#1036895)
* Mon May 15 2017 werner@suse.de
- Be aware that on s390/s390x the ttyS0 is misused
* Fri May 12 2017 werner@suse.de
- Reset extended screen TERM variables if no terminfo
- Better status line support even for tcsh
- Modernize /etc/ttytype as tset of ncurses use it
* Thu May  4 2017 werner@suse.de
- Off application keypad (keyboard transmit) mode
- Missed a meta prefix in new inputrs.keys
* Thu Apr 27 2017 werner@suse.de
- More 8bit key escape control sequences for XTerm
- Do not set INPUTRC as readline does know personal as well as system
  inputrc also make /etc/inputrc do set know sequences for both vi
  line editing modes as well as for emacs line editing mode.
- Do remove patch aaa_base-13.2+git20170308.c0ecf2e.dif not
  only from package but also from spec file
* Tue Apr 25 2017 lnussel@suse.de
- Update to version 13.2+git20170425.47e703a:
  * Add Enlightenment to the list of windowmanagers
  * Add a number of audio/video formats to be colorized
  * Revert "Avoid NAT on Bridges. Bridges are L2 devices, really."
  * aaa_base.pre: drop some system users from aaa_base and create them in the respective packages: bin,daemon,news,uucp,games,man
  * Remove /var/log/faillog, there no application using this left [bsc#980484]
  * Remove users and groups sys, mail, lp, wwwrun, ftp and nobody
* Wed Mar  8 2017 werner@suse.de
- Make lang.csh work again (bsc#1025673)
* Mon Mar  6 2017 ro@suse.de
- Update to version 13.2+git20170306.3deb627:
  * aaa_base.pre: drop some system users from aaa_base and create
    them in the respective packages: bin,daemon,news,uucp,games,man
* Thu Sep 15 2016 ro@suse.de
- Update to version 13.2+git20160915.106a00d:
  * enhance comment for NO_PROXY variable (bsc#990254)
  * Fix spelling of SUSE (skipped copyright statements - they need more thoughts)
  * fix regression introduced by fix for bnc#971567 (bnc#996442)
* Wed Aug 17 2016 werner@suse.de
- Correct logic error in usage of variable restricted (boo#994111)
- enhance comment for NO_PROXY variable (bsc#990254)
* Sat Aug  6 2016 ro@suse.de
- Update to version 13.2+git20160807.7f4c8c4:
  * switch IPv6 privacy extensions (use_tempaddr) back to 1
  * history see bsc#678066,bsc#752842,bsc#988023,bsc#990838
* Thu Aug  4 2016 werner@suse.de
- Do not use the = sign for setenv in /etc/profile.d/lang.csh
* Mon Aug  1 2016 werner@suse.de
- Follow the bash manual page that is respect --norc and --noprofile
* Thu Jun  9 2016 lnussel@suse.de
- Update to version 13.2+git20160609.bf76b13:
  * Mark scripts /etc/init.d/{boot.,after-,halt.}local as deprecated
* Wed Jun  1 2016 werner@suse.de
- lang.sh, lang.csh: if GDM_LANG equals system LANG then use system defaults
* Mon May 30 2016 opensuse-packaging@opensuse.org
- Update to version 13.2+git20160530.bd5210c:
  + Let the ~/.i18n values parsed as well if GDM_LANG is set (boo#958295)
  + Remove spurious assignment to unknown variable term from /etc/inputrc
  + chkconfig: return 1 trying to list unknown service (bnc#971567)
  + chckconfig: add --no-systemctl option
  + fix typo in last patch (no-systemctl support for chkconfig)
  + lang.sh, lang.csh: allow GDM to override locale
  + There is no kde4 anymore
  + Removed '/usr/bin/X11' from PATH (boo #982185)
* Tue Apr 26 2016 ro@suse.com
- fix typo in last patch (no-systemctl support for chkconfig)
* Fri Apr  8 2016 ro@suse.com
- chckconfig: add --no-systemctl option
* Thu Apr  7 2016 ro@suse.com
- chkconfig: return 1 trying to list unknown service (bnc#971567)
- Merge pull request #26 from andreas-schwab/master
- Remove spurious assignment to unknown variable term from /etc/inputrc
* Thu Feb 25 2016 werner@suse.de
- Let the ~/.i18n values parsed as well if GDM_LANG is set (boo#567324)
* Mon Dec 21 2015 lnussel@suse.de
- Update to version 13.2+git20151221.244f2a3:
  + drop old dns6 hack migration from 2002
  + remove more dropped variables
  + make chkconfig -a/-d work (bsc#926539)
  + avoid recursion if systemd call chkconfig back for sysv units
  + fix non-working line breaks
- make _service generate .changes
* Wed Dec  2 2015 werner@suse.de
- Replace UNICODE double dash with simple ASCII single dash (boo#954909)
* Tue Nov 24 2015 werner@suse.de
- Use the `+' for find's -exec option as this also respects white
  spaces in files names but is more like xargs.  Respect status
  of screen sessions.
* Tue Oct 27 2015 ro@suse.com
- suse.de-backup-rc.config: trigger also if only files changed
  that have spaces in their name (bnc#915259)
* Tue Oct 27 2015 ro@suse.com
- sysconf_addword: do not insert spaces at start of string (bnc#932456)
* Tue Oct 27 2015 ro@suse.com
- Merge pull request #19 from super7ramp/cleaning-references-to-suseconfig
  - drop references to sysconfig/suseconfig
  - drop SCANNER_TYPE variable
* Thu Jun 25 2015 ro@suse.com
- Merge pull request #25 from ptesarik/master
- Enable SysRq dump by default
- Revert "fix /etc/init.d/foo status return code (bnc#931388)"
- Merge pull request #23 from bmwiedemann/master
- fix /etc/init.d/foo status return code (bnc#931388)
* Tue Apr 28 2015 ro@suse.com
- xdg-environment: reduce list in /opt/* to gnome,kde4,kde3 (bnc#910904)
* Fri Apr 24 2015 ro@suse.com
- add SOCKS5_SERVER and socks_proxy to proxy settings (bnc#928398)
- Simplify version check
* Mon Mar  9 2015 werner@suse.de
- Handle also command lines starting with the env command
  as this is used by gnome xsessions (bsc#921172)
* Wed Feb 11 2015 werner@suse.de
- Correct the boolean in /etc/profile.d/lang.sh
* Wed Feb 11 2015 werner@suse.de
- Even if GDM has done language setup the personal ~/.i18n should
  be sourced (boo#567324)
* Mon Jan 26 2015 werner@suse.de
- Remove the official patch for fate#314974 as now part of systemd
- Merge pull request #21 from arvidjaar/bnc/907873
* Fri Dec  5 2014 UTC arvidjaar@gmail.com
- Avoid sourcing /etc/bash_completion.d twice
* Wed Nov 26 2014 aj@suse.de
- Fix spelling of SUSE
* Wed Oct 29 2014 werner@suse.de
- Add the official patch for Fate#314974 (bnc#903009)
* Thu Sep 11 2014 ro@suse.de
- adding more info to chkconfig list mode output for systemd (bnc#863781)
* Thu Sep 11 2014 lnussel@suse.de
- remove no longer supported sysconfig settings (bnc#721682)
- remove /etc/mailcap (bnc#856725, bnc#842938)
- add Makefile target to update mimetypes
* Mon Sep  8 2014 lnussel@suse.de
- update service man page
- always pass --full to systemctl (bnc#882918)
* Tue Aug 12 2014 lnussel@suse.de
- Muffle libGL error message when run under ssh (bnc#890189)
* Tue Jul 29 2014 ro@suse.de
- add inittab as ghost config
* Thu Jul 24 2014 werner@suse.de
- Add ls.zsh to file list
* Wed Jul 23 2014 werner@suse.de
- Avoid trouble with new ksh93v- 2014-06-25 and zsh shell code (bnc#888237)
* Mon Jul 21 2014 werner@suse.de
- Do not touch nor modify permissions if e.g. /root/.bash_history
  is a link to e.g. /dev/null (bnc#883260)
* Mon Jul 21 2014 werner@suse.de
- Avoid libGL error via ssh (bnc#869172)
* Thu Jul 17 2014 werner@suse.de
- In emacs the tcsh may used non-interactively (bnc#882579)
* Mon Jul 14 2014 ro@suse.com
- drop hint about PREVLEVEL from after.local comments (bnc#886176)
* Fri Jul 11 2014 ro@suse.com
- remove "text/js" from mime.types [bnc#812427]
* Wed Jul  2 2014 ro@suse.com
- drop re-creation of before.local and add a comment about not
  being supported if it had real content (bnc#869177)
- mark /etc/init.d/{boot,halt,after}.local as ghost (bnc#868416)
* Tue Jul  1 2014 lnussel@suse.de
- remove fate-314974.patch which was not accepted in git
* Wed Jun  4 2014 werner@suse.de
- Enable service script to return LSB status exit values (bnc#880103)
* Fri May  9 2014 ro@suse.de
- fix error message if zsh sources xdg-environment.sh if some pathes do not exist (bnc#875118)
* Wed Apr 16 2014 lnussel@suse.de
- remove mkinitrd script for mtab
* Mon Apr  7 2014 werner@suse.de
- For tcsh: be aware that sometimes strings in variables include a dash
* Mon Mar 10 2014 lnussel@suse.de
- move cron Recommends to -extras subpackage where the actual cron
  files are
- update COPYING file to silence rpmlint warning about outdated
  address
- adjust mktar script to new versioning scheme
- implement legacy actions (bnc#861124)
* Mon Mar  3 2014 thomas.blume@suse.com
- move tmp file removal parameters from cron to systemd (fate#314974)
  fate-314974.patch
* Thu Feb 27 2014 coolo@suse.com
- bump version to 13.2 and avoid tar updates
* Mon Feb 17 2014 werner@suse.de
- Avoid warning from grep if complete file is not found (bnc#864282)
* Mon Feb 17 2014 ro@suse.com
- remove etc/init.d/powerfail (bnc#864044)
* Fri Jan 31 2014 ro@suse.com
- drop sysconfig files: boot, clock, cron, shutdown as none of these are used anymore
* Wed Jan 29 2014 werner@suse.de
- Map the generic terminal type ibm327x to the terminal type dumb
* Wed Jan 29 2014 werner@suse.de
- Enable service script to reload systemd if required
* Mon Jan 27 2014 lnussel@suse.de
- print parse errors to stderr (bnc#860477)
* Fri Jan 24 2014 lnussel@suse.de
- handle targets in /sbin/service as well
- Check systemd service using LoadState (bnc#860083)
* Thu Jan 23 2014 werner@suse.de
- Avoid journal output as this may take time on pure journald systems (bnc#859360)
* Fri Jan 17 2014 werner@suse.de
- Do not load completions which depend on bash-completion package (bnc#856858)
* Tue Jan  7 2014 lnussel@suse.de
- make rcfoo usable for not enabled services (bnc#856986)
* Wed Dec 18 2013 werner@suse.de
- Use only bash and readline defaults for fallback completion (bnc#851908)
* Tue Dec 17 2013 lnussel@suse.de
- change mistakenly root:users group to root:root (bnc#843230)
* Fri Dec 13 2013 ro@suse.com
- Avoid NAT on Bridges. Bridges are L2 devices, really.
- Fix Default tag for RCCONFIG_BACKUP_DIR
* Mon Dec  9 2013 lnussel@suse.de
- remove {c,}sh.utf8 as testutf8 is a dummy anyways (bnc#849258)
- fix chkconfig --check (bnc#851374)
* Tue Nov 12 2013 ro@suse.com
- chkconfig: add option -L to only list enabled services (bnc#707823)
- updated comment in sysconfig.language for ROOT_USES_LANG (bnc#505417)
- tighten regexp of ignored files in chkconfig (bnc#828820)
- protect from reading home kshrc twice (bnc#848697)
* Wed Oct  2 2013 gber@opensuse.org
- Add support for mksh
- Do not use bashisms in PS1 for unknown shells
* Tue Oct  1 2013 mvyskocil@suse.cz
- Adds a minor fix - changes JRE_HOME only in a case it was not defined before (bnc#841284)
* Mon Sep 30 2013 werner@suse.de
- Use systemctl show to list the properties NeedDaemonReload, UnitFileState, and LoadState
  and then check fore daemon-reload, masked, and forbidden services (bnc#843123, FATE#313323)
* Fri Sep 27 2013 werner@suse.de
- Enable old boot scripts for systemd in rc.status if not already done (FATE#313323)
* Mon Aug 26 2013 aj@suse.com
- Fix last commit, rename the actual alias too.
* Fri Aug 23 2013 aj@suse.com
- Rename _ls alias to z_ls for zsh. In zsh strings that start with
  an underscore are reserved for completion. This fixes bnc#836067
* Wed Aug  7 2013 aj@suse.com
- avoid leaking kernel address information to userspace by using
  kernel.kptr_restrict=1 sysctl
- bash.bashrc: source vte.sh if existing (bnc#827248)
* Fri Jun 28 2013 lnussel@suse.de
- 'mountpoint' was moved to /usr
* Mon Jun 17 2013 coolo@suse.com
- move sysctl directories to filesystem rpm
* Mon May 27 2013 lnussel@suse.de
- move sysctl defaults to aaa_base (bnc#820443)
* Thu May 23 2013 werner@suse.de
- Add bash completion function to load completions dynamically (bnc#821411)
* Tue Apr 23 2013 werner@suse.de
- Require xz at build time (Who has removed xz from default?)
* Tue Apr 23 2013 werner@suse.de
- Personal bash completion and bash ls alias (bnc811030, bnc#799241)
* Thu Mar 28 2013 lnussel@suse.de
- also check /lib/systemd for compatibility (bnc#812291)
* Wed Mar 27 2013 lnussel@suse.de
- chkconfig: rh compatible check mode (bnc#811870)
* Wed Mar 27 2013 aj@suse.com
- Mark file  /lib/mkinitrd/scripts/boot-mtab.sh as exectuable (bnc#809842)
- Compress tarball with xz
* Mon Mar 25 2013 aj@suse.com
- Remove boot.localnet also from spec file
* Mon Mar 25 2013 aj@suse.com
- Update version number to 13.1
- Update to git head:
  * Remove boot.localnet
  * Revert "rc.status: allow to pass options to systemctl using SYSTEMCTL_OPTIONS"
    SYSTEMCTL_OPTIONS is now handled directly by systemctl.
* Wed Feb  6 2013 werner@suse.de
- Do not override /etc/adjtime if HWCLOCK is already gone (bnc#791485)
* Mon Feb  4 2013 werner@suse.de
- Avoid to stumble over missing /dev/stderr in boot script started
  by systemd (work around bnc#728774o but not solve it)
* Tue Jan 22 2013 lnussel@suse.de
- remove check whether systemd is running
* Sat Jan 19 2013 lnussel@suse.de
- call systemctl to enable/disable services (bnc#798510)
* Tue Jan  8 2013 werner@suse.de
- Let the bash check the winsize only if COLUMNS is exported (bnc#793536)
* Tue Jan  8 2013 werner@suse.de
- Also source environment for tcsh and bash if sudo is used
* Mon Jan  7 2013 ro@suse.com
- Merge pull request #1 from fcrozat/master
- rc.status: allow to pass options to systemctl using SYSTEMCTL_OPTIONS
* Tue Nov 20 2012 werner@suse.de
- Simplify and tighten the bash prompt
* Thu Nov 15 2012 lnussel@suse.de
- fix url to point to github
- change summary to say "openSUSE" (bnc#773245)
* Thu Nov 15 2012 coolo@suse.com
- remove boot.* again, new insserv shadows them
* Thu Nov 15 2012 dimstar@opensuse.org
- Add aaa_base-syntax-error.patch: Fix syntax error in rc.status.
* Tue Nov 13 2012 ro@suse.com
- merged last bits from gitorious:
  - from froh:
  - /etc/bash.bashrc: add prompt to the terminal "status line",
    which on most graphical terminals is the window title.
  - from fcrozat:
  - rc.status: output initscript status before systemd one.
  - rc.status: educate users on which systemctl command was started
  - rc.status: systemctl 195+ allows to not specify .service
* Tue Nov  6 2012 coolo@suse.com
- readd insserv for the remaining boot scripts
* Mon Nov  5 2012 coolo@suse.com
- readd some boot.* scripts that are required by insserv for not ported
  applications (they are empty though)
* Wed Oct 31 2012 werner@suse.de
- Enforce creation of /etc/adjtime even if no /etc/sysconfig/clock exists (bnc#779440)
* Thu Oct 25 2012 coolo@suse.de
- also move the file to /run
- generate utmp in /run not in /var/run
* Thu Oct 25 2012 coolo@suse.com
- /var/run/utmp should be packaged as /run/utmp
* Mon Oct 22 2012 werner@suse.de
- Ask terminal about status line in bash.bashrc
* Mon Oct 15 2012 aj@suse.de
- Update from git:
  * Remove /usr/lib/tmpfiles.d/loop.conf (bnc#784963).
* Fri Oct 12 2012 coolo@suse.com
- update from git:
  * remove all files not necessary for systemd
  * move files to /usr and leave symlinks around
- conflict with sysvinit
* Mon Oct  8 2012 aj@suse.de
- Update from git:
  * Fix typo in /usr/lib/tmpfiles.d/loop.conf
* Mon Oct  8 2012 coolo@suse.com
- update from git to get the latest change too
* Fri Oct  5 2012 werner@suse.de
- Try to resolve the bash completion problems with ls (bnc#725657)
* Thu Oct  4 2012 aj@suse.de
- Create loop devices via tmpfiles and not via /lib/udev/devices.
* Wed Sep 26 2012 aj@suse.de
- Fix linuxbase URLs to point to the current documentation
- Add README.packaging.txt.
* Tue Sep 25 2012 coolo@suse.com
- migrate to _service file to make it a bit more clear the .tar is
  not a random tar
* Thu Sep 20 2012 kukuk@suse.de
- SuSEconfig is finally gone [FATE#100011]
* Thu Sep 13 2012 coolo@suse.com
- explicitly buildrequire net-tools for /bin/hostname
* Tue Aug  7 2012 lnussel@suse.de
- honor $SYSTEMD_NO_WRAP again (bnc#774754)
* Tue Jul 31 2012 lnussel@suse.de
- fix service status for sysvscripts when booted with systemd (bnc#772028)
* Fri Jul 20 2012 jengelh@inai.de
- Add %%defattr to make files definitely owned by root
* Fri Jul 20 2012 werner@suse.de
- Redirect test if blogd is running otherwise it will never be done
* Fri Jul 13 2012 vuntz@opensuse.org
- Fix /etc/bash.bashrc for bash-completion again: the previous fix
  was not working for non-login shells, so directly source
  /etc/profile.d/bash_completion.sh from /etc/bash.bashrc
  (bnc#764288).
* Tue Jul 10 2012 werner@suse.de
- Also remove an possible but old /var/log/blogd.pid before initial
  start of blogd (bnc#763944)
* Wed Jul  4 2012 lnussel@suse.de
- support beeing called as rc* symlink wrapper (bnc#769902)
- use systemctl instead of loop for --status-all (bnc#769902)
* Sun Jul  1 2012 dimstar@opensuse.org
- Add aaa_base-bnc756012.patch: unset ftp_proxy is not the same
  as ftp_proxy="", which can drip libproxy over. (bnc#756012)
* Fri Jun 29 2012 lnussel@suse.de
- move environment settings for malloc checking to separate
  subpackage for easier handling of the feature via patterns
* Mon Jun 25 2012 vuntz@opensuse.org
- Change /etc/bash.bashrc to work with recent versions of
  bash-completion, that put files in /usr/share/bash-completion.
* Fri Jun 22 2012 werner@suse.de
- Move boot.msg away if writable before initial start of blogd (bnc#763944)
* Thu Jun 21 2012 lnussel@suse.de
- fix boot.localfs for new mount output (bnc#766035)
- use /run, preserve /run/no_blogd for shutdown
* Fri May 25 2012 werner@suse.de
- Drop HWCOCK option flag in favour of the adjtime file
* Wed May 23 2012 vuntz@opensuse.org
- Bump version to 12.2, to prepare for next version of openSUSE.
* Fri Apr 20 2012 lnussel@suse.de
- fix return values of systemd detection
* Mon Apr 16 2012 mvyskocil@suse.cz
- remove mingetty dependency from aaa_base as it's needed by sysvinit
* Mon Mar 19 2012 ro@suse.com
- remove bin from mime.types for application/x-stuffit (bnc#743741)
* Mon Mar 19 2012 ro@suse.com
- rc.status: also allow to specify files as /etc/rc.d/foo
  (bnc#734476)
* Mon Mar 19 2012 ro@suse.com
- update mime.types file (merged old file with upstream) (see bnc#720464)
- add primitive script to merge mime.types file
* Thu Mar 15 2012 werner@suse.de
- Try to fix several bash completion bug caused by fix for bug #725657
* Tue Mar 13 2012 werner@suse.de
- Oops add missed double quote (bnc#752061)
* Fri Mar  9 2012 werner@suse.de
- Yet an other bash completion problem worked around
* Fri Mar  9 2012 werner@suse.de
- Add old request from gitorious
* Wed Mar  7 2012 aj@suse.de
- Add patch from rjschwei@suse.com:
  * ln binary has been moved to user tree. This addresses bnc #747322
  comment 11
* Tue Mar  6 2012 aj@suse.de
- Add patch from rjschwei@suse.com:
  * The initviocons binary moved from /bin to /usr/bin as part of
    the UsrMerge project.
* Tue Mar  6 2012 werner@suse.de
- Fix some bash completion problems (bnc#738501)
* Fri Feb 10 2012 lnussel@suse.de
- remove requirement on systemd to avoid cycles.
  /bin/systemd-tmpfiles is only needed by boot.cleanup when actually
  booting the system using sysv.
* Thu Feb  9 2012 ro@suse.com
- chkconfig: bypass initscript enable/disable script if service
  shadowed by systemd
* Fri Jan 27 2012 seife+obs@b1-systems.com
- fix alljava.sh bug introduced with last commit (bnc#722252)
* Fri Jan 20 2012 lnussel@suse.de
- Make alljava.(c)sh friendly to third-party JVMs (bnc#722252)
* Mon Jan 16 2012 rhafer@suse.de
- Added "application/json" mimetype to /etc/mime.types (bnc#741546)
* Mon Jan  9 2012 werner@suse.de
- Strip boot. also from rc symbolic links (bnc#739217)
* Fri Dec 23 2011 werner@suse.de
- Use since_epoch of rtc0 and not raw system time
- If CMSO clock is in synch but nevertheless off by more than
* Sat Dec 10 2011 lars@samba.org
- Add --listmodules option to SuSEconfig; (bnc#736086).
* Thu Nov 24 2011 aj@suse.de
- Fix spec file for last change.
* Wed Nov 23 2011 aj@suse.de
- Remove tmpdirs.d handling, use tmpfiles now
* Tue Nov 22 2011 ro@suse.de
- random seed start script: use pool_size from kernel,
  not the old 512 bytes (bnc#730736)
* Thu Nov 10 2011 fcrozat@suse.com
- Ensure /sbin/service is not clearing SYSTEMD_NO_WRAP
* Mon Nov  7 2011 dmueller@suse.de
- add color aliases for grep variants
* Wed Nov  2 2011 lnussel@suse.de
- replace mtab with symlink in initrd already (bnc#727758)
- introduce SYSTEMD_NO_WRAP (bnc#727445)
* Thu Oct 27 2011 ro@suse.com
- rc.status: only push standard options start/stop/restart/..
  to systemd, otherwise use the normal init script
* Tue Oct 25 2011 werner@suse.de
- Enable direxpand patch of the bash (bnc#725657)
* Fri Oct 21 2011 werner@suse.de
- Add comment about systemd and runlevel in /etc/inittab (bnc#725138)
* Fri Oct 21 2011 pth@suse.de
- Change most aliases in ls.bash to shell functions.
* Wed Oct 19 2011 werner@suse.de
- Make completion for sudo smart (bnc#724522)
* Fri Oct 14 2011 lnussel@suse.de
- mount /media as tmpfs
- resolve symlink for rcXX -> XX.service sytemd magic
* Fri Sep 30 2011 uli@suse.com
- cross-build fix: use %%__cc macro
* Sat Sep 17 2011 jengelh@medozas.de
- Remove redundant tags/sections from specfile
- Use %%_smp_mflags for parallel build
* Fri Sep 16 2011 werner@suse.de
- Handle boot.* initcripts correctly under systemd
* Thu Sep 15 2011 werner@suse.de
- bash completion: add a space for unique results (bnc#717934)
* Fri Aug 19 2011 fcrozat@suse.com
- check if systemd is running and notify user
* Thu Aug 18 2011 ro@suse.com
- fix last change
- update FSF address in skeleton file
* Tue Aug  2 2011 werner@suse.de
- Correct check for COLD_BOOT in halt script (bnc#709825)
* Tue Aug  2 2011 ro@suse.com
- remove more occurrences of boot.loadmodules now in mkinitrd package
* Tue Aug  2 2011 ro@suse.com
- remove etc/sysconfig/kernel, lives now in mkinitrd package
* Tue Aug  2 2011 ro@suse.com
- sbin/service: skip *.disabled for --status-all (bnc#690282)
* Tue Jul 26 2011 werner@suse.de
- Add support for clicfs
* Mon Jul 18 2011 werner@suse.de
- Better support of quoted file and directory names (bnc#706075)
* Thu Jul 14 2011 werner@suse.de
- Do not use CDPATH for local paths (bnc#703682)
* Wed Jul  6 2011 werner@suse.de
- Let various bourne shell source their own local rc file (bnc#703855)
- Handle CDPATH for bash command completion for every case (bnc#703682)
* Thu Jun 30 2011 aj@suse.de
- Bump version number
- do not install /root/.exrc anymore, it's obsolete.
* Tue Jun 14 2011 lnussel@suse.de
- mount /run without noexec (bnc#699799)
* Tue May 31 2011 werner@suse.de
- Enable container check for devtmpfs (bnc#696026) to be able
  to use a static /dev within the container
* Tue May 31 2011 lnussel@suse.de
- add back telinit q call
- fix group and mode of /var/lock
* Mon May 30 2011 idonmez@novell.com
- Set DEFAULT_WM to kde-plasma, bnc#687781
* Fri May 27 2011 lnussel@suse.de
- boot.cleanup cleanup
- make /var/lock tmpfs too
- bind mount /var/run in boot.localfs
- drop /etc/sysconfig/sysctl (fate#312343)
* Tue May 24 2011 lnussel@suse.de
- dont' enable boot.ldconfig by default
- don't enable boot.clock by default (fate#312407)
- remove reference to runlevel 4 from skeleton.compat
* Mon May 23 2011 lnussel@suse.de
- drop /etc/sysconfig/sysctl.conf (fate#312343)
* Wed May 18 2011 lnussel@suse.de
- bind mount /run on /var/run
* Wed May 18 2011 lnussel@suse.de
- fix wrong logic in %%post
* Wed May 18 2011 werner@suse.de
- Avoid tput command if TERM variable is not set.
* Wed May 18 2011 lnussel@suse.de
- start boot.proc as soon as possible
- don't wait for bind mounts (bnc#690871)
* Tue May 17 2011 lnussel@suse.de
- create loop devices in %%post (bnc#661715)
- don't mount /sys/fs/cgroup/systemd as it makes programs think
  systemd is in use
* Mon May  9 2011 ro@novell.com
- rc.status: in rc_wait test for existance of binary
* Mon May  9 2011 ro@novell.com
- add COPYING file as requested
* Fri May  6 2011 werner@suse.de
- Avoid further trouble of the plusdir complete option of the bash
  (bug #681687)
* Thu May  5 2011 werner@suse.de
- Do not cause the bash to expand if dir path starts with ~ for the
  HOME of the user (disable plusdir option for this) (bnc#691883)
* Tue Apr 26 2011 werner@suse.de
- Mount memory based file systems found in /etc/fstab (bnc#675542)
* Thu Apr 21 2011 werner@suse.de
- Start blogd only once at boot
* Fri Apr 15 2011 werner@suse.de
- Fix for bnc#686186 and change for fate#309226
* Tue Apr  5 2011 ro@novell.com
- boot.cleanup: when cleaning var/run, try to symlink /var/run to /run
* Wed Mar 30 2011 ro@novell.com
- mount /run if needed
- /etc/init.d/boot: mount /run as tmpfs if not there yet
* Mon Mar 21 2011 lnussel@suse.de
- call osc ci after pushing changes
- make it work with older git
* Mon Mar 21 2011 werner@suse.de
- Avoid waiting on bind mounts in boot.localfs
- Be aware in refresh_initrd that modules used in initrd may use
  options in the /etc/modprobe.d/ files
* Thu Mar 17 2011 lnussel@suse.de
- add scripts to make tarball
* Fri Mar 11 2011 werner@suse.de
- Avoid to trap into execute escapes (bnc#678827)
* Wed Mar  9 2011 lnussel@suse.de
- sources are maintained in git now. Adopt package accordingly.
* Mon Mar  7 2011 ro@suse.de
- bump version to 11.5
* Mon Feb 28 2011 werner@suse.de
- Add missed ESC for screen escape sequences
* Tue Feb 22 2011 werner@suse.de
- Work around colon as breaking character in tab completion
- Allow arguments of command done by sudo to complete (bnc#673663)
* Fri Feb 18 2011 werner@suse.de
- Fix minimal support for the old fashion rc service links
* Thu Feb 17 2011 werner@suse.de
- Tag interactive boot scripts as interactive as systemd uses it
* Mon Feb 14 2011 lnussel@suse.de
- don't time out waiting for tmpfs (bnc#671468)
- make malloc checking configurable
* Fri Feb 11 2011 werner@suse.de
- Add minimal support for the old fashion way to handle services
  even with systemd
* Tue Feb  8 2011 werner@suse.de
- Use new rvmtab in boot.localfs if available
* Thu Feb  3 2011 werner@suse.de
- Redo fix for $HOME/.kshrc readed twice (bnc#560152)
* Wed Feb  2 2011 gber@opensuse.org
- changed LXDE to lxde in sysconfig.windowmanager
* Tue Feb  1 2011 werner@suse.de
- For plain bourne shells use `command -v' instead of `type -p'
- Avoid world writable temporary reverse mtab (bnc#665479, CVE-2011-0461)
* Tue Feb  1 2011 werner@suse.de
- Also do the job for tcsh users
- Be backward compatible to support existing sysconfig files
- Fix for bnc#668180: redirect stderr of pidofproc to /dev/null
* Sat Jan 29 2011 gber@opensuse.org
- changed /etc/profile.d/profile.sh so it treats DEFAULT_WM as the
  basename of the session file and parses the value of Exec into
  WINDOWMANAGER (bnc#667408)
- adopted the possible values of DEFAULT_WM to use the basename of
  the session file (bnc#667408)
* Fri Jan 28 2011 ro@suse.de
- fix typo in SuSEconfig manpage (bnc#662695)
* Tue Jan 25 2011 lnussel@suse.de
- package /lib/udev/devices/loop* to allow on demand loading of the
  loop module (bnc#661715)
* Tue Jan 25 2011 lnussel@suse.de
- at boot make sure /etc/mtab is a symlink (bnc#665494) so
  util-linux doesn't need to do it in %%post
- don't wait for loop images to appear as block devices (bnc#666150)
* Wed Jan 19 2011 lnussel@suse.de
- net.ipv6.conf.all.use_tempaddr has no effect, need to use
  net.ipv6.conf.default.use_tempaddr (bnc#494958#c2)
- set default values in /etc/sysconfig/sysctl to empty and mark
  deprecated. No default behavior change as kernel defaults actually
  match.
* Tue Jan 18 2011 bwiedemann@novell.com
- fix loop module not loaded with /etc/mtab symlink (bnc#665092)
* Mon Jan 17 2011 aj@suse.de
- Fix kernel value of IPv6 privacy in boot.ipconfig (bnc#664550).
* Sat Jan 15 2011 lnussel@suse.de
- fix mounting /dev/pts (bnc#664692)
* Wed Jan 12 2011 lnussel@suse.de
- rc.status: initialize terminal settings only once
- boot.cgroup: add init script to mount cgroups
- boot.localnet: remove useless use of cat and avoid ifup
- boot.localfs: don't update mtab if mtab is a link anyways
- boot.localfs: don't consider nofail mounts as missing
- boot: reorder and simplify mounting of file systems
* Tue Jan 11 2011 werner@suse.de
- Do not call `hostname -d' to avoid DNS lookup
* Tue Jan  4 2011 adrian@suse.de
- avoid trailing dot in HOSTNAME when no NIS domain is set
* Tue Dec 21 2010 werner@suse.de
- Test only for bit 64 (clock unsynchronized), if zero the kernel
  is within eleven minutes mode (Thanks goes to Rastislav David)
* Thu Dec 16 2010 werner@suse.de
- Touch /etc/init.d/after.local and /etc/init.d/before.local (bnc#659206)
* Wed Dec 15 2010 ro@suse.de
- boot.localfs: do not abort wait for udev just because
  /dev/.udev/queue does not exist (bnc#656028)
* Tue Dec  7 2010 werner@suse.de
- Work around broken network setups for login shells to get
  variable HOST set to nodename
- Do not use NIS/YP domainname but DNS domainman for HOSTNAME
* Tue Dec  7 2010 puzel@novell.com
- export GPG_TTY="`tty`" in /etc/bash.bashrc (bnc#619295)
* Thu Nov 18 2010 lnussel@suse.de
- own /var/log/wtmp, /var/run/utmp, /var/log/faillog and /var/log/btmp
* Wed Nov 17 2010 ro@suse.de
- fix typo (merge conflict overlooked)
* Wed Nov 17 2010 ro@suse.de
- fix postinstall to test for existence of /var/run/utmp
  before trying to chgrp
* Tue Nov 16 2010 aj@suse.de
- Remove get_kernel_version_fix_plus_in_kernel_string.patch after
  applying it to file directly.
* Tue Nov 16 2010 aj@suse.de
- Use group utmp for /var/run/utmp, btmp and lastlog (bnc#652877).
* Thu Nov 11 2010 werner@suse.de
- Do not set ENV in /etc/profile as well in /etc/csh.login (bnc#611966)
* Wed Nov 10 2010 ro@suse.de
- allow chkconfig to use different root filesystems (bnc#507382)
* Wed Nov 10 2010 ro@suse.de
- added service.8 man page from fedora (bnc#621286)
* Wed Nov 10 2010 werner@suse.de
- Make /usr/sbin/Check a bash script (bnc#626629)
* Wed Nov 10 2010 ro@suse.de
- keep /etc/mtab unchanged if it is a symlink (bnc#651555)
* Tue Nov  9 2010 lnussel@suse.de
- remove weird filelist generation code
* Tue Nov  9 2010 lnussel@suse.de
- remove /usr/sbin/Check
* Tue Nov  9 2010 lnussel@suse.de
- move chkstat calls to brp-permissions in brp-checks-suse
* Thu Nov  4 2010 lnussel@suse.de
- export ONLY_MODULE so modules can act differently when they are called
  specifically
* Wed Nov  3 2010 cristian.rodriguez@opensuse.org
- enable malloc debugging checks.
* Wed Nov  3 2010 werner@suse.de
- Do not remove /etc/adjtime but simply correct the third line
  for applications depending on CMOS time (bnc#650719)
* Thu Oct 21 2010 ro@suse.de
- abort if kernel has no devtmpfs, can not help here (bnc#648408)
* Tue Oct 19 2010 werner@suse.de
- Use refresh_initrd if TIMEZONE has changed (bnc#638185)
* Mon Sep 20 2010 werner@suse.de
- Add sudo completion bnc#639744
* Wed Sep 15 2010 werner@suse.de
- Fix for bnc#567951 - cshrc now allows xterm titles
- Fix for bnc#631454 - bash completion for regexpressions
- Fix for bnc#639392 - make pushd completion behaves like cd completion
* Wed Sep  8 2010 ro@suse.de
- add leading / to pre/post scripts (bnc#625763)
* Fri Sep  3 2010 trenn@novell.com
- Recognize "+" at the end of the kernel version correctly.
  From mmarek:
  Starting with 2.6.35, the kernel build by default appends a plus sign to
  the kernel version string when building in a git tree that is not in a clean
  tagged state.
* Fri Aug 27 2010 ro@suse.de
- switch SEND_OUTPUT_ON_NO_ERROR from yes to no in postinstall
  and only do that exactly once to switch the default (bnc#622203)
* Thu Aug 26 2010 ro@suse.de
- let boot.swap disable most swap partitions on shutdown
  so LVM and others can be shut down cleanly (bnc#631916)
* Wed Aug 25 2010 werner@suse.de
- Add a sysconfig option for enforcing blogd even with "fastboot"
  and/or "quiet" found on the kernel command line.
* Thu Aug 12 2010 dmueller@suse.de
- add a split provides for smooth upgrade
* Thu Jul 29 2010 ro@suse.de
- split off aaa_base extras subpackage with:
  - ls settings and aliases
  - bash completion
  - other generic shell aliases
  - quick_halt/poweroff/reboot script
  - some default cronjobs
- modified bash.bashrc and csh.cshrc to split out ls settings
- drop alias for dir: that one has its own binary for a while
- recommend aaa_base-extras from main package
* Tue Jul 27 2010 cristian.rodriguez@opensuse.org
- get_kernel_version : use O_CLOEXEC everywhere
* Fri Jul 16 2010 werner@suse.de
- Newer killproc sends only SIGTERM as required by LSB if -TERM is
  specified on the command line.  Use the default which is SIGTERM
  followed by SIGKILL if the timeout of 5 seconds is reached.
* Wed Jul 14 2010 mseben@novell.com
- change default value of cron sysconfig option
  SEND_OUTPUT_ON_NO_ERROR to "no" bnc#622203
* Mon Jul  5 2010 werner@suse.de
- Use alias shell builtin for ash and dash (bnc#619756)
* Thu Jun 17 2010 coolo@novell.com
- remove malloc-debug.* for final release
* Wed Jun 16 2010 ro@suse.de
- also skip /cgroup during unmount in boot.localfs
  (requested by kay)
* Tue Jun  8 2010 werner@suse.de
- Reflect name space change of former rush shell which know becomes
  pcksh, cpcksh, and rpcksh
* Wed Jun  2 2010 werner@suse.de
- Add support for the rush bourne shell (bnc#608727)
* Fri May 28 2010 werner@suse.de
- Implemenation of a workaround of missing console messages in
  blogd (bnc#593957) ... depends on package sysvinit-tools
* Wed May 19 2010 ro@suse.de
- drop chmod for /dev/shm from /etc/init.d/boot
  (workaround which is no longer needed and gives trouble now)
* Tue May 18 2010 werner@suse.de
- Avoid error on not set $TERM variable in csh login (bnc#560917)
* Tue May 18 2010 ro@suse.de
- set INPUTRC in csh similar to /etc/profile (bnc#560917)
* Tue May 18 2010 ro@suse.de
- add usbfs to tmpfs list in boot.localfs (bnc#569569)
  if "noauto" is changed to "defaults" in fstab for /proc/bus/usb
  then the fs is mounted at boot time (for some legacy software)
* Tue May 18 2010 ro@suse.de
- skip remount-rw for / if "readonlyroot" is specified on
  the boot commandline (bnc#445189)
* Tue May 18 2010 lars@linux-schulserver.de
- added smart_agetty manpage to fix bnc #342580
- fix self Provides/Obsoletes for aaa_skel
* Wed Apr 28 2010 ro@suse.de
- added /etc/tmpdirs.d for snippets to be called by boot.cleanup
  (shell scripts to recreate things in /tmp, /var/tmp, /var/run)
- move code from boot.cleanup to /etc/tmpdirs.d/01_aaa_base
  (all related to fate#303793)
* Tue Apr 27 2010 aj@suse.de
- Set version number to 11.3
* Tue Apr 27 2010 werner@suse.de
- Add screen control sequences to inputrc (bnc#598903)
* Thu Apr 15 2010 ro@suse.de
- boot.rootfsck: do not use /dev/shm/root as fallback but /dev/root
* Thu Apr 15 2010 ro@suse.de
- boot.localfs: update Should-Stop dependencies
* Thu Apr 15 2010 ro@suse.de
- removed /etc/rc.d.README as well
* Wed Apr 14 2010 werner@suse.de
- Use feature of pidof(1) of new sysvinit 2.88dsf
* Thu Apr  8 2010 ro@suse.de
- drop /sbin/init.d.README and /etc/init.d/README
  the manpage is "man 7 init.d"
* Mon Mar 29 2010 ro@suse.de
- boot.cleanup: do cleanup as well in shutdown case, faster
  than leaving it to the next boot and can speed up boot sequence
* Fri Mar 26 2010 sndirsch@suse.de
- add NO_KMS_IN_INITRD to sysconfig/kernel.
* Wed Mar 17 2010 werner@suse.de
- Add Forms Data Format (.fdf) for acroread and co (bnc#573202)
* Thu Mar 11 2010 ro@suse.de
- fix typo in boot.localfs (bnc#584090)
* Tue Mar  9 2010 lnussel@suse.de
- add "lock" group (bnc#552095, FATE#308360)
* Mon Mar  8 2010 ro@suse.de
- drop boot.sched
* Mon Mar  8 2010 ro@suse.de
- implemented more primitive status calls for boot.* scripts
* Mon Mar  8 2010 ro@suse.de
- implemented primitive status call for boot.rootfsck and
  boot.localfs
* Thu Mar  4 2010 ro@suse.de
- do not put ldconfig into background in recovery case (bnc#582597)
* Tue Mar  2 2010 werner@suse.de
- Add changes for dash and ksh from Guido Berhoerster
* Fri Feb 26 2010 ro@suse.de
- move remounting of /dev and /dev/shm to boot.localfs
  (bnc#583247)
* Thu Feb 25 2010 ro@suse.de
- add chmod for /dev/shm to be safe from udev
* Wed Feb 24 2010 pbaudis@suse.cz
- Fix $TIMEZONE description in /etc/sysconfig/clock (bnc#582292)
* Tue Feb 23 2010 ro@suse.de
- No longer call zic (the timezone compiler) from boot.clock for
  creating /etc/localtime: this file is created by YaST during
  installation; there is no need to recreate it at boot time.
  (This code was only executed on s390 and in xen guests, too.)
* Fri Feb 19 2010 meissner@suse.de
- enabled MALLOC_CHECK_ and MALLOC_PERTURB_ during testing
* Thu Feb 18 2010 ro@suse.de
- make sure options for /dev/pts are honored (bnc#580924)
* Thu Feb 18 2010 ro@suse.de
- Fix issue with chvt hanging, preventing restart (bnc#540482)
  (add --userwait to chvt call)
* Tue Feb 16 2010 ro@suse.de
- remove bogus splash check from boot.proc
* Mon Feb 15 2010 werner@suse.de
- Rename meta-mode to enable-meta-key in /etc/inputrc as
  bash 4.1 / readline library 6.1 use this key word
* Sun Feb 14 2010 ro@suse.de
- fix typo in comment in /etc/skel/.emacs (bnc#558055)
* Sun Feb 14 2010 ro@suse.de
- change test for tty1 in boot.localfs and boot.rootfsck
  (bnc#564325)
* Fri Feb  5 2010 ro@suse.de
- /etc/init.d/boot: use devtmpfs for /dev if available (bnc#561990)
* Thu Jan 14 2010 ro@suse.de
- do not rewrite /etc/adjtime needlessly (bnc#570245)
* Wed Jan 13 2010 ro@suse.de
- set NO_PROXY together with no_proxy (bnc#569310)
* Wed Jan 13 2010 ro@suse.de
- clean-tmp: use ctime instead of mtime and add -xdev
  to avoid crossing filesystem boundaries (bnc#568990)
* Wed Dec 16 2009 werner@suse.de
- Avoid to source/parse $HOME/.kshrc twice (bnc#560152)
* Tue Dec  8 2009 mvyskocil@suse.cz
- fixed JRE_HOME typo in alljava.sh (bnc#549395)
* Fri Dec  4 2009 ro@suse.de
- fix example in sysconfig.language (bnc#557283)
* Fri Dec  4 2009 ro@suse.de
- fix some issues with boot.clock and xen (bnc#550697)
* Wed Dec  2 2009 ro@suse.de
- mount /dev correctly also if devtmpfs
* Wed Nov 25 2009 ro@suse.de
- same for csh.login
* Tue Nov 24 2009 puzel@novell.com
- add '-R' to LESS variable in /etc/profile (bnc#554513)
* Wed Nov 18 2009 mseben@novell.com
- added SEND_OUTPUT_ON_NO_ERROR option to /etc/sysconfig/cron (fate#305279)
* Wed Nov 18 2009 ro@suse.de
- remove bash1 from /etc/shells (bnc#554131)
* Fri Oct 30 2009 mmarek@suse.cz
- wait for raid arrays to become clean before shutdown or reboot
  (fate#306823).
* Mon Oct 26 2009 meissner@suse.de
- disable malloc debugging again for the release. (rm /etc/profile.d/malloc-debug.*)
* Mon Oct 19 2009 werner@suse.de
- Use /bin/hostname for HOSTNAME instead of NIS domainname found
  in /proc/sys/kernel/domainname (bnc#540981)
* Wed Oct  7 2009 werner@suse.de
- Remove SuSEconfig.clock and simplify refresh_initrd (bnc#538357)
* Tue Oct  6 2009 werner@suse.de
- Refresh initrd if CMOS clock is set to local time (bnc#538357)
* Tue Oct  6 2009 werner@suse.de
- Use option -c on grotty command to diaable escape sequences in
  /etc/init.d/README (bnc#543957)
* Wed Sep 30 2009 werner@suse.de
- Use configurable meta-mode in /etc/inputrc (bnc#541379)
* Tue Sep 29 2009 werner@suse.de
- The halt script should not shutdown network for iSCSI (bnc#513928)
* Thu Sep 17 2009 ro@suse.de
- add bash completion for evince (bnc#540013)
* Wed Sep 16 2009 coolo@novell.com
- DO_FASTBOOT is now yes/no, no longer empty (bnc#538362)
* Thu Sep  3 2009 ro@suse.de
- fix CLEAR_TMP_DIRS_AT_BOOTUP (bnc#531514)
* Mon Aug 31 2009 ro@suse.de
- boot.clock:
  check if system timezone already set by initrd (bnc#534816)
* Tue Aug  4 2009 ro@suse.de
- etc/profile,etc/csh.login: remove output of /etc/motd
  and faillog, already printed by login (bnc#528003)
* Thu Jul 30 2009 ro@suse.de
- drop hacks for sles8 from pre/post scripts
- make use of sed -i instead of manual handling in pre/post
- aaa_base.specialfilelist: drop the ones that are not in aaa_base
* Thu Jul 23 2009 werner@suse.de
- Remove INFOPATH and INFODIR as info knowns about (bnc#524541)
* Wed Jul 22 2009 ro@suse.de
- fix typo in boot.cleanup
* Wed Jul 22 2009 ro@suse.de
- import some speedups from moblin
  boot.cleanup: use xargs and use -m option from mkdir
  boot.localnet: depend on boot.rootfsck instead of boot.cleanup
- adapt boot.clock to changed hwclock/util-linux:
  - drop --hctosys for utc case
  - replace by --systz for non-utc case
* Wed Jul 22 2009 werner@suse.de
- Fix expansion bug in bash completion without loosing expansion
  of the tilde for the users home directory (bnc#524224)
* Fri Jul 17 2009 rguenther@suse.de
- Move udev and net-tools back from PreReq to Recommends
* Fri Jul 17 2009 ro@suse.de
- update alljava.csh (expand PATH like alljava.sh bnc#480480)
* Wed Jul 15 2009 ro@suse.de
- update mailcap for text/html: change w3m call (bnc#479432)
* Tue Jul 14 2009 werner@suse.de
- Bash completion: make file type detection independent from file
  name for b(un)zip2, g(un)zip, and unzip (bnc#512386, bnc#512386)
* Tue Jul 14 2009 ro@suse.de
- added recommends for netcfg (bnc#519337)
* Sat Jun 13 2009 coolo@suse.de
- now that fixed glibc is in, we can enable malloc_check again
* Thu Jun 11 2009 coolo@novell.com
- /.buildenv is almost never a directory...
* Wed Jun 10 2009 ro@suse.de
- change condition for MALLOC_CHECK to test for /.buildenv
* Mon Jun  8 2009 coolo@suse.de
- do not set MALLOC_CHECK for now in build environemtns to continue
  building even if we have a problem there atm (bnc#509398)
* Tue May 12 2009 werner@suse.de
- Make some expansions work for bash completion (bnc#493303, bnc#487252)
* Fri May  8 2009 werner@suse.de
- Add missing line in boot.clock
* Thu May  7 2009 werner@suse.de
- At shutdown boot.clock should be executed *before* boot.apparmor
  otherwise it may happen that /etc/localtime is not readable and
  localtime(3) may fall back to UTC time as system default (bnc#492921).
* Thu Apr 30 2009 werner@suse.de
- First try to support root fs with type aufs (bnc#491890)
- Use usleep to wait on udev
* Tue Apr 28 2009 werner@suse.de
- Disable blogd on fastboot or quiet boot
- Move mkinitrd scripts to mkinitrd
* Tue Apr 21 2009 werner@suse.de
- Avoid possible race between rtc_cmos and running date
* Mon Apr 20 2009 coolo@suse.de
- boot.ldconfig: remove most of the checks / run ldconfig way less
- boot.localfs: STOP preload during fsck calls
* Mon Apr 20 2009 werner@suse.de
- boot.clock: make status argument work and add argument timezone
- boot.clock: for s390 make date command accurate as possible
- Rename mkinitrd script setup-rtc.sh to setup-clock.sh and
  add boot-clock.sh, also check for including boot-rtc.sh the
  existence of the rtc_cmos module to avoid fatal errors
* Fri Apr 17 2009 werner@suse.de
- boot.clock: write system time only back to HW clock if kernel
  time status shows that clocks are unsynchronized
- Add two helper scripts for mkinitrd to add and load rtc_cmos
  module and add /etc/localtime to initrd (bnc#492921)
* Thu Apr 16 2009 werner@suse.de
- Make boot.clock more tough due udev timings (bnc#492921)
- Remove /etc/adjtime in boot.clock if left over (bnc#495417)
* Wed Apr 15 2009 ro@suse.de
- updated alljava.{sh,csh} (bnc#492820)
* Mon Mar 30 2009 werner@suse.de
- bash.bashrc: append history to avoid override the history with
  two parallel bash sessions.
* Tue Mar 24 2009 ro@suse.de
- fix typo in comment in bash.bashrc (bnc#487742)
* Mon Mar  9 2009 ro@suse.de
- touch and chmod some files only if they do not exist before
  leave them alone otherwise
* Wed Mar  4 2009 meissner@suse.de
- MALLOC_CHECK_=3 (bnc#481582)
* Mon Feb 23 2009 ro@suse.de
- remove only content of tmpdirs, not the tmpdirs themselves
  in boot.cleanup (bnc#470511)
* Thu Feb 19 2009 schwab@suse.de
- Add .xz to /etc/DIR_COLORS.
* Thu Feb 19 2009 meissner@suse.de
- reenable MALLOC_CHECK_ and MALLOC_PERTURB_ for Factory.
* Mon Feb 16 2009 ro@suse.de
- fix typo in etc/init.d/rc (bnc#469242)
* Fri Feb 13 2009 ro@suse.de
- test if /sbin/splash exists in /etc/init.d/halt (bnc#467637)
* Thu Feb 12 2009 coolo@suse.de
- do not try fsck on file systems unknown to stat (kiwi live cds)
* Fri Feb  6 2009 werner@suse.de
- Enhance single user mode for shutdown (bnc#473043)
* Wed Feb  4 2009 ro@suse.de
- drop broken 0size file in man8
* Mon Jan 26 2009 coolo@suse.de
- removing the timeout, there is no good timeout value (bnc#426270)
* Fri Jan 23 2009 coolo@suse.de
- wait for udev to settle the modprobe events (bnc#426270)
* Wed Jan 21 2009 ro@suse.de
- fixed typo in xdg-environment.sh (thanks to mmeier)
* Wed Jan 21 2009 werner@suse.de
- Reenable Alt-BackSpace for delete word in XTerm in UTF-8 mode
* Tue Jan 20 2009 werner@suse.de
- Bash: support wildcards in completion of cd command (bnc#463477)
* Tue Jan 20 2009 ro@suse.de
- make mounting in /etc/init.d/boot less error prone
* Fri Jan 16 2009 ro@suse.de
- remount /dev in /etc/init.d/boot if already mounted (bnc#466718)
* Thu Jan  8 2009 werner@suse.de
- Do not jump back to HOME for a login shell (bnc#458940)
* Thu Jan  8 2009 ro@suse.de
- add quoting to xdg-environment.*sh (bnc#463175)
* Fri Dec 19 2008 ro@suse.de
- fix bug in /etc/init.d/boot to mount sysfs correctly if missing
* Tue Dec 16 2008 ro@suse.de
- fix metadata in sysconfig.cron (bnc#457093)
* Thu Dec 11 2008 ro@suse.de
- only mount /proc and /sys if not mounted already
  (bnc#457984)
* Wed Dec 10 2008 bwalle@suse.de
- Make /sbin/get_kernel_version a bit more tolerant: Accept
  '2.6.27.private-ppc64' as version string. (bnc #441821)
* Wed Dec 10 2008 werner@suse.de
- Do not set CMOS HW clock on XEN systems (bnc#422010)
- use mkill(8) instead of fuser
* Mon Dec  8 2008 ro@suse.de
- updated list of settings for DEFAULT_WM (from control.xml)
  (bnc#445646)
* Mon Dec  8 2008 ro@suse.de
- keep "you" from starting twice because of broken alias
  (bnc#441053)
* Fri Dec  5 2008 werner@suse.de
- Use the new vhangup tool to cause processes on vc's to quit.
  This avoids fuser call which may hang if NFS is used.
- The fuser call to terminate processes with write access to the
  root file system is not required anymore due fix for bnc#442753.
* Wed Dec  3 2008 ro@suse.de
- if /var is an extra partition, kill processes accessing it
  before calling umount (bnc#435315,bnc#450980)
* Mon Nov 24 2008 olh@suse.de
- speed up boot.rootfsck
  - remove useless checks to set MAY_FSCK
  - avoid execution of on_ac_power unless necessary
  - avoid stat call to detect root on net filesystem unless needed
* Thu Nov 20 2008 ro@suse.de
- comment fix in sysconfig.cron (related bnc#442059)
- chkconfig: fix when specifying run-levels (bnc#446839)
* Thu Nov 20 2008 werner@suse.de
- hwclock now allows to use --adjust and --hctosys with one call,
  caving us exactly 1s of CPU and boot time (bnc#441106)
* Wed Nov 19 2008 ro@suse.de
- don't try to check rootfs if it is a network filesystem
  (bnc#441234)
* Tue Nov 18 2008 ro@suse.de
- remove patch aaa_base.disable-ps3-vram-swap.patch again
* Tue Nov 18 2008 meissner@suse.de
- disable MALLOC debugging for openSUSE 11.1 RC1. (bnc#441937)
* Mon Nov 17 2008 werner@suse.de
- Make hwclock work: do not unmount root fs unintended (bnc#442753)
- Make hwclock work: load rtc_cmos module if available (bnc#444680)
* Mon Nov 17 2008 ro@suse.de
- boot.cleanup: cleanup ntp chroot (bnc#443423)
* Fri Nov 14 2008 mrueckert@suse.de
- remove the patching of the MAIL_LEVEL setting.
* Thu Nov  6 2008 werner@suse.de
- Fix chkconfig to make option `-s <serv> on' (bnc#422433)
* Wed Nov  5 2008 werner@suse.de
- rs.status: don't use escape seqs if not on a tty (bnc#422004)
* Wed Nov  5 2008 ro@suse.de
- usr/sbin/Check: skip dir if "." or ".." is in MANPATH
  (bnc#426646)
* Fri Oct 31 2008 werner@suse.de
- Do not override locale if already set by the GDM (bnc#440371)
* Thu Oct 23 2008 sassmann@suse.de
- add patch aaa_base.disable-ps3-vram-swap.patch to disable using
  video ram as swap on PS3. This this causes the system to hang
  with FW 2.50.
* Tue Oct 21 2008 werner@suse.de
- Make chkconfig be aware of new feature of insserv (bnc#422433)
* Tue Oct 21 2008 kukuk@suse.de
- Only set PAGER to less if less is installed [bnc#436958]
* Wed Oct 15 2008 ro@suse.de
- add missing ";;" in several boot scripts
  (bnc#455521,bnc#455522,bnc#455523,bnc#455524,bnc#455508,
  bnc#455511,bnc#455513)
* Tue Oct 14 2008 ro@suse.de
- add missing ";;" in boot.clock (bnc#432381)
* Thu Oct  9 2008 garloff@suse.de
- Remove SCHED_MINTIMESLICE/MAXTIMESLICE from sysconfig.kernel,
  it's been dysfunctional for a while.
* Thu Oct  2 2008 werner@suse.de
- Do not set TEXINPUTS to make luatex work (bnc#429345)
- Use /bin/grep in profile.csh (bnc#429336)
* Fri Sep 26 2008 dmueller@suse.de
- update chkconfig manpage (bnc#411221)
* Thu Sep 11 2008 mkoenig@suse.de
- skip fsck if running on battery [fate#303375]
* Thu Sep 11 2008 ro@suse.de
- modify_resolvconf is gone, call "netconfig update" instead
* Tue Sep  2 2008 hare@suse.de
- add 'hvc0' as valid console for s390x.
* Mon Aug 18 2008 ro@suse.de
- remove deprecated "-p" option from fillup_and_insserv call
- remove rc.config related snippets (from before sles8)
* Sun Aug 17 2008 ro@suse.de
- fix header for boot.localnet
* Mon Aug 11 2008 werner@suse.de
- Fix shell syntax in boot scripts from last change
- Fix some boot script dependencies
* Fri Aug  8 2008 werner@suse.de
- Implement forcefsck from kernels command line (bnc#379597)
* Fri Aug  8 2008 werner@suse.de
- In boot.localfs: generate list of virtual fs on the fly
* Thu Aug  7 2008 werner@suse.de
- In halt script: use option -r of umount
- In boot.localfs: be sure that / is not busy by using the new -w
  option of fuser for terminating all proccesses with write access
* Thu Aug  7 2008 schwab@suse.de
- Fix shell function syntax.
* Tue Aug  5 2008 werner@suse.de
- Start blogd after /dev/pts is mounted (bnc#410301) and related
  changes for better mainframe support in boot, rc, and halt.
* Mon Aug  4 2008 ro@suse.de
- added sourcing of command_not_found handlers to bash.bashrc
  (bnc#412558)
* Mon Aug  4 2008 schwab@suse.de
- Fix missing test in reboot script.
* Wed Jul 30 2008 werner@suse.de
- More work on bnc#379745: after sync, stop inactive md arrays,
  enforce clean state of active md arrays.
- Avoid error output /etc/rc.status due failed stty
* Mon Jul 28 2008 werner@suse.de
- Add missing test on ~/.hushlogin in csh.login
* Fri Jul 25 2008 werner@suse.de
- Make login procedure of bash and tcsh more equal (bnc#401470)
* Tue Jul 22 2008 werner@suse.de
- Restore the broken arch_special tar ball (bnc#410237)
- Remove boot.getclock as insserv now can handle this
- Some more cleanups for new insserv
* Fri Jul 18 2008 werner@suse.de
- Make boot scripts know about new upcoming startpar and insserv
* Wed Jul 16 2008 ro@suse.de
- compile get_kernel_version with largefile support (bnc#398593)
* Fri Jul  4 2008 werner@suse.de
- Add missing `test' in /etc/init.d/boot (bnc#406202)
* Thu Jul  3 2008 werner@suse.de
- Check for /sys/kernel/kexec_loaded before reading it (bnc#387601)
* Fri Jun 20 2008 dmueller@suse.de
- readd malloc debugging hooks for 11.1
- bump version
* Fri Jun 13 2008 werner@suse.de
- Detect SIGWINCH during boot and runlevel switch
* Mon Jun  9 2008 werner@suse.de
- Better workaround for colon in directors names (bnc#398369)
* Wed Jun  4 2008 werner@suse.de
- More on bnc#388327: do not umnount tmpfs devices like /dev
* Tue Jun  3 2008 meissner@suse.de
- remove malloc debugging for the release.
* Tue Jun  3 2008 werner@suse.de
- boot.localfs: /tmp could be a memory based tmpfs (bnc#388327)
* Mon Jun  2 2008 ro@suse.de
- marked /etc/bash.bashrc as config (bnc#382804)
* Mon Jun  2 2008 ro@suse.de
- change sysconf_addword to work with sed instead of ed
  (bnc#377131)
* Wed May 28 2008 werner@suse.de
- Make colon work in _cd_ expansion shell function even if part
  of COMP_WORDBREAKS (bnc#391955)
* Tue May 20 2008 werner@suse.de
- Remove last occurence of boot.setclock (bnc#384254)
* Mon May 19 2008 werner@suse.de
- Move udev from the Required to the PreRequired list (bnc#384254)
- Rename boot.setclock to boot.clock but preserve boot.getclock
  this avoid to get temporary boot.clock provided twice during
  update (bnc#384254)
* Fri May  9 2008 olh@suse.de
- enable swap to ps3vram in boot.swap
* Thu May  8 2008 werner@suse.de
- Read status of /sys/kernel/kexec_loaded into a variable
* Thu May  8 2008 aj@suse.de
- Fix specfile for last change.
* Wed May  7 2008 werner@suse.de
- Add both patches (aaa_base-chkconfig-help.patch and
  aaa_base-lsb-keywords-patch) to source tree
- Add kexec call in halt script if a kernel is loaded (bnc#387601)
* Tue May  6 2008 lrupp@suse.de
- added help for 'chkconfig -A' option (bnc#371548)
  (aa_base-chkconfig-help.patch)
- add some lsb-keywords to the init scripts
  (aa_base-lsb-keywords-patch)
- recommend cron as this is not installed per default
- disable "Obsoletes: tpctl" for now
- added aaa_base-rpmlintrc to suppress some rpmlint warnings
* Mon May  5 2008 werner@suse.de
- Replace `/bin/hostname -s' with `/bin/uname -n' (bnc#386621)
- Also change reference boot.clock in sysconfig and add boot.clock
  as an alias within boot.setclock (bnc#386354)
* Wed Apr 23 2008 werner@suse.de
- Force installing ncurses-utils to have tput and reset around
* Mon Apr 21 2008 werner@suse.de
- Apply last change also for insserv call
* Fri Apr 18 2008 werner@suse.de
- Split boot.clock into two scripts for boot and shutdown
  Todo: make insserv knowing about Required-Stop to merge them
  again to one boot.clock.
* Fri Apr 18 2008 werner@suse.de
- If tac is used for reversed reading set TMPDIR to /dev/shm
* Thu Apr 17 2008 werner@suse.de
- Fix wrong redirection of stdout/stderror in boot.localfs
* Tue Apr 15 2008 werner@suse.de
- Fix wrong regular bash expression (bnc#379745)
* Mon Apr  7 2008 dkukawka@suse.de
- fixed bnc#341035: removed /media/.hal-mtab from
  /etc/init.d/boot.rootfsck
* Wed Mar 19 2008 ro@suse.de
- add missing "#" before comments in last change
* Tue Mar 18 2008 werner@suse.de
- Use common code only once for halt/reboot/single
* Thu Mar  6 2008 werner@suse.de
- Touch file /success only on rw mounted root fs (bnc#367315)
* Tue Mar  4 2008 mkoenig@suse.de
- boot.localfs:
  fsck Option -m changed to -M
  change hotplug to nofail
* Tue Feb 26 2008 ro@suse.de
- updated mime.types (bnc#216934)
  - ecmascript changed from "es" to "ecma"
  - audio/x-it removed
  - text/x-csharp removed
* Tue Feb 19 2008 werner@suse.de
- boot.swap: compare inode/device pairs of listed swap devices and
  fstab swap entries (bnc#362935)
* Tue Feb 12 2008 rguenther@suse.de
- Add requires to /bin/login, required from inittab invoking
  mingetty with default arguments.
* Mon Feb 11 2008 werner@suse.de
- No indirect calls of binaries but use explicit path (bnc#353437)
* Thu Jan 31 2008 ro@suse.de
- run yast2 firstboot if needed in etc/init.d/boot (#354738)
* Thu Jan 24 2008 werner@suse.de
- Set HW clock before mounting the local file systems
* Wed Jan 23 2008 ro@suse.de
- use if/then instead of plain test
* Wed Jan 23 2008 mrueckert@suse.de
- only copy the secring if it really exists.
* Wed Jan 23 2008 ro@suse.de
- don't overwite root/.gnupg/secring.gpg
* Mon Jan 14 2008 aj@suse.de
- Fix typo.
* Fri Jan 11 2008 ro@suse.de
- skeleton.compat (fix bash error) (#351386)
* Wed Jan  9 2008 werner@suse.de
- Test for the sticky bit on /etc/profile.d/*.(sh|csh) files and
  if set for a file do not source it (bug #340737)
* Tue Jan  8 2008 ro@suse.de
- remove checks for sysconfig/dump and DUMP_ACTIVE (#348656)
- updated "you" alias (#326075)
- weaken requires for logrotate to recommends (#348549)
* Tue Jan  8 2008 werner@suse.de
- Fix small typo in /etc/rc.status function rc_check()
* Mon Jan  7 2008 schwab@suse.de
- Cleanup gpg agent sockets on boot.
* Mon Jan  7 2008 schwab@suse.de
- Fix last change.
- Cleanup.
* Tue Dec 18 2007 ro@suse.de
- don't remove /var/run/utmp during boot to fix "who -b" (#302036)
* Fri Dec 14 2007 ro@suse.de
- remove requires for aaa_skel
- provide and obsolete aaa_skel (dropped package)
* Wed Dec 12 2007 werner@suse.de
- Adjust file for hwclock<->sysclock only on UTC hwclock (#223365)
* Mon Dec 10 2007 ro@suse.de
- moved /etc/skel/.inputrc and /etc/skel/.emacs from aaa_skel to
  here
* Wed Dec  5 2007 dmueller@suse.de
- add .lzma to DIR_COLORS
* Tue Dec  4 2007 werner@suse.de
- Do not read ~/.bashrc in case of /bin/sh (bug #340952)
* Mon Dec  3 2007 ro@suse.de
- for zsh, do not source bash.bashrc (#343621)
* Fri Nov  9 2007 olh@suse.de
- do not run swapoff -a during shutdown, only deactivate swapfiles
  swap can not become unclean like filesystems (#342757)
* Wed Oct 31 2007 ro@suse.de
- added psmisc as requires (fuser needed for /etc/init.d/reboot)
  (#334247)
* Tue Oct 30 2007 ro@suse.de
- added sysconf_addword to /usr/sbin (#328599)
* Tue Oct 30 2007 ro@suse.de
- fix setting for XDG_DATA_DIRS (#300678)
* Tue Oct 30 2007 ro@suse.de
- remove remounting of rootfs from boot.rootfsck
  (handled by initrd for quite a while already)
  (#335174,#286759)
* Fri Oct 19 2007 meissner@suse.de
- add malloc-debug.csh to special files too.
* Wed Oct 17 2007 meissner@suse.de
- renabled MALLOC_CHECK_ for FACTORY, for both sh and csh.
* Tue Oct 16 2007 schwab@suse.de
- Remove .hal-mtab on boot [#329688].
* Tue Oct 16 2007 ro@suse.de
- second try to fix hostname setting (#300571)
* Tue Oct  9 2007 ro@suse.de
- remove sysconfig/sw_management (#331955)
* Fri Oct  5 2007 jjolly@suse.de
- Using hostname option from 'ip' boot parameter (#300571)
* Fri Sep 14 2007 ro@suse.de
- sysconfig/sysctl: enhance ENABLE_SYSRQ value:
  apart from yes/no this variable can hold a numeric value
  to enable specific sysrq controls (#257405)
- default is now "176" (allow s,u,b)
* Thu Sep 13 2007 meissner@suse.de
- remove MALLOC_CHECK_ for RC1.
* Wed Sep 12 2007 werner@suse.de
- Some cleanups in /etc/init.d/halt which may help for #309123
* Tue Sep 11 2007 coolo@suse.de
- always patch XDG_* (#300678 - with the help of werner)
- fix typo in xdg-enviroment
* Tue Sep  4 2007 maw@suse.de
- Add /usr/share/gnome to XDG_DATA_DIRS (#307213).
* Tue Sep  4 2007 bwalle@suse.de
- get_kernel_version: make check more strict to usage on kernel
  dumps (#307326)
* Fri Aug 31 2007 rguenther@suse.de
- Drop procps BuildRequires again.
* Wed Aug 29 2007 werner@suse.de
- Sort out useful terminals before accessing them (bug #293842)
* Fri Aug 17 2007 schwab@suse.de
- Remove some unnecessary verboseness when waiting for processes.
* Sat Aug 11 2007 dmueller@suse.de
- rebuild ldconfig cache if its corrupt (#259001)
- fix boot.localfs output (#285865)
* Fri Aug 10 2007 schwab@suse.de
- Remove conflicting readline bindings [#299415].
* Fri Aug 10 2007 trenn@suse.de
- Enhance comments for ACPI_DSDT= variable in sysconfig/kernel
* Fri Aug  3 2007 dmueller@suse.de
- re-add change lost in last update
* Wed Aug  1 2007 adrian@suse.de
- add mimetypes for .ymp and .ymu files (#295677)
* Mon Jul 30 2007 dmueller@suse.de
- remove /bin/ps prereq and replace it with $SHELL
* Fri Jul 27 2007 coolo@suse.de
- revert the last two changes as they break too much for the moment
* Fri Jul 27 2007 werner@suse.de
- Add /bin/ps to PreReq and procps to BuildRequires for last change
* Thu Jul 19 2007 werner@suse.de
- Add restricted detection in profile and bash.bashrc (#293038)
* Thu Jul 19 2007 werner@suse.de
- Small correction in inputrc for urxvt, mlterm, and konsole
* Mon Jul 16 2007 werner@suse.de
- Update inputrc to fit current xterm and others (bug #262330)
* Fri Jun 22 2007 coolo@suse.de
- add a special case for splash not terminating - it's there on
  purpose
* Fri Jun 22 2007 coolo@suse.de
- remove 8 seconds worth of sleep() time from shutdown
* Wed Jun 20 2007 dmueller@suse.de
- skeleton: change sendmail to generic smtp dependency
- etc/init.d/*: add Short-Description tags
- add insserv_cleanup postun
* Mon Jun 18 2007 coolo@suse.de
- let klogd sync its own file instead of all partitions
* Mon Jun 18 2007 werner@suse.de
- Sometimes /etc/sysconfig/bootsplash is missed (bug #284891)
* Tue Jun  5 2007 mkoenig@suse.de
- remove nfs, now part of nfs-client
* Tue Jun  5 2007 ro@suse.de
- etc/init.d/boot.localfs:
  - handle /sys more like /proc
- etc/init.d/halt:
  - don't umount /proc in the end, halt(8) might need it
  - source sysconfig/bootsplash since we try to use $SPLASH
* Mon Jun  4 2007 mfabian@suse.de
- Bugzilla #279934: ssh sends the locale environment variables
  even for non-login shells, therefore one should not test for
  SSH_TTY in /etc/profile.d/*.ssh but for SSH_CONNECTION,
  otherwise /etc/profile.d/lang.{sh,csh} overwrites the locale
  with the system default again (Thanks to Werner Fink).
* Mon Jun  4 2007 werner@suse.de
- Be sure the the option -P of shutdown works (bug #274042)
* Fri Jun  1 2007 lnussel@suse.de
- move permissions.local to permissions package
* Fri Jun  1 2007 lnussel@suse.de
- move sysconfig.boot.crypto to cryptsetup package
* Wed May 30 2007 varkoly@suse.de
- move sysconfig.mail into yast2-mail
* Wed Apr 25 2007 werner@suse.de
- Check for exported PS1 variable (bug #261203)
* Tue Apr 24 2007 lnussel@suse.de
- move boot.crypto to util-linux-crypto (#257884)
* Mon Apr 16 2007 werner@suse.de
- Remove old Makefile check shorten boot time by 2 secs (#262676)
* Mon Mar 19 2007 rguenther@suse.de
- Do not require suse-build-key.
- Do not mess with roots keychain.
* Tue Mar 13 2007 werner@suse.de
- Fix of the fix for bugzilla #244788: be sure that the ~/.bashrc
  is sourced once, not more not less.
* Wed Mar  7 2007 werner@suse.de
- Use colored root prompt (bugzilla #144620)
* Tue Mar  6 2007 rguenther@suse.de
- fix order of changelog entries
- do not fix owner and group of RPM_BUILD_ROOT
* Thu Mar  1 2007 ro@suse.de
- remount /proc and /sys to make sure fstab options are in effect
  (#250237)
* Thu Mar  1 2007 ro@suse.de
- added "application/flash-video flv" to mime.types (#245507)
* Thu Mar  1 2007 ro@suse.de
- accept spaces in dirname in nfs client script (#232356)
* Tue Feb 27 2007 werner@suse.de
- Oops, check also for profile within bashrc before assuming the
  default behaviour of the bash (#244788)
* Mon Feb 26 2007 werner@suse.de
- Do not source bashrc twice if sourcing profile for ssh (#244788)
- Expand local ./files for manual pages within bash (#248865)
* Thu Feb 15 2007 werner@suse.de
- Use plain bourne shell syntax for bug #231716 (bug #245740)
* Wed Feb 14 2007 werner@suse.de
- Both bash and tcsh should have the same path (bug #227416)
- Be carefull about X11 paths (bug #227416)
- bash complete: if cdable_vars is set expand variables on cd,
  handle CDPATH variable, and append the / on the result if missed
* Tue Feb 13 2007 werner@suse.de
- Correct lang.sh (bug #241056)
- Add support for new init feature INIT_HALT=POWEROFF/HALT
* Mon Jan 29 2007 sbrabec@suse.cz
- Removed references to /opt/gnome.
* Mon Jan 29 2007 werner@suse.de
- boot.crypto: use boot.localfs instead of $local_fs, remove the
    boot.klog and dependcies of boot.localfs (#140226)
- boot.crypto: add support for restart/reload of services for
    interactive usage of boot.crypto (#146388)
- boot.crypto: add latest support for cryptsetup from
    Chris Rivera (Fate#253)
- boot.crypto: check return values of losetup for short passphrase
    (#197493)
* Fri Jan 26 2007 ro@suse.de
- boot.localfs: use grep instead of bash-loop to speedup
  parsing for large /proc/partitions (#201501)
- fixed javascript entries in mime.types (#216934)
- added comment to permissions.local about letting the file
  end with a newline (#224151)
- drop CREATE_INFO_DIR sysconfig variable, obsolete for years.
  (#231584)
- added Required-Start: to boot.sched (#231676)
- mark /etc/profile.d files as config (#232083)
* Fri Jan 19 2007 werner@suse.de
- Don't mix shell and environment variable within locale (#236063)
* Fri Jan 19 2007 ro@suse.de
- /etc/profile.d/xdg-environment.{sh,csh}
  respect /opt/*/share/applications and /etc/opt/*/xdg
  (Fate#301042)
* Tue Jan 16 2007 meissner@suse.de
- enable malloc debug again for factory.
* Fri Jan 12 2007 werner@suse.de
- Don't use shell function if the program 'which' exists (#231716)
* Fri Jan 12 2007 ro@suse.de
- added SYNC_ZMD_TO_ZYPP to sysconfig/sw_management
* Thu Dec 21 2006 ro@suse.de
- remove aspx from /etc/mime.types (#229258)
* Wed Dec 20 2006 ro@suse.de
- call umount in "rcnfs stop" if there are any active nfs mounts
  (#103217)
* Fri Dec  8 2006 olh@suse.de
- adapt s390 inittab patch
* Thu Dec  7 2006 olh@suse.de
- add also runlevel 4 to the disabled /sbin/smart_agetty entry (223983)
* Mon Dec  4 2006 werner@suse.de
- Escape not only braces but all COMP_WORDBREAKS (#225284)
* Wed Nov 29 2006 ro@suse.de
- added rxvt-unicode,screen-256color,xterm-256color to DIR_COLORS
- removed rbash from /etc/shells (#223159)
* Mon Nov 20 2006 ro@suse.de
- added sysconfig/sw_management to set preferred update stack
  if both are installed (defaulting to zlm) (#219390)
* Wed Nov 15 2006 werner@suse.de
- Remove /etc/init.d/Makefile (bug #204383)
- Append /dev/shm/initrd.msg to /var/log/boot.msg
- Make ls alias work even for rbash (bug #214254)
* Tue Nov  7 2006 meissner@suse.de
- disable MALLOC debugging for the 10.2 release.
* Thu Nov  2 2006 ro@suse.de
- added Requires for udev (since it's used in Required-Start)
  (#214291)
* Fri Oct 20 2006 mls@suse.de
- chkconfig: add --allservices option, unify -l and -t handling
* Wed Sep 27 2006 ro@suse.de
- extend error in SuSEconfigs check_for_space (#208193)
* Wed Sep 27 2006 ro@suse.de
- do not export ORGANIZATION if empty (breaks mailx)
* Tue Sep 19 2006 ro@suse.de
- remove SuSEconfig.news and set NNTPSERVER and ORGANIZATION
  from /etc/sysconfig/news directly in /etc/profile and
  /etc/csh.login (fate#300892)
* Thu Sep 14 2006 kukuk@suse.de
- Remove global, fixed umask value and add hint about login.defs
  and pam_umask.so [Fate#3621]
* Wed Sep 13 2006 seife@suse.de
- add support for cleaning up after failed userspace suspend
* Fri Sep  8 2006 dmueller@suse.de
- fix startx path
* Fri Sep  8 2006 olh@suse.de
- run boot.proc after boot.localfs to keep sysrq enabled
  move xfs probe_dmapi from boot.proc to boot.localfs
* Thu Aug 31 2006 sndirsch@suse.de
- moved xdm init script and displaymanger sysconfig to xorg-x11
* Tue Aug 29 2006 ro@suse.de
- removed ash from requires (old for mkinitrd) (#202074)
- added net-tools to requires (for boot.localnet) (#202078)
* Thu Aug 24 2006 olh@suse.de
- skip boot.clock if system time was older than mkinitrd buildtime
- add hint for vim syntax to rc.status and rc.splash
* Tue Aug 22 2006 werner@suse.de
- Use new init feature of redo of utmp records if needed (#148038)
* Sat Aug 19 2006 sndirsch@suse.de
- call SuSEconfig.xdm (moved to /etc/X11/xdm/SuSEconfig.xdm) in
  xdm init script (Bug #200299)
* Fri Aug 11 2006 sndirsch@suse.de
- /usr/sbin/Check:
  * add /usr/share/fonts/* to the list of directories, in which
    compressed (.Z) files should be uncompressed first (before
    being compressed (.gz) again)
* Tue Aug  8 2006 werner@suse.de
- Use configured for all prompts during interactive boot (#184042)
- Enable multiline option for ksh if available (#192070)
- Restore utmp after transition from cold single user mode to an
  other runlevel state (#148038)
- Do not run the boot scripts at switch from cold single user mode
  to reboot or halt state (#196174)
* Mon Aug  7 2006 ro@suse.de
- removed SuSEconfig.sortpasswd (unused for ages) (fate#300894)
- remove sysconfig variable SORT_PASSWD_BY_UID
* Mon Aug  7 2006 kukuk@suse.de
- Remove SuSEconfig.zmessages [Fate#300893]
- remove sysconfig variables MAIL_LEVEL and MAIL_REPORTS_TO
* Wed Aug  2 2006 sndirsch@suse.de
- aaa_base.pre: cleanup (removed obsolete X11R6 handling stuff)
- don't try to compress fonts in new truetype font directory
* Tue Aug  1 2006 olh@suse.de
- keep ENABLE_SYSRQ= at the end in /etc/sysconfig/sysctl
* Fri Jul 28 2006 olh@suse.de
- remove root/.gnupg/suse_build_key~ from archive
* Fri Jul 28 2006 olh@suse.de
- clearify usage of Required-start and Should-Start (#181972)
  minimal required order is: udev, rootfsck, cleanup, localnet
  everything else is optional
- remove dropped boot.ibmsis prereq
* Thu Jul 27 2006 olh@suse.de
- move gpg stuff from prep to install section in specfile,
  to fix quilt setup *.spec
* Thu Jul 27 2006 ro@suse.de
- avoid error on new installation with fix for #190597
* Tue Jul 25 2006 schwab@suse.de
- Fix last change.
* Tue Jul 25 2006 sndirsch@suse.de
- /etc/{profile,csh.login}: fixed $XKEYSYMDB/$XNLSPATH for X.Org 7
- /etc/init.d/xdm:
  * fixed init script for X.Org 7
  * cleanup
* Mon Jul 24 2006 ro@suse.de
- fixed RCCONFIG_BACKUP_DIR (move to /var/adm/backup/sysconfig)
  (#190597)
* Mon Jul 10 2006 meissner@suse.de
- enable MALLOC_PERTURB_ and MALLOC_CHECK_ for hardcore
  malloc debugging and failure.
* Mon Jul 10 2006 kssingvo@suse.de
- fixed language error in comment of sysconfig.cron (bugzilla#190967)
* Mon Jul  3 2006 kssingvo@suse.de
- new gnupg requires $HOME/.gnupg for trustdb.gpg (faking no longer
  possible)
* Thu May 25 2006 olh@suse.de
- boot.loadmodules is optional for boot.localfs (#130995)
* Fri May 19 2006 ro@suse.de
- added sysconfig variable DMAPI_PROBE to be able to set
  /proc/sys/fs/xfs/probe_dmapi early enough in the boot process
  (#176371)
* Thu May 11 2006 werner@suse.de
- bash.bashrc: check for already set PS1 variable (bug #172753)
* Wed May 10 2006 sndirsch@suse.de
- sysconfig.{displaymanager,language}: kdm3 --> kdm (Bug #168745)
* Fri Apr 28 2006 ro@suse.de
- fix build
* Thu Apr 27 2006 werner@suse.de
- bash.bashrc: back to the roots, use -a for l and la (bug #153303)
* Thu Apr 27 2006 cthiel@suse.de
- obsolete tpctl on x86_64
* Wed Apr 26 2006 dmueller@suse.de
- fix sles specific settings in fillup templates (#169639)
* Tue Apr 25 2006 ro@suse.de
- comment out "-9" default for GZIP in profile/csh.cshrc (#168800)
* Tue Apr 25 2006 werner@suse.de
- Use the which shell function only for the bash (bug #168662)
* Sun Apr 23 2006 sndirsch@suse.de
- fixed xdm script (Bug #168633)
* Thu Apr 20 2006 ro@suse.de
- mount debugfs to /sys/kernel/debug if supported (#162214)
* Thu Apr 20 2006 ro@suse.de
- get current build key from suse-build-key rpm
* Wed Apr 19 2006 sndirsch@suse.de
- etc/init.d/xdm:
  * set LD_LIBRARY_PATH/LD_RUN_PATH accordingly if Xgl and ATI
    proprietary ("fglrx") driver are in use
* Tue Apr 11 2006 werner@suse.de
- csh.login: allow file pattern globbing during package profiles
    sourcing (#164944)
- boot.localfs: avoid extern programs
* Mon Apr 10 2006 ro@suse.de
- fix separator in sysconfig/displaymanager (#162602)
* Mon Apr 10 2006 werner@suse.de
- Bash completion: expand also for sections of posix manual pages
  and include section 0 into search scheme (bug #160782)
* Wed Apr  5 2006 ro@suse.de
- boot.localfs: replaced cut by sed (#163756)
* Mon Apr  3 2006 garloff@suse.de
- Add DOMU_INITRD_MODULES variable to sysconfig.kernel.
* Mon Apr  3 2006 ro@suse.de
- fix /etc/profile.d/xdg-enviroment.csh (#158283)
* Wed Mar 29 2006 ro@suse.de
- added ShouldStart for boot.multipath to boot.localfs (#160511)
- added update from ttyS0 to ttySG0 for SGI Altix in postinstall
  (#140401)
* Thu Mar 23 2006 dmueller@suse.de
- Fix init 3/rcxdm stop for default DISPLAYMANAGER
* Thu Mar 23 2006 werner@suse.de
- Handle in the system wide csh.cshrc if a tcsh without login files
  first option is used.
* Wed Mar 22 2006 werner@suse.de
- Be sure that prompt strings can be used by the bash (bug #159983)
- Do not be fooled by /usr/local/bin/hostname
* Wed Mar 22 2006 hare@suse.de
- Move dependencies for boot.loadmodules to be started prior
  to boot.localfs (#130995)
* Tue Mar 21 2006 hare@suse.de
- Fix wait for missing block devices.
* Mon Mar 20 2006 hare@suse.de
- make boot.localfs wait for missing block devices (#149979).
* Mon Mar 20 2006 uli@suse.de
- fixed s390 console entries in inittab: vt220 is xterm (don't
  ask me, I just work here...) and on ttyS1, 3270 is on
  /dev/3270/ttycons (bug #159143)
* Fri Mar 17 2006 ro@suse.de
- move HALT_SOUND from sysconfig/suseconfig to sysconfig/shutdown
- add HALT_POWERDOWN_INSERT to sysconfig/shutdown
  which can contain a command to be run directly beore halt
  e.g. for UPS shutdown
* Thu Mar 16 2006 werner@suse.de
- Make cold boot into single user work even for `s'
- Restart udev after warm reached single user mode (bug #158613)
* Thu Mar 16 2006 werner@suse.de
- Do not overwrite VISUAL and HISTFILE of (pd)ksh (bug #158467)
* Tue Mar 14 2006 dmueller@suse.de
- fix DISPLAYMANAGER_SHUTDOWN default to "auto"
* Tue Mar 14 2006 ro@suse.de
- fixed typo in SuSEconfig.functions (#156414)
* Mon Mar 13 2006 werner@suse.de
- Make all shells happy (pdksh/ksh/bash/ash) (bug #155970, #148251)
* Mon Mar 13 2006 ro@suse.de
- updated /root/.gnupg/suse_build_key (#156971)
* Mon Mar 13 2006 ro@suse.de
- added "127.0.0.1" to "NO_PROXY_FOR" in sysconfig/proxy (#155736)
* Wed Mar  8 2006 werner@suse.de
- Make ksh happy with escape sequeneces in echo msg (bug #155823)
* Wed Mar  1 2006 ro@suse.de
- move rest of displaymanager variables over here (#148468)
- rename KDM_SHUTDOWN to DISPLAYMANAGER_SHUTDOWN
- DIR_COLORS: change for class ORPHAN (#153569)
- remove backup file /etc/init.d/.boot.rootfsck.swp (#154386)
* Wed Mar  1 2006 werner@suse.de
- Help pdksh and ksh with the which shell function
* Mon Feb 27 2006 werner@suse.de
- Use `-A' instead of `-a' for LS options (bug #153303)
- Use double quotes for value of RUN_PARALLEL (bug #153567)
* Tue Feb 21 2006 ro@suse.de
- handle nfs4 like nfs (#151816)
* Thu Feb 16 2006 ro@suse.de
- remove size from dmesg call in boot.klog
* Tue Feb 14 2006 olh@suse.de
- remove check for an obsolete yast2 start script
* Thu Feb  9 2006 ro@suse.de
- updated /etc/mime.types (#119173)
* Thu Feb  9 2006 werner@suse.de
- Force a reset in /etc/bash.bashrc as workaround for new readline
  library which solves the text wrapping bug #148844
* Mon Feb  6 2006 werner@suse.de
- Help the bash parser in case of the which shell function if an
  alias was used previous (bug #148251)
* Fri Feb  3 2006 ro@suse.de
- remove another call to /sbin/update-modules.dep
* Thu Feb  2 2006 agruen@suse.de
- Remove /sbin/update-modules.dep: we always keep modules.dep up
  to date in the kernel and kernel module package %%post and
  %%postun scripts.
* Wed Feb  1 2006 ro@suse.de
- do not remove /etc/mtab* again in boot.localfs (#147048)
* Wed Feb  1 2006 olh@suse.de
- use private devnode for root device if /dev is empty (#147162)
  require cpio
* Mon Jan 30 2006 ro@suse.de
- added /sbin/smart_agetty and line to /etc/inittab (#41623)
* Mon Jan 30 2006 ro@suse.de
- etc/init.d/boot: remove selinux hook (#146631)
- etc/init.d/boot.clock: add seconds for s390 case (#145884)
* Mon Jan 30 2006 ro@suse.de
- remove mount_hack patch
- added "-m" to fsck call in boot.localfs (ignore mounted fs)
* Thu Jan 26 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Wed Jan 25 2006 dmueller@suse.de
- remove $QTDIR handling from /etc/profile.d/profile.(c)sh, is now
  in /etc/profile.d/qt3.(c)sh
* Wed Jan 25 2006 aj@suse.de
- Hack the hack.
* Wed Jan 25 2006 aj@suse.de
- Hack boot.localfs for Bug 145400.
* Mon Jan 23 2006 ro@suse.de
- removed SuSEconfig.insserv_cleanup again, obsolete
- modprobe loop if not already there
* Mon Jan 23 2006 ro@suse.de
- boot.localfs: require boot.udev
- boot.rootfsck: remove obsolete umount of /lib/klibc/dev
* Thu Jan 19 2006 ro@suse.de
- added SuSEconfig.insserv_cleanup
* Mon Jan 16 2006 schwab@suse.de
- Don't strip binaries.
- Use RPM_OPT_FLAGS.
* Mon Jan 16 2006 mmj@suse.de
- added SEND_MAIL_ON_NO_ERROR and SYSLOG_ON_NO_ERROR for
  sysconfig.cron [#135619]
* Wed Jan 11 2006 mlasars@suse.de
- added DAILY_TIME and MAX_NOT_RUN to sysconfig.cron (#114761)
* Tue Jan 10 2006 mls@suse.de
- chkconfig: return error status in compatibility mode
- chkconfig: display S runlevel in compatibility mode [#88213]
* Tue Dec 27 2005 ro@suse.de
- etc/init.d/boot: tmpfs -> udev (mount label)
* Wed Dec 21 2005 werner@suse.de
- Fix typo in boot.clock
* Tue Dec 20 2005 werner@suse.de
- Enable a new sysconfig boolean SYSTOHC, if set to yes do the
  old way with wrting back system to CMOS clock, if set to no
  do not adjust nor write back to CMOS clock.
* Tue Dec 20 2005 ro@suse.de
- remove devs from requires list
* Fri Dec 16 2005 ro@suse.de
- removed SHMFS_SIZE (#138451)
- removed SHMFS_OPTIONS
- chmod 1777 /dev/shm (just a directory in tmpfs, not mountpoint)
* Wed Nov 30 2005 ro@suse.de
- updated boot.localfs (no fake dev/shm mount)
* Mon Nov 28 2005 ro@suse.de
- if sorting passwd/group is enabled, then preserve permissions
  (#133905)
* Mon Nov 28 2005 ro@suse.de
- removed boot.shm (no longer needed with /dev on tmpfs)
* Wed Nov 23 2005 ro@suse.de
- really remove DEV_ON_TMPFS variable
* Wed Nov 23 2005 ro@suse.de
- remove reference to DEV_ON_TMPFS in /etc/init.d/boot.localfs
- remove DEV_ON_TMPFS variable
- mount tmpfs to /dev in /etc/init.d/boot
* Wed Nov 23 2005 ro@suse.de
- added cifs to blacklist in boot.localfs (#134352)
* Wed Nov 23 2005 ro@suse.de
- use bash for boot.swap
* Mon Nov 21 2005 schwab@suse.de
- Remove spurious error message.
* Mon Nov 21 2005 werner@suse.de
- Apply new (u)limits policy also for tcsh users
- Make the bash which alias a smart shell function (bug #133808)
* Wed Nov 16 2005 dmueller@suse.de
- don't reset kernel default ulimits in /etc/profile
* Tue Nov 15 2005 werner@suse.de
- Add /sbin/service to handle boot/runlevel services (bug #115927)
- Use parted if fdisk fails in get_swap_id (bug #121699)
* Mon Nov 14 2005 hare@suse.de
- Remove calls to blkid; obsolete by now (Feature #113001)
* Thu Nov 10 2005 werner@suse.de
- Handle directory names even with white spaces (bug #132950)
* Wed Nov  9 2005 werner@suse.de
- Do not overwrite the user's choise of WINDOWMANAGER
* Tue Nov  8 2005 werner@suse.de
- Never export UID/EUID variables
- Set UID/EUID variables readonly if not known
- Export MAIL variable, this is done by login but not by xdm
* Mon Nov  7 2005 werner@suse.de
- Make scanning for zip archives not depending on suffix but one
  file type (bug #128791)
- Add support for experts, by using ~/.bash.expert all completion
  extensions will be skipped (bug #128791)
* Fri Nov  4 2005 werner@suse.de
- Source profile/csh.login for the case that the user executes
  from a remote system a command with the ssh.  This to get, e.g.
  the full path usable on the local system.
* Wed Nov  2 2005 ro@suse.de
- remove usr/bin/pkgmake and usr/bin/pkgpack
* Wed Nov  2 2005 werner@suse.de
- Be sure that paths are glob expanded (bug #131964)
* Wed Nov  2 2005 ro@suse.de
- require mingetty (used in inittab coming from this package)
  (#131286)
* Wed Oct 26 2005 ro@suse.de
- updated comments in sysconfig/displaymanager template (#118200)
* Wed Oct 26 2005 werner@suse.de
- Do not mix csh/sh key words in profile
* Wed Oct 26 2005 werner@suse.de
- Handle the pdksh as ksh in system wide bash.bashrc and profile
- Make system wide csh.login and profile more common
- Do not source system wide bash.bashrc twice used shell ksh
* Tue Oct 25 2005 werner@suse.de
- Make bash.bashrc usable even with ash parser
- Use ENV to force the usage of bash.bashrc for all bourne shells
- Do not set twm as default window manager if empty in sysconfig
  to help wmlist in system xinitrc and sys.xsession (bug #130459)
- Move exported variables for (t)csh into csh.login (bug #104126)
* Tue Oct 18 2005 garloff@suse.de
- skeleton: License is LGPL.
- skeleton.compat: New; should be usable as a template for both
  SUSE and non-SUSE (but LSB, RH, ...) systems.
* Fri Oct 14 2005 werner@suse.de
- Add the DOS like cd.. macro (bug #118826)
- Add kdvi/kghostview/kpdf and pdflatex to the bash complete's
* Thu Oct 13 2005 mjancar@suse.cz
- boot.cleanup: remove /var/log/sa/sadc.LOCK
* Fri Oct  7 2005 ro@suse.de
- remove boot.idedma and sysconfig/ide (move to hdparm)
* Tue Sep 27 2005 ro@suse.de
- changed comment in sysconfig/displaymanager (#118200)
* Sun Sep 25 2005 schwab@suse.de
- Fix last change.
* Tue Sep  6 2005 ro@suse.de
- added fake mount for /dev to boot.localfs (#113409)
* Mon Sep  5 2005 coolo@suse.de
- avoid "Starting KDM" twice during bootup (#115219 - reviewed by
  Werner)
* Fri Sep  2 2005 ro@suse.de
- added DEV_ON_TMPFS to /etc/sysconfig/kernel (#114400)
* Thu Sep  1 2005 mls@suse.de
- chkconfig: show 'B' runlevel in --list mode (#88213)
* Tue Aug 30 2005 ro@suse.de
- fix typo in etc/profile.d/alljava.csh (-L -> -l)
* Mon Aug 29 2005 ro@suse.de
- added "-t noopts=hotplug" to fsck options (#112946)
* Thu Aug 25 2005 kukuk@suse.de
- Don't set DEFAULT_WM to twm if it is not set
* Thu Aug 25 2005 werner@suse.de
- Unset LC_ALL in rcxdm
- Remove workaround for KDM bug in rcxdm (bug #112774)
* Thu Aug 25 2005 werner@suse.de
- Handle KDM/KDE bug in locale handling (bug #112774)
* Wed Aug 24 2005 ro@suse.de
- recode update-messages/de/aaa_base to utf8
* Tue Aug 23 2005 kukuk@suse.de
- Complete comment about force-reload in init.d/skeleton
* Fri Aug 19 2005 werner@suse.de
- Make sure that we really have /sbin in path even (bug #105681)
* Thu Aug 18 2005 ro@suse.de
- changed you alias (#105479)
* Thu Aug 18 2005 coolo@suse.de
- do not sleep but sync after the log file is written
* Thu Aug 18 2005 werner@suse.de
- Do not set and export proxy control variables if empty (#104727)
- Set LC_ALL to POSIX in rc.status for well defined locale for
  all boot and runlevel scripts (bug #105322)
- Make DISABLE_ECN work even for "no" (bug #105175)
* Wed Aug 17 2005 werner@suse.de
- Remove the -p option from faillog in csh.login
- Add check for new tcsh 6.14 which does not use dspmbyte
* Tue Aug 16 2005 werner@suse.de
- Add splash handling to boot.crypto (bug #104592)
* Tue Aug 16 2005 ro@suse.de
- remove raw1394 and video1394 from MODULES_LOADED_ON_BOOT (#99691)
* Mon Aug 15 2005 ro@suse.de
- added svg to mime.types (#104086)
* Mon Aug 15 2005 ro@suse.de
- fix last change
* Mon Aug 15 2005 mjancar@suse.cz
- boot.cleanup now depends on boot.quota to make quota work
  with $CLEAR_TMP_DIRS_AT_BOOTUP (#58564)
* Fri Aug 12 2005 werner@suse.de
- Add sbin dirs of gnome and kde tp PATH if exist (bug #104058)
* Thu Aug 11 2005 dmueller@suse.de
- Fix "you" alias to use /sbin/yast2 (/sbin is no longer in path)
* Wed Aug 10 2005 werner@suse.de
- Bash expansion: escape not only spaces but also braces (#103177)
* Tue Aug  9 2005 werner@suse.de
- Delete not mounted loop devices in boot.localfs (bug #102549)
* Fri Aug  5 2005 werner@suse.de
- Add parallel booting and startpar to the manual page init.d(7)
* Thu Aug  4 2005 ro@suse.de
- fix typo in sysconfig/proxy
* Thu Aug  4 2005 werner@suse.de
- Use /etc/sysconfig/windowmanager instead of
  /etc/SuSEconfig/profile for WINDOWMANAGER.
* Thu Aug  4 2005 ro@suse.de
- typo in boot.localfs: shm vs tmpfs (#43704)
- added wmv to DIR_COLORS (#99632)
* Thu Aug  4 2005 schwab@suse.de
- Fix syntax error in complete.bash
* Wed Aug  3 2005 werner@suse.de
- Fix new mount point check in boot.crypto (bug #100536)
- Add profile.sh and profile.csh as replacement for
  the removed SuSEconfig.profile for runtime user profile.
* Wed Aug  3 2005 ro@suse.de
- added HTTPS_PROXY handling (#95647)
* Tue Aug  2 2005 ro@suse.de
- fix typos in profile.d/lang.{sh,csh}
* Tue Aug  2 2005 ro@suse.de
- remove some outdated variables from SuSEconfig.profiles
* Tue Aug  2 2005 werner@suse.de
- Feature request 100207: make language/locale configuration
  a dynamic one and support the users ~/.i18n file.
* Tue Aug  2 2005 ro@suse.de
- remove capability from MODULES_LOADED_ON_BOOT in sysconfig/kernel
* Thu Jul 28 2005 werner@suse.de
- Sanity check in boot.crypto: be sure that the mount point exists.
* Wed Jul 27 2005 ro@suse.de
- sort order of arguments for "find" to avoid warning (#95861)
* Thu Jul 14 2005 uli@suse.de
- set JAVA_HOME etc. correctly on lib64 platforms
* Fri Jun 24 2005 ro@suse.de
- gdm has been moved to /opt/gnome/sbin
* Thu Jun 23 2005 ro@suse.de
- SuSEconfig.zmessages: don't skip on FASTRUN (#87376)
* Fri Jun 17 2005 werner@suse.de
- Do not overwrite exported variables in bash and tcsh (bug #91141)
* Fri Jun 17 2005 ro@suse.de
- changed "swapon -a" to "swapon -ae" in boot.rootfsck (#91067)
* Mon Jun 13 2005 kukuk@suse.de
- Unify min/max days in /etc/shadow
- Fix group of /var/log/lastlog, add to filelist
* Thu Jun  9 2005 werner@suse.de
- Set correct min/max days for password handling in /etc/shadow
* Mon May 23 2005 ro@suse.de
- updated sysconfig/displaymanager
* Thu May 19 2005 werner@suse.de
- Minor: exit status 7 for boot scripts is failed (aka not running)
* Wed May 18 2005 ro@suse.de
- add SHMFS_OPTIONS to /etc/sysconfig/kernel (#84034)
* Wed May 18 2005 werner@suse.de
- Cleanup boot and rc master scripts to use make like boot
  behaviour for parallel boot
* Wed Apr 20 2005 ro@suse.de
- aaa_base.post: be more careful with subfs mounts in fstab
  (#75394)
* Mon Apr 18 2005 mls@suse.de
- chkconfig: don't default to all services for -a and -d (#74371)
* Thu Apr 14 2005 agruen@suse.de
- Add etc/sysconfig/kernel:SKIP_RUNNING_KERNEL variable which
  allows to turns off the /etc/init.d/running-kernel init script.
* Tue Apr 12 2005 ro@suse.de
- etc/mailcap: replace xanim by xine (#75913)
* Wed Mar 30 2005 werner@suse.de
- Make change in boot.crypto for the new losetup (see bug #74441)
* Wed Mar 23 2005 ro@suse.de
- cryptoloop: handle SL9.2 case
  (twofish256 using loop_fish is called twofishSL92)
* Wed Mar 23 2005 werner@suse.de
- Load cryptoloop and twofish modules for twofish256  (#73818)
* Mon Mar 21 2005 ro@suse.de
- etc/mailcap: fixed realplayer path (#74071)
* Fri Mar 18 2005 werner@suse.de
- Enable the boot.crypto user to force a file system check (#73818)
* Fri Mar 18 2005 ro@suse.de
- setDefaultJava analog to setJava script (#71055)
* Wed Mar 16 2005 werner@suse.de
- Add workaround for wrong exit status of debugreiserfs (#72887)
- Overwrite the primitive losetup passphrase prompt (bug #65341)
* Wed Mar 16 2005 ro@suse.de
- remount rootfs in any case in boot.rootfsck (#72334)
  need to do this to pick up additional mount options from fstab
  like acl,xattr,...
* Mon Mar 14 2005 ro@suse.de
- test for presence of /etc/fstab before trying to modify
* Mon Mar 14 2005 ro@suse.de
- added iterm to /etc/DIR_COLORS (#72223)
* Mon Mar 14 2005 ro@suse.de
- change all subfs entries below /media in /etc/fstab to noauto
* Mon Mar 14 2005 mls@suse.de
- chkconfig: don't complain if /etc/inetd.conf doesn't exist (#65640)
* Fri Mar 11 2005 ro@suse.de
- only try to umount devfs in lib/klibc/dev if mounted
* Fri Mar 11 2005 ro@suse.de
- more fixes to boot.rootfsck
* Thu Mar 10 2005 ro@suse.de
- fix typo in SuSEconfig.profile
- add sysconfig variable for klogconsole (#71983)
- boot.rootfsck: use the info we get from initrd
* Tue Mar  8 2005 werner@suse.de
- Move `ssh sends locale' check into SuSEconfig.profile (#65747)
* Fri Mar  4 2005 ro@suse.de
- skip extra magic if ROOTFS_BLKDEV is already set (from initrd)
* Thu Mar  3 2005 werner@suse.de
- Add check for ssh logins which provide their own locale (#65747)
* Mon Feb 28 2005 ro@suse.de
- replace image/x-ico by image/x-icon in mime.types (#57025)
* Mon Feb 28 2005 schwab@suse.de
- /etc/init.d/boot.swap: handle missing fdisk.
* Mon Feb 28 2005 ro@suse.de
- added boot.udev to deps of boot.loadmodules
* Wed Feb 23 2005 ro@suse.de
- updated etc/profile.d/xdg*
* Thu Feb 17 2005 werner@suse.de
- Add /etc/bash_completion.d/ for getting package dependend
  completions for the bash (bug #50946)
* Fri Feb 11 2005 ro@suse.de
- added x/bzip-2 to /etc/mailcap (#50761)
* Thu Feb 10 2005 ro@suse.de
- update_modules.dep: use find if available (from matz)
* Wed Feb  9 2005 ro@suse.de
- moved /etc/profile.d/xdg-enviroment.* from desktop-data-SuSE
  to this package
* Tue Feb  8 2005 ro@suse.de
- fixed type in sysconfig/displaymanager (#50569)
* Mon Feb  7 2005 olh@suse.de
- load raw1394, video1394 and capability per default
  via MODULES_LOADED_ON_BOOT (#49912)
* Mon Jan 31 2005 ro@suse.de
- added "Config: xdm" to DISPLAYMANAGER_XSERVER_TCP_PORT_6000_OPEN
  (#50225)
* Mon Jan 31 2005 ro@suse.de
- moved resmgr and kbd from Required-Start to Should-Start in xdm
* Mon Jan 31 2005 coolo@suse.de
- add a xdm: resmgr dependency to avoid sessions without permissions
* Thu Jan 27 2005 werner@suse.de
- Do not write to stderr on complete error and also complete for
  local binaries with the same name as the global one (#50223)
* Wed Jan 26 2005 werner@suse.de
- Do not beep if HALT_SOUND is no (bug #49928)
- POSIX do not allow `==' at string compare with test
* Wed Jan 26 2005 werner@suse.de
- mc can not handle prompts with xterm title sequences (#50189)
* Wed Jan 26 2005 schwab@suse.de
- Fix rec_rem.  Also cleanup /var/lock.
* Wed Jan 26 2005 ro@suse.de
- activate boot.cleanup
* Tue Jan 25 2005 werner@suse.de
- Fix ls alias for the zsh to support space in file names (#49437)
* Thu Jan 20 2005 coolo@suse.de
- update ldconfig also on shutdown - then the libs are likely to be
  in cache and it will be quicker
* Thu Jan 20 2005 coolo@suse.de
- do not call ldconfig on every NFS mount
- moved timezone settings to boot.clock
* Tue Jan 18 2005 ro@suse.de
- allow override to enable sysrq on boot commandline (#47533)
- extended comment in PROMPT_FOR_CONFIRM variable (#49842)
* Sun Jan 16 2005 ro@suse.de
- use correct archive for sysconfig-parts
* Fri Jan 14 2005 ro@suse.de
- split cleanup part from boot.localnet and move earlier
  in the sequence (after boot.localfs, maybe after boot.quota)
- added INSTALLED_LANGUAGES variable to sysconfig/language
* Tue Dec 21 2004 werner@suse.de
- Fix the tilde expansion bug in _cd_ and _exp_ complete shell
  function in the bash complete profile
- Add executions points for a before.local and after.local script
  in /etc/init.d/rc
* Thu Dec 16 2004 ro@suse.de
- quote usage of dircolors (#49312)
* Tue Dec 14 2004 ro@suse.de
- added LC_PAPER to SuSEconfig.profiles (#46248)
* Wed Dec  8 2004 ro@suse.de
- boot.crypto: replaced "." by ":" when prompting for password
  (#49037)
* Tue Dec  7 2004 ro@suse.de
- rcnfs: don't waste time if all nfs entries are noauto (#48996)
* Fri Dec  3 2004 ro@suse.de
- fixed failure message in boot.localfs (#48900)
* Tue Nov 30 2004 ro@suse.de
- removed /usr/bin/linkto (only used by setJava) (#48690)
* Fri Nov 19 2004 ro@suse.de
- added dmg as application/octet-stream in mime.types (#48258)
* Mon Nov 15 2004 ro@suse.de
- redirect errors to /dev/null when looking for old ssh-sockets
  on reboot cleanup (#48227)
* Mon Nov  8 2004 ro@suse.de
- remove /etc/profile.dos (not active by default anyway)
* Fri Nov  5 2004 schwab@suse.de
- filesize: use stat.
* Tue Nov  2 2004 ro@suse.de
- fixed typo in boot.localfs (#47808)
* Fri Oct 29 2004 ro@suse.de
- Removed dependencies from /etc/init.d/boot.clock
  Clock is now set correctly before a dump is taken (#42376)
* Fri Oct 29 2004 sndirsch@suse.de
- xdm init script:
  * added kbd to Required-Start (Bug #47388)
* Tue Oct 26 2004 schwab@suse.de
- Spelling fixes.
* Wed Oct 20 2004 werner@suse.de
- Group splash functionality into one /etc/rc.splash file
* Wed Oct 20 2004 sndirsch@suse.de
- xdm init script: fixed PIDFILE for kdm/gdm (Bug #47292)
* Wed Oct 13 2004 werner@suse.de
- Make the make like boot behaviour to the default (bug #45191).
* Tue Oct 12 2004 lmuelle@suse.de
- Use TERM instead of SIGTERM in rc.status as SIGTERM is unknown by /bin/kill.
* Tue Oct 12 2004 ro@suse.de
- adding entry for sysfs to fstab (#46821)
* Mon Oct 11 2004 ro@suse.de
- boot script: call /usr/lib/YaST2/startup/YaST2.Second-Stage
  for continue mode if present (#46886)
* Mon Oct 11 2004 ro@suse.de
- boot.localnet: tmp-race when removing old ssh-agent sockets
  (#47063) and handle /var/lock like /var/run
* Wed Oct  6 2004 ro@suse.de
- changed comment in sysconfig.sysctl (#46880)
* Mon Oct  4 2004 mls@suse.de
- set progressbar to full at end of halt script
- don't call /sbin/splash if /proc was unmounted
* Sun Oct  3 2004 ro@suse.de
- default PROXY_ENABLED to no in sysconfig.proxy (#46635)
* Fri Oct  1 2004 ro@suse.de
- reversed sequence of boot.klog and boot.crypto
  (makes kernel log messages go to console 10 a bit earlier
  for the normal case)
* Fri Oct  1 2004 werner@suse.de
- Make xterm title in prompt work even with multibyte characters
- boot.crypto: redraw passphrase prompt all 2 seconds
* Wed Sep 29 2004 mls@suse.de
- call splash with -S option if system gets halted
- show "system is down" message
* Thu Sep 23 2004 werner@suse.de
- Detect swap partitiion even with new label (bug #45912)
* Thu Sep 23 2004 werner@suse.de
- Redirect error messages to stderr in safe-rm
* Thu Sep 23 2004 mls@suse.de
- call splash with $pos:$delta for animated progress bar
- don't print boot.* services in 'chkconfig -l' if they are
  off in all runlevels
* Thu Sep 23 2004 ro@suse.de
- removed boot.quota from Start line in boot.localnet,boot.ldconfig
  (needs to run later #43564)
* Wed Sep 22 2004 ro@suse.de
- use safe-rmdir in suse.de-clean-tmp (#45612)
- remove suse.de-clean-vi
* Wed Sep 22 2004 werner@suse.de
- Make safe-rm more safer and implement a safe-rmdir (bug #45629)
* Mon Sep 20 2004 mls@suse.de
- complete overhaul of bootsplash progressbar/event handling
* Mon Sep 20 2004 werner@suse.de
- Re-enable further hdparm options for (E)IDE/ATA disks.
* Mon Sep 20 2004 garloff@suse.de
- Remove boot.sched from forced insserv in %%post.
* Mon Sep 20 2004 garloff@suse.de
- boot.sched: Handle def-timeslice (instead of max-timeslice).
* Sat Sep 18 2004 ro@suse.de
- updated alljava.sh,alljava.csh (#45555)
* Fri Sep 17 2004 ro@suse.de
- updated java handling (from skh)
  new /usr/bin/setJava
  removed /usr/bin/setJava.pl,/sbin/conf.d/SuSEconfig.alljava
  removed /var/adm/fillup-templates/sysconfig.java
* Fri Sep 17 2004 werner@suse.de
- Be sure that tcsh rehash internal locale settings in csh.utf8
* Thu Sep 16 2004 werner@suse.de
- Catch Ctrl-C first in boot script (bug #36728)
* Mon Sep 13 2004 ro@suse.de
- make startx a bit smarter (#44822)
* Mon Sep 13 2004 werner@suse.de
- Re-enable complete even for bash version 3.00 (bug #45050)
* Wed Sep  8 2004 adrian@suse.de
- change X-UnitedLinux-Should-Start to Should-Start
- xdm startup does not wait for hwscan anymore
* Mon Sep  6 2004 ro@suse.de
- updated SuSEconfig.alljava and /etc/profile.d/alljava.*sh (skh)
* Sat Sep  4 2004 werner@suse.de
- Fix cut&paste error in /etc/init.d/boot
* Fri Sep  3 2004 werner@suse.de
- Switch to new startpar with make like behaviour
- Disable this feature for now
* Wed Sep  1 2004 werner@suse.de
- Make spaces on path names on ~ expansion work (bug #43792)
* Tue Aug 31 2004 ro@suse.de
- clean up notify messages
* Mon Aug 30 2004 ro@suse.de
- added variables MAX_DAYS_IN_LONG_TMP and LONG_TMP_DIRS_TO_CLEAR
- added code to handle these in cron-cleanup-tmp (#43701)
* Sat Aug 28 2004 schwab@suse.de
- rc.status: use size of terminal connected to stdout, not stdin.
* Sat Aug 28 2004 ro@suse.de
- fix missing "fi" in /etc/init.d/boot
* Wed Aug 25 2004 werner@suse.de
- Make counter varaible to a local one in rc.status
- Provide a Makefile for booting
  * Enable parallel boot with make
  * Todo: get the status of each service from the make
* Fri Aug 20 2004 ro@suse.de
- set MAIL_LEVEL to warn on SLES
* Tue Aug 17 2004 ro@suse.de
- implement new update-messages in SuSEconfig.zmessages
- default MAIL_LEVEL to new value "off"
* Thu Aug 12 2004 ro@suse.de
- added GPL boilerplate to /etc/init.d/skeleton (#43581)
* Wed Aug 11 2004 nashif@suse.de
- firstboot should start before xdm.
* Fri Aug  6 2004 ro@suse.de
- boot.localfs: MODULES_DIR is not defined, don't use
* Fri Jul 23 2004 ro@suse.de
- fix typo in /etc/cron.daily/suse.de-check-battery (#32007)
* Tue Jul  6 2004 sndirsch@suse.de
- xdm init script:
  * gdm needs option "--no-console" if no local Xserver should be
    started (Bug #42787)
* Mon Jun 21 2004 ro@suse.de
- re-activate nfs rc-script by default (#41672)
- remove ShouldStart for nfslock in nfs rc-script (obsolete)
* Tue Jun 15 2004 ro@suse.de
- added image/x-ico to /etc/mime.types (#42025)
* Tue May 25 2004 ro@suse.de
- usr/sbin/Check: quote to catch filenames with spaces (#41003)
- usr/sbin/Check: use "-n" with gzip
* Tue May 25 2004 ro@suse.de
- etc/profile: for iSeries fix condition to call initviocons
  (#41105)
* Wed May 12 2004 ro@suse.de
- mime.types: added OOo mimetypes (#38546)
- mailcap: replaced lynx with w3m
* Mon May 10 2004 ro@suse.de
- update java handling scripts (#39482)
* Thu May  6 2004 kukuk@suse.de
- Change primary group of nobody with usermod and don't add it
  twice [Bug #39969]
- Set LC_ALL to C in pre/post script [Bug #39968]
- Fix Description in sysconfig templates [Bug #39932]
* Thu Apr 29 2004 werner@suse.de
- Add info to cryptotab aka nick name of the device (bug #39344)
* Wed Apr 28 2004 bk@suse.de
- S390: update inittab patch: use mingetty for login(not sulogin)
- S390: add arch_special patch for sysconfig.displaymanager
* Fri Apr 23 2004 ro@suse.de
- added IPV6_MLD_VERSION to sysconfig/sysctl to be able
  to workaround bugs in other networking hardware
* Thu Apr 22 2004 ro@suse.de
- re-create nroff source for resolv+ man-page (#39246)
* Tue Apr 20 2004 ro@suse.de
- /usr/sbin/Check: don't pack source-control files (#39103)
* Fri Apr 16 2004 ro@suse.de
- don't try to fix swap-sig on platforms without resume (#38929)
* Thu Apr 15 2004 ro@suse.de
- fix boot.rootfsck (#38953)
* Wed Apr 14 2004 ro@suse.de
- boot.idedma: more robust against wrong settings (#38829)
* Wed Apr 14 2004 werner@suse.de
- Fix some typos in init.d.7 (used for /etc/init.d/README),
  correction from tervde@hawkmoon.mn.org
* Thu Apr  8 2004 werner@suse.de
- Change /etc/profile.d/sh.utf8 respectivly /etc/profile.d/csh.utf8
  to support the reverse case of removing .UTF-8 from LANG (#35091)
* Tue Apr  6 2004 ro@suse.de
- /usr/sbin/Check: use new -root option for chkstat (c-version)
* Fri Apr  2 2004 kukuk@suse.de
- Cleanup /var/lock/lvm in boot.localnet
* Thu Apr  1 2004 ro@suse.de
- boot.rootfsck: only try to check filesystem if we have the
  needed device node (real fix will need device mapper started
  before boot.rootfsck)
* Thu Apr  1 2004 schwab@suse.de
- .inputrc: Add bindings for Alt modified cursor keys.
* Thu Apr  1 2004 kukuk@suse.de
- Don't delete files in all subdirectories in /var/lock [#37759]
- Delete __db* files in /var/lib/rpm
* Wed Mar 31 2004 ro@suse.de
- boot.crypto: load loop_fish2 also for twofish* (#36872)
* Wed Mar 31 2004 ro@suse.de
- added try-restart for rcnfs and rcxdm (#37613)
* Tue Mar 30 2004 ro@suse.de
- move depmod-code to /sbin/update-modules.dep to avoid
  missing one of two places all the time
- update SuSEconfig.alljava: support BEAJava2 if installed
* Tue Mar 30 2004 agruen@suse.de
- #37509: `depmod -a' didn't always get run when needed at boot
  time.
* Tue Mar 30 2004 werner@suse.de
- Changes within /etc/profile and /etc/csh.cshrc to source
  the new files /etc/profile.d/sh.utf8 respectivly
  /etc/profile.d/csh.utf8 if the new variable in
  /etc/sysconfig/language AUTO_DETECT_UTF8 is set to "yes".
  Beside this the files can be sourced by the users
  ~/.profile or ~/.login.  This is for bugzilla #35091.
* Sun Mar 28 2004 garloff@suse.de
- Update comments in skeleton. Should-Start/Stop are official now.
- Don't change ulimits in /etc/profile if they are set by
  /etc/initscript (ulimit package, see #34323).
* Fri Mar 26 2004 ro@suse.de
- added "manual" to "ifup lo" in boot.localnet
* Fri Mar 26 2004 werner@suse.de
- Be sure to get a valid device if showconsole fails (bug #36870)
* Wed Mar 24 2004 werner@suse.de
- Fix cut&paste error within boot.crypto
* Wed Mar 24 2004 ro@suse.de
- replace /etc/modules.conf by /etc/modprobe.conf in SuSEconfig
- boot.localnet: check if find is present and work around if not
  (fix for /usr on nfs)
- integrate cshrc patch
* Wed Mar 24 2004 mjancar@suse.cz
- boot.localfs: replace /etc/modules.conf by /etc/modprobe.conf
* Tue Mar 23 2004 mls@suse.de
- chkconfig: remove extra spaces in --list output (#32226)
- chkconfig: fix exit status in --set (#33700)
- chkconfig: add undocumented --level option (#34379)
* Tue Mar 23 2004 mmj@suse.de
- /var/tmp should not be in TMP_DIRS_TO_CLEAR pr. default
* Tue Mar 23 2004 werner@suse.de
- Set traps for SIGINT not only in rc but also in boot (bug #36728)
- Add some lines to rc and boot for extended bootcycle (bug #32641)
- Add some magic shell lines for restoring swap partitions
* Mon Mar 22 2004 ihno@suse.de
- delete *.orig files
* Wed Mar 17 2004 ro@suse.de
- add etc/init.d/ to calls for insserv_force_if_yast in postinstall
* Tue Mar 16 2004 mfabian@suse.de
- Bugzilla #36155: use "set dspmbyte euc" also for locales
  which use GB2312 charmap because Chinese input via xcin
  won't work in tcsh if this is not set.
* Tue Mar 16 2004 ro@suse.de
- clean /etc/mtab already after mounting root-fs
* Tue Mar  9 2004 ro@suse.de
- add some quotes to boot.localfs
* Mon Mar  8 2004 ro@suse.de
- boot.clock: also start for "single" (#35413)
* Sun Mar  7 2004 ro@suse.de
- boot.rootfsck: remove bklid-cache tmpfile in /dev/shm
- boot.localfs: update blkid-cache first
* Fri Mar  5 2004 ro@suse.de
- removed SuSEconfig.hostname
- removed sysconfig variables CHECK_ETC_HOSTS
  and BEAUTIFY_ETC_HOSTS (no longer used)
- removed no longer existing modules from SuSEconfig --quick
* Thu Mar  4 2004 ro@suse.de
- mount /dev/shm with -n flag (/ is still ro at that time)
- move last redirect & reexec call in halt-script after killall5
* Tue Mar  2 2004 ro@suse.de
- don't try to check root-fs if root-fs is nfs
* Tue Mar  2 2004 ro@suse.de
- split boot.shm from boot.swap (and mount shm real early)
- split boot.rootfsck from boot.localfs
* Mon Mar  1 2004 mmj@suse.de
- Fix reference to SDB [#35191]
* Wed Feb 25 2004 ro@suse.de
- remove 2.2-kernel hack in boot.localfs (#34942)
- go straight into reboot if fsck tells us so (#34815)
* Tue Feb 24 2004 sndirsch@suse.de
- xdm init script:
  * fixed start() (when xdm is used) and probe(); PIDFILE is now
    <filename> instead of "-p <filename>" before
* Mon Feb 23 2004 snwint@suse.de
- get_kernel_version: drop gzip warning (#21057)
* Mon Feb 23 2004 ro@suse.de
- /root/.gnupg/suse_build_key and pubring.gpg mode 0600 (#31982)
* Mon Feb 23 2004 ro@suse.de
- updated xemacs info-dir list in mkinfodir (#34844)
* Sat Feb 21 2004 schwab@suse.de
- Remove redirections on stty calls, can cause spurious job control
  signals.
* Fri Feb 20 2004 stepan@suse.de
- fix #31289 (progress bar walking backwards)
* Wed Feb 18 2004 ro@suse.de
- move modprobe.conf to module-init-tools package
* Wed Feb 18 2004 msvec@suse.cz
- fixed spelling in the boot message
* Tue Feb 17 2004 ro@suse.de
- add K*-links in /etc/init.d/boot.d on update
* Tue Feb 17 2004 ro@suse.de
- update for boot.idedma from Ladislav
* Tue Feb 17 2004 ro@suse.de
- prepare split of /etc/init.d/halt script
  K*-links in /etc/init.d/boot.d are not yet present
* Mon Feb 16 2004 ro@suse.de
- clean_tmp_at_bootup: take care of files starting with -
* Sun Feb 15 2004 olh@suse.de
- update /etc/DIR_COLORS, no bright for .cmd suffix. it hurts
* Fri Feb 13 2004 kukuk@suse.de
- etc/init.d/skeleton: Fix syntax error
* Fri Feb 13 2004 ro@suse.de
- handle /var/run/{u,}screens (#32814)
* Thu Feb 12 2004 ro@suse.de
- removed modules.conf and it's handling
- modprobe.conf will hopefully move to module-init-tools
- removed outdated notify mails
- removed ULconfig hack
* Sat Feb  7 2004 sndirsch@suse.de
- sysconfig.displaymanager:
  * added DISPLAYMANAGER_XSERVER_TCP_PORT_6000_OPEN
* Thu Feb  5 2004 sndirsch@suse.de
- sysconfig.displaymanager:
  * improved description for DISPLAYMANAGER_REMOTE_ACCESS (#34238)
* Sat Jan 31 2004 sndirsch@suse.de
- sysconfig.displaymanager:
  * document, that DISPLAYMANAGER_REMOTE_ACCESS setting is currently
    only used for XDM (Bug #34238)
* Thu Jan  8 2004 ro@suse.de
- fix typo in last change
* Thu Jan  8 2004 ro@suse.de
- etc/profile: don't add $HOME/bin to PATH if HOME="/"
- boot.localnet: avoid possible errors on cleaning temporary dirs
  (#33678)
* Wed Jan  7 2004 kukuk@suse.de
- Remove nsswitch.conf manual page (is now part of man-pages)
* Sat Dec 20 2003 sndirsch@suse.de
- modprobe.conf.common:
  * fixed alias for nvidia kernel module
* Wed Dec 10 2003 werner@suse.de
- Redirect tty in boot.crypto only in interactive case (bug #32014)
* Wed Dec 10 2003 kukuk@suse.de
- Backup /etc/gshadow and merge passwords into /etc/group on update
* Tue Dec  9 2003 ro@suse.de
- added gpm as Should-Start tag to /etc/init.d/xdm
  (needed if gpm is used as repeater) (#33576)
* Thu Dec  4 2003 ro@suse.de
- added man pages for SuSEconfig.8, quick_halt.8, safe-rm.8)
* Thu Dec  4 2003 ro@suse.de
- for now, rename /etc/sysconfig/hardware to /etc/sysconfig/ide
- /etc/sysconfig/hardware will be a directory for the new
  hwconfig stuff (see package sysconfig)
* Tue Dec  2 2003 kukuk@suse.de
- Move nscd files into nscd package
* Mon Dec  1 2003 kukuk@suse.de
- Move /etc/netgroup to netcfg package
* Thu Nov 27 2003 kukuk@suse.de
- Move /etc/ld.so.conf to glibc package [Bug #33277]
- Move /etc/nsswitch.conf to glibc package
* Tue Nov 18 2003 ro@suse.de
- added "Command: /sbin/mkinitrd" for INITRD_MODULES (#28888)
* Mon Nov 17 2003 sndirsch@suse.de
- modprobe.conf changes:
  * removed agpgarti810 alias (module no longer exists)
  * removed "agp_try_unsupported" option for agpgart (option no
    longer exists in kernel 2.6)
  * removed preinstall lines for DRM modules; specific agp module
    (+ apgart module) is now loaded automatically by new
    hotplug(-beta) tools
* Fri Nov 14 2003 schwab@suse.de
- /etc/init.d/boot.klog: fix quoting.
* Fri Nov 14 2003 sndirsch@suse.de
- xdm script:
  * create/remove xdm-pid/xdm-error symlinks in /etc/X11/xdm on the
    fly if xdm is started/stopped
* Mon Nov 10 2003 garloff@suse.de
- skeleton: return 0 for stop, even if binary or config file are
  missing. (Reasoning: See kukuk post on packagers, 2003-11-07.)
* Thu Oct 30 2003 schwab@suse.de
- /etc/init.d/halt: handle usbfs like usbdevfs.
* Mon Oct 20 2003 ro@suse.de
- Check: try to set permissions even if non-root, but do it
  only below RPM_BUILD_ROOT (and if that is set)
* Sat Oct 18 2003 kukuk@suse.de
- Don't generate /etc/gshadow any longer
- Build as normal user
- Add SELinux support
* Sat Oct 11 2003 schwab@suse.de
- Don't try to set resource limits beyond current hard limit.
- ksh has ulimit -s.
* Tue Oct  7 2003 ro@suse.de
- boot.localfs: don't mount filesystems marked as _netdev (#26148)
* Mon Oct  6 2003 ro@suse.de
- fixed cron.daily/suse.de-check-battery for ppc (#32007)
* Mon Oct  6 2003 ro@suse.de
- fix nobody entry in etc/shadow if sp_lstchg set to 0 (#32011)
* Mon Oct  6 2003 werner@suse.de
- In case of stop do umounting in reverse order (bug #32013)
* Mon Sep 22 2003 werner@suse.de
- Fix bzip2/gzip -cd completion (bug #31517)
* Sun Sep 21 2003 mfabian@suse.de
- Bugzilla #31451: use a simpler bash prompt for UTF-8 locales.
  Fancy stuff like setting the xterm title bar breaks commandline
  editing in bash in UTF-8 locales. That is probably a bash
  bug, but until this is fixed, using a simpler prompt is a good
  workaround.
* Sat Sep 20 2003 garloff@suse.de
- Fix comments before timeslices in sysconfig.kernel. Default to
  not change them, do issue an "unused" message in this case.
* Fri Sep 19 2003 ro@suse.de
- always make sure tmpdirs exist during boot (#31308)
  (/tmp /tmp/.X11-unix /tmp/.ICE-unix /var/tmp /var/tmp/vi.recover)
* Thu Sep 18 2003 werner@suse.de
- Do not boot in parallel in interactive mode (bug #31195)
* Thu Sep 18 2003 ro@suse.de
- keep char-major-81-[0-9] from modules.conf on update (#31239)
* Wed Sep 17 2003 ro@suse.de
- re-added /opt/gnome/bin (too many problems)
* Tue Sep 16 2003 ro@suse.de
- removed /opt/gnome/bin and /opt/gnome2/bin from PATH (#30844)
* Mon Sep 15 2003 werner@suse.de
- Terminate all vlock sessions to unlock VT switching (bug# 30827)
* Mon Sep 15 2003 sndirsch@suse.de
- xdm script:
  * source /etc/profile.d/desktop-data.sh if it exists (Bug #30850)
* Thu Sep 11 2003 werner@suse.de
- Fix typo in boot.crypto script (bug #30526)
* Wed Sep 10 2003 uli@suse.de
- OK, so in IBMspeak(tm) VT220 means linux. Whatever...
* Wed Sep 10 2003 uli@suse.de
- added commented-out entry for VT220 terminal on s390* to
  /etc/inittab (bug #29239)
- added correct terminal types for 3215/3270 and VT220 consoles
  on s390* to /etc/ttytype (bugs #29239, #29240)
* Wed Sep 10 2003 ro@suse.de
- boot.localnet: call ifup with "-o rc" (#30377)
- set char-major-212 to off (#29202)
* Mon Sep  8 2003 ro@suse.de
- rpmv4 package db filename is Packages, not packages.rpm (#30257)
* Mon Sep  8 2003 ro@suse.de
- added java-jnlp types to mime.types and mailcap
* Mon Sep  8 2003 garloff@suse.de
- boot.sched: Read /proc/sys/kernel/HZ and leave sched timslices
  alone if HZ non-existing. If it is, make sure, min-timeslice
  is larger than the minimum. Scale max-timeslice if min-timeslice
  needed adjustment.
- Update comments in sysconfig.kernel file.
* Fri Sep  5 2003 werner@suse.de
- Fix console handling in case of a serial line
- Try to fix bug #30138 -- switch back to tty1 for halt/reboot
* Thu Sep  4 2003 werner@suse.de
- Fix the cd TAB expansion (bug #29631, #29734)
* Thu Sep  4 2003 draht@suse.de
- #30100: /etc/init.d/boot.localnet /var/tmp/vi.recover symlink
  race condition security fix.
* Wed Sep  3 2003 ro@suse.de
- sysconfig/kernel: keep INITRD_MODULES as first variable (#29931)
* Wed Sep  3 2003 werner@suse.de
- Enable umount to run losetup -d (bug #29523)
* Tue Sep  2 2003 ro@suse.de
- bootup-clean in boot.localnet: only remove files below /var/run
* Tue Sep  2 2003 ro@suse.de
- CLEAR_TMP_DIRS_AT_BOOTUP can also be a list of directories
  allowing to have a separate list for this task (#27358)
* Tue Sep  2 2003 kukuk@suse.de
- bash.bashrc: use absolute path to ls [Bug #29013]
* Mon Sep  1 2003 garloff@suse.de
- skeleton, bug #29589: Update comments.
- skeleton: Support condrestart, but warn user to use LSB syntax.
* Fri Aug 29 2003 mjancar@suse.cz
- add /etc/modprobe.conf (#28263)
* Fri Aug 29 2003 mfabian@suse.de
- Bugzilla #29629: source /etc/sysconfig/language in
  /etc/init.d/xdm.
* Fri Aug 29 2003 ro@suse.de
- changed setup for cfg-files: one file with full filelist entries
* Thu Aug 28 2003 ro@suse.de
- removed all occurences of feedback@suse.de and replaced
  them with hints to http://www.suse.de/feedback
* Tue Aug 26 2003 agruen@suse.de
- Update sysconfig meta information for ACPI DSDT in
  (/etc/sysconfig/kernel).
* Tue Aug 26 2003 ro@suse.de
- added windowmaker to windowmanagers sysconfig comment (#29172)
* Mon Aug 25 2003 garloff@suse.de
- Add parameters SCHED_MIN/MAXTIMESLICE to sysconfig.kernel.
- Add boot.sched init script that sets the kernel CPU scheduler
  timeslices.
* Fri Aug 22 2003 trenn@suse.de
- Modified sysconfig-parts/sysconfig.kernel:
  settings to load own DSDT with mk_initrd added
* Thu Aug 21 2003 werner@suse.de
- Do not overwrite tty line settings on SSH remote lines (#29012)
* Mon Aug 18 2003 garloff@suse.de
- boot.localfs: Should start boot.scsidev before (#29083)
- rc.config: Add /sbin:/usr/sbin to PATH if no sbin in PATH found.
- skeleton: force-reload should act like try-restart if signalling
  is not supported (#28687).
* Mon Aug 18 2003 ro@suse.de
- complete shmfs fix (#28704)
* Mon Aug 18 2003 ro@suse.de
- added/updated realplayer entries in mailcap and mime.types
* Fri Aug 15 2003 draht@suse.de
- /etc/init.d/boot: "Mounting /proc device" -> "/proc filesystem"
* Fri Aug 15 2003 ro@suse.de
- added "restart" targets for most boot.xy start-files
- added metadata for sysconfig files
* Fri Aug 15 2003 ro@suse.de
- shmfs is no longer supported in 2.6 kernels, use tmpfs which is
  the same anyway (#28704)
* Thu Aug 14 2003 ro@suse.de
- added sysconfig variable IPV6_PRIVACY
* Tue Aug 12 2003 ro@suse.de
- load ipv6 module if IPV6_FORWARD is set to "yes" (#28553)
* Mon Aug 11 2003 garloff@suse.de
- /etc/init.d/skeleton: Consider a not running service a success
  in try-restart function. Document that try-restart is in LSB now.
* Sat Aug  9 2003 stepan@suse.de
- add deleted bootsplash hooks in /etc/init.d/boot again.
* Fri Aug  8 2003 ro@suse.de
- syconfig/printer is gone (#27259)
* Wed Aug  6 2003 ro@suse.de
- changed gdm path to /opt/gnome/bin ...
* Thu Jul 31 2003 poeml@suse.de
- change group of wwwrun user from nogroup to www [#21782]
- change login shell of wwwrun user from /bin/bash to /bin/false
* Wed Jul 30 2003 mfabian@suse.de
- send notify mails with correct charset from SuSEconfig.
  (notify files can be either in ISO-8859-15 or UTF-8 encoding).
* Mon Jul 28 2003 ro@suse.de
- always move include local file last in modules.conf (#27681)
- change gdm path to /usr/bin (#28226)
* Sat Jul 26 2003 mludvig@suse.cz
- Added aliases for tunnel devices (sit, gre, ipip) to modules.conf
* Fri Jul 25 2003 werner@suse.de
- More work on base completion (fix bug #18329 partly)
* Thu Jul 24 2003 agruen@suse.de
- Add check for bash_completion script to bash.bashrc: This
  script can be installed from the bash-completion package.
* Tue Jul 22 2003 schwab@suse.de
- Fix use of sort.
- Fix more uses of chown.
* Wed Jul 16 2003 schwab@suse.de
- Fix chown syntax: use colon instead of period between user and group.
* Mon Jul 14 2003 uli@suse.de
- reenabled ctrlaltdel in /etc/inittab on s390*, can be triggered
  with z/VM 4.3 command "SIGNAL SHUTDOWN ..."
* Mon Jul 14 2003 kukuk@suse.de
- useradd.local is now part of shadow package
* Fri Jul  4 2003 lmb@suse.de
- Fix build on s390(x) broken by previous change.
* Fri Jul  4 2003 lmb@suse.de
- Fix dependencies for boot.lkcd and make sure swap isn't clobbered
  before the dump has been recovered (#26727)
* Tue Jul  1 2003 sndirsch@suse.de
- removed .xinitrc from filelist (not required any longer); better
  use the global xinitrc in /etc/X11/xinit/
* Mon Jun 23 2003 ro@suse.de
- remove leftover ssh-agent sockets on boot (#27463)
- don't check for active xntp when writing clock back to cmos
  (#27378)
- mount sysfs if available on boot (#27449)
* Tue Jun 17 2003 werner@suse.de
- Add new parallel featured boot scripts
* Mon Jun  2 2003 ro@suse.de
- also remove /tmp/uscreens when /tmp/screens are removed
  during boot (#26871)
* Tue May 27 2003 ro@suse.de
- added /opt/gnome/info to info dirs in Check script
* Mon May 26 2003 ro@suse.de
- implement try-restart in nscd start-script (#27128)
* Thu May 22 2003 agruen@suse.de
- Split: put mkinitrd in its own package.
* Fri May 16 2003 werner@suse.de
- Next step on parallel boot scheme: reduce I/O calls
* Thu May 15 2003 ro@suse.de
- mk_initrd: call insmod with full module path
* Mon May  5 2003 ro@suse.de
- Check: don't try to gzip bzipped files (#21121)
* Mon May  5 2003 ro@suse.de
- corrected comment in /etc/inittab
* Tue Apr 29 2003 werner@suse.de
- First try of a parallel boot scheme
* Tue Apr 15 2003 mls@suse.de
- mk_initrd: integrate dhcp support
* Tue Apr  8 2003 ro@suse.de
- try workaround for wrong depmod if running kernel is different
  from installed kernel (#26114)
* Mon Apr  7 2003 ro@suse.de
- changed SuSEconfig.profiles: don't export RC_foo (#24637)
* Mon Apr  7 2003 kukuk@suse.de
- Fix mk_initrd for modules ending with *.ko (kernel 2.5.xx)
- Make head/tail calls POSIX conform
* Fri Apr  4 2003 ro@suse.de
- changed version to BUILD_DISTRIBUTION_VERSION
* Fri Apr  4 2003 msvec@suse.de
- fixed broken sorting order (#24637)
* Thu Apr  3 2003 schwab@suse.de
- Fix trailing space in /etc/init.d/xdm.
* Tue Apr  1 2003 stepan@suse.de
- update mk_initrd to look in /etc/bootsplash and have nicer
  user notification
* Tue Apr  1 2003 ro@suse.de
- rcnfs: changed comment: added another sleep before
  example for backgrounded mount
* Thu Mar 20 2003 sndirsch@suse.de
- sysconfig.displaymanager: fixed description for s390 (Bug #21236)
- xdm init script: don't any longer start xdm, if no Xserver is
  configured and remote access is not enabled (Bug #25154)
* Tue Mar 18 2003 ro@suse.de
- added ntp-pf-31 and bt-proto-[0234] to modules.conf (#25525)
- don't use wc in /etc/init.d/rc (#25572)
* Tue Mar 18 2003 werner@suse.de
- Re-enable Ctrl/Shift cursors keys of new XTerm for readline lib
  (bug #25528)
* Thu Mar 13 2003 kukuk@suse.de
- Only change ftp home directory of user does not modify it
  [Bug #25245]
* Tue Mar 11 2003 ro@suse.de
- start boot.loadmodules before boot.idedma
  (otherwise the devices need not be present)
* Tue Mar 11 2003 schwab@suse.de
- chkconfig: don't fail if /sbin is not in $PATH (lost change).
* Mon Mar 10 2003 snwint@suse.de
- added '-P' to df to fix initrd size calculation (#24984)
* Mon Mar 10 2003 ro@suse.de
- add /dev/md0 to initrd in mkinitrd (#24959)
* Sun Mar  9 2003 ro@suse.de
- support blackdown-jre in SuSEconfig.alljava
- really activate /etc/init.d/boot.loadmodules (#24922)
* Fri Mar  7 2003 ro@suse.de
- removed SuSEconfig.doublecheck (e.g. apache vs. apache2 will
  always have duplicates) (#20568)
* Wed Mar  5 2003 ro@suse.de
- provide mkinitrd
* Mon Mar  3 2003 ro@suse.de
- removed outdated part of comment in sysconfig/language (#24535)
* Fri Feb 28 2003 ro@suse.de
- clean-tmp cron.daily-script: leave pipes alone (like sockets)
* Thu Feb 27 2003 ro@suse.de
- moved named user to bind packages
* Thu Feb 27 2003 ro@suse.de
- removed the gdm-binary hack (/etc/init.d/xdm)
- removed the attr hack from mk_initrd
* Wed Feb 26 2003 ro@suse.de
- mk_initrd: copy libattr with bin/cat ...
* Tue Feb 25 2003 werner@suse.de
- Beautify mkinfodir and let it support title lines
* Fri Feb 21 2003 ro@suse.de
- merged mime.types with apache2 table (#23988)
- corrected url in mime.types
* Wed Feb 19 2003 ro@suse.de
- fix 20034 again (HISTCONTROL=ignoreboth)
* Wed Feb 19 2003 werner@suse.de
- Fix complete.bash just for the case that IFS is initial unset
* Tue Feb 18 2003 ro@suse.de
- export HISTSIZE in /etc/profile
* Mon Feb 17 2003 mls@suse.de
- don't pack devices into initrd, ash will create them with
  createpartitiondevs
* Fri Feb 14 2003 ro@suse.de
- update boot.idedma and sysconfig.hardware from lslezak
* Wed Feb 12 2003 werner@suse.de
- Fix bug #23105: get all info entries with mkinfodir
* Tue Feb 11 2003 ro@suse.de
- Check: add pfm files to blacklist
- Check: only work below buildroot if UID!=0
* Mon Feb  3 2003 ro@suse.de
- expanded list of vga= lines in mk_initrd
* Thu Jan 30 2003 ro@suse.de
- removed SuSEconfig.man_info: mkinfodir is called by YaST
  if needed (and packages should call install-info during
  installation if not running under YaST)
- removed SuSEconfig.aaa_at_first: ldconfig is called by YaST
* Wed Jan 29 2003 mls@suse.de
- new version of chkconfig that understands inetd/xinetd services
* Wed Jan 29 2003 ro@suse.de
- removed explicit requires for acl
* Tue Jan 28 2003 sndirsch@suse.de
- enabled Xcursor themes for xdm again; "core" theme with old
  behaviour is now default
* Mon Jan 27 2003 ro@suse.de
- add variable IPV6_FORWARD
* Mon Jan 27 2003 ro@suse.de
- expand blacklist in Check
* Fri Jan 24 2003 sndirsch@suse.de
- disabled Xcursor themes for xdm
* Thu Jan 23 2003 ro@suse.de
- removed SuSEconfig.fonts (in xf86tools package)
* Mon Jan 20 2003 stepan@suse.de
- source /etc/sysconfig/bootsplash before defining rc_splash only
- fix splash binary path in rc.status
* Fri Jan 17 2003 ro@suse.de
- fix include statement in modules.conf
* Thu Jan 16 2003 ro@suse.de
- xinitrc might not be present in /etc/skel
* Thu Jan 16 2003 ro@suse.de
- added modules.conf.local as cfg-noreplace
* Thu Jan 16 2003 ro@suse.de
- revert gid of "users" to 100 (move postponed)
* Wed Jan 15 2003 ro@suse.de
- split off insserv to own package
* Wed Jan 15 2003 ro@suse.de
- added boot.loadmodules script (#19376)
- added MODULES_LOADED_ON_BOOT to sysconfig/kernel
* Tue Jan 14 2003 sndirsch@suse.de
- xdm init script: it's possible again to specify xdm as WM
* Mon Jan 13 2003 ro@suse.de
- Check: don't gzip fonts.cache*
* Fri Jan 10 2003 werner@suse.de
- let XTerm know about current directory
* Fri Jan  3 2003 stepan@suse.de
- incorporate bootsplash patch into aaa_base
- update progress bar hooks
* Thu Dec 19 2002 werner@suse.de
- Do not set unedit for tcsh running in ansi-term/shell mode
  (should work in shell mode of emacs 21 and is required for
  ansi-term).
* Tue Dec 17 2002 msvec@suse.de
- possibility to turn the proxy on|off (PROXY_ENABLED)
- comment for GOPHER_PROXY
* Mon Dec 16 2002 ro@suse.de
- removed sysconfig_parts-bootsplash.dif
* Fri Dec 13 2002 ro@suse.de
- added patch to mkinitrd for future modutils (mcihar@suse.cz)
* Tue Dec 10 2002 ro@suse.de
- updated sysconfig templates with versions from lslezak
* Fri Dec  6 2002 werner@suse.de
- More changes for rc_check and rc_status: remember local status upto
  the next verbose output of the state.
* Thu Dec  5 2002 bk@suse.de
- mkinitrd update:
  o check packaged programs for missing libraries
  o handle signals which terminate with proper cleanup and exit
  o show the error messages from mount to help in case of problems
  o employ safer names for temp files using mktemp for the temp dir
* Wed Dec  4 2002 werner@suse.de
- Make rc_check to see a difference between local and global status
* Tue Dec  3 2002 ro@suse.de
- gid for users is 500 for new installations
* Thu Nov 28 2002 werner@suse.de
- Just an other enhancment (and fix for bug #21940) for complete.bash
* Mon Nov 25 2002 ro@suse.de
- another place to mount proc before access (#21965)
* Mon Nov 25 2002 ro@suse.de
- fix typo in SuSEconfig.profiles (#17651)
* Fri Nov 22 2002 sndirsch@suse.de
- SuSEconfig.fonts:
  * call 'fc-cache' to create 'font.cache' files if necessary;
    these are required by Xft1/Xft2
* Thu Nov 21 2002 draht@suse.de
- added iso suffix to /etc/mime.types, type octet-stream.
* Tue Nov 19 2002 mfabian@suse.de
- call /usr/sbin/cidfont-x11-config from SuSEconfig.fonts
* Mon Nov 18 2002 stepan@suse.de
- update aaa_base-bootsplash.dif to use /sbin/splash.sh instead of
  splash.sh
* Mon Nov 18 2002 olh@suse.de
- update mk_initrd to sles8 status
* Mon Nov 18 2002 stepan@suse.de
- split bootsplash.diff into aaa_base-bootsplash.dif and
  sysconfig_parts-bootsplash.dif.
- add script counter and additional hooks for progress
  measuring (bootsplash)
* Fri Nov 15 2002 kukuk@suse.de
- etc/nsswitch.conf: Remove dns6, remove libc5 from compat descr.
  [Bug #21784]
* Tue Nov 12 2002 ro@suse.de
- updated neededforbuild
* Mon Nov 11 2002 schwab@suse.de
- chkconfig: don't fail if /sbin is not in $PATH.
* Tue Nov  5 2002 ro@suse.de
- cut /... from IPADDR in SuSEconfig.hostname (#21524)
* Tue Nov  5 2002 ro@suse.de
- added "tty-ldisc-2 serio" to modules.conf.common (#21215)
* Tue Nov  5 2002 ro@suse.de
- etc/init.d/boot.klog: if no klogconsole is found, use dmesg
  to set the kernel loglevel
* Mon Nov  4 2002 ro@suse.de
- added ",v" as file-ending to be ignored in SuSEconfig.doublecheck
  (#21508)
* Wed Oct 30 2002 ro@suse.de
- added xf86 to neededforbuild (for /etc/skel/.xinitrc)
* Tue Oct 29 2002 sndirsch@suse.de
- fixed stop/reload/status target for gdm in xdm script (Bug #18533)
* Fri Oct 25 2002 pthomas@suse.de
- Resurrect ROOT_LOGIN_REMOTE in sysconfig.displaymanager
  in order to make remote access by root via xdm configurable.
* Thu Oct 24 2002 olh@suse.de
- disable a few more aliases in modules.conf on ppc:
  block-major-88 block-major-89 block-major-90 block-major-91
* Mon Oct 21 2002 ro@suse.de
- added block-major-117 as evms
* Thu Oct 17 2002 olh@suse.de
- disable a few aliases in modules.conf on ppc:
  char-major-9 char-major-206 block-major-11 char-major-86
  personality-8
* Wed Oct  9 2002 ro@suse.de
- changed HISTCONTROL in /etc/bash.bashrc to ignoreboth (#20034)
* Fri Sep 27 2002 ro@suse.de
- fix Check (broke with fileutils POSIX changes)
* Thu Sep 26 2002 olh@suse.de
- uname -m == ppc64 is lib/, not lib64/ (#20228)
* Tue Sep 24 2002 froh@suse.de
- remove the 'dasd' module from the list of modules explicitely added by
  mk_initrd:  it is attracted as a dependency automatically and may now be
  savely renamed to dasd_mod. (#19308)
* Mon Sep 23 2002 ro@suse.de
- removed looking for DISPLAYMANAGER/WINDOWMANAGER in /opt/kde{,2}
  because only /opt/kde3 makes sense currently
* Fri Sep 20 2002 sndirsch@suse.de
- use kdm if possible when DISPLAYMANAGER is not set (Bug #19364)
* Thu Sep 19 2002 pthomas@suse.de
- Add FSCK_MAX_INST with a default value of 10 to sysconfig/boot
  and use the variable in init.d/boot.localfs. This limits the
  number of fsck instances that may run in parallel and fixes
  bug #18273.
* Thu Sep 19 2002 werner@suse.de
- New insserv 0.99.7
  * speedup (really:)
  * move none LSB scripts to max start order (bug #9893)
* Tue Sep 17 2002 mfabian@suse.de
- change initialization of 'dspmbyte' in /etc/csh.cshrc
  to make it work for UTF-8 locales as well.
  Use `locale charmap` to find out the correct value for dspmbyte.
* Fri Sep 13 2002 froh@suse.de
- s390,s390x: added dasd_devfs_compat to ShouldStart of boot.localfs (#18752)
- s390,s390x: enabled full mod_dasd support in mkinitrd (#19308)
- s390,s390x: fixed zfcp support in mkinitrd (#19638)
- s390,s390x: made ttyS0 the console tty in arch_special/s390/inittab.dif
- fixed modprobe-based module dependency checking in mk_initrd
* Thu Sep 12 2002 ro@suse.de
- added /bin/zsh to /etc/shells (#19598)
* Thu Sep 12 2002 snwint@suse.de
- resolve module deps for each kernel individually (#18382)
* Thu Sep 12 2002 ro@suse.de
- added ULconfig symlink if built on UL
* Thu Sep 12 2002 ro@suse.de
- removed "sleep 2" between sending SuSEconfig mails
* Wed Sep 11 2002 ro@suse.de
- don't ask for interactive bootup by default
  (enable with "confirm" as kernel parameter or
  PROMPT_FOR_CONFIRM="yes" in /etc/sysconfig/boot)
* Tue Sep 10 2002 ro@suse.de
- set char-major-10-134 to off (avoid annoying message)
* Mon Sep  9 2002 zoz@suse.de
- changed in modules.conf: alias char-major-166 from acm to off
  (Bug 10815)
* Mon Sep  9 2002 ro@suse.de
- changed char-major-81 from bttv to videodev
- added char-major-81-[0-3] as off (#19122)
* Sun Sep  8 2002 ro@suse.de
- added multipath as raid-style fs (#19109)
* Fri Sep  6 2002 mls@suse.de
- chkconfig changes:
  * added --force option to call insserv with -f
  * automatically use --force if more than one service has to
    be changed
  * added --check option to check the state of a service
* Thu Sep  5 2002 kukuk@suse.de
- Fix group of ftp user
* Wed Sep  4 2002 werner@suse.de
- Fix endless loop in case of more than two loops are crosses
  over in the deependcies found by insserv (bug #18847)
* Tue Sep  3 2002 mls@suse.de
- various mk_initrd changes:
  * use lib64 on 64-bit systems
  * use /var/tmp instead of /tmp (/tmp may be tmpfs)
  * use new ash builtin 'createpartitiondevs' to create missing devs
  * made root-on-lvm work by telling the kernel the right device
* Mon Sep  2 2002 msvec@suse.cz
- change the default prompt timeout to 5s (15 is too long)
* Sun Sep  1 2002 ro@suse.de
- provide and obsolete idedma
* Fri Aug 30 2002 ro@suse.de
- use gnome2-gdm as displaymanager if configured (#18611)
* Fri Aug 30 2002 msvec@suse.cz
- allow configurable confirm prompt timeout (CONFIRM_PROMPT_TIMEOUT)
* Thu Aug 29 2002 ro@suse.de
- changed comment for interactive bootup in sysconfig/boot
* Wed Aug 28 2002 mls@suse.de
- make mkinfodir utf8-resistant
- mk_initrd changes: lvm support, vga resolutions, module deps
* Wed Aug 28 2002 werner@suse.de
- Avoid noise if timer counter is terminated
* Tue Aug 27 2002 schwab@suse.de
- /etc/init.d/nfs: use rc_status -u when unused.
* Tue Aug 27 2002 werner@suse.de
- Add timer count for interactive message (bug #18361)
* Tue Aug 27 2002 stepan@suse.de
- add resolution 1600x1200 to mk_initrd splash detection
* Mon Aug 26 2002 werner@suse.de
- Make newline after interactive message (bug #18310)
* Sun Aug 25 2002 garloff@suse.de
- skeleton:
  * Fix two typos (in comments) and clarify some comments
  * Note about the fact that rc.status is not part of LSB
    and will only work on UL based Linux distros.
  * probe is not part of LSB either
* Wed Aug 21 2002 ro@suse.de
- fixed typo in boot.localnet (#18145)
- updated mk_initrd for pivot_root case (from mls)
* Tue Aug 20 2002 werner@suse.de
- Be nice and inform the admin that his/her script isn't executable
* Mon Aug 19 2002 draht@suse.de
- check for existence of xfs font server before attemting to
  restart it.
* Mon Aug 19 2002 olh@suse.de
- remove rcnetwork start from /etc/init.d/boot
  now handled in YaST2.fistboot
* Mon Aug 19 2002 werner@suse.de
- Fix typo in /etc/init.d/boot
* Mon Aug 19 2002 mfabian@suse.de
- do the 'xset fp rehash' only for local displays.
  Thanks to Roman Drahtmueller <draht@suse.de>.
* Mon Aug 19 2002 mfabian@suse.de
- add 'xset fp rehash' to SuSEconfig.fonts
  and a 'killproc /usr/X11R6/bin/xfs -USR1' if xfs is running.
* Mon Aug 19 2002 werner@suse.de
- New version of insserv 0.99.6 to fix bug #18049:
  * Do not use list of optional services as indicator for `already
    known' due to the optional services in /etc/insserv.conf
* Mon Aug 19 2002 froh@suse.de
- mkinitrd: fix the /proc/mounts scan to find the _last_ mounted '/'
  instead of the first.
* Sun Aug 18 2002 olh@suse.de
- prereq acl
* Fri Aug 16 2002 froh@suse.de
- fixed use_pivot_root
- use_pivot_root for root device specified via LABEL= or UUID= in
  root_dir/etc/fstab
* Fri Aug 16 2002 stepan@suse.de
- change sysconfig and boot.proc to fit boot splash theming
* Thu Aug 15 2002 ro@suse.de
- remove boot.setup from required tags in boot.* scripts
* Thu Aug 15 2002 werner@suse.de
- New version of insserv 0.99.5:
  * Speed up by expanding the required line only once
  * Better support of foreign scripts
* Thu Aug 15 2002 kukuk@suse.de
- nscd: move $named to should start
- xdm: move $syslog to should start
* Thu Aug 15 2002 kukuk@suse.de
- Reorder insserv calls
* Thu Aug 15 2002 ro@suse.de
- make sure CUPS_SERVER is unset before reading sysconfig.printer
  in SuSEconfig.profiles (#17651)
* Wed Aug 14 2002 werner@suse.de
- New version of insserv 0.99.4
  * Fix dendency scanner of insserv: only not installed services
    should be mentioned (bug #17699)
  * Fix insserv linked listings for dendencies: link only in if not
    already done.
  * No time consuming qsort anymore
* Tue Aug 13 2002 ro@suse.de
- fixed insserv-patch again: only check for any "/" in arg
* Tue Aug 13 2002 ihno@suse.de
- applied the patch for inittab for s390 also for s390x
* Mon Aug 12 2002 werner@suse.de
- Make relative path etc/init.d/ work again.
* Mon Aug 12 2002 werner@suse.de
- Now insserv only accepts local files if ./ is used (bug #17608)
* Mon Aug 12 2002 werner@suse.de
- Make insserv to be able to remove links even if not found within
  the default runlevels.
* Mon Aug 12 2002 ro@suse.de
- split off fillup to separate package
* Mon Aug 12 2002 ro@suse.de
- insserv.conf: nfs is optional
* Sat Aug 10 2002 kukuk@suse.de
- Requires "distribution-release", not "suse-release".
* Fri Aug  9 2002 froh@suse.de
- made mk_intrd less verbose and check for /etc/zfcp.conf
* Fri Aug  9 2002 ro@suse.de
- removed files in /etc/ppp (move to sysconfig package)
* Thu Aug  8 2002 stepan@suse.de
- update mk_initrd to support bootsplash themes.
* Thu Aug  8 2002 froh@suse.de
- add dasd support
- always create an initrd on s390
* Thu Aug  8 2002 werner@suse.de
- Shorten timeouts of interactive boot (bug #17516)
- Make interactive option message more intuitive (bug #17517)
* Thu Aug  8 2002 ihno@suse.de
- corrected boot.localfs and boot.klog to avoid messages like
  /etc/init.d/boot.d/S05boot.localfs: line 1: /sbin/showconsole: No such file or directory
- corrected boot.clock to avoid message
  /etc/init.d/boot.d/S08boot.clock: line 55: /sbin/hwclock: No such file or directory
* Wed Aug  7 2002 werner@suse.de
- Fix inputrc for xterm and add some more keys (bug #15002)
* Wed Aug  7 2002 ro@suse.de
- changed init-manpg for runlevel 2 (no _remote_ network) (#17489)
- remove starting of rpc.statd from nfs startscript
- add Should-Start for nfslock in nfs startscript
- default nfs startscript to "off" (#17425)
* Wed Aug  7 2002 ro@suse.de
- added md-personalities to modules.conf
* Tue Aug  6 2002 ro@suse.de
- gid for ftp is 49 not 50 (50 is used elsewhere)
* Tue Aug  6 2002 ro@suse.de
- rename GMT to HWCLOCK, not to UTC
* Mon Aug  5 2002 froh@suse.de
- Add zfcp support to mk_initrd
- changed pivot_root to always mount / ro, and to pivot with /mnt/tmp,
  which is unmounted immediately after the pivot_root.
* Mon Aug  5 2002 ihno@suse.de
- inserted rcnetwork start/stop in /etc/init.d/boot for
  YaST.firstboot
* Mon Aug  5 2002 kukuk@suse.de
- Add PreRequires for devs package (we need /dev/null)
- nscd: Fix required and should start services
- skeletion: $time is required start
* Mon Aug  5 2002 kukuk@suse.de
- boot.crypto: boot.md and boot.lvm are "Should-Start"
- aaa_base.post: Run insserv for boot.crypto after boot.localfs
* Sat Aug  3 2002 ro@suse.de
- updated java handling scripts from Petr Mladek
* Fri Aug  2 2002 olh@suse.de
- use DIR_COLOR defaults from 8.0 and earlier for packages
  no bold for symlinks
* Thu Aug  1 2002 ro@suse.de
- move ftp-user's home to /srv/ftp (#17366)
* Thu Aug  1 2002 ro@suse.de
- fix SuSEconfig.doublecheck using an extra "eval" (#17347)
* Wed Jul 31 2002 olh@suse.de
- remove hwclock_wrapper, use hwclock directly
* Wed Jul 31 2002 ro@suse.de
- renamed rc.config.aaa_base.oldstat to removed_variables.aaa_base
- renamed src-archive rc.config_parts to sysconfig_parts
* Tue Jul 30 2002 ro@suse.de
- removed sysconfig.mouse
* Mon Jul 29 2002 ro@suse.de
- suse.de-backup-rc.config: accept missing rc.config
- fix devpts mount in boot.localfs
- rename sysconfig/clock: GMT to UTC (#17265)
- rename groups not only in /etc/group but also in gshadow
- added /bin/mv /bin/cat /usr/bin/cmp
  (fileutils, textutils and diffutils) to prereq
* Mon Jul 29 2002 sndirsch@suse.de
- adjusted modules.conf for x86_64 (agpgart support now in kernel)
* Sat Jul 27 2002 kukuk@suse.de
- Some changes to the etc/group file for UL [Bug #17240]:
  wwwadmin was renamed to www
  game was renamed to games
  ftp was added with gid 50
  floppy was added with gid 19
  cdrom was added with gid 20
  console was added with gid 21
  utmp was added with gid 22
- etc/passwd: user ftp is in group ftp now
- Add grep and sed to PreRequires
- Remove sysconfig and vi_clone from Requires
- Move etc/motd to distribution-release specific package [Bug #17264]
* Tue Jul 23 2002 werner@suse.de
- Let do the bash the command complete for grep (bug #17128)
- Better check for complete options
* Mon Jul 22 2002 olh@suse.de
- move the agpgart preinstall to <arch>, new x86_64 file, from i386
* Mon Jul 22 2002 sndirsch@suse.de
- added options for sisfb kernel module to modules.conf.i386;
  required for DRI support on SiS chips
* Fri Jul 19 2002 mls@suse.de
- fixed /etc/csh.cshrc and /etc/csh.login so they can cope with
  unset variables
* Thu Jul 18 2002 kukuk@suse.de
- Add mktemp, find and xargs to Requires (SuSEconfig.doublecheck)
* Wed Jul 17 2002 kukuk@suse.de
- Fix creation of etc/defaultdomain
- Add hwscan to Should-Start in xdm init script
- Remove mysql account
* Wed Jul 17 2002 kukuk@suse.de
- Replace aaa_dir with filesystem in Requires
* Wed Jul 17 2002 werner@suse.de
- Extend PATH expansion for bash/tcsh (fix bug #15952)
* Tue Jul 16 2002 kukuk@suse.de
- SuSEconfig.doublecheck: check if /etc/rc.config exists (#17021)
* Tue Jul 16 2002 kukuk@suse.de
- Use new syntax in insserv.conf
* Tue Jul 16 2002 werner@suse.de
- New insserv version with
  * Allow empty `Required-Start' list (bug #17010)
  * Reverse check for requires in case of delete (bug #17009)
* Mon Jul 15 2002 snwint@suse.de
- mkinitrd
  * explicit -t ext2 for mounting initrd
  * add all md devices (not just md0)
* Sat Jul 13 2002 schwab@suse.de
- boot.klog: require boot.localfs to get writable root filesystem.
- boot: fix status message
* Fri Jul 12 2002 werner@suse.de
- New insserv version with
  * correct should-start scanner
  * Use `+' sign as mark for optional services
* Fri Jul 12 2002 mls@suse.de
- fixed postinstall script to be 'sh -e' resistant
- changed mk_initrd to ignore comments in lilo.conf
* Thu Jul 11 2002 olh@suse.de
- adjust DIR_COLORS for executables, works better with some
  global SuSE defaults (#16975)
* Thu Jul 11 2002 kukuk@suse.de
- Adjust init script headers to the serial -> setserial change
* Tue Jul  9 2002 werner@suse.de
- Fix some bash completions (bug #16051)
* Mon Jul  8 2002 kukuk@suse.de
- Don't create /etc/rc.config
- Remove user adabas, amanda, postgres, mdom, fax, gnats, firewall,
  fnet, oracle and gdm.
- Remove groups mdom, firewall, oinstall, dba, logmastr, pkcs11
* Mon Jul  8 2002 kukuk@suse.de
- Use X-UnitedLinux-Should-Start for boot/init scripts
- Change comment in rc.config, that this file is obsolete
  [Bug #16859]
* Sat Jul  6 2002 kukuk@suse.de
- Add new pseudo services to insserv.conf
* Sat Jul  6 2002 garloff@suse.de
- Update skeleton to reflect latest LSB init script specifiactions
  and X-UnitedLinux-Should-Start/Stop spec.
* Fri Jul  5 2002 kukuk@suse.de
- Use %%ix86 macro
* Tue Jul  2 2002 ro@suse.de
- also append all mails to admin to /var/log/update-messages
* Tue Jul  2 2002 ro@suse.de
- removed ircd,squid users
* Tue Jul  2 2002 werner@suse.de
- insserv:
  * Warn only if the runlevels of a enabled service are given but wrong
  * Use requiresv() instead of ln_sf()
  * Improve manual page for impatient readers
* Tue Jul  2 2002 ro@suse.de
- removed users dpbox,vscan,wnn,perforce,db4web
- removed groups dosemu,localham,perforce
* Mon Jul  1 2002 ro@suse.de
- added "you" alias
* Mon Jul  1 2002 ro@suse.de
- added SHMFS_SIZE to /etc/sysconfig/kernel and code in
  /etc/init.d/swap to handle it (#15954)
* Mon Jun 24 2002 ro@suse.de
- require ash for mk_initrd
* Fri Jun 21 2002 ro@suse.de
- split of permissions package with permissions files
  chkstat script and manpage and SuSEconfig.permissions
* Thu Jun 20 2002 jsrain@suse.cz
- Added variable CUPS_SERVER from /etc/sysconfig/printer to profile
* Thu Jun 20 2002 ro@suse.de
- removed dos2unix and unix2dos aliases, we have a extra package
  (#15664)
* Mon Jun 17 2002 ro@suse.de
- removed user pop (created by qpopper package now)
* Thu Jun 13 2002 ro@suse.de
- changed insserv: call internal ln_sf and not link,
  we don't need a hardlink for missing scripts
* Thu Jun 13 2002 mls@suse.de
- mkinitrd: nicer output, no pivot_root call for ext3
* Thu Jun 13 2002 msvec@suse.cz
- added forgotten gnome and vt102 terminals to DIR_COLORS
* Thu Jun 13 2002 msvec@suse.cz
- updated DIR_COLORS (use standard colors, more file types)
* Thu Jun 13 2002 schwab@suse.de
- Add fillup for sysconfig/boot.
* Mon Jun 10 2002 msvec@suse.de
- removed runlevel for si from inittab, it's ignored anyways
* Fri Jun  7 2002 ro@suse.de
- removed zope user (created by package now)
* Mon Jun  3 2002 ro@suse.de
- remove /usr/share/doc/support (outdated support forms)
- remove some old unused cruft from specfile
* Fri May 31 2002 werner@suse.de
- Change code in rc script for initiallize system up from
  cold single user mode
- New code in rc and boot script for interactive boot mode
- Update to insserc 0.99:
  * Now we're knowing about (X-SuSE-)Should-Start/Stop
  * Implement detecting of missed required services even if
    system facilities are required with error exit
  * Implement a force option -f/--force to avoid error exit.
* Wed May 29 2002 ro@suse.de
- removed OPENWINHOME variable (in xview package now)
- removed variables MAPLE,DMARSCONF,CRPATH,BLENDERDIR
  from SuSEconfig.profiles
* Sun May 26 2002 ro@suse.de
- removed bootsetup.dif from arch_special stuff
* Fri May 24 2002 kukuk@suse.de
- Remove obsolete user ingres
- Remove user cyrus and postfix, remove group postfix and maildrop
* Wed May 22 2002 schwab@suse.de
- Add vt102 to list of terminals in /etc/DIR_COLORS.
* Wed May 22 2002 mantel@suse.de
- fix modules.conf entry for usbserial
* Wed May 22 2002 kukuk@suse.de
- Remove at user, created by at package
* Tue May 21 2002 ro@suse.de
- no 64bit dirs for "normal" ppc
- remove sourcing of rc.config from rc-scripts
- remove most traces of rc.config where obsolete
- remove /lib/YaST/bootsetup, /lib/YaST/bootsetup.conf
* Sat May 18 2002 olh@suse.de
- add lib64 dirs for ppc and ppc64 to ld.so.conf
* Fri May 17 2002 garloff@suse.de
- Changes to skeleton init script
  * Fix typo (from mmj)
  * Add more comments describing the syntax of INIT INFO section
  * Update comments to match LSB-1.1 (and post 1.1 changes reported
    by kukuk)
* Mon May 13 2002 ro@suse.de
- removed another occurrence of DEFAULT_LANGUAGE in a comment
* Mon May 13 2002 ro@suse.de
- remove DEFAULT_LANGUAGE
* Fri May 10 2002 ro@suse.de
- only output clock message if really calling hwclock (#15747)
* Wed May  8 2002 werner@suse.de
- Fix bug #15584: insserv now warns about current runlevel script
* Tue May  7 2002 mfabian@suse.de
- fix a bug in SuSEconfig.profiles which made the option
  ROOT_USES_LANG="ctype" fail if RC_LC_CTYPE was non-zero.
* Mon Apr 29 2002 kukuk@suse.de
- Fix Check to work as normal user if we use RPM_BUILD_ROOT
* Thu Apr 25 2002 ro@suse.de
- removed CONSOLE_SHUTDOWN, CHECK_INITTAB
- removed SuSEconfig.inittab (handled by yast2 now)
- SuSEconfig.doublecheck ignore files ending in "~" (#15752)
- SuSEconfig.doublecheck also ignore other backup extensions (#15974)
- suse.de-backup-rc.config: don't try to cat directories (#15796)
- don't try to save options for qeth,lcs,ctc (#15971)
- removed lines about special (2.2kernel) options for modules above
- re-did inittab.dif for s390
* Fri Apr 19 2002 ro@suse.de
- test if fonts subdir exists before touch-ing it in SuSEconfig.fonts
* Thu Apr 18 2002 kukuk@suse.de
- Add more lib64 paths for x86_64 to ld.so.conf
* Thu Apr  4 2002 ro@suse.de
- generate shadow and gshadow fillup-templates in aaa_base.pre
- mark fillup-templates for shadow shadow passwd group as ghost
* Thu Apr  4 2002 bk@suse.de
- aaa_base.pre: add group pkcs11 for openCryptoki administration
* Thu Apr  4 2002 ro@suse.de
- accept TERM=gnome in DIR_COLORS (#15644)
* Thu Mar 28 2002 ro@suse.de
- test for existence of /sbin/blogd before trying to send signals
* Wed Mar 27 2002 ro@suse.de
- fixed some more permissions (kwintv,kradio)
* Tue Mar 26 2002 ro@suse.de
- removed s-bit from kscd in permissions.easy (#15548)
* Mon Mar 25 2002 ro@suse.de
- updated permissions files
* Mon Mar 25 2002 ro@suse.de
- removed KDEDIR,KDEDIRS from SuSEconfig.profiles
  (set in /etc/kde3rc now)
* Mon Mar 25 2002 ro@suse.de
- changed comments in inittab about rc.config (#15457)
* Mon Mar 25 2002 snwint@suse.de
- handle splash properly if using a different root dir (#12427)
* Sun Mar 24 2002 ro@suse.de
- ignore ifcfg files with ipaddr=0.0.0.0 in SuSEconfig.hostname
* Sun Mar 24 2002 snwint@suse.de
- mk_initrd:
  run /sbin/fsck.jfs if jfs is used for root (#13886)
  add /sbin:/usr/sbin to PATH (#12926)
  allow using a different /tmp dir (for users with tmpfs on /tmp, #15310)
* Sat Mar 23 2002 ro@suse.de
- SuSEconfig ignore .orig backups of sub-scripts (#15408)
* Thu Mar 21 2002 arvin@suse.de
- only restore routes in ip-up for isdn when the connection
  has dialmode auto (bug #15236)
* Wed Mar 20 2002 ro@suse.de
- updated fillup to current version
  (now really keep rc.config header)
* Tue Mar 19 2002 ro@suse.de
- obsolete variable KWM_GIMMICK_PIXMAP (#14635)
* Fri Mar 15 2002 ro@suse.de
- boot.idedma: no output if nothing is configured/done
* Thu Mar 14 2002 ro@suse.de
- obsolete old variable USE_KERNEL_NFSD
* Wed Mar 13 2002 ro@suse.de
- removed "-S" from LESS setting in /etc/profile,/etc/csh.cshrc
  (#14951)
* Wed Mar 13 2002 ro@suse.de
- replaced manpage for route.conf.5 from mmj
* Tue Mar 12 2002 werner@suse.de
- bash.bashrc: If LS_COLROS is set but empty, the terminal
  has no colors.
- csh.cshrc: If LS_COLROS is set but empty, the terminal
  has no colors.
* Tue Mar 12 2002 ro@suse.de
- comment out raidstop part in /etc/init.d/halt
  (raidstop needs an argument, normal shutdown is done by kernel)
* Mon Mar 11 2002 werner@suse.de
- Fix part of bug #14741: Check for TERM=dumb to avoid
  colored output on.
* Mon Mar 11 2002 werner@suse.de
- Make TAB completion of `export' more handy
* Mon Mar 11 2002 ro@suse.de
- don't test for XNTPD_INITIAL_NTPDATE being empty, since the
  default is now "AUTO-2"
- use rcxntpd ntptimeset in poll.tcpip
- only test for rc_active xntpd in halt/reboot
- updated fillup and run "make test"
- no colon at end of message in halt-script (#14705)
* Sun Mar 10 2002 ro@suse.de
- source sysconfig/proxy in SuSEconfig.profiles (#14742)
* Fri Mar  8 2002 ro@suse.de
- removed cipe_maxdev from modules.conf (#14652)
- remove obsolete IRDA_IRQ, PCMCIA from rc.config (#14636,#14634)
- removed obsolete part of comment from sysconfig/language (#14639)
* Thu Mar  7 2002 mfabian@suse.de
- SuSEconfig.fonts: run xftcache only when really necessary
  (to make SuSEconfig.fonts execute faster)
* Thu Mar  7 2002 ro@suse.de
- remove some orphaned/obsolete rc.config variables:
  GOPHER_PROXY, HOW_TO_HANDLE_COMMERCIAL_LIBS, START_KERNELD
* Wed Mar  6 2002 sndirsch@suse.de
- handles DISPLAYMANAGER=console in xdm script (Bug #14540)
* Wed Mar  6 2002 ro@suse.de
- rc-script: export REDIRECT (#14544)
* Wed Mar  6 2002 werner@suse.de
- Fix bug #14527: test if stdout is a termnal
* Tue Mar  5 2002 kukuk@suse.de
- Use correct option for tar/bzip2
* Tue Mar  5 2002 ro@suse.de
- print filenames in SuSEconfig.doublecheck (#14466)
* Tue Mar  5 2002 ro@suse.de
- updated comment for sysconfig.proxy (#14442)
* Tue Mar  5 2002 ro@suse.de
- fillup has been fixed (thanks to jd)
* Mon Mar  4 2002 ro@suse.de
- back to previous fillup
  (rather lose the header than lose a variable)
* Mon Mar  4 2002 ro@suse.de
- insserv.conf: $network changed to "network pcmcia hotplug"
* Mon Mar  4 2002 draht@suse.de
- changes to permissions.*, mostly terminal emulator -s, and
  minor cleanup (SVGAlib, last-minute fixes removed).
* Mon Mar  4 2002 ro@suse.de
- changed rc.config.d to sysconfig in comment for RCCONFIG_BACKUP_DIR
  (#14237)
* Fri Mar  1 2002 ro@suse.de
- fix fillup for corner case (basefile only consits of a header)
* Fri Mar  1 2002 ro@suse.de
- boot.localnet: no "done" if "setting up domainname" is not shown
* Thu Feb 28 2002 ro@suse.de
- check if modules.dep file has size > 0, otherwise regenerate
* Thu Feb 28 2002 mantel@suse.de
- removed entry for pvrcore devices (no longer needed)
* Thu Feb 28 2002 ro@suse.de
- modules.conf update: get KEEPOPTIONS first and collect them
  in a second run (#14055)
* Wed Feb 27 2002 arvin@suse.de
- for ppp run poll.tcpip, ip-up.local and ip-down.local in the
  background and detach from stdout.
* Wed Feb 27 2002 ro@suse.de
- cleanup: remove oldish rc.config variables
  GENERATE_PERL_SYSTEM_INCLUDES, LOAD_MEMSTAT_MODULE,
  START_IDEDMA, START_USB
* Tue Feb 26 2002 werner@suse.de
- Re-enable files and directories for rsh/ssh/scp on TAB compelete
* Tue Feb 26 2002 ro@suse.de
- fix another problem of Check script with RPM_BUILD_ROOT
* Mon Feb 25 2002 ro@suse.de
- re-added: set up loopback interface real early in boot process
  (skipped if /etc/sysconfig/network/ifcfg-lo doesn't exist)
* Mon Feb 25 2002 mls@suse.de
- added extended version of chkconfig and chkconfig manpage
* Mon Feb 25 2002 ro@suse.de
- moved CHECK_PERMISSIONS, PERMISSION_SECURITY, CONSOLE_SHUTDOWN
  to /etc/sysconfig/security
- moved CHECK_INITTAB and HALT_SOUND to /etc/sysconfig/suseconfig
- rc.config.aaa_base.*console are obsolete
* Mon Feb 25 2002 ro@suse.de
- fixed headlines for install_initd and remove_initd
* Mon Feb 25 2002 arvin@suse.de
- run poll.tcpip in background
* Mon Feb 25 2002 snwint@suse.de
- mk_initrd: there might be more than one module with the
  same name (#13833)
* Mon Feb 25 2002 kkeil@suse.de
- update /etc/ppp/ip-up (#12818)
  * IP_RESEND support
  * start poll.tcpip by default
* Fri Feb 22 2002 werner@suse.de
- Fix bug #13743: do not use START_XNTPD but test runlevel service
- Do not dup stdin to stdout for stty in profile
* Thu Feb 21 2002 ro@suse.de
- add requires for sysconfig package
- use smarter code from boot sequence for ldconfig and depmod
  also in SuSEconfig
* Thu Feb 21 2002 werner@suse.de
- Workaround for stopped stty command
- Fix bug 13489: do not try to solve file/var complete feature
  of bash complete builtin.  Make _file_ shell function know
  more about other things than files.
* Thu Feb 21 2002 ro@suse.de
- added "nis" to automount entry for default nsswitch.conf
* Thu Feb 21 2002 ro@suse.de
- boot.localnet: output short hostname only (#13674)
  add NIS to echo when setting domainname
* Wed Feb 20 2002 ro@suse.de
- updated fillup again (#13508)
* Wed Feb 20 2002 kkeil@suse.de
- change ippp part to use ip and sysconfig (#12818)
* Mon Feb 18 2002 ro@suse.de
- fillup changed handling of comment blocks (#13508)
* Mon Feb 18 2002 ro@suse.de
- fix boot.klogd: move blogd kill -IO up to start section
* Mon Feb 18 2002 ro@suse.de
-  moved mk_initrd to mkinitrd and provide symlink mk_initrd
* Sat Feb 16 2002 ro@suse.de
- moved boot.quota to quota package
- make setting of hostname and domainname more verbose (#13369)
- started unifying messages for boot subscripts
* Fri Feb 15 2002 schwab@suse.de
- modules.conf: move AGP entries from i386 to common.
* Fri Feb 15 2002 ro@suse.de
- moved boot.ibmsis to ibmsis package
* Fri Feb 15 2002 ro@suse.de
- removed old unused code from etc/init.d/boot (#13164)
* Thu Feb 14 2002 ro@suse.de
- added /tmp/.ICE-unix to list of dirs to recreate after cleanup
* Thu Feb 14 2002 ro@suse.de
- updated java handling scripts from pmladek
- reduced SuSEconfig.aaa_at_first (step 1)
* Thu Feb 14 2002 draht@suse.de
- changes to permissions.*, part-I. Continues in part-II.
* Thu Feb 14 2002 draht@suse.de
- exchange root/.gnupg/suse_build_key so that build@suse.de will
  not expire in root's keyring.
* Thu Feb 14 2002 draht@suse.de
- prevent the use of a keyring list when adding build@suse.de to
  root's keyring via gpg (--no-default-keyring)
* Thu Feb 14 2002 ro@suse.de
- fix SuSEconfig.hostname for localhost/lo (#13110,#13225)
* Wed Feb 13 2002 stepan@suse.de
- use default kernel names on alpha.
* Wed Feb 13 2002 ro@suse.de
- added logrotate to requires
* Wed Feb 13 2002 garloff@suse.de
- Add umountizo to quick_halt script.
* Mon Feb 11 2002 mantel@suse.de
- clean up modules.conf file (remove obsolete comments)
* Mon Feb 11 2002 werner@suse.de
- Newer kernels do have a /proc/acpi not /proc/sys/acpi
* Mon Feb 11 2002 mantel@suse.de
- added modules.conf entries for nVidia nforce chipset
* Sun Feb 10 2002 poeml@suse.de
- implement some chkconfig functionality
* Sun Feb 10 2002 ro@suse.de
- tar option for bz2 is now "j"
* Sat Feb  9 2002 bk@suse.de
- nsswitch.conf holds vital configuration - should be noreplace
  post install script should check that all needed entries
  (e.g. autofs:  files - don't know if really, just an idea)
  are there(should possibly be discussed with regard to update)
* Thu Feb  7 2002 ro@suse.de
- lsb-ified names of cron.daily scripts (#13027)
  (make the filenames start with suse.de)
- split up the aaa_base part of these scripts into tasks
* Thu Feb  7 2002 arvin@suse.de
- removed check for START_NAMED from ip-up
- mention poll.tcpip in ppp section of ip-up
* Thu Feb  7 2002 mantel@suse.de
- mount /proc/sys/fs/binfmt_misc when needed
* Wed Feb  6 2002 werner@suse.de
- We should save our entropy within a file which isn't cleared
  at boot time, shouldn't we.
* Wed Feb  6 2002 ro@suse.de
- sysconfig/cron_daily -> sysconfig/cron
* Tue Feb  5 2002 tiwai@suse.de
- correct typos and alias/options for sound stuff in
  /etc/modules.conf.
* Tue Feb  5 2002 ro@suse.de
- remove old check for SENDMAIL_TYPE from SuSEconfig
* Mon Feb  4 2002 poeml@suse.de
- move modify_resolvconf and its man page to the sysconfig package
- MODIFY_RESOLV_CONF_DYNAMICALLY goes from rc.config to
  /etc/sysconfig/network/config
- patches from sles7-ppc:
  - /etc/profile: iSeries console support in /etc/profile
  - mk_initrd: know the kernel names on ppc64
* Mon Feb  4 2002 ro@suse.de
- added forgotten sysconfig/news handling to postinstall
* Mon Feb  4 2002 ro@suse.de
- updated fillup to 1.10
* Mon Feb  4 2002 ro@suse.de
- moved ORGANIZATION, NNTP_SERVER to sysconfig/news
- removed CLOSE_CONNECTIONS variable
- fixed output for some SuSEconfig subscripts
* Mon Feb  4 2002 mantel@suse.de
- added entry for sonypi
* Sat Feb  2 2002 ro@suse.de
- SuSE GmbH -> SuSE Linux AG replacement
- replaced invalid suse e-mail addresses by feedback@suse.de
- moved DEFAULT_PRINTER to sysconfig/printer
* Fri Feb  1 2002 ro@suse.de
- updated ld.so.conf for s390x
* Fri Feb  1 2002 werner@suse.de
- Fix bug #13017: xdvi knows about gzip dvi, make .. work on TAB
- Call /etc/init.d/boot system was booted cold into single user
* Thu Jan 31 2002 mfabian@suse.de
- use timestamp file var/adm/SuSEconfig/lastrun.SuSEconfig.fonts
  to check whether mkfontdir needs to run, this should be more
  reliable than just checking whether a directory modification
  date is newer than its fonts.dir file.
* Thu Jan 31 2002 ro@suse.de
- moved cron.daily scripts do_mandb and clean_catman to man package
  (and their respective sysconfig variables)
- commented out mandb call in suseconfig.man_info
* Thu Jan 31 2002 ro@suse.de
- xdm: export KDEROOTHOME as /root/.kdm
- moved sysconfig.locate, and cron.daily scripts updatedb
  and clean_core to findutils-locatedb package
* Thu Jan 31 2002 ro@suse.de
- modified fillup to keep file-header only in rc.config
  (thanks to jd)
* Wed Jan 30 2002 ro@suse.de
- removed zshrc and zshenv (moved to zsh package)
- removed old checks for YAST_ASK, all these values are gone now
- rc.status: added status unknown (4) as specified by LSB
- added status (unknown) and stop (not implemented) return values
  for boot.xyz scripts
* Tue Jan 29 2002 ro@suse.de
- SuSEconfig.doublecheck: ignore subdirs of /etc/sysconfig
* Tue Jan 29 2002 ro@suse.de
- fillup fixed for templates starting with newline
* Tue Jan 29 2002 ro@suse.de
- removed /opt/kde2 from KDEDIRS again
* Tue Jan 29 2002 ro@suse.de
- fixed cron.daily script aaa_base_updatedb (thanks to mvidner)
* Tue Jan 29 2002 ro@suse.de
- SuSEconfig.profiles: set KDEDIR to /opt/kde3, /opt/kde2
  (/opt/kde3 preferred, both if exist)
- set QTLIB to /usr/lib/qt3, /usr/lib/qt2 (as above)
- set KDEDIRS to /etc/X11/kde3/:/opt/kde3/:/opt/kde2/
  if /opt/kde2 or /opt/kde3 exists
* Mon Jan 28 2002 werner@suse.de
- fix bug #12935: handle bzip/gzip options for uncompressing
* Mon Jan 28 2002 ro@suse.de
- fillup:
  - added new functionality due to the first variable block of
    basefile:
    The first variable block of basefile can hold header information
    for the basefile that should always be part of the resulting
    outputfile.
    The former version handles all variable blocks transparently.
    Now if former version ignores the first variable block of
    basefile the comment up to an empty line is taken nevertheless.
- removed DUMMY_SEPARATOR hack from postinstall
- SuSEconfig.hostname: don't write HOSTNAME, only modify hosts
* Mon Jan 28 2002 ro@suse.de
- Check: don't gzip XftCache files
- removed MODEM from rc.config (obsolete)
- set values to empty where YAST_ASK was before
* Sun Jan 27 2002 schwab@suse.de
- Don't use obsolete sort options for field selection.
- Don't duplicate each empty line in /etc/rc.config.
* Fri Jan 25 2002 mfabian@suse.de
- check for existance of xftcache and mkfontdir in
  SusEconfig.fonts
* Thu Jan 24 2002 mls@suse.de
- use /bin/splash to create bootsplash pictures
* Thu Jan 24 2002 mfabian@suse.de
- use full path '/usr/X11R6/bin/xftcache' instead of just
  'xftcache' in SuSEconfig.fonts.
* Thu Jan 24 2002 ro@suse.de
- moved cron.daily related variables to sysconfig/cron_daily
- cleaned up aaa_base_clean_core
* Wed Jan 23 2002 ro@suse.de
- added sysconfig/hardware
- fixed domainname setting in boot-script (problem if empty)
* Wed Jan 23 2002 ro@suse.de
- added boot.idedma
* Tue Jan 22 2002 ro@suse.de
- read sysconfig/java in SuSEconfig.alljava
* Tue Jan 22 2002 ro@suse.de
- moved more SuSEconfig only variables to sysconfig/suseconfig
- moved FROM_HEADER to sysconfig/mail
- removed SuSEconfig.mini_mail (obsolete for long)
* Tue Jan 22 2002 werner@suse.de
- Fix bug #11744: make TAB expansion work with wildcard
* Tue Jan 22 2002 ro@suse.de
- CREATE_JAVA_LINK is in sysconfig/java again
- fixed SuSEconfig.doublecheck
* Tue Jan 22 2002 ro@suse.de
- added INSTALL_DESKTOP_EXTENSIONS to sysconfig/windowmanager
* Mon Jan 21 2002 mfabian@suse.de
- add call to 'xftcache' to SuSEconfig.fonts
* Mon Jan 21 2002 ro@suse.de
- fixed typos in specfile (BOOT_SPLASH moved)
* Mon Jan 21 2002 ro@suse.de
- moved proc/sys related variables to sysconfig/sysctl
* Mon Jan 21 2002 ro@suse.de
- moved DEFAULT_WM to sysconfig/windowmanager
* Mon Jan 21 2002 ro@suse.de
- updated modify_resolvconf and it's manpage from SLCS version
* Fri Jan 18 2002 garloff@suse.de
- added umountizo to halt script (if binary is existing and
  intermezzo filesystems are mounted)
- updated comments in skeleton
* Fri Jan 18 2002 ro@suse.de
- added nosmbfs to mount options in boot.localfs (#12627)
- removed noauto check in rcnfs (#12687)
* Fri Jan 18 2002 ro@suse.de
- added user mail, uid 8 , home: /var/spool/clientmqueue
- added group intermezzo, gid 63
- added intermezzo entries to modules.conf
* Thu Jan 17 2002 ro@suse.de
- fixed comment in skeleton script
* Thu Jan 17 2002 ro@suse.de
- removed /S.u.S.E from UPDATEDB_PRUNEPATHS
  (only used on live-eval which has no updatedb/locate running)
- added /opt/gnome2/lib to ld.so.conf
- added /opt/gnome2/bin to PATH if existant
* Wed Jan 16 2002 ro@suse.de
- fixed cyrus home dir
* Wed Jan 16 2002 ro@suse.de
- moved PROXY variables to sysconfig/proxy
- moved sysconfig/updatedb to sysconfig/locate
* Wed Jan 16 2002 ro@suse.de
- moved TIMEZONE and GMT to sysconfig/clock
* Wed Jan 16 2002 kukuk@suse.de
- Add defaultdomain.5 manual page
* Tue Jan 15 2002 sndirsch@suse.de
- small change in xdm script: use kdm in /opt/kde3/bin if available,
  otherwise try to use kdm in /opt/kde2/bin
* Tue Jan 15 2002 ro@suse.de
- removed network rc.config variables and FQHOSTNAME
- removed network,dummy,route,boot.loopback
- removed /sbin/bootp (if anybody wants this needs a total rewrite)
- updated SuSEconfig.hostname
- fixme: /etc/ppp/ip-up needs to be updated
* Mon Jan 14 2002 ro@suse.de
- moved SuSEconfig related variables to /etc/sysconfig/suseconfig
  ENABLE_SUSECONFIG, MAIL_REPORTS_TO, MAIL_LEVEL, CREATE_INFO_DIR,
  CREATE_JAVALINK
- moved basic network variables to rc.config.aaa_base.oldnet
  for quicker removal
  NETCONFIG*,IPADDR_*,NETDEV_*,IFCONFIG_*
* Mon Jan 14 2002 ro@suse.de
- complete move of INITRD_MODULES to /etc/sysconfig/kernel
* Mon Jan 14 2002 snwint@suse.de
- mk_initrd: INITRD_MODULES has been moved to /etc/sysconfig/kernel
* Mon Jan 14 2002 ro@suse.de
- fixed SuSEconfig.profiles for DEFAULT_WM
* Mon Jan 14 2002 werner@suse.de
- The halt script should know about raidstop
* Mon Jan 14 2002 mantel@suse.de
- added alias binfmt-0004 binfmt_coff
* Mon Jan 14 2002 kukuk@suse.de
- Move DEFAULT_WM to sysconfig.displaymanager
- Remove ROOT_LOGIN_REMOTE and PASSWD_USE_CRACKLIB from rc.config
- Remove SERIAL_CONSOLE from rc.config and SuSEconfig.inittab
* Fri Jan 11 2002 garloff@suse.de
- Fix remount bug (bug #11923)
- Make ip-up start of SuSEfirewall dependant on rc.d symlinks
* Fri Jan 11 2002 kukuk@suse.de
- remove all obsolete YP variables from rc.config
* Thu Jan 10 2002 ro@suse.de
- removed /usr/games/bin from path
* Thu Jan 10 2002 kukuk@suse.de
- Domainname is now in /etc/defaultdomain
* Wed Jan  9 2002 ro@suse.de
- only move rc.config.new to rc.config if awk worked
* Wed Jan  9 2002 ro@suse.de
- added comment about logfiles to permissions.local header (#12163)
* Wed Jan  9 2002 ro@suse.de
- boot.md and boot.lvm are in other packages, don't call insserv
  for these here
* Tue Jan  8 2002 ro@suse.de
- added opt/kde3/lib to ld.so.conf
* Tue Jan  8 2002 ro@suse.de
- moved MOUSE from rc.config to sysconfig/mouse
- renamed sysconfig/lang -> sysconfig/language
- added opt/kde3/bin to path if existant
- moved DISPLAYMANAGER to sysconfig/displaymanager
- moved DEFAULT_LANGUAGE to sysconfig/language
* Tue Jan  8 2002 werner@suse.de
- Add fetchnews call to /etc/ppp/poll.tcpip
- Add syslog messages on start and end of /etc/ppp/poll.tcpip
* Mon Jan  7 2002 mantel@suse.de
- changed name from mwavedd to mwave in /etc/modules.conf
* Fri Jan  4 2002 kukuk@suse.de
- Remove rcnscd status hack
- Allow longer version strings in get_kernel_version [Bug #12731]
* Fri Jan  4 2002 kukuk@suse.de
- Add group "nobody" with gid 65433, make this primary group for
  user nobody, add nobody to group "nogroup" (To be LSB conform).
* Wed Jan  2 2002 kukuk@suse.de
- Add more entries to etc/mime.types (fixes [Bug #2899])
* Thu Dec 20 2001 sndirsch@suse.de
- /usr/sbin/Check: symbolic link /usr/X11R6/lib/X11/fonts/TTF no
  longer compressed
* Wed Dec 19 2001 mfabian@suse.de
- SuSEconfig.fonts:
  don't copy lines with only white space and digits from
  fonts.scale.* to fonts.scale (thanks to sndirsch@suse.de for
  the suggestion).
* Wed Dec 19 2001 mfabian@suse.de
- SuSEconfig.fonts:
  add TTF and Type1 directories
  don't copy empty lines from fonts.scale.* to fonts.scale
* Fri Dec 14 2001 werner@suse.de
- Do not scan dangling sym link with insserv
* Fri Dec 14 2001 werner@suse.de
- Avoid casts use pointer instead
* Fri Dec 14 2001 werner@suse.de
- Be aware that strsep(3) make pointer arithmetic and we should
  remember the starting address of any string handled by strsep(3)
* Fri Dec 14 2001 draht@suse.de
- removed postgres paths from permissions*
* Fri Dec 14 2001 ro@suse.de
- removed SMTP from rc.config template (which is START_SENDMAIL)
  SMTP will be removed from rc.config by sendmail update
* Thu Dec 13 2001 werner@suse.de
- Intergrate insserv-0.92.dif patch to insserv sources
- Fix bug #12482: make a difference between provided services
  and the names of the scripts its self.
* Wed Dec 12 2001 draht@suse.de
- permissions.paranoid, hosts.* mode 600, now 644.
* Wed Dec 12 2001 werner@suse.de
- csh.cshrc: move symlinks from expand to ignore, no WINDOWID for
  konsole, some comments about using local system and user csh.cshrc.
- csh.login: some comments about using local system csh.login,
  no WINDOWID for konsole.
* Wed Dec 12 2001 ro@suse.de
- move from rc.config.d to sysconfig
* Mon Dec 10 2001 ro@suse.de
- added variable UPDATEDB_PRUNEFS
- moved all updatedb variables to /etc/rc.config.d
* Mon Dec 10 2001 ro@suse.de
- moved boot.md and boot.lvm to their respective packages
* Mon Dec 10 2001 ro@suse.de
- removed aaa_base_clean_instlog, aaa_base_rotate_logs,
    /etc/logfiles and MAX_DAYS_FOR_LOG_FILES
* Fri Dec  7 2001 ro@suse.de
- removed rcboot.setup (has to go to kbd package now)
* Fri Dec  7 2001 werner@suse.de
- Next try of getting LSB conform exit status of rc_check
* Wed Dec  5 2001 ro@suse.de
- moved variables to kbd package:
  KEYTABLE, KBD_RATE, KBD_DELAY, KBD_NUMLOCK, KBD_CAPSLOCK, KBD_TTY
  CONSOLE_FONT, CONSOLE_SCREENMAP, CONSOLE_UNICODEMAP, CONSOLE_MAGIC
- moved boot.setup to kbd package
- added rc_active to /etc/rc.status and removed checks for foreign
  START variables using rc_active
- moved boot.isapnp to isapnp package
* Wed Dec  5 2001 ro@suse.de
- use insserv_and_fillup macro
- moved GPM_ variables to GPM package
- removed START_ variables
- some scripts do still reference START variables
  (START_XNTPD,START_QUOTA,START_AUTOFS)
* Fri Nov 30 2001 ro@suse.de
- removed /usr/etc stuff (links for mime.*)
* Tue Nov 27 2001 ro@suse.de
- integrated splash diff
- removed 7.0 compat hacks in specfile
- etc/init.d/boot: split into nice little pieces
- removed kerneld, dosemu and xosview from bootscript
* Mon Nov 26 2001 ro@suse.de
- updated java-selection scripts from Petr
* Thu Nov 22 2001 werner@suse.de
- Fix bug #12014: allow filenames for mkdir complete
- Fix bug #12408: avoid error message of compgen if an option will
  be expanded on the command line.
- Allow spaces as component of file and directory names (#12422)
- Add complete feature for man command, now comands and sections
  can be expanded (man <TAB>, man 5 <TAB>, ...)
* Thu Nov 22 2001 ro@suse.de
- added /usr/openwin/man and /usr/gnome/man hardcoded to
  Check's manpath
* Wed Nov 21 2001 ro@suse.de
- export _SUSECONFIG_PROFILE
* Wed Nov 21 2001 schwab@suse.de
- mk_initrd: check that /etc/lilo.conf exists before trying to read it.
* Thu Nov 15 2001 ro@suse.de
- separated java settings from /etc/profile and /etc/csh.login
  to /etc/profile.d/alljava.{sh,csh}
- exporting variables like JAVA_HOME and JDK_HOME (#12143)
- bugfixes and extensions for SuSEconfig.alljava
* Wed Nov  7 2001 ro@suse.de
- added etc/rc.config.d/displaymanager.rc.config
* Fri Nov  2 2001 ro@suse.de
- don't always fsck root fs if on LVM
* Mon Oct 29 2001 ro@suse.de
- fixed gshadow owner and permissions in postinstall
* Fri Oct 26 2001 ro@suse.de
- updated comment in chkconfig-fake
* Fri Oct 19 2001 ro@suse.de
- removed suid bits for cdrecord permissions.{paranoid,secure}
- added artswrapper to permission, suid in easy only
- updated mk_initrd for ext3 support
* Tue Oct 16 2001 ro@suse.de
- added rc.config variable DISPLAYMANAGER_REMOTE_ACCESS
- added another chroot in gpg build key code
- ip-up: moved firewall-start code to a function and
    use code-fragment from SuSEfirewall2
* Sun Oct 14 2001 bk@suse.de
- change char-major-108 to ppp_generic(real provider, bug 5255)
* Thu Oct 11 2001 werner@suse.de
- Update of the manual page of route.conf(5)
* Wed Oct 10 2001 ro@suse.de
- source profile in /etc/zshenv before zshrc and everything else
  (#9870)
* Wed Oct 10 2001 werner@suse.de
- Close bug #11635 and source /etc/bash.bashrc.local if exists
- Remove shell option `cdspell' to avoid unwanted corrections
* Tue Oct  9 2001 snwint@suse.de
- ppc kernel is either vmlinux or vmlinuz
* Mon Oct  8 2001 snwint@suse.de
- no .suse fallback kernel on ppc (see #11495)
* Thu Oct  4 2001 ro@suse.de
- create subdir in main source archive and move unpack to setup
  section in specfile (don't use setup macro because of perms)
* Thu Oct  4 2001 werner@suse.de
- Allow .exe for complete of unzip
* Tue Oct  2 2001 ro@suse.de
- revert previous fix: simply call SuSEfirewall2 if START_FW2 is
  set to "yes"
* Tue Oct  2 2001 ro@suse.de
- switch between SuSEfirewall and SuSEfirewall2 using
  /sbin/kernelversion in /etc/ppp/ip-up (#11490)
* Tue Oct  2 2001 werner@suse.de
- Make user ~ listing work again even if used with bash
  complete feature (#11512)
* Thu Sep 27 2001 ro@suse.de
- removed /etc/SuSE-release, /etc/issue and /etc/issue.net
- added requires to suse-release
* Tue Sep 25 2001 ro@suse.de
- fixed mk_initrd "no space left" (#11333)
* Tue Sep 25 2001 ro@suse.de
- /etc/profile: source SuSEconfig.profile once, but only once
  (#11277)
* Mon Sep 24 2001 ro@suse.de
- clean_core: do also search for core-files like core.[0-9]*
* Mon Sep 24 2001 ro@suse.de
- added option --nomodule to SuSEconfig
* Sat Sep 22 2001 bjacke@suse.de
- add all fixes for filename vulnerability
* Sat Sep 22 2001 kukuk@suse.de
- make 'old' less vulnerable to filename attacks (reported by bjacke)
* Sat Sep 22 2001 kukuk@suse.de
- Move inittab with /sbin/init.d away and install new one (#11173)
* Fri Sep 21 2001 werner@suse.de
- Initialize integer n in route script
- Remove route.conf.old handling because YaST2 handles
  this now more appropiate
* Fri Sep 21 2001 ro@suse.de
- fix test for working gpg again (#11108)
* Fri Sep 21 2001 werner@suse.de
- Add a loop detection for ~/.bashrc reading /etc/profile
- Move complete part of /etc/bash.bashrc into
  /etc/profile.d/complete.bash to avoid parser errors of
  other shells.
* Thu Sep 20 2001 ro@suse.de
- added force-reload for etc/init.d/nfs (#9053)
* Thu Sep 20 2001 kukuk@suse.de
- umount /proc after calling vgchange (#11095)
* Thu Sep 20 2001 snwint@suse.de
- suppress mke2fs warnings 'could not erase sector...' (#11083)
* Thu Sep 20 2001 mls@suse.de
- mk_initrd changed to automagically determine splash screen size
  if no -s option is given
* Thu Sep 20 2001 werner@suse.de
- Some command completes also need file completes (BUG #11087)
* Thu Sep 20 2001 mls@suse.de
- fix /etc/profile to init the terminal only in interactive
  sessions, otherwise programs like xinit will hang in stty
* Thu Sep 20 2001 ro@suse.de
- set hwclock in shutdown only if xntp is fully configured
* Thu Sep 20 2001 werner@suse.de
- Avoid not existing info dirs in csh.cshrc
* Thu Sep 20 2001 snwint@suse.de
- mk_initrd: check for lvm if a root device is explicitly given (#8958)
* Wed Sep 19 2001 ro@suse.de
- removed old comments about SuSEconfig and DISPLAYMANAGER
* Wed Sep 19 2001 werner@suse.de
- Better tty check for coloured status messages in boot scripts
- Remove pcmcia from $network due pcmcia does its own routing
* Tue Sep 18 2001 kukuk@suse.de
- Add group man for LSB conformance
* Tue Sep 18 2001 ro@suse.de
- prevent "sorted" passwd,group on new installation
* Tue Sep 18 2001 ro@suse.de
- added etc/inittab to noreplace files
- changed bash completion for export command
* Mon Sep 17 2001 ro@suse.de
- allow run of SuSEconfig modules in FASTRUN mode if $r is set
  added SuSEconfig.inittab and SuSEconfig.hostname to the list
  of these modules (FASTRUN) (#10430)
- added warning comments to etc/inittab about CHECK_INITTAB
  (#10740)
* Thu Sep 13 2001 mls@suse.de
- mkinitrd: added oem resize support, support for splash image sizes
* Wed Sep 12 2001 ro@suse.de
- commented out animation in initrd
* Wed Sep 12 2001 uli@suse.de
- changed permissions entry /usr/bin/vmware -> /usr/bin/vmware.bin
* Wed Sep 12 2001 uli@suse.de
- changed login shell for db4web from /bin/false to /bin/bash
* Tue Sep 11 2001 ro@suse.de
- set 'dspmbyte' variable to 'big5' when LANG is zh_TW* to enable
  convenient editing of traditional Chinese on the tcsh commandline
- SuSEconfig.doublecheck only checks lines containing "=" (#10443)
* Tue Sep 11 2001 ro@suse.de
- updated user description fields in passwd file (thanks to msvec)
* Tue Sep 11 2001 uli@suse.de
- added application/x-rad to mime.types
* Tue Sep 11 2001 ro@suse.de
- use extra tmpfile for update of passwd et al
* Mon Sep 10 2001 stepan@suse.de
- new mk_initrd. Create headers necessary for splash kernel
  patch version 0.9.8
* Mon Sep 10 2001 ro@suse.de
- alias char-major-116 to off by default (#10404)
* Mon Sep 10 2001 ro@suse.de
- re-diffed splash patch
* Mon Sep 10 2001 ro@suse.de
- touch shadow/gshadow in postinstall, might not be present
* Sun Sep  9 2001 ro@suse.de
- rewrote pre/postinstall handling for passwd et al to not use
  bin/fillup because of it's charset limitiations, but use the
  utilities "sort" and "uniq"
* Sun Sep  9 2001 ro@suse.de
- integrate s390 special case into etc/init.d/boot
  (the patch did not apply anymore anyway)
* Fri Sep  7 2001 mantel@suse.de
- moved Linux-ABI stuff to i386 specific file
- added personalities needed by Linux-ABI
* Fri Sep  7 2001 werner@suse.de
- network script: Add workaround ethernet driver modules:
  Try to load them in order even if a device is disabled.
* Fri Sep  7 2001 stepan@suse.de
- new mk_initrd: added option -s to add boot splash animation, if
  installed and concatenate the bootsplash jpeg file to initrd.
- new aaa_base_splash.diff: cleaned up diff and test for rc.config
  variable $BOOT_SPLASH before playing any animation.
* Fri Sep  7 2001 ro@suse.de
- fixed db4web user entry (id 70, grp users, home:/opt/db4web)
* Fri Sep  7 2001 uli@suse.de
- added user db4web
* Fri Sep  7 2001 werner@suse.de
- Workaround for broken complete feature of the bash: the
  filter pattern for files are also applied an directories
- boot.crypto: add timeout option for losetup
* Fri Sep  7 2001 stepan@suse.de
- updated splash patch: hook to trigger YaST
  startup and unified runlevel reached hook.
* Thu Sep  6 2001 garloff@suse.de
- Unexport NFS before umounting if applicable (hint from ak again).
* Thu Sep  6 2001 snwint@suse.de
- mk_initrd: 'rmdir' failed if no initrd was required, fixed
* Wed Sep  5 2001 garloff@suse.de
- Set sane PATH in quick_halt (hint from ak).
- Add it to the cfg file list, so user changes will be backed up.
* Tue Sep  4 2001 ro@suse.de
- moved quick_halt/reboot/poweroff to /sbin
* Tue Sep  4 2001 garloff@suse.de
- Added quick_halt/reboot/poweroff script.
* Tue Sep  4 2001 ro@suse.de
- LESS setting in etc/profile had got lost, set to "-M -S -I" again
* Mon Sep  3 2001 werner@suse.de
- Fix reopened bug #9923
- Fix bug #8440
* Mon Sep  3 2001 stepan@suse.de
- added 2 more hooks for splash animation viewer.
* Mon Sep  3 2001 werner@suse.de
- Do not export UID, EUID, USER, MAIL, and LOGNAME (#10088)
* Sat Sep  1 2001 poeml@suse.de
- /etc/init.d/boot: add iSeries native I/O support
- /etc/profile: set TERM=vt100 for iSeries virtual console
* Sat Sep  1 2001 ro@suse.de
- use wrapper for hwclock to combine arch-specific hacks in one place
* Fri Aug 31 2001 olh@suse.de
- add ppc PReP Serie E to hwclock special case
  add /opt/cross/bin to PATH
* Fri Aug 31 2001 ro@suse.de
- added hooks for local plugins in /etc/csh.cshrc and /etc/csh.login
  (#9980)
* Thu Aug 30 2001 werner@suse.de
- Add some complete rules to bash.bashrc
- Do not source ~/.bashrc if not bash
- Source ~/.alias only if shell is not ash
* Wed Aug 29 2001 stepan@suse.de
- add boot script hooks to call splash screen animation program
  in case splash screen is seen.
* Wed Aug 29 2001 ro@suse.de
- added LESS_ADVANCED_PREPROCESSOR="no" to /etc/profile
- set LESS variables in /etc/profile only if LESS is not set
- SuSEconfig.alljava rewritten by Petr Mladek
- /usr/bin/linkto (readlink) and /usr/bin/setJava added
- /usr/sbin/setDefaultJava added
* Tue Aug 28 2001 ro@suse.de
- etc/init.d/network: re-worked "status" output (#9059)
* Tue Aug 28 2001 ro@suse.de
- etc/init.d/nfs: return "unused" for status if no nfs in fstab
    fixed typo (shares vs. shared)  (#9053)
* Mon Aug 27 2001 ro@suse.de
- removed lockd code from /etc/init.d/nfs
  (no longer needed, kernel triggers lockd thread itself)
- added cron.daily/aaa_base_backup_rc.config to make backups
  of etc/rc.config and etc/rc.config.d/* analog to rpmdb (#9875)
- moved rc.config-variables for backups (rpmdb and rc.config)
  to /etc/rc.config.d
* Mon Aug 27 2001 ro@suse.de
- added code to use correct geometry for console ouput of rc script
  if REDIRECT is set
* Fri Aug 24 2001 ro@suse.de
- cleaned up the nfs rc-script:
    explicit lockd start is only needed for the 2.2 case
    check return from startproc for every daemon that is really used
    do nfsmount and ldconfig only if we are really going to mount
    nfs volumes
* Fri Aug 24 2001 draht@suse.de
- Added /usr/sbin/traceroute6 + /var/{run,lib}/smpppd to
  /etc/permissions.*
* Thu Aug 23 2001 ro@suse.de
- added variable CWD_IN_USER_PATH for UID >= 100
  and changed CWD_IN_ROOT_PATH to work for UID < 100
- remove SuSEconfig lockfile if aborted by user (ctrl-c)
* Thu Aug 23 2001 ro@suse.de
- fixed security problem when CLEAR_TMP_DIRS_AT_BOOTUP was active
  (arbitrary directories could be wiped during reboot)
- changed KDEDIR to /opt/kde2 and QTDIR to /usr/lib/qt2
  in sbin/conf.d/SuSEconfig.profiles (sets user environment vars)
* Tue Aug 21 2001 werner@suse.de
- Add check of dead lock file in poll.tcpip
* Tue Aug 21 2001 draht@suse.de
- Added /etc/smpppd.conf and /etc/smpppd-c.conf to
  /etc/permissions.{easy,secure,paranoid}.
* Mon Aug 20 2001 ro@suse.de
- call hwclock --adjtime before hwclock --hctosys at boot time
- call hwclock --systohc at halt/reboot time       (#9173)
- nscd does not support SIGHUP, return rc_failed 3 (#9767)
* Mon Aug 20 2001 draht@suse.de
- permissions.{easy,secure,paranoid} update to reflect config bugs
  in the inn package. Fixes bugid #9606.
* Mon Aug 20 2001 ro@suse.de
- etc/bash.bashrc: test if proc is mounted before trying to
  determine current shell
* Mon Aug 20 2001 ro@suse.de
- refined gpg exec test in postinstall
* Fri Aug 17 2001 ro@suse.de
- etc/profile: test if proc is mounted before trying to
  determine current shell
* Fri Aug 17 2001 ro@suse.de
- etc/profile: replaced "ls" by "/bin/ls" PATH might not be set
* Thu Aug 16 2001 ro@suse.de
- dropped users: lnx, yard, ixess, virtuoso, nps, skyrix, dbmaker,
  fixadm, fib, fixlohn, codadmin
- dropped groups: lnx, yard, dbmaker, fix, codine
- integrated aaa_base.patch
* Thu Aug 16 2001 werner@suse.de
- Add new /etc/profile and /etc/bash.bashrc together with
  an /etc/profile.d/alias.ash for ash shell
* Tue Aug 14 2001 snwint@suse.de
- mk_initrd: run 'raidautorun' only if raid is used; add xor module
  if missing; hint to run lilo
* Mon Aug 13 2001 snwint@suse.de
- made mk_initrd a separate source file
- mk_initrd: run 'raidautorun' in initrd
* Mon Aug 13 2001 ro@suse.de
- changed neededforbuild <sp_libs> to <sp-devel>
* Mon Aug 13 2001 ro@suse.de
- remove xntpd from $remote_fs again (in insserv-dif)
* Mon Aug 13 2001 ro@suse.de
- "apm=power-off" in cmdline will be accepted to run "halt -p"
  (#9255)
- changed default viewer in /etc/mailcap from "xv" to "display"
  (#9618)
- use "/sbin/modprobe" instead of "modprobe" to load agpgart
* Fri Aug 10 2001 ro@suse.de
- rcdummy: always return rcfailed 3 for status if dhclient
- added /var/log/localmessages to /etc/logfiles
- rcrandom: always return true for status
* Thu Aug  9 2001 werner@suse.de
- New insserv version 0.92 with better loop detection.
* Wed Aug  8 2001 ro@suse.de
- fixed status calls for dummy and nfs rc scripts (#9035) (#9053)
* Wed Aug  8 2001 olh@suse.de
- $remote_fs needs xntpd now, update insserv.conf and insserv.8
* Wed Aug  8 2001 froh@suse.de
- added handling of s390 system time set to local time (#9455)
* Tue Aug  7 2001 ro@suse.de
- removed SuSEconfig.susedynamic (we haven't had these in years)
  and rc.config variable HOW_TO_HANDLE_COMMERCIAL_LIBS
- SuSEconfig does not change the runlevel in /etc/inittab any more
  leave this to YaST* (#1076)
- SuSEconfig.inittab will just comment existing S0 lines in inittab
  if SERIAL_CONSOLE is empty (#8600)
- aaa_base_clean_core: do nothing if RUN_UPDATEDB != yes
  (just commented the code, not deleted) (#9553)
- added ORPHAN to /etc/DIR_COLORS (#8209)
- fixed typo in boot.crypto (extra #) (#9621)
* Tue Aug  7 2001 werner@suse.de
- Boot scripts: exit status 7 in stop case is success and is
  mapped to exit status 0
* Mon Aug  6 2001 ro@suse.de
- split SuSEconfig in more modules
- fixed duplicate check to use rc.config.d as well
- removed dosemu hack in SuSEconfig (etc/dosemu.users.* disappeared)
* Mon Aug  6 2001 werner@suse.de
- Fix bug in insserv service link handler
* Sat Aug  4 2001 kukuk@suse.de
- Fix etc/logfiles for squid [Bug #9611]
* Fri Aug  3 2001 werner@suse.de
- New route and network init scripts (bugs #6052, #9082)
* Wed Aug  1 2001 kukuk@suse.de
- Check for /proc/driver/rtc in cron.daily/aaa_base (new location
  with kernel 2.4) [Bug #9451]
- Fix path to sendmail rc.config variables [Bug #9474]
- Unset variable s in etc/profile [Bug #9540]
- Add comment to sbin/chkconfig why it is there and why it is not
  possible to implement it with our LSB conform runlevel system
  [Bug #9521].
* Tue Jul 31 2001 werner@suse.de
- Update to insserv 0.9
- On halt/reboot: Check if loop device was enabled with losetup
- On halt/reboot: touch /success
- On boot: not only remove /fastboot but also /forcefsck and /success
* Tue Jul 31 2001 kukuk@suse.de
- Move RC_L* variables and ROOT_USES_LANG into lang.rc.config
- SuSEconfig.profiles: source lang.rc.config
- remove GOPHER_PROXY (gopher is obsolete today)
- remove delete rule for nscd init script
* Mon Jul 30 2001 froh@suse.de
- fixed arch_special patches for s390
* Mon Jul 30 2001 kukuk@suse.de
- Move /etc/default/useradd to the shadow package
* Thu Jul 19 2001 froh@suse.de
- integrated changes from 7.2-s390 in modules.conf.tar.bz2:
- modules.conf.s390: channel device module options are if kernel=2.2
- Update modules.conf.s390 and symlink modules.conf.s390x to it
* Thu Jul 19 2001 olh@suse.de
- move agpgart entries to i386 in modules.conf
  add firewire entries for ppc
* Wed Jul 18 2001 kukuk@suse.de
- Add patch for [Bug #9358] (no keytable loaded at first boot)
* Thu Jul 12 2001 ro@suse.de
- move skyrix home to /opt/skyrix
* Thu Jul 12 2001 ro@suse.de
- fix typo in BOOT_SPLASH code
- added raidstart call (needed when persistent md devices are uses
  and md is compiled as modules)
* Thu Jul 12 2001 ro@suse.de
- added rc.config variable BOOT_SPLASH to turn splash-screen
  off after kernel-load
- BOOT_SPLASH defaults to "no" on SLES
* Wed Jul 11 2001 ro@suse.de
- removed informix user and group (#9136)
* Sun Jul  8 2001 ro@suse.de
- removed START_NAMED variable (in other packages) (#8899)
* Thu Jul  5 2001 ro@suse.de
- fixed buglet in Check
* Thu Jul  5 2001 kukuk@suse.de
- Remove info box at first boot about root login
* Tue Jul  3 2001 mantel@suse.de
- updated alias entries for iBCS2 (now: abi-ibcs)
* Tue Jul  3 2001 ro@suse.de
- don't search for core files on ncpfs filesystems
* Tue Jun 26 2001 ro@suse.de
- updated zshrc from mmj
* Mon Jun 25 2001 cstein@suse.de
- rewrote /etc/rc.d.README *again* ...  (bug #9120)
- reorganized and extended /etc/DIR_COLORS (e.g. included some more
  image extensions and added colouring for sound files)
- some cosmetic changes to /etc/inittab
* Mon Jun 25 2001 ro@suse.de
- change shell for sapdb user to /bin/bash
- remove trace of empress user in fillup-template for shadow
* Thu Jun 21 2001 cstein@suse.de
- changed etc/rc.status variable rc_missed, whose content did
  not match its purpose
- rearranged etc/profile, added and corrected comments
- rewrote much of etc/profile.dos and added the 'sys' command
- rewrote etc/rc.d.README
- changed comments in etc/rc.status
* Wed Jun 20 2001 cstein@suse.de
- corrected some things in lib/YaST/*, especially stylistic issues
  and grammatical mistakes in the English message strings.
* Tue Jun  5 2001 mantel@suse.de
- removed comment referring to obsolete kerneld in /etc/modules.conf
  closes bug #7757
* Tue May 29 2001 ro@suse.de
- added /media to UPDATEDB_PRUNEPATH in rc.config
* Wed May 23 2001 werner@suse.de
- Use correct shell variable for script path at boot logging
* Tue May 22 2001 werner@suse.de
- Avoid font initialization for other runlevels than N aka
  boot in boot.crypto
* Mon May 21 2001 bk@suse.de
- preserve more options from /etc/modules.conf:
  preserve aliases and module options of all eth, tr and ci interfaces
  preserve options of ctc, iucv and xpram modules
  (aliases are set by default)
* Mon May 21 2001 werner@suse.de
- Add a workaround in /etc/init.d/boot to get forcing
  of execution of boot.crypto working correct.
* Tue May 15 2001 ro@suse.de
- modularize hostname part from SuSEconfig to SuSEconfig.hostname
- call SuSEconfig (with args) in bootscript if needed
* Mon May 14 2001 ro@suse.de
- added isapnp_reset=0 as option for isa-pnp in modules.conf
* Mon May 14 2001 ro@suse.de
- added /var/log/httpd/jserv.log and mod_jserv.log to logfiles
* Mon May 14 2001 snwint@suse.de
- mk_initrd: add lvm-mod if / on lvm
* Mon May 14 2001 draht@suse.de
- permissions.* change: /usr/bin/man suid man -> suid root
* Fri May 11 2001 zoz@suse.de
- modify_resolvconf now always leaves a proper r.c. after restore
  (Bug 8135)
* Fri May 11 2001 werner@suse.de
- Simple change in xdm init script to avoid failed message (bug#7411)
* Fri May 11 2001 kkaempf@suse.de
- (#7949) silently remove runme_at_boot if yast2 was not installed
* Thu May 10 2001 werner@suse.de
- Add keyboard and terminal initialization in boot.crypto
* Thu May 10 2001 snwint@suse.de
- copy ld-*so* to initrd, not ld-2.2.so
- put /dev/rd/* into initrd (lvm only)
- make it work in chroot environment
* Thu May 10 2001 werner@suse.de
- Better formating of skipped/failed messages of /etc/init.d/rc
- Map status greater than 7 to 1 in /etc/rc.status
- Avoid boot logging of sulogin shell and pass phrase on losetup
* Wed May  9 2001 draht@suse.de
- removed suid from straps (scotty package) in permissions*
* Tue May  8 2001 ro@suse.de
- tty-ldisc-3 now dependent from kernel_version(ppp/ppp_async)
  (fix for #7842)
* Tue May  8 2001 draht@suse.de
- changed the copyright notice of /etc/permissions.local (removed)
  (resolves bug #7867)
* Tue May  8 2001 poeml@suse.de
- update man page modify_resolvconf.8
* Tue May  8 2001 zoz@suse.de
- modify_resolvconf: added -p to all cp (Bug 7582)
- modify_resolvconf: does not leave stale tmp files any longer
    (Bug 7883)
- modify_resolvconf: removed another possible endless loop
    (Bug 7316)
- ip-up: now creates resolv.conf backups for every interface
    (Bug 7686)
* Tue May  8 2001 ro@suse.de
- added bttv to keepoptions (#6391)
* Mon May  7 2001 werner@suse.de
- Move boot.crypto before touch other files and
  files systems (besides /)
* Mon May  7 2001 snwint@suse.de
- dropped vmlinuz_24 from mk_initrd (#7715)
- mk_initrd now under GPL
* Mon May  7 2001 ro@suse.de
- changed DO_QUINT to HALT_SOUND (#7456)
* Fri May  4 2001 ro@suse.de
- updated comment for CLEAR_TMP_DIRS_AT_BOOTUP (#7605)
* Fri May  4 2001 mantel@suse.de
- added entry for IBM thinkpad in modules.conf.i386
* Fri May  4 2001 uli@suse.de
- fixed handling of special case IBMJava2-JRE in SuSEconfig.alljava
* Thu May  3 2001 ro@suse.de
- fix bug in code for CLEAR_TMP_DIR_ON_BOOT (#7599)
* Thu May  3 2001 ro@suse.de
- added rc.config variables for INITRD_MODULES (long overdue)
  and for DO_QUINT
- added alias for mwavedd to modules.conf on i386
- added chroot to gpg-call in post-install (#7540)
* Thu May  3 2001 werner@suse.de
- Disable quint at halt/reboot
* Thu May  3 2001 zoz@suse.de
- replaced wrong modify_resolvconf with the new version, which i
  already tried to check in at Mon Apr 30 14:23:40 CEST 2001
* Wed May  2 2001 kukuk@suse.de
- Fix syntax error in modules.conf for SPARC
* Mon Apr 30 2001 draht@suse.de
- added vmware-ping to permissions*
* Mon Apr 30 2001 zoz@suse.de
- modify_resolvconf: fixed bug 7316 and added support for multiple
  modifikation (is needed for pppoe; arvin)
* Mon Apr 30 2001 ro@suse.de
- added sapdb group and user sapdb (/var/opt/sapdb)
* Sat Apr 28 2001 draht@suse.de
- added /etc/crontab to permissions files (#6411)
* Fri Apr 27 2001 werner@suse.de
- Do message of skipped services in yellow not in red (#7338)
- Even on quite status check we should rember the state
* Thu Apr 26 2001 werner@suse.de
- Fix line drawing of rc.status even if we're in check status mode
* Thu Apr 26 2001 ro@suse.de
- updated comment in etc/ppp/ip-up (from arvin)
* Thu Apr 26 2001 ro@suse.de
- check also for permissions.local.rpmsave
* Thu Apr 26 2001 mantel@suse.de
- added alias char-major-10-181 toshiba
* Thu Apr 26 2001 ro@suse.de
- commented "options parport_pc" in modules.conf (#7143)
* Thu Apr 26 2001 ro@suse.de
- changed comment for GMT (#3907)
* Wed Apr 25 2001 ro@suse.de
- updated ip-up from arvin (use modify-resolvconf)
- made ip-down a symlink to ip-up again (had got lost)
- added net-pf-24 alias for 2.4 case
* Wed Apr 25 2001 cstein@suse.de
- Updated some of the descriptions in the files rc.config_parts/*
  according to changes in 7.2
  I also corrected some grammar and style issues.
* Tue Apr 24 2001 draht@suse.de
- More additions: kamplus -> /etc/permissions.*
* Tue Apr 24 2001 draht@suse.de
- updates to permissions files, among them: opie, /etc/init.d,
  /usr/src/packages/*, mtr, phoenix
* Tue Apr 24 2001 mantel@suse.de
- remove bttv option
* Tue Apr 24 2001 mantel@suse.de
- rename lvm to lvm-mod in modules.conf
- add option for bttv in modules.conf
* Tue Apr 24 2001 ro@suse.de
- removed pcnfsd from insserv list
* Tue Apr 24 2001 ro@suse.de
- removed pcnfsd startscript (now in bcnfsd/bwnfsd package)
  it's variables and rc-links
- removed old rc-links for cron and kerneld
* Mon Apr 23 2001 ro@suse.de
- removed kerneld startscript and variable
- removed cron startscript and variable (moved to cron package)
- Make nscd init script LSB ready (kukuk)
- Fix missing newline after `rc_status -v'.
- use "halt -p" also if kernel runs acpi (#6989)
* Mon Apr 23 2001 ro@suse.de
- moved pre/post script to separate files
- fix handling of permissions.local (#7087)
  (erroneously was in file-list during 7.1)
* Mon Apr 23 2001 ro@suse.de
- added patch for boot-script to start SuSEconfig after YaST2
  only if needed
* Fri Apr 20 2001 mfabian@suse.de
- remove LESSCHARSET from /etc/profile and /etc/csh.cshrc.
  Setting it to "latin1" is not useful, this is the default anyway
  unless "UTF-8" is found in LC_ALL, LC_CTYPE or LANG, then the
  default is utf-8. Therefore, setting LESSCHARSET=latin1 prevents
  automatic detection of UTF-8 locales.
- set LESS, LESSOPEN, and LESSCLOSE in /etc/csh.cshrc to the same
  values as in /etc/profile. Remove less options from PAGER.
- do not source /etc/SuSEconfig/csh.cshrc and
  /etc/SuSEconfig/profile if LANG is already set to prevent
  overriding locale variables already present in the environment.
- enable editing in EUC encoding in /etc/csh.cshrc for the
  languages where this makes sense.
- don't add backup files to fonts.scale in SuSEconfig.fonts
* Thu Apr 19 2001 kukuk@suse.de
- Start network after usbmgr [Bug #7024]
* Thu Apr 19 2001 werner@suse.de
- Re-enable -s/-u for rc_status and set appropiate exit value
* Tue Apr 17 2001 arvin@suse.de
- commented alias for autofs4
- removed mssclampfw for kernel 2.4
* Thu Apr 12 2001 garloff@suse.de
- Updated skeleton: try-restart works as documented now.
* Wed Apr 11 2001 ro@suse.de
- added rc.config variable CLEAR_TMP_DIRS_AT_BOOTUP defaulting
  to "no"
* Wed Apr 11 2001 ro@suse.de
- added echo line for boot.crypto
* Wed Apr 11 2001 schwab@suse.de
- mk_initrd: Use vmlinuz and vmlinuz.suse as default list of kernels on
  ia64.
* Wed Apr 11 2001 ro@suse.de
- changed boot.crypto to allow blank-lines and comments
  in /etc/cryptotab
* Wed Apr 11 2001 kukuk@suse.de
- Use .exrc and .xinitrc for root from aaa_skel
* Tue Apr 10 2001 ro@suse.de
- updated comment for ROOT_LOGIN_REMOTE (#412)
* Tue Apr 10 2001 ro@suse.de
- changed headline for SuSEconfig.alljava to bin/bash (#6854)
- added insserv call for boot.crypto and removed change from boot
* Tue Apr 10 2001 ro@suse.de
- added etc/init.d/boot.crypto and code in boot script to call it
- added rc.config variable START_CRYPTO_FILESYSTEMS default "yes"
- updated zshrc from mmj@suse.de
- updated rc.status from werner@suse.de
* Mon Apr  9 2001 zoz@suse.de
- fixed modify_resolvconf to keep all unhandled options plus some
  minor changes
- added manpage for modify_resolvconf
* Wed Apr  4 2001 bk@suse.de
- move alias char-major-108 ppp_asnc to non-2.2 block(new dev in 2.4)
* Tue Apr  3 2001 zoz@suse.de
- added modify_resolvconf to /sbin
  added MODIFY_RESOLV_CONF_DYNAMICALLY to rc.config.aaa_base
- patched /etc/init.d/boot to call "modify_resolvconf cleanup"
- patched /etc/ppp/ip-up to use modify_resolvconf for ipppd
* Tue Apr  3 2001 kukuk@suse.de
- Move install_lsb/remove_lsb to /usr/lib/lsb
* Tue Apr  3 2001 kkaempf@suse.de
- dont check for /lib/YaST2 anymore
  run SuSEconfig during initial boot
* Tue Mar 27 2001 froh@suse.de
- fixed arch_special/s390/inittab.dif
- changed "patch < $file" into "patch --input=$file" in specfile, to
  make the patch file name visible in .build.log
* Thu Mar 22 2001 ro@suse.de
- fixed entries for uucp logfiles in /etc/logfiles (#6150)
- added fix from werner to etc/init.d/rc (stat->status)
* Wed Mar 21 2001 ro@suse.de
- removed POVRAYOPT from /etc/profile (#6781)
- changed text in initscript update notify mail (#6743)
- changed LESS environment variables in /etc/profile for updated
  less package
* Fri Mar 16 2001 ro@suse.de
- fix passwd entry for man on update (#6290)
- fix disk space reporting in rotate_logs cronjob (#4945)
- clean old yp bindings on boot (#6265)
* Tue Mar 13 2001 draht@suse.de
- inndstart set to 4754 in both permissions.easy and secure.
* Mon Mar 12 2001 ro@suse.de
- fixed nfs-start script: statd and lockd in /sbin ; also start if
  START_AUTOFS is set to yes  (#6699)
- replaced all uname -r hacks in modules.conf by kernelversion call
  (#6652)
* Sat Mar 10 2001 schwab@suse.de
- Adjust ia32 lib paths in ld.so.conf for ia64.
* Fri Mar  9 2001 fehr@suse.de
- change mk_initrd to search for the new naming scheme of liblvm
  when root fs is on lvm LV
* Tue Mar  6 2001 arvin@suse.de
- use pppox on kernel 2.2 and pppoe on 2.4 as alias char-major-144
* Tue Mar  6 2001 uli@suse.de
- added CREATE_JAVALINK to rc.config that controls operation
  of SuSEconfig.alljava
- fixed SuSEconfig.alljava for package names containing "-"
* Mon Mar  5 2001 ro@suse.de
- *shadow to 640/grp shadow in %%post
* Mon Mar  5 2001 ro@suse.de
- specfile fix
* Mon Mar  5 2001 ro@suse.de
- one permissions.local is enough: update the one in specfile
  and remove the one from extra source (#6498)
* Mon Mar  5 2001 ro@suse.de
- don't put GNOMEDIR IN /etc/SuSEconfig/profile (#3617)
- moved "umask 022" from rc.config to SuSEconfig (#6491)
  (let's see what will happen with the modules)
* Mon Mar  5 2001 ro@suse.de
- fix mode for passwd,group (if other umask in update)
* Mon Mar  5 2001 snwint@suse.de
- automatically adjust initrd size
* Mon Mar  5 2001 ro@suse.de
- added fixes in modules.conf for ppp vs ppp_generic
- added fixes for ppc parallel port (io 0x3bc)
- use "manpath -q" to determine MANPATH in /etc/profile
* Wed Feb 28 2001 ro@suse.de
- moved hwclock call in bootscript after mounting filesystems
  (#6404)
* Mon Feb 26 2001 ro@suse.de
- fixed typo in specfile
* Fri Feb 23 2001 ro@suse.de
- replace use of aaa_base_versions by build-generated .buildenv
* Wed Feb 14 2001 werner@suse.de
- Migrate showconsole to sysvinit
* Wed Feb 14 2001 ro@suse.de
- split modules.conf into common and arch-specific part
- removed serial start script    (#6342)
- fixed SuSEconfig start message (#1801)
* Tue Feb 13 2001 ro@suse.de
- removed routed script and rc.config-variable
  (is in own package now)
* Mon Feb 12 2001 ro@suse.de
- fixed typo in modules.conf comment
* Fri Feb  9 2001 ro@suse.de
- really corrected agetty levels: all 1-5
* Fri Feb  9 2001 ro@suse.de
- fixed SuSEconfig for correct init-levels for agetty on Ser-Cons
* Wed Feb  7 2001 ro@suse.de
- fixed typos in postinstall mail
* Mon Feb  5 2001 werner@suse.de
- New showconsole version 0.9
  * now with better interface for boot logging
- New rc.status to fit LSB specs
- Changes scriptes within /etc/init.d/:
  * rc to fit better boot logging and console switching
  * halt to fit boot logging, new sound and forgotten swaps devices
  * boot to fit boot logging and new swapon behavior
  * skeleton to fit changed startproc/killproc/checkproc and LSB
* Tue Jan 23 2001 ro@suse.de
- fixed postinstall (modules.conf)
- fixed permissions (isdnctrl et al re-added)
* Mon Jan 22 2001 ro@suse.de
- fixed modules.conf update
* Mon Jan 22 2001 ro@suse.de
- moved permissions to extra src archive
- updated permissions from draht
* Fri Jan 19 2001 ro@suse.de
- start yast1/2 firstboot-scripts with a real console
* Thu Jan 18 2001 ro@suse.de
- fixed printing of root-login message
* Wed Jan 17 2001 ro@suse.de
- deleted db2 users and groups (46,47,48 uid and gid)
* Wed Jan 17 2001 schwab@suse.de
- Add ia32 lib paths to ld.so.conf.
* Wed Jan 17 2001 ro@suse.de
- fixed buglet in postinstall when parsing old modules.conf
* Wed Jan 17 2001 kukuk@suse.de
- Fix removal of root login message on SPARC
* Wed Jan 17 2001 ro@suse.de
- copy old {boot,halt}.local if non-empty
* Mon Jan 15 2001 ro@suse.de
- fixed typo in root-login msg and added cr
* Mon Jan 15 2001 werner@suse.de
- Simple workaround for 2.4 kernels: don eat our messages
  if signaled
* Mon Jan 15 2001 ro@suse.de
- xdm-script depends on ypbind (not ypclient) (#5626)
- added var/log/{nmb,smb} to etc/logfiles (#5684)
* Sat Jan 13 2001 snwint@suse.de
- mk_initrd changes:
  - continue with next kernel/initrd on errors
  - create initrd even if modules are missing
    (exit code 9 is returned in tese cases)
  - keep old initrd if a new one could not be made
* Fri Jan 12 2001 grimmer@suse.de
- corrected beep tone in /etc/init.d/halt from 200 Hz to 440 Hz
  to make sensitive listeners happy
* Fri Jan 12 2001 garloff@suse.de
- mount shm fs to /dev/shm if available (2.4 kernels) in
  /etc/init.d/boot script
- recognize /dev/shm as shm mount point in reboot/halt script
* Fri Jan 12 2001 ro@suse.de
- added WDM to displaymanagers in SuSEconfig
  (wdm was there already) (#5557)
* Thu Jan 11 2001 ro@suse.de
- changed references to klogd (moved to /sbin)
* Thu Jan 11 2001 ro@suse.de
- removed pre-install i810 from modules.conf again
* Thu Jan 11 2001 ro@suse.de
- move kill of blogd before yast1 start
* Thu Jan 11 2001 bk@suse.de
- added aliases for ppp-compress-18(ppp_mppe) and 24(ppp_deflate)
  to modules.conf
* Wed Jan 10 2001 mantel@suse.de
- load module mssclampfw for pppox
* Tue Jan  9 2001 ro@suse.de
- added comment for ROOT variable in SuSEconfig
* Tue Jan  9 2001 snwint@suse.de
- fixed mk_initrd to _really_ create no initrd unless necessary
* Mon Jan  8 2001 ro@suse.de
- added perforce user and group  and entry for logfiles
* Mon Jan  8 2001 ro@suse.de
- fixed message for missing xf86configfile (#4687)
- removed NAMESERVER and SEARCHLIST from default-rc.config
- comment NAMESERVER and SEARCHLIST for update
- make /sbin/bootp write resolv.conf itself
- move kill for blogd before yast2 start (#5315)
- added wdm to list of possible DISPLAYMANAGERs (#4664)
* Mon Jan  8 2001 ro@suse.de
- fixed remaining occurences of conf.modules
* Sun Jan  7 2001 kkeil@suse.de
- new etc/ppp/ip-up srcipt (#BUG 3949)
* Thu Jan  4 2001 schwab@suse.de
- mk_initrd: increase initrd size.
* Tue Jan  2 2001 schwab@suse.de
- Fix get_kernel_version to make sure the version string is not
  truncated.
* Sat Dec 30 2000 kukuk@suse.de
- Don't add links to serial scrips on SPARC and s390 (we don't have it)
* Thu Dec 21 2000 ro@suse.de
- fixed handling of suse-build key
* Wed Dec 20 2000 ro@suse.de
- added DISABLE_ECN rc.config variable and code to boot-script (#4890)
- added tbz to DIR_COLORS (#4794)
- added code to sbin/conf.d/SuSEconfig.profiles to set RC_LANG
  from DEFAULT_LANG using the mapping in locale.alias
- fixed rc_done test in rc.config on update
* Wed Dec 20 2000 bk@suse.de
- Make permissions.paranoid consistent with last months /var/run
  permissions change to make it root.root 755. (Fix for bug #2857)
* Wed Dec 20 2000 bk@suse.de
- changed kernel OSS examples comment to reflect ALSA.
* Mon Dec 18 2000 kkeil@suse.de
- fixed mk_initrd (had been modified based on older version before)
* Mon Dec 18 2000 ro@suse.de
- changed mysql to /var/lib/mysql
* Sun Dec 17 2000 ro@suse.de
- added osst alias to modules.conf
- don't copy old init-scripts but send mail to root
* Fri Dec 15 2000 werner@suse.de
- New showconsole 0.6
  * Now we're able to do ioctl TIOCGDEV to fetch real tty of
    /dev/console, this requires a patched kernel during compile
    (Thanks to Kurt Garloff)
  * Old way remains as fallback, if kernel dosn't support TIOCGDEV
* Fri Dec 15 2000 snwint@suse.de
- different kernel files on alpha/ia64/ppc in mk_initrd
* Fri Dec 15 2000 werner@suse.de
- insserv makefile fixed
* Fri Dec 15 2000 ro@suse.de
- added personal-firewall calls to ip-up
- touch root/.bash_history in postinstall and chmod 600
- fix for csh.login if ( -o /dev/$tty && ${?prompt} ) date
- added /root/.gnupg/pubring.gpg as config-noreplace
* Fri Dec 15 2000 werner@suse.de
- Make /etc/zshrc compatible with TERM kvt and gnome
- Update insserv
  * Make s and b identical to S and B
  * Move LSB directory to /lib/lsb/ and set
    compatibility link /usr/lib/lsb
  * install_initd is a script now
* Fri Dec 15 2000 ro@suse.de
- fixed typo in boot-script
* Thu Dec 14 2000 ro@suse.de
- improved preserving entries from previous modules.conf
* Thu Dec 14 2000 ro@suse.de
- improved handling for klogconsole in boot-script:
  call klogconsole with -l 7 -r 0 if SERIAL_CONSOLE is set
* Wed Dec 13 2000 ro@suse.de
- added quotes for $des in LVM-start code in boot-script
* Wed Dec 13 2000 ro@suse.de
- applied patch from lmuelle for mk_initrd (#4587)
* Wed Dec 13 2000 ro@suse.de
- fix if DEFAULT_WM has more than one entry (#4497)
- fix for LVM if root partition is reiserfs (#4429)
- fix postgres entries in etc/logfiles      (#4403)
- fix typo in etc/init.d/powerfail          (#4158)
- add route for local-net even for 2.2.*    (#4143)
* Tue Dec 12 2000 ro@suse.de
- added opt/kde2/lib to etc/ld.so.conf
- only load memstat module if rc.config-variable is set
* Tue Dec 12 2000 fehr@suse.de
- Add changes (to /etc/init.d/boot and /sbin/mk_initrd) to allow a
  LVM logical volume as root device
* Mon Dec 11 2000 werner@suse.de
- Replace deletion of boot.msg with a move to boot.omsg to
  be able to read the messages during shutdown wrote by blogd.
- Set TERM to vt102 on serial console in master rc
- Update of showconsole (now blogd should never hold a controlling
  tty anymore).
- Add wdm to the handled X Display Managers
* Sun Dec 10 2000 kukuk@suse.de
- Add new mk_initrd for 2.4 kernels
- init.d/boot: Don't move away boot.msg, we deleted it already
- rc.config: Quote $rc_done test
* Sun Dec 10 2000 kukuk@suse.de
- Unpack showconsole in setup
* Thu Dec  7 2000 werner@suse.de
- Make single user mode less verbose
* Thu Dec  7 2000 werner@suse.de
- Add showconsole 0.4 with its boot log daemon blogd
- Change boot, halt, and rc to use showconsole and blogd
- Make halt more robust if umount fails
- setterm writes escape sequences to stdout (halt)
- Fix bug in etc/ppp/poll.tcpip
- Update to insserv 0.7 (now $networks includes pcmcia)
- Add Kurts skeleton with changes due newer LSB spec
* Wed Dec  6 2000 schwab@suse.de
- Allow dashes in etc/permissions.d filenames.
* Tue Dec  5 2000 ro@suse.de
- added rest of scripts to insserv call
- added raid0run call to boot script
* Tue Dec  5 2000 kukuk@suse.de
- Add /usr/bin/z81 to /etc/permissions.easy
* Mon Dec  4 2000 ro@suse.de
- Check: skip freetype directory
* Mon Dec  4 2000 ro@suse.de
- added /var/log/uucp as uucp.uucp 755 to etc/permissions
* Sun Dec  3 2000 ro@suse.de
- updated insserv to 0.6
- removed IRCSERVER stuff from SuSEconfig and rc.config
  (in ircii package as SuSEconfig.ircii)
- add SuSEconfig.alljava to set jre and jdk links
* Wed Nov 29 2000 ro@suse.de
- SuSEconfig: leave resolv.conf alone
- removed CREATE_RESOLVCONF from etc/rc.config
* Tue Nov 28 2000 ro@suse.de
- update to insserv-0.5 (support for facilities)
* Mon Nov 27 2000 ro@suse.de
- first fixup for etc/init.d movement
* Mon Nov 27 2000 ro@suse.de
- clean_tmp: leave sockets alone
- move sbin/init.d to etc/init.d
- removed start scripts for inetd rpc nfsserver rwhod
  (in other packages)
* Sun Nov 26 2000 olh@suse.de
- use hwclock in PowerMacs, add MTX+ SMP bwclock support
- rm -fv /tmp/screens on startup
* Fri Nov 24 2000 ro@suse.de
- renamed LANGUAGE to DEFAULT_LANGUAGE in /etc/rc.config
  and /sbin/SuSEconfig
- updated insserv to 0.4
- simplyfied code to rename rc.config-variables in postinstall
- split modules SuSEconfig.fonts and SuSEconfig.profiles
  from main script
- skip /usr/X11R6/lib/X11/fonts/CID in Check
- add opt/kde2/bin to PATH if exists
- fixed double-var check for SuSEconfig
- Check: don't compress links pointing to a directory
* Wed Nov 22 2000 werner@suse.de
- Make /etc/inputrc knowing about TERM kvt and gnome
- Change owner and permissions of /var/run  (root.root with 0755)
* Fri Nov 17 2000 ro@suse.de
- /sbin/init.d/boot:
  no hwclock for s390
  move hwclock earlier in boot process
- remove conf.modules symlink  (#4297)
* Fri Nov 17 2000 sndirsch@suse.de
- added "options agpgart agp_try_unsupported=1" to modules.conf
  to use agpgart also with chipsets that are not detected
  automatically by the kernel module
* Thu Nov 16 2000 werner@suse.de
- Use kdm of KDE2 if available
- Add comment for killproc usage (see manual page of killproc)
* Thu Nov 16 2000 werner@suse.de
- new boot scheme:
  * remove rctab
  * add new insserv(8)
  * update init.d(7)
  * change spec to use insserv
  * remove runlevel links
  * add LSB comments to the boot scripts of aaa_base
  * Update inittab to fit LSB runlevels
* Wed Nov  8 2000 bk@suse.de
- added PAM config (was moved to SuSEconfig.pam, and thus removed
  from the "quick" scripts) again to the "quick"(important) scripts
  (like sendmail, kdm and so on).
  This is a problem when e.g. yast only calls SuSEconfig -quick
  and the the login config would not habe been changed...
* Fri Nov  3 2000 ro@suse.de
- SuSEconfig: call mkfontdir with encodings if present
- Check: don't zip encodings.dir
* Thu Nov  2 2000 ro@suse.de
- added user pop (/var/lib/pop)
* Fri Oct 27 2000 ro@suse.de
- wwn home to /var/lib/wnn
* Fri Oct 27 2000 bk@suse.de
- added user wnn for package fwnn from mfabian
* Thu Oct 26 2000 mantel@suse.de
- use new autofs4 (alias autofs autofs4)
- added alias for Moxa multiport serial cards
* Mon Oct 23 2000 ro@suse.de
- removed etc/protocols again: already part of netcfg package
* Mon Oct 23 2000 werner@suse.de
- Ignore error during restart of routing (#4178)
* Mon Oct 23 2000 ro@suse.de
- added etc/protocols (#4183)
* Fri Oct 20 2000 werner@suse.de
- Make colored output faster
- Fix the three `eating' lines within sbin/init.d/boot
- Add nosmbf for umounting to avoid timeouts due smbf
* Tue Oct 17 2000 mantel@suse.de
- added pre-install directives for video modules
* Fri Oct 13 2000 mantel@suse.de
- added new alias to /etc/modules.conf for iBCS2
* Thu Oct 12 2000 ro@suse.de
- /sbin/init.d/nfs: fixed for nfs-utils without k-prefix
* Thu Oct 12 2000 kukuk@suse.de
- Move PAM support from SuSEconfig into extra module
* Sun Oct  8 2000 kukuk@suse.de
- Fix missing %%endif
* Fri Oct  6 2000 kukuk@suse.de
- Add lib64 to ld.so.conf on sparc64
* Thu Sep 28 2000 ro@suse.de
- added dummy script /sbin/chkonfig (always exit 0)
* Thu Sep 28 2000 ro@suse.de
- SuSEconfig: added parameter "--module name"
- SuSEconfig: added languages japanese and korean
- SuSEconfig: fixed handling for files in etc/permissions.d
- etc/profile: TEXINPUTS: added /usr/share/doc/.TeX
- permissions: added cvem and adamem (no-suid in secure)
- added /usr/bin/bash to etc/shells (#4026)
* Thu Sep  7 2000 mantel@suse.de
- added alias char-major-10-130 softdog to /etc/modules.conf
* Thu Sep  7 2000 bk@suse.de
- added arch-special diff for sbin/init.d/network for s390 (mtu 1450)
* Thu Sep  7 2000 ro@suse.de
- /sbin/init.d/serial find ports without ls
- /sbin/init.d/boot no klogconsole if SERIAL_CONSOLE is set
* Mon Sep  4 2000 ro@suse.de
- SuSEconfig: check for duplicated values in /etc/rc.config (#234)
- disabled fsck-progress bars for s390
- echo a newline before writing localhost entry to /etc/hosts (#3048)
- use awk for filesize script (#3635)
- cosmetic fix in Check for RPM_BUILD_ROOT ending in "/"
- fix sequence of ports in /sbin/init.d/serial (#3728)
- added simple manpage for chkstat (#3742)
* Wed Aug 23 2000 kendy@suse.cz
- Removed setting of PRINTER env. variable from /etc/profile
- Added DEFAULT_PRINTER to /etc/rc.config and SuSEconfig modified
  to assign it to PRINTER in /etc/SuSEconfig/{profile,csh.cshrc}
* Wed Aug 23 2000 ro@suse.de
- added user vscan: 65,/var/spool/vscan,/bin/false
- added group maildrop: 59
* Fri Aug 18 2000 kkeil@suse.de
- mk_initrd changes:
  * support for 2.4 kernel versions
  * optional parameter for easy use with other configurations
* Sat Aug  5 2000 kukuk@suse.de
- Don't show on SPARC root login message
- fsck should not use progress bar on serial console
- Use bzip2
* Mon Jul 24 2000 kukuk@suse.de
- Add rc.status patch from Werner
* Fri Jul 21 2000 kukuk@suse.de
- daily cronjob should clean /var/cache/man, not /var/catman
* Fri Jul 21 2000 bk@suse.de
- Cosmetic fix for /etc/ppp/ip-up (removes /etc from "cat x /etc >>y")
* Fri Jul 21 2000 kukuk@suse.de
- Remove user empress [Bug #3464]
* Tue Jul 18 2000 ro@suse.de
- added kde2 apps to /etc/permissions
* Mon Jul 17 2000 ro@suse.de
- skyrix home to /opt/skyrix/skyrix36
- added cipe entries to modules.conf
- added kwintv and kv4lsetup to permissions.{easy,secure}
* Mon Jul 17 2000 werner@suse.de
- SuSEconfig's profile: only send the console magic `(B' if
  we have TERM=linux _and_ if stdout is connected to a terminal.
* Sat Jul 15 2000 kukuk@suse.de
- passwd: Move "man" home directory to /var/cache/man
* Sun Jul  9 2000 ro@suse.de
- updated options for bttv (commented) in modules.conf
* Thu Jul  6 2000 ro@suse.de
- removed dbgrp and dbuser again: useless
* Thu Jul  6 2000 werner@suse.de
- Better messages formating in /sbin/init.d/boot and /sbin/init.d/serial
* Thu Jul  6 2000 ro@suse.de
- added generic db user and group: dbuser,dbgrp,/var/lib/dbuser
* Thu Jul  6 2000 snwint@suse.de
- added get_kernel_version
- changed mk_initrd to use get_kernel_version
* Wed Jul  5 2000 bk@suse.de
- Fixed ip-{up|down}.local calls for pppoe
* Mon Jul  3 2000 werner@suse.de
- Add application/x-ns-proxy-autoconfig with *.pac to mime.types
* Fri Jun 30 2000 werner@suse.de
- Add usbdevfs to pre-umounting
- Do pre-umounting in reverse order to avoid busy devices
- use case ... esac to speed up pre-umounting
* Fri Jun 30 2000 werner@suse.de
- Fix xdm boot script to know about rc shell functions.
* Thu Jun 29 2000 ro@suse.de
- added ip-down as config file (#2954)
- updated ip-up script:
  - added NETCONFIG_PCMCIA (BUG 2646)
  - clean up firewall setup, added calls to /sbin/SuSEfirewall
  - removed nscd restarts, since nscd host cache is disabled(default)
- updated permissions files for new i4l file layout (#3016)
  - fixed path to isdnctrl and isdnbutton in permissions*
  - permissions.easy: isdnctrl only for uucp users
- use parport_ax instead of parport_pc
    on sparc in modules.conf (#2988)
* Mon Jun 26 2000 ro@suse.de
- dont allow login in runlevel 0 and 6
- dont initialize consoles 1-12 if framebuffer is active
* Sun Jun 25 2000 bk@suse.de
- fixed arch_special/s390/inittab.dif
* Sun Jun 25 2000 bk@suse.de
- remove serial scripts on s390, console fix for bootsetup on s390
* Wed Jun 21 2000 werner@suse.de
- Remove device check from route boot script
- Add some newer devices and file systems for `umount'ing
* Tue Jun 20 2000 kukuk@suse.de
- pkgmake: Add bz2 support
* Tue Jun 20 2000 ro@suse.de
- commented alias for unzip
- added fillup manpage
* Mon Jun 19 2000 werner@suse.de
- Fix always failed message for hwclock setting and enabled xntpd
* Mon Jun 19 2000 olh@suse.de
- allow login in runlevel 0 and 6
  initialize consoles 1-12 if framebuffer is active
* Thu Jun  8 2000 werner@suse.de
- Fix sourcing of /etc/rc.status if not within root fs
- Change YaST2 path for SuSE 7.0  (now /usr/lib/YaST2/)
* Wed Jun  7 2000 bk@suse.de
- updated spec for 6.4-s390
* Sun Jun  4 2000 ro@suse.de
- added missing oldstat file
* Wed May 31 2000 werner@suse.de
- Add /etc/rc.status for status handling within boot scripts
- Change all boot scripts to use /etc/rc.status
- Move parts of /sbin/init.d/boot.setup to /sbin/init.d/kbd
  of package kbd
- Move links of /sbin/init.d/boot.setup and /sbin/init.d/serial
  to /sbin/init.d/boot.d/
- Add /etc/ppp/pool.tcpip and a comment in /etc/ppp/ip-up
- Add %%{_fixowner} and %%{_fixgroup} macros
* Mon May 29 2000 kasal@suse.cz
- changed SuSEconfig to set LC_CTYPE even for root (if allowed in rc.config)
* Fri May 26 2000 bk@suse.de
- Updated alsa config examples in modules.conf
* Tue May 23 2000 kukuk@suse.de
- Add /etc/host.conf
- Don't let SuSEconfig create /etc/host.conf
- Don't add kerneld variable to rc.config on SPARC
* Thu May 18 2000 ro@suse.de
- fixed problem in chkstat
* Thu May 18 2000 kukuk@suse.de
- Use /var/games as homedirectory for user games
* Tue May 16 2000 kukuk@suse.de
- With 7.0, move /usr/doc -> /usr/share/doc
- Add /var/spool/cron to etc/permissions*
* Fri May 12 2000 kukuk@suse.de
- Fix syntax error in SuSEconfig
* Thu May 11 2000 ro@suse.de
- added zope user, group daemon, shell /bin/false, /var/lib/zope
* Wed May 10 2000 ro@suse.de
- run SuSEconfig.kdm even in fastrun mode
* Tue May  9 2000 ro@suse.de
- added user codadmin and group codine
* Fri May  5 2000 bk@suse.de
- changed RC_LANG fallback for english from POSIX to en_US
* Fri May  5 2000 mantel@suse.de
- added alias char-major-195 NVdriver
* Thu Apr 27 2000 ro@suse.de
- changed home-dirs from /tmp to /var/lib/$USERNAME
* Wed Apr 26 2000 ro@suse.de
- tmp-races fix reworked
* Tue Apr 25 2000 ro@suse.de
- fixed possible new location of XF86Config (#2793)
* Tue Apr 25 2000 ro@suse.de
- fixed tmp-races with aaa_base_clean_tmp
* Wed Apr 19 2000 ro@suse.de
- updated fillup to 1.06
* Mon Apr 17 2000 ro@suse.de
- set SETUPDUMMYDEV to no by default (#2448)
* Mon Apr 17 2000 ro@suse.de
- added gdm to comment for DISPLAYMANAGER variable
* Fri Apr 14 2000 ro@suse.de
- removed ppc: show_of_path moved to package yaboot
* Wed Apr 12 2000 ro@suse.de
- for 7.0 and above: rpc-script moved to portmap package
* Wed Apr 12 2000 ro@suse.de
- for 7.0 and above: removed rwhod,inetd,nfsserver start-script
  and related rc-config variables (moved to these packagges resp.)
* Mon Apr 10 2000 ro@suse.de
- cleanup the arch-specifics
* Sun Apr  9 2000 bk@suse.de
- fixed for new archs
- add inittab and rc.config patches on s390
* Thu Apr  6 2000 ro@suse.de
- fixed typo in /etc/shells: /usr/bin/tcsh (not tcs)
* Wed Apr  5 2000 mantel@suse.de
- added alias net-pf-1 -> unix
* Tue Apr  4 2000 werner@suse.de
- route: Add a patch from Andreas Schwab and make it work for all cases.
- Speed up the reverse shell function for bigger /etc/route.conf
* Fri Mar 31 2000 ro@suse.de
- added rc.config-variable SERIAL_CONSOLE and code in SuSEconfig
  to handle this
* Thu Mar 30 2000 uli@suse.de
- /sbin/init.d/boot calls hwclock with "--mtxplus --directisa" on
  MTX+ machines
* Tue Mar 28 2000 olh@suse.de
- add show_of_path.sh to ppc:/usr/sbin, needed for yaboot.conf
* Mon Mar 27 2000 schwab@suse.de
- Add /usr/ia64-suse-linux/lib to ld.so.conf.
* Thu Mar 23 2000 ro@suse.de
- updated comment for USE_KERNEL_NFSD
* Thu Mar 23 2000 ro@suse.de
- etc/logfiles: added firewall and radius logfiles
    cleaned up a bit
* Tue Mar 21 2000 kukuk@suse.de
- Use on all platforms except Intel "halt -p" as default
  command [Bug/2103]
* Fri Mar 17 2000 werner@suse.de
- Fix MANPATH in /etc/csh.cshrc:
  use system default in /etc/manpath.config
* Fri Mar 17 2000 uli@suse.de
- /sbin/init.d/boot: run clock if on Mac, else run hwclock
* Tue Mar 14 2000 werner@suse.de
- Use kernel command line to set poweroff option of halt
- Add /bin/ksh to /etc/shells
* Mon Mar 13 2000 ro@suse.de
- removed *.kss from /etc/permissions.*: no suid/sgid needed anymore
* Fri Mar 10 2000 ro@suse.de
- /sbin/isdnctrl to 4755 in permissions.easy
* Fri Mar 10 2000 ro@suse.de
- moved /opt/kde/bin/apm_proxy from permissions to permissions.secure
* Thu Mar  9 2000 bk@suse.de
- set RC_LC_COLLATE to POSIX per default, this fixes problems
  with bash and unexpected [A-Z] wildcard behaviour.
* Wed Mar  8 2000 bk@suse.de
- disabled setting of host route in ISDN ip-down case(from kkeil)
* Wed Mar  8 2000 werner@suse.de
- Don't run mandb with straycats on.
* Wed Mar  8 2000 ro@suse.de
- fixed specfile
* Wed Mar  8 2000 werner@suse.de
- Remove network devices in reverse order to avoid hangs with aliased
  devices.
* Wed Mar  8 2000 ro@suse.de
- moved usr{add,del}.local to user{add,del}.local
* Wed Mar  8 2000 ro@suse.de
- /sbin/isdnctrl: added to permissions.easy as 2755
    and to permissions.secure as  750
* Tue Mar  7 2000 kkeil@suse.de
- set isdn entry in modules.conf to off
* Mon Mar  6 2000 bk@suse.de
- small path correction in alsa driver documentation comment.
* Mon Mar  6 2000 bk@suse.de
- added alias char-major-144 pppox for PPP over Ethernet (PPP over X)
* Sun Mar  5 2000 ro@suse.de
- added alias net-pf-10 ipv6
* Sun Mar  5 2000 ro@suse.de
- fix for taking old modules.conf settings even if file
  was called conf.modules before
* Sun Mar  5 2000 snwint@suse.de
- new mk_initrd: fixed modprobe parsing bug
* Sat Mar  4 2000 ro@suse.de
- fixed buglet when calling SuSEconfig from inst-sys
* Fri Mar  3 2000 werner@suse.de
- Fix bootsetup (/usr/share/info/ and fix of first login message)
* Fri Mar  3 2000 werner@suse.de
- Don't set dummy device for dhcp configured interface
* Fri Mar  3 2000 bk@suse.de
- Disabled removing resolv.conf in ISDN case if it did not exist before
  auto DNS, for better DNS function.
* Fri Mar  3 2000 ro@suse.de
- added alias fb0 to off in modules.conf
* Thu Mar  2 2000 ro@suse.de
- /opt/kde/bin/kvt from 4755 to 2755 [#1954]
- fixed typo in bootsetup.conf [#2071]
* Thu Mar  2 2000 ro@suse.de
- use temporary PATH when checking DEFAULT_WM [#1777,#1778]
* Thu Mar  2 2000 ro@suse.de
- added NETCONFIG_PCMCIA to rc.config template
* Thu Mar  2 2000 ro@suse.de
- added /var/log/fetchmail to etc/logfiles [#2070]
- specfile fixes for sparc
- restart service before zipping the logfile if needed [#2006]
- /usr/bin/emacs removed from permissions.paranoid
- deleted/changed some old comments from permissions.paranoid [#1415]
- moved unix_chkpwd and pwdb_chkpwd from permissions to permissions.secure
* Thu Mar  2 2000 ro@suse.de
- added usr/share/man/allman to MANPATH in etc/profile
* Wed Mar  1 2000 bk@suse.de
- ip-up: added Support for dynamic DNS assignment by ipppd option ms-get-dns
* Wed Mar  1 2000 ro@suse.de
- added entry for char-major-29 (off / fb)
* Tue Feb 29 2000 mantel@suse.de
- added alias for tap[0-16]
* Mon Feb 28 2000 ro@suse.de
- updated /root/.exrc
* Mon Feb 28 2000 ro@suse.de
- updated mkinfodir again
* Sat Feb 26 2000 snwint@suse.de
- added new mk_initrd
* Fri Feb 25 2000 ro@suse.de
- added char-major-67 coda and binfmt-0008 binftm_aout
* Fri Feb 25 2000 sndirsch@suse.de
- added entry for agpgarti810 kernel module in /etc/modules.conf
* Thu Feb 24 2000 ro@suse.de
-mkinfodir: update from werner (discard errors)
* Thu Feb 24 2000 kukuk@suse.de
- nsswitch.conf: Add comment about "dns6"
- sbin/init.d/nscd: Add "sleep 1" for "restart" [Bug 1966]
- move rc.config variable START_ISAPNP into isapnp package
- add rc.config.sparc.aaa_base
- add support for /proc/sys/kernel/stop-a to sbin/init.d/boot
* Wed Feb 23 2000 bk@suse.de
- add alias char-major-108 ppp_async to make ppp work with future 2.4 kernel
* Wed Feb 23 2000 ro@suse.de
- Check: don't gzip ttf-fonts
* Tue Feb 22 2000 ro@suse.de
- added ingres user (id 63, group sys, home /opt/tngfw/ingres, /bin/bash)
  to passwd and shadow-template
* Tue Feb 22 2000 ro@suse.de
- added unix_chkpwd and pwdb_chkpwd as sgid shadow to permissions.easy
  and as 755 to permissions
* Mon Feb 21 2000 garloff@suse.de
- Fixed pgp/metamail entry and commented it out (#1960)
* Mon Feb 21 2000 ro@suse.de
- changed skyrix-home
* Mon Feb 21 2000 ro@suse.de
- serial (char-major-[45]) to off for sparc
* Mon Feb 21 2000 ro@suse.de
- re-use important fields of etc/modules.conf
* Mon Feb 21 2000 ro@suse.de
- renamed cron.daily scripts to have prefix aaa_base_
- aaa_base_clean_crons: if RUN_UPDATEDB!=yes
    then work without locate (#1655)
* Sun Feb 20 2000 bk@suse.de
- removed dir /etc from cat to resolv.conf(bug #1934)
- removed obsolete and inactive code for restarting nscd(bug #1453)
- updated ALSA Example in modules.conf
* Fri Feb 18 2000 mantel@suse.de
- Added vtx module
* Fri Feb 18 2000 ro@suse.de
- added gdm|GDM to the list of possible display managers
* Thu Feb 17 2000 mantel@suse.de
- added alias char-major-10-175   agpgart
  - added alias char-major-89       i2c-dev
* Wed Feb 16 2000 ro@suse.de
- added rc-config Variable ENABLE_SYSRQ
* Tue Feb 15 2000 ro@suse.de
- split cron.daily in pieces:
  backup_rpmdb, clean_catman, clean_core, clean_instlog,
  clean_tmp, do_mandb, rotate_logs, updatedb
  and keep aaa_base for the leftovers and sourcing of cron.daily.local
* Tue Feb 15 2000 ro@suse.de
- sometimes it's better to close the editor first...
* Tue Feb 15 2000 ro@suse.de
- umount /dev/pts in halt (#1935)
- test mdstop not mdadd in halt (#1764)
* Tue Feb 15 2000 ro@suse.de
- fix typo in /sbin/init.d/boot (#1951)
* Mon Feb 14 2000 garloff@suse.de
- Added vgetty and pacct to the list of logfiles
* Fri Feb  4 2000 ro@suse.de
- added /bin/true and /usr/bin/rbash to /etc/shells
* Wed Feb  2 2000 ro@suse.de
- typo-fix in /sbin/init.d/route
* Sun Jan 30 2000 ro@suse.de
- added update for route and route.conf.5 supporting rejected routes
* Thu Jan 27 2000 ro@suse.de
- updated zshrc
- updated /sbin/init.d/route for routes with same address but
  different genmask
* Wed Jan 26 2000 ro@suse.de
- updated profile and zshrc for new zsh version
* Thu Jan 20 2000 ro@suse.de
- usr/X386/lib removed from ld.so.conf
* Thu Jan 20 2000 ro@suse.de
- finally fixed YP typo in /sbin/init.d/boot
* Tue Jan 18 2000 ro@suse.de
- fixed INFOPATH in etc/profile:
    is now: INFODIR=/usr/local/info:/usr/share/info:/usr/info
* Tue Jan 18 2000 ro@suse.de
- info and man to /usr/share for build-dist >= 6.3
- fix SuSEconfig and mkinfodir for usr/share/info
- fix buglet in sbin/init.d/route
* Mon Jan 17 2000 kukuk@suse.de
- Remove "db" entries from etc/nsswitch.conf
- Add new rules for pam/cracklib to SuSEconfig
- /sbin/init.d/boot: Use new options for hwclock [Bug 1573]
* Mon Jan 17 2000 ro@suse.de
- added patch so ldconfig will only be started on boot when needed
* Fri Jan 14 2000 ro@suse.de
- ld.so.conf: only add arch-specific dirs for each arhitecture
- Check: compress /usr/share/info
- powerfail: added ""
- uucp: user home changed to /etc/uucp
- gdm: finally added to etc/shadow
- use "" around filenames when searching for old files in tmp
* Mon Jan  3 2000 ro@suse.de
- added "df -k ." after output of newly created logfile-backups
* Mon Jan  3 2000 ro@suse.de
- changed cron.daily to use four-digit year for old logfiles
  and rpm-db backups
* Mon Dec 20 1999 olh@suse.de
- set char-major-[45] to off on ppc to prevent possible crashes
* Tue Dec 14 1999 ro@suse.de
- fixed "login as root" message for screens > 80 columns
* Mon Dec 13 1999 mantel@suse.de
- added aliases for sl0 and sl1
* Mon Dec  6 1999 ro@suse.de
- moved uucp-home to /var/spool/uucp (#1486)
* Mon Dec  6 1999 ro@suse.de
- etc/logfiles: removed doubles for squid-logfiles
- cron.daily/aaa_base: back to old behaviour:
    copy the logfile and then zero the working one
* Thu Dec  2 1999 ro@suse.de
- fixed typo in nscd - script (min kernel 2.2)
- added rcnscd link
* Tue Nov 30 1999 ro@suse.de
- fixed csh.cshrd (cdwcmd)
* Fri Nov 26 1999 mantel@suse.de
- set alias char-major-15 off to prevent trying to load joystick module
* Wed Nov 24 1999 ro@suse.de
- default BEAUTIFY_ETC_HOSTS to no (#1125)
- Check: don't compress URW (#1127)
    exit if non-root (#1130)
- added entries from kg to mailcap (#1129)
- added konsole_grantpty,kcheckpass,pt_chown,gnome-pty-helper to
  etc/permissions
- etc/logfiles: archive only news.all (no other news logfile)
- usr/bin/filesize: quote $1 (#1337)
- fixed PATH typo in etc/profile (#1378)
* Thu Nov 11 1999 ro@suse.de
- cyrus user now had id 96
* Wed Nov 10 1999 ro@suse.de
- fixed bug in cron.daily/aaa_base
* Tue Nov  9 1999 ro@suse.de
- added floppy-devices with 666 to permissions.easy and .secure
* Mon Nov  8 1999 ro@suse.de
- updated ip-up: changed commented calls for ipfwadm to ipfwadm-wrapper
* Mon Nov  8 1999 ro@suse.de
- updated comment for NETCONFIG
* Mon Nov  8 1999 ro@suse.de
- start bdflush for kernels up to 2.2.10
* Sun Nov  7 1999 ro@suse.de
- fixed: empty lines with done (from not starting kerneld/bdflush)
* Sun Nov  7 1999 ro@suse.de
- etc/ppp/ip-up: use ip-{up,down}.local if present/executable
* Sat Nov  6 1999 ro@suse.de
- updated mkinfodir
* Fri Nov  5 1999 ro@suse.de
- halt: no vg-call if /etc/lvmtab.d doesn't exist
* Thu Nov  4 1999 ro@suse.de
- updated initrd
* Wed Nov  3 1999 ro@suse.de
- fixed sequence in nfsserver
* Wed Nov  3 1999 ro@suse.de
- added char-major aliases for (43,49,56,57,73) as off
- only do vgscan if /etc/lvmtab.d exists
* Tue Nov  2 1999 ro@suse.de
- fixed problem/typo in rc-script
* Tue Nov  2 1999 ro@suse.de
- changed comment for START_LOOPBACK
- added alias char-major-109 lvm
- check if rpc.mountd exists (before starting or killing it)
- check if rpc.ugidd exists (before starting or killing it)
* Mon Nov  1 1999 ro@suse.de
- moved oracle-home to opt/oracle
* Mon Nov  1 1999 ro@suse.de
- fixed typo in /etc/profile (bug#938)
- fixed typo in /sbin/init.d/boot
* Sun Oct 31 1999 garloff@suse.de
- usb-serial 240 and (commented out) usbcore (180) modules aliases
* Sun Oct 31 1999 garloff@suse.de
- Added acm (USB modem) module alias
* Fri Oct 29 1999 ro@suse.de
- added group logmastr
- fixed bug in cron.daily
* Thu Oct 28 1999 ro@suse.de
- updated mk_initrd
* Wed Oct 27 1999 ro@suse.de
- added xemacs info path to mkinfodir
- added patches for boot/halt enabling LVM functionality
* Wed Oct 27 1999 ro@suse.de
- start lockd in nfs and nfsserver
- etc permissions: removed /usr/sbin/sendmail, /var/spool/mqueue
    and /etc/sendmail.cf
- etc permissions.paranoid: removed /usr/sbin/sendmail,
    /etc/sendmail.cf
  (all these are now in /etc/permissions.d/sendmail)
- added user dpbox (61,/var/spool/dpbox,/bin/false) and group localham
- added notify for old-firewall package
* Tue Oct 26 1999 ro@suse.de
- updated mk_initrd
- don't start rpc.ugidd by default
* Mon Oct 25 1999 ro@suse.de
- fixed typo in cron.daily/aaa_base
* Mon Oct 25 1999 ro@suse.de
- added -C for fsck
* Mon Oct 25 1999 ro@suse.de
- added modules.conf and added link conf.modules
* Sun Oct 24 1999 kettner@suse.de
- Added hook for YaST2 into /sbin/init.d/boot
- Fixed ownerships of aaa_base.tar.gz
* Sun Oct 24 1999 kettner@suse.de
- Added YaST2 start to boot script
* Sun Oct 24 1999 ro@suse.de
-sbin/init.d/{boot,single}: no need to run "update" for 2.2 kernels
* Sat Oct 23 1999 ro@suse.de
-permissions.easy: chage from 4755 to 2755 (sgid shadow)
* Sat Oct 23 1999 ro@suse.de
-nfsserver: fixed startscript (kukuk@suse.de)
* Sat Oct 23 1999 ro@suse.de
- etc/nsswitch.conf: completed comment
- sbin/mk_initrd: added script
* Fri Oct 22 1999 ro@suse.de
- SuSEconfig: remember rlogind when configuring for CRACKLIB
* Tue Oct 19 1999 ro@suse.de
- etc/profile: unset DIR (BUG#410)
- etc/permissions.d: respect files for packages (BUG#394)
- etc/logfiles: added squid logs (BUG#676)
* Mon Oct 18 1999 ro@suse.de
- updates for /sbin/init.d/{boot,boot.setup,rc} from werner
- fix aliases for recode (BUG#299)
- move /usr/openwin/bin last in PATH (BUG#313)
- reload apache if config-files have been changed by cron.daily (BUG#413)
    (added field in etc/logfiles containing the service name)
- created mysql user (id 60, /var/mysql, /bin/false) (BUG#465)
- added comment to nsswitch.conf (BUG#401)
- /sbin/init.d/boot : stop the mdarray before ckraid (BUG#633)
* Thu Oct 14 1999 kukuk@suse.de
- nsswitch.conf.5.gz: Update with a newer version
- /var/adm/fillup-templates/rc.config.aaa_base: Add PASSWD_USE_CRACKLIB
- /sbin/SuSEconfig: Change /etc/pam.d/{login|passwd} to honor
    PASSWD_USE_CRACKLIB
* Wed Oct 13 1999 garloff@suse.de
- conf.modules: IrDA devices, sample ALSA config and netlink_dev
- /etc/profile: source /etc/profile.dos moved to /etc/skel/.bashrc
- /etc/logfiles: (from BK) added squid log files to /etc/logfiles
    [bugzilla ID 546]
* Tue Oct 12 1999 garloff@suse.de
- added /usr/local/sbin to root PATH. Added comment about
  /etc/profile being overwritten, when updating the distro.
  Added aliases beep and unmount and some help for D*S command
  users.
- halt script now waits 2 seconds before actually shutting down
  (might be a poweroff!). beep on halt.
* Thu Sep 16 1999 ro@suse.de
- added "Requires vi_clone"
* Mon Sep 13 1999 bs@suse.de
- ran old prepare_spec on spec file to switch to new prepare_spec.
* Wed Sep  8 1999 bs@suse.de
- added user oracle and group oinstall, dba
* Tue Aug 24 1999 uli@suse.de
- added -fsigned-char to fillup Makefile (PPC)
* Sun Aug 22 1999 bs@suse.de
- changed old to use full year
* Mon Aug 16 1999 bs@suse.de
- /etc/permissions:  moved chkey from permissions to permissions.easy
- sbin/SuSEconfig: do not restart nscd anymore (caching is disabled now)
- etc/cron.daily/aaa_base:  use mv instead of cp for old log files.
- added group fix and users fixlohn, fixadm and fib.
* Wed Aug  4 1999 bs@suse.de
- Check:
  o changed to exclude man pages starting with ".".
  o use MANPATH for man directories.
- added groups sys (gid 3) and audio (gid 17)
- /sbin/init.d/nscd:  don't start nscd on 2.0 kernel.
* Thu Jul 29 1999 bs@suse.de
- fixed /etc/ppp/ip-up to let /etc/resolv.conf be created with 644.
- changed printed message in /sbin/init.d/nscd
* Thu Jul 22 1999 bs@suse.de
- dont take nsswitch.5.gz from ldpman but include it in src.rpm
* Thu Jul 22 1999 bk@suse.de
- fix for nscd restart in etc/ppp/ip-up
* Wed Jul 21 1999 bs@suse.de
- typo fix in SuSEconfig
* Wed Jul 21 1999 bs@suse.de
- SuSEconfig:  redirect output of nscd to /dev/null if not standard
  stdout
* Tue Jul 20 1999 bs@suse.de
- removed sbin/init.d/ipfwadm
- make sure, that home dir of uucp is reset
- new version of etc/runlevel.fallback
* Tue Jul 20 1999 bs@suse.de
- moved mount/umount from /etc/permissions to /etc/permissions.easy
* Mon Jul 19 1999 bs@suse.de
- SuSEconfig: added parameter --norestarts
* Mon Jul 19 1999 bs@suse.de
- sbin/init.d/routed:  fixed restart case
- etc/profile: fixed prompt for zsh
* Mon Jul 19 1999 bs@suse.de
- sbin/init.d/network:  fixes for dhcp.
- sbin/init.d/boot: mount /dev/pts if not mounted via /etc/fstab.
- sbin/SuSEconfig:  restart nscd if resolv.conf changes.
- var/adm/fillup-templates/rc.config.aaa_base: spell fixes.
* Mon Jul 19 1999 bs@suse.de
- direct "login as root message" to /etc/issue-SuSE-first-run and
  print it vi /sbin/init.d/rc.
* Sun Jul 18 1999 bk@suse.de
- Added alias rehash='hash -r' from garloff@suse.de to /etc/profile
- Added function remount(/bin/mount -o remount,$*) from garloff@suse.de
  to /etc/profile Example: remount ro /
* Sat Jul 17 1999 bk@suse.de
- added /sbin/init.d/nscd restart to /etc/ppp/ip-up
- moved /etc/ppp/ip-up von config-noreplace to normal config.
- fixed aaa_base-rc.config-fillup LANG comments
* Fri Jul 16 1999 ro@suse.de
- updated rc-scripts for network and route
* Thu Jul 15 1999 bs@suse.de
- /lib/YaST/bootsetup:  added "login as root" message in french
* Thu Jul 15 1999 bs@suse.de
- /lib/YaST/bootsetup:  added "login as root" message (in color!)
- /sbin/init.d/boot.setup:  fixed problems with serial console
  (from kettner@suse.de)
- etc/profile:  changed PS1 for zsh.
- SuSEconfig: skipped USE_NIS_FOR_RESOLVING.
- /etc/cron.daily/aaa_base: set always ownership and rights of logfiles
- etc/permissions:
  o removed logfiles handled by /etc/logfiles
  o changed entry for yardstat
- etc/logfiles: added /var/log/xdm.errors
- added user nps, skyrix, dbmaker - group dbmaker
* Mon Jul 12 1999 bs@suse.de
- SuSEconfig:  print nickname to /etc/hosts only once
- /etc/inputrc:  changed behaviour of Home and End
- /sbin/init.d/halt:  use -p if /proc/apm exists.
- /etc/permission:  added /var/lib/gdm
- start random initilization earlier.
- /etc/cron.daily/aaa_base:
    o set ownership and rights of backuped log file.
    o use $TMP_DIR/. instead of $TMP_DIR for searching bogus tmp files.
- minor typo fixes in sbin/init.d/kerneld and sbin/init.d/boot.
- etc/profile:  added /opt/bin to PATH
* Thu Jul  8 1999 ro@suse.de
- removed /usr/bin/quota from permission files: no suid root needed
* Tue Jul  6 1999 ro@suse.de
- added ham entries for conf.modules
* Tue Jun 29 1999 ro@suse.de
- removed outdated comments about locales in profile
* Tue Jun 29 1999 ro@suse.de
- updated nscd start script
* Mon Jun 28 1999 ro@suse.de
- updated csh.cshrc
* Mon Jun 28 1999 ro@suse.de
- /sbin/init.d/boot: set empty domainname if unset in /etc/rc.config
- /sbin/SuSEconfig: modify /etc/pam.d instead of login.defs
  if root-login-remote is true
* Fri Jun 25 1999 bk@suse.de
- fixed etc/ppp/ip-up
* Thu Jun 24 1999 ro@suse.de
- added etc/ppp/ip-{up,down} (conf-noreplace)
* Thu Jun 24 1999 ro@suse.de
- moved nfsserver start: S13 -> S17 , K27 -> K23 (after ypclient)
- moved pcnfsd start: S13 -> S17 , K27 -> K23
* Wed Jun 23 1999 ro@suse.de
- addded entries for netrom/rose to conf.modules
- reactivated ipx/netatalk in conf.modules
* Tue Jun 22 1999 ro@suse.de
- permissions: rxvt to root.tty and mode 2755 in permissions.easy
* Mon Jun 21 1999 ro@suse.de
- permissions: xterm to root.tty and mode 2755
* Fri Jun  4 1999 ro@suse.de
- /sbin/init.d/nscd: exit silently if /usr/sbin/nscd in not executable
* Tue Jun  1 1999 ro@suse.de
- added user cyrus (home=/usr/cyrus, group=mail)
* Fri May 21 1999 ro@suse.de
- added user & group "postfix"
* Sun May  2 1999 ro@suse.de
- added block-major 48 and 72 as off to conf.modules
* Fri Apr 30 1999 ro@suse.de
- added /opt/kde/bin/apm_proxy (SUID only in permissions.easy)
* Fri Apr 30 1999 ro@suse.de
- updated bootp script to work with 2.2
* Tue Apr 27 1999 ro@suse.de
- bugfix in /sbin/init.d/nscd (packaed only for glibc-2.1)
* Mon Apr 19 1999 ro@suse.de
- added mouse comment to conf.modules
* Mon Apr 19 1999 ro@suse.de
- added gdm user: group shadow, home /var/lib/gdm
* Fri Apr 16 1999 ro@suse.de
- SuSEconfig: fixed for italian
* Fri Apr 16 1999 ro@suse.de
- bugfix in xdm set LC_ variables only if unset
* Fri Apr 16 1999 ro@suse.de
- SuSEconfig: some special cases for LANGUAGE (not yet in locale.alias)
- xdm: read and export LC_*-variables
* Fri Apr 16 1999 ro@suse.de
- SuSEconfig: set RC_LANG according to LANGUAGE (from YaST)
* Thu Apr 15 1999 ro@suse.de
- fixed usage-msg in rcnetwork (added "|probe")
* Wed Apr 14 1999 ro@suse.de
- fixed rcnetwork skript: restart
* Wed Apr 14 1999 ro@suse.de
- added ppp-submodules to conf.modules
- added binfmt-0064 as binfmt_aout
* Wed Apr 14 1999 ro@suse.de
- added RC_LC_* Variables to fillup_templates/rc.config.aaa_base
- modified SuSEconfig to set the LC_* Variables according to settings
  in /etc/rc.config
- permissions: /usr/bin/chkey: 4755, but 755 for secure/paranoid
* Sun Apr 11 1999 bs@suse.de
- etc/profile,SuSEconfig: changed stuff for internationalization.
* Thu Apr  8 1999 ro@suse.de
- fixed problem in /sbin/init.d/boot: gpm is in usr/sbin
- pkgmake: don't remove "no newline" lines
* Tue Apr  6 1999 bs@suse.de
- removed route.orig
* Tue Apr  6 1999 bs@suse.de
- /sbin/init.d/boot: recreate modules.dep, if /etc/conf.modules is newer.
* Tue Apr  6 1999 bs@suse.de
- /sbin/init.d/dummy: toggled cases for dummy vs dummy0
* Tue Apr  6 1999 bs@suse.de
- sbin/init.d/halt:  changed "halted" message
- /etc/permissions:  set /etc/aliases to 644
* Tue Apr  6 1999 bs@suse.de
- don't use grep in /sbin/init.d/dummy
* Tue Apr  6 1999 bs@suse.de
- /etc/profile:  use "ulimit -Sc 0"
* Tue Apr  6 1999 bs@suse.de
- added IP_TCP_SYNCOOKIES to rc.config
* Tue Apr  6 1999 bs@suse.de
- rc.config:  fixed description for NFS_SERVER_UGID
- sbin/init.d/route:  applied Bernds patch for avoiding double routes
- sbin/init./boot: added IP_TCP_SYNCOOKIES setting
* Thu Apr  1 1999 uli@suse.de
- /etc/permissions: changed pppd to 6754
* Wed Mar 31 1999 uli@suse.de
- /etc/permissions.easy: changed perms for v4l-conf, xtvscreen* from
  4750 to 4755
* Tue Mar 30 1999 bs@suse.de
- new conf.modules from mantel@suse.de
- /etc/cron.daily/aaa_base:  removed tetex stuff (is in
  /etc/cron.daily/tetex)
- /etc/permissions:  - set bttvgrab etc to 4750
  - use xawtv instead of xawt
  - set kvt to 4755 in all configs
- /sbin/init.d/boot:  only run depmod if modules.dep is not the newest
    file.
* Fri Mar 26 1999 ro@suse.de
- fixed typo in sbin/init.d/rc
* Thu Mar 18 1999 ro@suse.de
- start portmap in bootsetup before yast
- sbin/init.d/rpc: check if portmap already running and restart
* Thu Mar 18 1999 ro@suse.de
- added user fnet with group uucp for fidopoint software
* Mon Mar 15 1999 ro@suse.de
- updated /sbin/init.d/xdm for gdm
- updated csh.cshrc
* Wed Mar 10 1999 ro@suse.de
- fixed typo in /etc/profile : LESS=-M -S -I  -> LESS="-M -S -I" :(
* Wed Mar 10 1999 ro@suse.de
- gnuplot changed to 755 in permissions and to 4755 in permissions.eazy
* Wed Mar 10 1999 ro@suse.de
- fixed GID's for IBM-DB2 groups
* Tue Mar  9 1999 ro@suse.de
- updated script /sbin/init.d/dummy (from werner):
  - use netmask 255.255.255.255 for ifconfig
  - use metric 1 for route to dummy device
* Tue Mar  9 1999 ro@suse.de
- added startscript for nscd (only packed for glibc-2.1 distros)
  and rc.config variable START_NSCD
- added users/groups for IBM-DB2: users: db2fenc1, db2inst1, db2as
    groups:db2fadm1, db2iadm1, db2asgrp
- /bin/mount 755 in permissions.{secure,paranoid}
- set LESS to "-M -S -I" in etc/profile
- added "TERM screen" to etc/DIR_COLORS
- changed entry in etc/shells from /bin/passwd to /usr/bin/passwd
* Tue Feb 16 1999 bs@suse.de
- SuSEconfig: fixed problem with CONSOLE_MAGIC
* Thu Feb 11 1999 uli@suse.de
- /sbin/init.d/boot: fixed bug that prevented the execution of ckraid
* Wed Jan 20 1999 bs@suse.de
- added CONSOLE_MAGIC to /etc/SuSEconfig/profile,csh.login
* Tue Jan 19 1999 bs@suse.de
- use "echo -en" to write CONSOLE_MAGIC on ttys.
* Tue Jan 19 1999 bs@suse.de
- /etc/permissions.easy: set kde screesaver to sgid shadow.
* Mon Jan 18 1999 bs@suse.de
- made CONSOLE_MAGIC more flexible
* Mon Jan 18 1999 bs@suse.de
- fonts:  - removed "YAST_ASK" from CONSOLE_FONT
  - use "setfont -u" instead of "loadunimap"
  - do no font things, if CONSOLE_FONT is empty
* Sun Jan 17 1999 bs@suse.de
- added CONSOLE_FONT, CONSOLE_SCREENMAP, CONSOLE_UNICODEMAP and CONSOLE_MAGIC
  to /etc/rc.config
- %%post: rc.config: change FONT/TRANSLATION to CONSOLE_FONT/CONSOLE_UNICODEMAP
- sbin/init.d/single,boot.setup:  use new variables for setting font.
* Sat Jan 16 1999 bs@suse.de
- etc/permission: disabled suid of suidperl and xcpustate
* Fri Jan 15 1999 bs@suse.de
- etc/nsswitch.conf: use "compat" for passwd and group.
- added /usr/bin/rpmlocate
- conf.modules: fixed typo (af_package -> af_packet)
- etc/permissions:  set yardsrv to 6755
    fixed mqueue path
- sbin/SuSEconfig: inittab: modify only lines beginning wityh "^ca:".
- etc/DIR_COLORS: added .bz2
* Thu Jan 14 1999 bs@suse.de
- etc/permissions:  added /usr/sbin/suexec
- /sbin/init.d/inetd: fixed typo "resart"
- /sbin/init.d/cron: fixed typo "retart"
- /sbin/init.d/boot: added section for IP_FORWARDING
- /etc/profile:  added PROMPT_COMMAND (dashed out)
- /sbin/init.d/halt:  fixed problem with non succeeding umount.
- /etc/logfiles: added /var/log/news/news
- /etc/cron.daily: use "-f" instead of "-e" for check_log_file
* Fri Dec 18 1998 bs@suse.de
- minor fixes in /sbin/init.d/route
* Thu Dec 17 1998 bs@suse.de
- changed mail text for xwrapper
* Thu Dec 17 1998 bs@suse.de
- fixed WINDOWMANAGER in /etc/SuSEconfig/csh.cshrc
- fiex /etc/csh.cshrc (problem, if /etc/SuSEconfig is empty)
* Mon Dec 14 1998 bs@suse.de
- fixed ~ for news
* Mon Dec 14 1998 bs@suse.de
- etc/profile.d/profile,csh.cshrc:  set WINDOWMANAGER only if empty
* Mon Dec 14 1998 bs@suse.de
- SuSEconfig: - start SuSEconfig.sendmail and SuSEconfig.ypclient even
    in fast run mode. (Again!?)
* Mon Dec 14 1998 bs@suse.de
- etc/permissions:  added screen-3.7.6
* Mon Dec 14 1998 bs@suse.de
- moved /root/bin/cron.daily to /etc/cron.daily/aaa_base
* Mon Dec 14 1998 bs@suse.de
- added man page for resolv+
* Sun Dec 13 1998 bs@suse.de
- fixed alias proble in /sbin/init.d/network
* Sun Dec 13 1998 bs@suse.de
- removed /sbin/init.d/boot.d from /etc/permissions
* Sun Dec 13 1998 bs@suse.de
- delete usr/i486-linux-libc6/lib/libqimgio.so if it is a symlink
- sbin/init.d/network:  do not delete network aliases in stop.
- updated runlevel.fallback
- removed man pages for fstab and nfs (were forgotten in util).
- fixed /etc/SuSE-release
* Sun Dec 13 1998 bs@suse.de
- added old man pages fstab and nfs (from ldpman-1.17)
* Sun Dec 13 1998 bs@suse.de
- added support forms again.
* Sat Dec 12 1998 bs@suse.de
- disabled sorting of passwd by default
- make sure, that root is on the first line, when sorting passwd.
- SuSEconfig:  start newaliases for smail
* Sat Dec 12 1998 bs@suse.de
- cleaned output of /sbin/init.d/rc
- installed a .xinitrc with twm as default for root (noreplace)
* Sat Dec 12 1998 bs@suse.de
- sbin/init.d/boot:  fixed "failed" message, if fsck had to do something.
* Sat Dec 12 1998 bs@suse.de
- SuSEconfig: - start SuSEconfig.sendmail and SuSEconfig.ypclient even
    in fast run mode.
  - create resolve.conf only if "$DHCLIENT" != yes
* Sat Dec 12 1998 bs@suse.de
- fixed permissions
- removed gen-dir-node
* Fri Dec 11 1998 bs@suse.de
- conf.modules:  added net-pf-17
    removed double entry for char-major-14
- %%pre:  use fillup for group and shadow.
- fixed strings with "S.u.S.E."
- moved ugidd from nfsserver to rpc script
- SuSEconfig:  fixed problem, if initdefault runlevel disapeared.
- sbin/init.d/boot: create always a new /etc/psdevtab
- cron.daily:  delete old tmp dirs too (if MAX_DAYS_IN_TMP is set)
- DIRCOLORS: fixed comment
- switched some cfg files to noreplace
- etc/profile:  deleted MM_RUNASROOT
- another try to set prompt.
* Thu Dec 10 1998 bs@suse.de
- SuSEconfig: fixed problem with DEFAULT_WM
- replaced startkde with kde
- added man page for nsswitch.conf.
* Tue Dec  8 1998 bs@suse.de
- set DEFAULT_WM=kde
- etc/logfiles:  added /var/log/rinetd.log, rsyncd.log
- etc/permission:  added /var/log/xdm.errors, /var/log/lastlog
    deleted double entry for bttvgrab
- added user virtuoso
- added named to shadow (again?)
- etc/profile:  skipped PROMPT_COMMAND
    skipped INPUTRC - we have a patched readline
- lib/YaST/SuSEconfig.functions fixed echo_warning
- sbin/SuSEconfig:  sort /etc/passwd and /etc/group by uid.
* Sun Dec  6 1998 bs@suse.de
- moved support forms to package support.
- don't include directories (aaa_dir is for this)
- moved /etc/skel to aaa_skel.
* Sun Dec  6 1998 bs@suse.de
- fixed permissions of /etc.
* Sat Dec  5 1998 bs@suse.de
- get rid of old unchanged local files.
* Sat Dec  5 1998 bs@suse.de
- SuSEconfig:  check /usr/X11R6/lib/X11/fonts/local for mkfontdir
- sbin/init.d/*:  make better output.
- etc/rc.config:  new escape sequences rc_done_up, rc_failed_up and
    rc_skipped.  Activated colors.
* Thu Dec  3 1998 bs@suse.de
- /etc/ld.so.conf /usr/i486-linux-libc5/lib=libc5
* Thu Dec  3 1998 bs@suse.de
- added /etc/SuSE-release
- sbin/init.d/boot:  use reboot -f in "emergency mode"
* Thu Dec  3 1998 ro@suse.de
- added sp and sp_libs to neededforbuild
* Wed Dec  2 1998 bs@suse.de
- minor fix in serial.
* Wed Dec  2 1998 bs@suse.de
- use sgmtools instead of linuxdoc for build
* Mon Nov 30 1998 bs@suse.de
- fixed /sbin/init.d/kerneld
- added /usr/sbin/rc* links.
* Fri Nov 27 1998 bs@suse.de
- fixed PROMPT_COMMAND
* Thu Nov 26 1998 bs@suse.de
- /sbin/init.d/*  new flags added (reload, restart, etc.)
- /sbin/init.d/boot.setup,single:  added TRANSLATION
- /sbin/bootp:  security fixes
    does not need grep and sed anymore.
- /sbin/init.d/route  accepts a special net device for parameter.
- new: sbin/init.d/ipfwadm - a startup script that works with ipfwadm and
    ipchains
- usr/bin/old:  fixed problem if param has a trailing /
- etc/logiles:  added /var/log/postgresql.log
- sbin/init.d/makerunlvl: deleted
- added groups xok, trusted and modem (used in /etc/permissions.paranoid)
- SuSEconfig: fixed buglet with DEFAULT_WM.
* Tue Nov 24 1998 bs@suse.de
- removed /usr/lib/pgsql/lib from ld.so.conf
* Fri Nov 20 1998 bs@suse.de
- rpc: portmap has been moved to /sbin
* Thu Nov 19 1998 bs@suse.de
- cron.daily:  fixed problems with wrong settings of MAX_DAYS_FOR_LOG_FILES
  and MAX_DAYS_IN_TMP.
* Wed Nov 18 1998 bs@suse.de
- fixed deletion of utmp in /sbin/init.d/boot
* Tue Nov 17 1998 bs@suse.de
- use DEFAULT_WM for WINDOWMANAGER.
* Tue Nov 17 1998 bs@suse.de
- use zic in SuSEconfig and /sbin/init.d/boot to setup timezone.
* Tue Nov 17 1998 bs@suse.de
- bootsetup.conf:  search for future files in kernel sources and touch them
- sbin/init.d/boot:  cleanup /var/run
    start /sbin/init.d/boot.d/* a little bit later
- skipped use of /etc/default.keytab - load keytable directly via
  /sbin/init.d/kbd
- etc/skel/{.xinitrc,.xsession}:  smoothing
- etc/skel/.holiday: removed (confuses non german users)
- etc/zshrc:  is not a link to profile anymore.  but profile is sourced.
- etc/profile: fixes for zsh.
- root/bin/cron.daily:  - don't use locate if locatedb is older than 7 days.
  - use MANPATH as well as manpath
- sbin/init.d/zzreached:  deleted (rc does this job now)
- etc/permissions:  added /etc/shadow-
- etc/ld.so.conf (added /usr/lib/pgsql/lib temporally)
- etc/rc.config:  added localhost to NO_PROXY
- etc/shells.in:  does not exist anymore - use /etc/shells directly.
* Thu Nov 12 1998 bs@suse.de
- etc/inittab:  switched wait to bootwait (for new init)
- sbin/init.d/skeleton:  deleted double line
- etc/csh.login: fixed condition for settc
* Thu Oct 29 1998 ro@suse.de
- fillup: accept empty target file
* Mon Oct 26 1998 ro@suse.de
- fillup: make clean first ; added include errno.h in services.c
* Fri Oct 23 1998 ro@suse.de
- update: fillup-1.05
* Wed Oct  7 1998 ro@suse.de
- fixed "wrong quotes" in rc.config template
* Mon Oct  5 1998 ro@suse.de
- etc/mime.types added missing from apache/mime.types
  etc/profile added 2>/dev/null for unalias ls
  etc/csh.cshrc changed fi to endif
  sbin/SuSEconfig: check is QTDIR is usr/X11R6/lib/qt or usr/lib/qt
  sbin/init.d: rc, skeleton: new versions from werner
  var/adm/fillup/aaa_base.rc.config additions needed for new rc
* Mon Sep 28 1998 ro@suse.de
- added extensions to etc/profile and etc/csh.cshrc:
  source files in etc/profile.d ending in .sh resp. .csh
* Mon Sep 28 1998 ro@suse.de
- new csh.cshrc: fixed ls command
- profile: modifixations for TEXINPUT, LS_OPTIONS, PROMPT_COMMAND
- rctab: new version
- modifications to support 2.1 kernels
  - /sbin/init.d/rc[23].d  S12rpc -> S08rpc, S08nfs -> S09nfs
    K28rpc -> K37rpc, K37nfs -> K36nfs
  - /sbin/init.d/nfsserver added support for knfsd
  - /sbin/init.d/serial    cua* -> ttyS*
- /sbin/bootp added file
- modified /sbin/init.d/boot:    accept/respect value for IP_DYNIP
  added new detection for root on UMSDOS
- modified /sbin/init.d/network: for bootp and dhclient
- modified /sbin/init.d/route:   for dhclient
- modified /sbin/init.d/rpc:     no exit if YP_DOMAINNAME is set
- start cron after xntpd
  - /sbin/init.d/rc[23].d S20cron -> S21cron, K20cron -> K19cron
- /var/adm/fillup-templates/rc.config.aaa_base added
  - $USE_KERNEL_NFSD switch to use alternate nfs-server
  - $USE_KERNEL_NFSD_NUMBER number of servers to launch
- /etc/inittab: added commented lines for l4 and l5
- aaa_base.spec:
    passwd: switched -2 to 65534; added user named uid 44 , home /var/named
    group:  switched -2 to 65534; added group named gid 44 with user named
    give message whether files were unchanged or modified
- skel: removed etc/skel/.seyon/protocols.old
* Mon Sep  7 1998 bs@suse.de
- conf.modules:  enabled sound.
- new versions of etc/csh.*
- etc/skel/.xserverrc.secure:  start Xwrapper instead of X.
- root/bin/cron.daily:  switched sourcing of /etc/rc.config and path
    setting for texhash.
- security fix in /usr/bin/pkgpack
* Fri Aug 21 1998 bs@suse.de
- applied Marcs minor security fix to /lib/YaST/bootsetup
* Wed Aug 12 1998 bs@suse.de
- added user and group informix
* Mon Aug 10 1998 bs@suse.de
- added CINTSYSDIR=/usr/lib/cint to /etc/profile.d/*
* Thu Aug  6 1998 bs@suse.de
- added es, fr & it to MANPATH
* Wed Jul 29 1998 bs@suse.de
- /sbin/init.d/halt:  do last umount with "-n"
* Wed Jul 29 1998 bs@suse.de
- added rxvt and kvt to /etc/permission*
* Wed Jul 29 1998 bs@suse.de
- chmod 600 to etc/*shadow in %%post section.
* Wed Jul 29 1998 bs@suse.de
- etc/skel/.xinitrc:  test for several window mangers, if $WINDOWMANAGER
  does not exist.
- SuSEconfig: start sub scripts with bash instead of sh.
* Mon Jul 27 1998 bs@suse.de
- new conf.modules
- fixed /etc/profile for ksh
- changed (un)mounting of proc in /sbin/init.d/{halt,boot}
- new versions of .xinitrc and .xsession
- added french an italian to lib/YaST/bootsetup
- added 'test -z "$fastboot"' to sbin/init.d/boot
- redesigned sbin/init.d/dummy added - should work with non module
  dummy devies too now.
- root/bin/cron.daily:  added /etc/logfiles
- new version of sbin/init.d/skeleton
- sbin/init.d/boot: start depmod even if /proc/sys/kernel/modprobe
  exists.
- etc/permissions:
  - added /etc/rmtab.
  - removed sgid uucp from cu and minicom - admin should add you to group
    uucp if you want to have access to modem
* Mon Jul 20 1998 bs@suse.de
- Check:  use mktemp
- installpkg, pkgtool, removepkg: deleted (use YaST to install .tar.gz)
- etc/permission*: - added kscd, bttv and kradio
  - updated all start/stop scripts
  - added new X server.
- etc/profile: use kde for WINDOWMANAGER
- rc.config: added /S.u.S.E. to UPDATEDB_PRUNEPATHS
- updatet etc/runlevel.fallback
- cron.daily:  make file command on old core files.
- SuSEconfig: don't bother user with warning (no /etc/XF86Config), when
    DISPLAYMANAGER is set to console.
* Fri Jul 17 1998 bs@suse.de
- new conf.modules
* Thu Jul 16 1998 bs@suse.de
- added group video
* Wed Jul 15 1998 bs@suse.de
- deleted "=libc5" entries from /etc/ld.so.conf (problems with ld)
* Wed Jul 15 1998 bs@suse.de
- fixed version in bootsetup
* Tue Jul 14 1998 bs@suse.de
- skipped /etc/ld.so.conf in SuSEconfig
- added /etc/ld.so.conf as %%config
* Mon Jul 13 1998 bs@suse.de
- new versions of:
  - etc/csh.cshrc
  - sbin/rctab
  - man page for rctab
  - etc/skel/.emacs (for emacs 20)
- lib/YaST/bootsetup.conf:  deleted perl stuff (is done by SuSEconfig.perl now)
- added kde suids to /etc/permission.{easy,secure}
- added etc/nsswitch.conf
- sbin/init.d/boot:  initialize pnp a little bit earlier.
  Variable START_ISAPNP added.
- added /opt/gnome/lib to etc/ld.so.conf.in
- etc/profile added /opt/gnome/bin to path.
- SuSEconfig:  added KDEDIR, GNOMEDIR, XADIDIR, QTDIR, DV_IMMED_HELP,
  MAPLE, RASMOLPATH, DMARSCONF and CRPATH for /etc/SuSEconfig/*
  most of them were in /etc/profile
- cron.daily: unset MANPATH manpath added
* Wed Jul  8 1998 bs@suse.de
- fixed syntax error in /sbin/init.d/boot
- added user firewall
- added groups firewall and public
* Mon Jul  6 1998 bs@suse.de
- /root/bin/cron.daily: - fixed /usr/man/allman/de/whatis
  - added /var/log/ntp, changed /var/log/news
- SuSEconfig: added flag BEAUTIFY_ETC_HOSTS
- /sbin/init.d/boot:  - added quota check
  - "detabed"
  - added call of ckraid if mdadd fails.
- new version of sbin/init.d/xdm added.
- deleted double entry of HTTP_PROXY from /etc/rc.config.
- /etc/permission: deleted sgid uucp from /usr/X11R6/bin/seyon
- added /sbin/init.d/zzreached.
* Mon Jun 15 1998 bs@suse.de
- updated /usr/bin/pkgpack
* Fri Jun 12 1998 bs@suse.de
- added BLENDERDIR to SuSEconfig
* Tue Jun  2 1998 bs@suse.de
- added /usr/i486-linux-libc5/lib to ld.so.conf.in
* Thu May 28 1998 bs@suse.de
- removed suid bits from xosview
* Thu May 28 1998 bs@suse.de
- moved xosview from /etc/permissions to /etc/permissions.*
* Thu May 28 1998 bs@suse.de
- etc/permissions:  added /usr/lib/ircd
* Wed May 27 1998 bs@suse.de
- added user irc for ircd.
* Tue May 26 1998 bs@suse.de
- added /usr/X11R6/lib/Xaw95 to /etc/ld.so.conf.in
- SuSEconfig:  - fixed FROM_HEADER in /etc/SuSEconfig/*
- rc.config: added comment for routed
- added /etc/issue.net
- /sbin/init.d/nfs:  fixed problem with "dashed out" entries in /etc/fstab
- concatinated /etc/skel/.Xdefaults an /etc/skel/.Xresources
- /sbin/init.d/rpc fixed check of START_PORTMAP and NFS_SERVER
- /usr/sbin/Check:  force gzip of files.
* Wed May 13 1998 bs@suse.de
- /etc/permissons*:  removed suid bit for xload
- /lib/YaST/bootsetup: fixed texhash problem
* Tue Apr 21 1998 bs@suse.de
- sbin/init.d/{boot.setup,single}:  switched call of loadunimap and setfont
  again.  Problem will be fixed correctly in kbd package for 6.0...
* Fri Apr 17 1998 bs@suse.de
- fixed home entry for squid in /etc/passwd.
- added creation of /boot in %%pre
- fixed problems in %%pre, if grep does not exist
* Thu Apr 16 1998 bs@suse.de
- SuSEconfig: - added MAXHOME, HTTP_PROXY, FTP_PROXY, GOPHER_PROXY and
    NO_PROXY to /etc/SuSEconfig/*
  - fixed problem, if NETCONFIG isn'y set properly
  - set /etc/lilo.conf to 600
- bootsetup.conf:  added call of texhash
- inittab: added powerfail entry for ARGO UPS
- sbin/init.d/boot: enable dynamic IP patch if IP_DYNIP is set to yes
* Mon Mar 30 1998 bs@suse.de
- set custom-file in /etc/skel/.emacs
- passwd: changed german names to english
- added "-s" to mandb call in SuSEconfig
- added checks for tmp and var/tmp in %%pre
* Thu Mar 26 1998 bs@suse.de
- moved symlinks to directories (/usr/tmp, /usr/spool, ...) to aaa_dir
- added /sbin/init.d/rwhod (rc.config+/etc/permissions+symlinks)
- sbin/init.d/boot:
  - fixed problems with
  - swapping on MD devices
  - mounting of devices, that need a module to be loaded
  - don't start kerneld if /proc/sys/kernel/modprobe exists
- sbin/init.d/kerneld:
  - don't start kerneld if /proc/sys/kernel/modprobe exists
- sbin/init.d/boot.setup & sbin/init.d/single:
  - switched call of loadunimap & setfont
- added notice for ~/.xserverrc to Xwrapper-Mail
- lib/YaST/bootsetup.conf: added creation of /etc/psdevtab
- deleted "exit 0" from *.local scripts, since it causes trouble when
  these scripts are sourced (e.g. cron.daily and cron.daily.local)
- deleted tmp and var/tmp (is in aaa_dir)
* Wed Mar 18 1998 bs@suse.de
- added iBCS to conf.modules...
* Thu Mar 12 1998 bs@suse.de
- use "ixess" instead of "ixware" for ixware user.
* Wed Mar 11 1998 bs@suse.de
- SuSEconfig: don't mail reports if called with "--quick".
- added message for Xwrapper and old XSuse server.
- SuSEconfig.functions:  delete testfile after test
* Tue Mar 10 1998 bs@suse.de
- SuSEconfig:  fixed problem with ro mounted /usr
* Mon Mar  9 1998 bs@suse.de
- pkgmake:  use -ko for rcs
    skip "No newline at end of file" messages
- rc.config:  create header in %%post
    added LANGUAGE, CHECK_INITTAB, DISPLAYMANAGER & CONSOLE_SHUTDOWN
- SuSEconfig:
  - added /etc/inittab stuff
  - added SUSE_DOC_HOST to /etc/SuSEconfig/profile &
    /etc/SuSEconfig/csh.cshrc
- bootsetup.conf: don't run cron.daily after first installation.
- permissions:  sgid disk to most cd-players
- csh.cshrc: fixed TAB expansion for tar command
- create /sbin/init.d/README automatically while building package
* Tue Mar  3 1998 bs@suse.de
- cron.daily:  fixed check_logfile
* Mon Mar  2 1998 bs@suse.de
- set sbin/init.d/* etc/skel/* to %%config
- set executable bit to some *.local
- added sbin/init.d/random (by Theodore Ts'o <tytso@mit.edu>)
* Sun Mar  1 1998 bs@suse.de
- etc/permissions: - deleted suid for XServer (we have Xwrapper now).
  - added entries for bttvgrab
  - reset /dev/zero to 666
- added user ixware
- updated man page init.d.7
- don't call sendmail in cron.daily
- /sbin/init.d/network - added ppp case
- SuSEconfig: fixed handle of USE_NIS_FOR_RESOLVING
- etc/csh.*: new versions
- etc/skel/.emacs: new version
- cron.daily: delete old log file backups even when no new backup is created
- etc/inittab: added entry for powerfail (not activated)
- etc/issue:  set version to 5.2
- lib/YaST/bootsetup:  set version to 5.2
- sbin/init.d/nfs: don't do anything for noauto nfs systems
* Wed Feb 11 1998 ro@suse.de
- changed etc/issue for Business Linux
* Tue Feb 10 1998 bs@suse.de
- fixed MD5SUM in /lib/YaST/SuSEconfig.functions
* Mon Feb  9 1998 bs@suse.de
- fixed /lib/YaST/SuSEconfig.functions
* Sat Feb  7 1998 bs@suse.de
- wait for Return when bootup for the first time.
- etc/csh.cshrc:  fixed color ls options
- etc/skel/.cshrc: added ispell command.
* Thu Feb  5 1998 bs@suse.de
- added user amanda.disk
- some changes to etc/csh.cshrc
- changed comment in sbin/init.d/serial
- SuSEconfig: added some stuff to /etc/SuSEconfig/*
    added new params --nonewpackage & --force
    moved functions to /lib/YaST/SuSEconfig.functions
- etc/profile: - call dircolors with "-b".
  - set OPENWINHOME only, when /usr/openwin/lib exists
* Tue Feb  3 1998 bs@suse.de
- added group wwwadmin
- added /etc/netgroup
- use "news" as default for NNTPSERVER in etc/rc.config
- fixed comment in etc/skel/.exrc
- cron.daily:  - added CMOS battery check
  - cron.daily.local will now be sourced, so you can use
    check_log_file for your own files.
  - let user decide (rc.config) how old old man pages are
  - added some files to check_log_file
- etc/inittab: fixed entry for xdmsc
- added /sbin/init.d/halt.local
- set $YP_DOMAINNAME in sbin/init.d/boot also.
- etc/profile:  set ~/bin at the beginning of PATH - root has /sbin:/usr/sbin
    in front of it.  Also added support for different machines
    in ~/bin.
* Wed Jan 28 1998 bs@suse.de
- added userdel.local
* Tue Jan 13 1998 bs@suse.de
- new group "disk" added.
* Thu Dec 11 1997 bs@suse.de
- etc/skel/.emacs:  auctex fix
* Tue Dec  9 1997 bs@suse.de
- added *.SuSE-dynamic/*.SuSE-static stuff to SuSEconfig
* Mon Dec  8 1997 bs@suse.de
- switched headline of /sbin/init.d/rc to /bin/bash
* Tue Dec  2 1997 bs@suse.de
- fixed xpath in csh.login
- create cron.daily.local & permissions.local via %%post (and dont include
  as files)
* Mon Nov 24 1997 bs@suse.de
- skipped fillup etc/passwd and etc/group in %%pre section (we don't have
  any non root files in this package anymore)
* Tue Nov 18 1997 bs@suse.de
- delete /var/lock/*/* at bootup
* Tue Nov 18 1997 bs@suse.de
- SuSEconfig: added tab in generated /etc/hosts
- sbin/rctab: fixed restore
* Tue Nov 18 1997 bs@suse.de
- disabled appletalk in /etc/conf.modules
* Mon Nov 17 1997 bs@suse.de
- etc/permissions: dev/zero is now 644
* Sun Nov 16 1997 bs@suse.de
- removed all non root directories (included in aaa_dir)
- sbin/init.d/network: skip ppp devices
* Sat Nov 15 1997 bs@suse.de
- added SuSE X-Server to etc/permissions.*
* Fri Nov 14 1997 bs@suse.de
- %%pre : do fillup etc/{passwd,group} if bin/fillup exists
* Fri Nov 14 1997 bs@suse.de
- added "/tmp/.X11-unix  root.root 1777"  to etc/permissions
* Thu Nov 13 1997 bs@suse.de
- cron.daily: changes for check_log_file
* Wed Nov 12 1997 bs@suse.de
- SuSEconfig: don't run ldconfig in inst-sys
* Tue Nov 11 1997 bs@suse.de
- lib/YaST/bootsetup: switched to version 5.1
- etc/profile: fixed source for ksh
- sbin/initd/xdm: added kdm functionality
* Thu Oct 30 1997 bs@suse.de
- moved etc/group to %%pre section in spec file.
* Thu Oct 30 1997 bs@suse.de
- SuSEconfig & rc.config: do fixes for new sendmail package
* Tue Oct 28 1997 bs@suse.de
- added .xtalkrc to skel
* Tue Oct 28 1997 bs@suse.de
- added /opt/kde/lib to ld.so.conf.in
* Fri Oct 24 1997 bs@suse.de
- prepared for autobuild
- home of user news moved to /var/lib/news
- cron.daily: added REINIT_MANDB (reinitialize /var/catman/index.bt)
    fixed call of sendmail
- SuSEconfig: added USE_NIS_FOR_RESOLVING flag for resolv.conf
- added permissions.paranoid (thanx to Marc Schaefer)
- added directory usr/empress
- moved /usr/local/man and /usr/local/info to the beginning of search
  pathes
- explicitely umount proc in sbin/init.d/halt
- nfserver: added start of rpc.ugidd
- added creation of usradd.local
- etc/permissions: added Hylafax stuff
- sbin/init.d: use "umount -n" in sulogin case
- route: new version
- csh.cshrc: XUSERFILESEARCHPATH fixed
- conf.modules: added specialix devices
- added usr/doc/support/suppform.txt
