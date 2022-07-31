#
# spec file for package acpid
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


Name:           acpid
Version:        2.0.33
Release:        1.6
Summary:        Daemon to execute actions on ACPI events
License:        GPL-2.0-or-later
Group:          System/Daemons
URL:            https://sourceforge.net/projects/acpid2/
Source:         https://downloads.sourceforge.net/project/acpid2/%{name}-%{version}.tar.xz
Source3:        README.SUSE
Source5:        events.power_button
Source6:        thinkpad_handler
Source7:        power_button
Source8:        acpid.service
Source9:        events.thinkpad
Source10:       events.sleep_button
Source11:       sleep_button
# PATCH-MISSING-TAG -- See http://wiki.opensuse.org/openSUSE:Packaging_Patches_guidelines
Patch1:         acpid-makefile.patch
#BuildRequires:  systemd-rpm-macros
#%systemd_ordering

%description
ACPID is a flexible, extensible daemon for delivering ACPI events. It
listens to a file (/proc/acpi/event) and, when an event occurs,
executes programs to handle the event. The start script loads all
needed modules.

%prep
%setup -q
%patch1

cp %{SOURCE3} %{SOURCE5} %{SOURCE6} %{SOURCE7} %{SOURCE9} %{SOURCE10} %{SOURCE11} .

%build
export CFLAGS="%{optflags}"
export LDFLAGS="-Wl,-z,relro,-z,now"
%configure
%make_build

%install
%make_install BINDIR=%{_sbindir}
install -Dm 744 thinkpad_handler %{buildroot}%{_libexecdir}/acpid/thinkpad_handler
install -Dm 644 events.thinkpad %{buildroot}%{_sysconfdir}/acpi/events/thinkpad
mkdir -p %{buildroot}/%{_unitdir}
install -m 644 %{SOURCE8} %{buildroot}/%{_unitdir}
ln -sf %{_sbindir}/service %{buildroot}%{_sbindir}/rcacpid

# formerly installed, but no longer useful with systemd. Keep as documentation.
cp -p events.power_button events.sleep_button power_button sleep_button samples/
# for the rpmlint fascists
mv samples examples
# keep the logfile
install -dm 755 %{buildroot}%{_localstatedir}/log
touch %{buildroot}%{_localstatedir}/log/acpid

%pre
%service_add_pre acpid.service

%post
%service_add_post acpid.service

%postun
%service_del_postun acpid.service

%preun
%service_del_preun acpid.service

%files
%dir %{_sysconfdir}/acpi
%dir %{_sysconfdir}/acpi/events
%{_sysconfdir}/acpi/events/thinkpad
%{_libexecdir}/acpid
/%{_unitdir}/%{name}.service
%{_sbindir}/rcacpid
%{_sbindir}/acpid
%{_sbindir}/kacpimon
%{_bindir}/acpi_listen
%doc README.SUSE README Changelog examples
%{_mandir}/man8/acpid.8%{?ext_man}
%{_mandir}/man8/acpi_listen.8%{?ext_man}
%{_mandir}/man8/kacpimon.8%{?ext_man}
%ghost %config(noreplace,missingok) %{_localstatedir}/log/acpid

%changelog
* Sat Oct 16 2021 Dirk Müller <dmueller@suse.com>
- update to 2.0.33:
  - Detect newer GNOME power manager.
  - openrc-shutdown: Set shutdown time to 'now'.
  - Attempt to open input layer devices whose permissions have changed.
  - Comments added.
* Mon Aug 23 2021 Marcus Meissner <meissner@suse.com>
- allow DeviceAllow=char-input to make character input work again
  (was blocked by ProtectClock=true check added)
* Tue Jul 27 2021 Johannes Segitz <jsegitz@suse.com>
- Added hardening to systemd service(s). Modified:
  * acpid.service
* Mon Jan  4 2021 Dirk Müller <dmueller@suse.com>
- spec-cleaner run
* Wed Aug 21 2019 Aaron Stern <ukbeast89@protonmail.com>
- Update to version 2.0.32
  * Remove filename argument from --nosocket option
  * Fix race during startup
* Sun Mar 17 2019 Jan Engelhardt <jengelh@inai.de>
- Reduce %%systemd_requires to %%systemd_ordering:
  %%service_* can deal with its absence.
- Reduce boasting wording in description.
* Wed Mar  6 2019 Matthias Eliasson <elimat@opensuse.org>
- Update to version 2.0.31
  * Add events for keyboard illumination up/down
  * kacpimon: Bump connection limit to 100
- Run spec-cleaner
* Fri Sep 28 2018 egotthold@suse.com
- Update to version 2.0.30
  * configure: Don't use AC_FUNC_MALLOC, AC_FUNC_REALLOC.
  * samples: powerbtn: extend the list of known PMS
  * samples: powerbtn: fix kde4 power management detection
* Sun Jul 29 2018 jengelh@inai.de
- Use noun phrase in summary.
* Sat Jun  9 2018 antoine.belvire@opensuse.org
- Update to 2.0.29:
  * Decouple -d and -f options.  Bug #15.
  * Rename acpid_debug -> debug_level.
  * Log missing input layer as a warning.
* Sat Nov  4 2017 aavindraa@gmail.com
- Update to version 2.0.28
  * Fix intermittent "Address already in use"
  * inotify: process all inotify messages in buffer
  * Use proper lengths for inotify buffers.
* Mon Nov 28 2016 msuchanek@suse.com
- Remove ExclusiveArch. At least some ARM boards emulate ACPI events with their
  power button driver. At worst the daemon will be superfluous on some systems.
  (bsc#1012325)
* Mon Apr 25 2016 p.drouand@gmail.com
- Update to version 2.0.27
  * Fix out of tree build (sock.c ud_socket.c)
  - kacpimon: fix out of tree build (kacpimon/Makefile.am)
  - input_layer: Allow repeated reporting of VOLUME keys (input_layer.c)
- Remove some extra tags
* Sun Jan 17 2016 mpluskal@suse.com
- Update to 2.0.26
  * Fix build warning with new kernel headers.
  * Fix build with musl libc.  Define isfdtype() if libc doesn't
    have it.
  * Fix out of tree build.
* Sat Sep 26 2015 mpluskal@suse.com
- Update to 2.0.25
  * Remove release process from README.
  * Fix missing libc_compat.h in release tarball.
- Changes for 2.0.24
  * Avoid using SW_VIDEOOUT_INSERT if it isn't available.
  * Add support for Copy and Restart keys.
  * Add support for non-glibc libc's.
  * Fix compiler warnings.
  * Add systemd info to documentation.
- Update project url
- Cleanup spec file with spec-cleaner
- Obey default CFLAGS
* Tue Dec 16 2014 p.drouand@gmail.com
- Update to version 2.0.23
  + Avoid using KEY_MICMUTE if it doesn't exist.
    (input_layer.c)  (Lonnie Abelbeck)
  + Add troubleshooting section to man page.
    (acpid.8)  (Ted Felix)
* Tue Aug 12 2014 p.drouand@gmail.com
- Update to version 2.0.22
  + Add support for F20.  Debian Bug #738611.
  + Fix for repeated mute keys on some ThinkPad models.
  + Add "-t" short option for "--tpmutefix".
  + Update man page for --tpmutefix.
- Remove "Configure it in /etc/sysconfig/powermanagement." in the
  description; the sysconfig file doesn't exist anymore
- Changes from version 2.0.21
  + Add new <drop> action.  Debian #732277.
* Tue Aug  5 2014 dimstar@opensuse.org
- Fix rcacpid symlink to point to /usr/sbin/service, not the
  systemd .service file: the service file is actually not
  executable.
* Fri Feb 14 2014 oneukum@suse.com
- correct pointer at further documentation in README
* Thu Dec 12 2013 p.drouand@gmail.com
- Update to version 2.0.20
  - Improve build and release documentation.
    (README)  (Ted Felix)
  - Fix for Debian bug #719659.  Improved handling of systems with
    large numbers of input layer connections.  Better error handling.
    (connection_list.h connection_list.c inotify_handler.c input_layer.c
    netlink.c proc.c sock.c acpid.c)  (Ted Felix, Ben Winslow)
  - Update .gitignore for Eclipse.
    (.gitignore)  (Ted Felix)
- Remove unused rcacpid from sources
- Change systemd for systemd-rpm-macros requirement; full systemd
  environment is not needed to build
- Rename README.SuSE in README.SUSE to fix suse-wrong-suse-capitalisation
  rpmlint warning
* Sat Oct 19 2013 p.drouand@gmail.com
- Drop sysvinit dupport; acpid doesn't build for distributions which
  use sysvinit
* Tue Aug 13 2013 mchang@suse.com
- power_button: iterate systemd-logind sessions and do nothing if a
  active X session found (bnc#810125)
* Fri Aug  2 2013 werner@suse.de
- Use sourceforge download as below http://tedfelix.com/linux/
  the tar ball has been removed
* Thu Jul  4 2013 seife+obs@b1-systems.com
- remove power and sleep button handlers -- now handled by systemd
  just keep them as examples in the documentation
* Wed Jul  3 2013 seife+obs@b1-systems.com
- remove obsolete thinkpad_acpi modprobe config (bnc#792172)
* Tue Jun  4 2013 crrodriguez@opensuse.org
- Also remove After=syslog.target from unit file (target does
  not exists anymore)
* Tue Jun  4 2013 crrodriguez@opensuse.org
- 2.0.19 release
- README improvements  (README)  (Ted Felix)
- man page additions  (acpid.8)  (Ted Felix)
    (kacpimon/libnetlink.c)  (Ted Felix)
- Add support for mic mute (KEY_MICMUTE).
    (input_layer.c)  (Ted Felix)
- Fix format of video/tabletmode event string.  CRITICAL.
    (input_layer.c)  (Ted Felix)
- Add how to kill acpid to kacpimon man page.
    (kacpimon.8)  (Ted Felix)
- Add info on logind.conf's HandlePowerKey to man page.
    (acpid.8)  (Ted Felix)
- Remove ExecStop from systemd unit, not required.
* Tue Jan 15 2013 trenn@suse.de
-  Catch and process sleep event correctly, even if no X is
  running.
* Sun Sep 23 2012 crrodriguez@opensuse.org
- 2.0.17 release
    (configure.ac)  (Ted Felix)
  - Check for chmod.
    (configure.ac)  (Ted Felix)
  - Add support for tablet mode switch.
    (input_layer.c)  (Fabian Henze)
  - Incorrect sizeof() usage for memset.
    (libnetlink.c)  (Auke Kok)
  - Close some unclosed fd's.
    (acpid.c event.c ud_socket.c)  (Auke Kok)
  - Do not create pid file when running in foreground.
    (acpid.c)  (Cristian Rodriguez)
  - Free regular expression.
    (event.c)  (Cristian Rodriguez)
- acpid-wrong-memset.patch removed, is upstream
* Sun Aug 19 2012 crrodriguez@opensuse.org
- Improve systemd unit
  * run in the foreground
  * use netlink only as /proc/acpi files are deprecated.
* Mon Apr  2 2012 tabraham@novell.com
- Update to acpid 2.0.16
  + Add tests for required functions to configure.ac.
    (configure.ac)  (Ted Felix)
  + Move fchmod() before bind() on socket.  Debian bug #664705.
    (sock.c ud_socket.c ud_socket.h)  (Ted Felix)
  + Switch back to chown() as fchown() doesn't appear to work with sockets.
    (sock.c)  (Ted Felix)
  + Add support for headphone (and other) jack switch events.
    (input_layer.c)  (AlexanderR)
  + Add notes on making the tarball.
    (README)  (Ted Felix)
* Fri Mar 16 2012 tabraham@novell.com
- Update to acpid 2.0.15
  + Improve man page (Debian bug #656676)
    (acpid.8 acpi_listen.8)  (Ted Felix)
  + Change makefile to get rid of double slashes on install paths.
    Note: This change was lost due to introduction of autoconf which
    wiped out the old Makefile.  (Makefile)  (Gilles Espinasse)
  + Switch from Makefile to autoconf build system.  Fix some related
    warnings.
    (Makefile Makefile.am README TODO acpi_ids.c acpi_ids.h acpid.h
    configure.ac connection_list.h event.c kacpimon/Makefile.am
    kacpimon/makefile proc.h sock.h)
    (Cristian Rodriguez)
  + Fix build warnings uncovered by new gcc settings from autoconf.
    (inotify_handler.c input_layer.c kacpimon/acpi_ids.c kacpimon/acpi_ids.h
    kacpimon/connection_list.c kacpimon/connection_list.h
    kacpimon/input_layer.c kacpimon/kacpimon.c kacpimon/netlink.c netlink.c
    proc.c sock.c)
    (Ted Felix)
  + Remove fcntl() calls to set FD_CLOEXEC and replace with
    CLOEXEC flags within the various open(), recvmsg() and other calls.
    Requires kernel version 2.6.23 and above.
    (acpi_listen.c inotify_handler.c input_layer.c libnetlink.c netlink.c
    proc.c ud_socket.c)
    (Cristian Rodriguez)
  + Add SOCK_NONBLOCK to ud_create_socket().
    (ud_socket.c) (Cristian Rodriguez)
  + Use isfdtype() instead of getsockopt() in is_socket().  Use fchmod(),
    fstat(), and fchown() instead of the non-"f" versions in open_sock().
    (sock.c) (Cristian Rodriguez)
  + Use __attribute__ for argument checking in acpid_log().
    (input_layer.c log.h netlink.c ud_socket.c) (Cristian Rodriguez)
  + Close only the open fds in close_fds().
    (acpid.c) (Cristian Rodriguez)
  + Use accept4() with SOCK_CLOEXEC and SOCK_NONBLOCK in ud_accept().
    Remove unnecessary calls to fcntl() in process_sock().
    (sock.c ud_socket.c) (Cristian Rodriguez)
  + Use asprintf() instead of snprintf() in process_sock().
    (sock.c) (Cristian Rodriguez)
  + Use TEMP_FAILURE_RETRY macro instead of bogus checks for EINTR.
    (acpi_listen.c acpid.c event.c input_layer.c libnetlink.c netlink.c
    proc.c ud_socket.c) (Cristian Rodriguez)
  + Use safer, faster, and more modern functions asprintf(), fstatat(),
    openat(), and fdopen() in the configuration file processing.
    (event.c) (Cristian Rodriguez)
- refreshed patches - acpid-makefile.patch acpid-wrong-memset.patch
* Tue Jan 17 2012 tabraham@novell.com
- Update to acpid 2.0.14
  + fixed brace style (Ted Felix)
  + added support for a "K" suffix on event strings to indicate
    that they may have originated from a keyboard input layer
    device. This can be used to differentiate between a power
    switch on the keyboard, and a power switch on the computer's
    case. (Ted Felix)
  + Added a pathname to connection along with a find_connection_name()
    Modifications to process_inotify() to log IN_DELETE events.
    Additional debugging output (Ted Felix)
* Sat Dec 31 2011 crrodriguez@opensuse.org
- Put acpid back in %%{_sbindir} /usr is nowdays mounted by the
  initrd
* Tue Dec 27 2011 idonmez@suse.com
- Fix wrong size parameter in memset call
* Fri Dec 16 2011 crrodriguez@opensuse.org
- Update to acpid 2.0.13
* Mon Sep 26 2011 fcrozat@suse.com
- Use latest systemd RPM macros.
* Fri Sep 23 2011 fcrozat@suse.com
- Ensure acpid is enabled on initial install, under systemd
* Sat Sep 17 2011 jengelh@medozas.de
- Remove redundant tags/sections from specfile
- Use %%_smp_mflags for parallel build
* Wed Aug 24 2011 fcrozat@suse.com
- Use systemd macros to enable acpid service.
* Tue Aug 23 2011 aj@suse.de
- Remove _service file.
* Tue Aug 23 2011 glin@suse.com
- Add the check for gnome-settings-daemon in power_button since
  gnome-power-manager has been integrated into
  gnome-settings-daemon. bnc#711148
* Sat May 21 2011 vlado.paskov@gmail.com
- Version update to 2.0.10 for systemd support
* Wed Mar  9 2011 coolo@novell.com
- update to 2.0.8:
  - Fixed "comparison between signed and unsigned integer expressions"
    error with gcc 4.6.  (libnetlink.c) (Eugeni Dodonov)
  - Fixed unused variable "type" with gcc 4.6.  (libnetlink.c) (Jiri Skala)
* Wed Dec 22 2010 aj@suse.de
- Update to 2.0.7:
  * Reduced the startup logging and skipped processing of "." and ".."
    in the config files directory
  * Added CD-related buttons.
  * Removed the "getppid() == 1" hack from daemonize().
  * Added FD_CLOEXEC to the input layer fd's.
  Obsoletes patches acpid-2.0.5-forking.patch and
  acpid-2.0.6-event-skip-messages.patch.
* Fri Nov 19 2010 seife@opensuse.org
- fix systemd service file (acpid is in /sbin, not /usr/sbin)
* Tue Nov  9 2010 cristian.rodriguez@opensuse.org
- use full RELRO here.
* Tue Oct 12 2010 cristian.rodriguez@opensuse.org
- fix logic
* Tue Oct 12 2010 cristian.rodriguez@opensuse.org
- Do not warn on "skipping .. and ." directory entries
* Sat Oct  2 2010 aj@suse.de
- Add systemd configuration.
- Always fork, even if called from PID 1.
* Sat Oct  2 2010 aj@suse.de
- Update to version 2.0.6:
  * cleanup of code and build infrastructure
  * Support netlink and input layer
* Sat Oct  2 2010 aj@suse.de
- Split up acpi in its own package.
* Wed Sep  2 2009 glin@novell.com  
- Don't shutdown if dalston-power-applet is running.
* Sun Aug 30 2009 aj@suse.de
- Remove enable from hotkey setting for think_acpi to get rid of this
  kernel message:
  "Please remove the hotkey=enable module parameter, it is deprecated.
  Hotkeys are always enabled."
* Thu Jul  9 2009 seife@suse.de
- remove obsolete cruft from acpid init script
- fix syntax error in "rcacpid probe" (bnc#508574)
* Wed Apr 22 2009 seife@suse.de
- update to version 1.0.10
  - Add a -C (--clientmax) command line flag to set max number of
    non-root socket connections.
  - Set the maximum number of socket clients to 256 by default.
  - Close clients that have disconnected.
  - Give up and exit() if 5 accept() calls fail in a row.
  - Open /dev/null O_RDWR, rather than O_RDONLY.
- this fixes bnc#491455
* Wed Apr 15 2009 crrodriguez@suse.de
- fix boot warning about /etc/modprobe.d/thinkpad_acpi
* Mon Mar  9 2009 mmarek@suse.cz
- renamed modprobe config to /etc/modprobe.d/50-thinkpad_acpi.conf
  (required by new module-init-tools).
* Wed Feb  4 2009 seife@suse.de
- update to version 1.0.8:
  - various code cleanups, enable stricter compiler warnings
  - fix typos in man pages. (acpid.8, acpi_listen.8)
  - stop processing ACPI events when a lockfile exists (see acpid.8)
  - add -l (--logevents) option to enable logging of all events.
    Due to a number of reports of log flooding (bad ACPI BIOS?), the
    new default is to NOT log events
  - add pidfile support and a -p (--pidfile) option to change it
  - close client file descriptors on exec()
  - fix a fd leak on error
* Mon Jan 26 2009 ro@suse.de
- change fillup call from "-Y" to "-y" the boot script has
  been present in this package for long enough (SLES10-GA)
* Sun Nov 16 2008 hmacht@suse.de
- Don't shutdown if a kde4 session is running and the power button
  is pressed, powerdevil will care (bnc#443210)
* Thu Oct 16 2008 thoenig@suse.de
- Fix documentation reference and vendor names in thinkpad_acpi
  (bnc#410684)
* Wed Oct 15 2008 seife@suse.de
- fix syntax error in acpid init script (bnc#435503)
* Mon Sep  1 2008 hmacht@suse.de
- different config files for different rules:
    events.thinkpad and events.power_button
* Thu Aug  7 2008 hmacht@suse.de
- add power_button script to care about button presses if there
  is no active X session
* Sun Jun  8 2008 hmacht@suse.de
- minor fixes to the thinkpad_handler script (bnc#371927)
* Fri Jun  6 2008 hmacht@suse.de
- add script for enabling/disabling bluetooth via hotkey on
  Thinkpads (bnc#371927)
* Tue May 20 2008 thoenig@suse.de
- The game is not over yet:  Re-introduce hotkey mask for
  thinkpad_acpi.modprobe (bnc#369535, bnc#382343)
* Tue Feb 26 2008 thoenig@suse.de
- Drop hotkey masks for thinkpad_acpi.modprobe
* Tue Sep 11 2007 thoenig@suse.de
- Fix hotkey mask for thinkpad_acpi.modprobe (#308191)
* Wed Aug  8 2007 thoenig@suse.de
- remove loading of ACPI modules, they are now being loaded
  automatically (#216564)
- rename ibm_acpi.modprobe to thinkpad_acpi.modprobe as the kernel
  module was renamed (#297812)
* Mon Jul 30 2007 seife@suse.de
- fix "--skip-unsupported" warnings on module load (b.n.c #293758)
* Tue Jul  3 2007 seife@suse.de
- update to version 1.0.6
  mostly our patches included upstream
- adjust init script to the new pcc-acpi module
* Tue Jun 19 2007 thoenig@suse.de
- Add $local_fs to Required-Start (b.n.c #285472)
* Mon Jun  4 2007 lrupp@suse.de
- clean builddir after build is finished
- own /var/log/acpid (#280469)
* Tue Apr 24 2007 trenn@suse.de
- compile some more files with rpm_opt flags
- remove/fix:
  +E: acpid unknown-lsb-tag # X-UnitedLinux-Should-Start:
  +E: acpid unknown-lsb-tag # X-UnitedLinux-Should-Stop:
* Tue Apr 10 2007 hmacht@suse.de
- add modules dock and bay to probed laptop modules
* Thu Mar 29 2007 rguenther@suse.de
- add /etc/modprobe.d directory
* Fri Nov 17 2006 hmacht@suse.de
- remove CPUFreq modules loading, acpid is not available on all
  architectures. Move handling to proper place --> HAL init script
  (novell bug 220682)
* Mon Nov 13 2006 hmacht@suse.de
- do not "fail" if there is no CPUFreq support, print descriptive
  message instead (novell bug 219757)
* Wed Oct 18 2006 seife@suse.de
- unload asus_acpi on unsupported machines.
- load cpufreq_acpi after speedstep-smi module.
- load the cpufreq_conservative governor (bug 163767).
- ignore editor backup files for the event configuration.
- package the provided action script samples under documentation.
- cleanup the specfile %%prep section.
* Tue Oct 17 2006 hmacht@suse.de
- load CPUFreq modules before acpi modules, otherwise we would
  exit without acpi support
* Tue Sep 12 2006 hmacht@suse.de
- load CPUFreq modules in acpid for now because they have to be
  already loaded when HAL starts
* Thu Jun  1 2006 thoenig@suse.de
- rcacpid: do not probe unsupported modules if
  LOAD_UNSUPPORTED_MODULES_AUTOMATICALLY is set to yes
  (b.n.c #180654)
- rcacpid: be verbose about which modules are being probed or
  loaded.
* Tue Feb 21 2006 rw@suse.de
- never try laptop modules on ia64 (bug #146291)
* Wed Feb 15 2006 thoenig@suse.de
- revert hotkey mask for IBM ACPI back to 0xffff (bug #150357)
- add documentation hints for IBM ACPI driver
* Thu Feb  9 2006 seife@suse.de
- do not try the hotkey modules on ia64 (bug #146291)
* Mon Feb  6 2006 seife@suse.de
- do not load ac and battery modules on ia64 (bug #140249)
- untangle the "suse-files.tar" packaging mess
- after a kernel update, rescan the laptop modules
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Thu Nov 24 2005 seife@suse.de
- move daemon from /usr/sbin to /sbin to remove the $remote_fs
  dependency and start sooner
- log via syslog instead of using the own logfile mechanism
* Tue Oct 25 2005 thoenig@suse.de
- changed hotkey mask for ibm_acpi from 0xffff to 0xffef so that
  the driver does not block Fn-F5 (switch Bluetooh on/off) on IBM
  ThinkPads (closes #128088)
* Wed Oct  5 2005 dmueller@suse.de
- add norootforbuild
* Sat Sep 24 2005 seife@suse.de
- rework last patch, fix a memleak in addition to the fd leak.
* Fri Sep 23 2005 seife@suse.de
- fix filedescriptor leak on client disconnect (bug #117884)
* Thu Sep  8 2005 thoenig@suse.de
- fixed probing of laptop modules (closes #115819)
* Wed Sep  7 2005 thoenig@suse.de
- changed modprobe.d/ibm_acpi to be even more verbose (more Fn-Fxx
  will be reported (see #115127 and closes re-opened #113625)
* Wed Aug 31 2005 ro@suse.de
- removed config-dist.sh (ExclusiveArch is already there)
* Tue Aug 30 2005 thoenig@suse.de
- added sony_acpi and pcc_acpi to be probed on first run (SUSE
  feature request r6125)
* Mon Aug 29 2005 thoenig@suse.de
- fixed probe function of rcacpid
* Mon Aug 29 2005 thoenig@suse.de
- added install parameter for ibm_acpi to enable verbose output
  of hotkey (#113625)
* Thu Aug 25 2005 thoenig@suse.de
- rcacpid now probes laptop modules once and will only
  load those modules at a later point if modprobe succeeded.
* Wed Aug 10 2005 thoenig@suse.de
- added three modules to DEFAULT_ACPI_MODULES:
  * asus_acpi
  * ibm_acpi
  * toshiba_acpi
- added $SYSCONFDIR/modprobe.d/ibm_acpi for ibm_acpi to load the
  module with "experimental=1"
* Fri Aug  5 2005 seife@suse.de
- load ACPI modules in /etc/init.d/acpid.
* Fri Aug  5 2005 trenn@suse.de
- Activate acpid by default again (use -Y to force, was disabled
  in old setups, but we need it urgently now)
- Deleted suse stuff (acpid_proxy,...), only use acpid to forward
  acpi events to other apps/services.
- updated acpid (1.0.3 -> 1.0.4) acpi (0.07 -> 0.09)
- changed config to not process acpi events, just forward them
* Mon May  2 2005 mmj@suse.de
- Fix warning about chdir return value not being caught
* Mon Apr  4 2005 pth@suse.de
- Fix signed/unsigned warnings
* Thu Nov 25 2004 zoz@suse.de
- rcacpid status now reports service acpid as unused if acpid was
  started from rcpowersaved (Bug 48432)
* Thu Nov 11 2004 zoz@suse.de
- added /var/lib/acpi with proper permissions to filelist. Further
  acpid_proxy won't create that dir if missing. (Bug 47729)
* Mon Sep  6 2004 seife@suse.de
- clean up config file for sysconfig editor
* Thu Aug 26 2004 trenn@suse.de
- deleted debian stuff
* Fri Aug 13 2004 trenn@suse.de
- updated to acpid from 1.0.1 to version 1.0.3 and
  acpi Version from 0.06 to 0.07
* Fri May 14 2004 trenn@suse.de
- P4 Hyperthreading patch from pth@suse (#39017)
* Tue Apr  6 2004 trenn@suse.de
- rcacpid stop  does not return skipped anymore on none acpi systems
  this prevented acpid to uninstall on these systems  (#38508)
* Thu Mar 18 2004 seife@suse.de
- updated README.SuSE and default config (#36208)
* Wed Mar  3 2004 trenn@suse.de
- add %%restart_on_update and %%stop_on_removal in .spec file
* Tue Feb 24 2004 trenn@suse.de
- deleted ac_on_power, is now in powersave package
* Mon Feb 23 2004 trenn@suse.de
- deleted -y parameter in inserv, to not start by default
  powersave gets confused otherwise, only one daemon is allowed
  to access /proc/acpi/event
* Wed Nov  5 2003 olh@suse.de
- do not start the build if not required
* Mon Sep 22 2003 zoz@suse.de
- fixed naming of actions in acpid_proxy (Bug 31357)
- fixed metadata and description of actions in sysconfig template
  (Bug 31357)
- fixed startscript to unload modules if requested (Bug 31357)
- set default action for lid closure to 'ignore', because 'throttle'
  breaks some laptops (Bug 31529)
* Sat Sep 20 2003 ro@suse.de
- fix typo in sysconfig-file
* Thu Sep 18 2003 trenn@suse.de
- bug 30913 and 31265
  lid state is now read out correctly (CLOSE->CLOSED)
  corrected parts for throttling
  action kde_term fixed (determine kde user)
  action kde_logout additionally added
* Tue Sep 16 2003 trenn@suse.de
- bug 30399 -> lid read out of /proc/acpi/lid/... now
  and changed frequency scaling from deprecated /acpi/processor
  to cpufreqd
* Wed Sep 10 2003 kukuk@suse.de
- rcacpid: Fix return codes, fix try-restart, fix probe (don't
  compare with non existing FOO config file), fix restart (restart
  should honor modified sysconfig file).
* Tue Sep  2 2003 trenn@suse.de
- on_ac_adapter: more stable and
  check for desktop
  start acpid by default
* Thu Aug 28 2003 trenn@suse.de
- fixed bug in sysconfig.acpi template
* Thu Aug 28 2003 trenn@suse.de
- added on_ac_power
* Tue Aug 26 2003 trenn@suse.de
- added action tags for sysconfig file
* Thu Aug 14 2003 ro@suse.de
- added exclusivearch line to specfile
* Sun Jul 20 2003 zoz@suse.de
- Removed ACPI_MODULES_NOT_TO_LOAD from /etc/init.d/acpid and
  /etc/sysconfig/powermanagement. now we use ACPI_MODULES instead.
  This works also with 2.5/6 kernels and you may add one of the
  modules asus_acpi or toshiba_acpi to this variable.
* Sat Mar  1 2003 zoz@suse.de
- fixed acpid: Did not call acpid_proxy with event information
- splitted ACPI_BUTTON_LID into ACPI_BUTTON_LID_OPEN and
  ACPI_BUTTON_LID_CLOSE
- added some actions for button events to acpid_proxy
  + kde_term     (terminate all KDE sessions)
  + wmaker_term  (terminate all wmaker sessions)
  + standby      (switches to S1. This may crash the system. Test it before!)
  + suspend      (switches to S3 if kernel is 2.5 or newer)
  + hibernate    (switches to S4 if kernel is 2.5 or newer
  + throttle     (reduce processor performance, enable maximum processor throttlin
    put disk into sleep state)
  + dethrottle   (restore settings like before throttle)
- for proper throttling added ACPI_THROTTLED_DISK_TIMEOUT and
  ACPI_THROTTLED_KUPDATED_INTERVAL
- provided some usefull information in README.SuSE
* Mon Feb 24 2003 zoz@suse.de
- enhanced sysconfig metadata and descriptions
- added ACPI_MODULES_NOT_TO_UNLOAD, because there are modules which
  oops when unloaded
- added ACPI_BUTTON_SLEEP
- added some more actions for button events
* Fri Feb 21 2003 mmj@suse.de
- Add sysconfig metadata [#22676]
* Sat Feb  8 2003 zoz@suse.de
- added 'acpi': a tool providing battery and thermal information
  (like apm in package apmd)
* Tue Sep 17 2002 ro@suse.de
- removed bogus self-provides
* Fri Sep  6 2002 zoz@suse.de
- added comments to sysconfig variables (Bug 18654)
- fixed specfile to fillup /etc/sysconfig/powermanagement properly
* Tue Aug 13 2002 zoz@suse.de
- added PreReq insserv_prereq fillup_prereq
* Tue Aug  6 2002 zoz@suse.de
- initial package: version 1.0.1
- added init script which loads acpi modules as well
- provided acpid_proxy (apmd like) which cares about all events
