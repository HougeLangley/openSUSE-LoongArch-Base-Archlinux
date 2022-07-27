#
# spec file for package acl
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


# Ring0 does not have system-user-bin/system-user-daemon
%bcond_without acl_tests

Name:           acl
%define lname	libacl1
Summary:        Commands for Manipulating POSIX Access Control Lists
License:        GPL-2.0-or-later AND LGPL-2.1-or-later
Group:          System/Filesystems
Version:        2.3.1
Release:        2.5
URL:            https://savannah.nongnu.org/projects/acl
#Git-Web:	http://git.savannah.gnu.org/cgit/acl.git/
#Git-Clone:	git://git.sv.gnu.org/acl
Source:         https://download.savannah.nongnu.org/releases/acl/acl-%version.tar.xz
Source1:        https://download.savannah.nongnu.org/releases/acl/acl-%version.tar.xz.sig
Source2:        baselibs.conf
# http://savannah.nongnu.org/project/memberlist-gpgkeys.php?group=acl
Source3:        %name.keyring

#BuildRequires:  autoconf
#BuildRequires:  automake
#BuildRequires:  gettext-tools-mini
#BuildRequires:  libattr-devel
#BuildRequires:  libtool
#BuildRequires:  pkgconf-pkg-config
%if %{with acl_tests} && 0%{?suse_version} > 1320
BuildRequires:  user(bin)
BuildRequires:  user(daemon)
%endif

%description
getfacl and setfacl commands for retrieving and setting POSIX access
control lists.

%package -n %lname
Summary:        A dynamic library for accessing POSIX Access Control Lists
Group:          System/Libraries
%ifarch ppc64
# bug437293
Obsoletes:      libacl-64bit
%endif
# Added for 12.1
Provides:       libacl = %version-%release
Obsoletes:      libacl < %version-%release

%description -n %lname
This package contains the libacl.so dynamic library which contains the
POSIX 1003.1e draft standard 17 functions for manipulating access
control lists.

%package -n libacl-devel
Summary:        Header files for the POSIX ACL library
Group:          Development/Libraries/C and C++
Requires:       %lname = %version
Requires:       glibc-devel
Provides:       acl-devel = %version
Obsoletes:      acl-devel < %version
%ifarch ppc64
# bug437293
Obsoletes:      libacl-devel-64bit
%endif

%description -n libacl-devel
This package contains all necessary include files and libraries needed
to develop applications that require libacl.

%prep
%setup -q

%build
autoreconf -fi

# Disable -D_FORTIFY_SOURCE=3 for now
# as explained here: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=104964
%global optflags %(echo %{optflags} | sed 's/-D_FORTIFY_SOURCE=3/-D_FORTIFY_SOURCE=2/')

export OPTIMIZER="%optflags -fPIC"
export DEBUG=-DNDEBUG
CFLAGS="%optflags"

%ifarch %ix86 i586
export CFLAGS="%optflags -D_FILE_OFFSET_BITS=64"
%endif

%configure \
	--disable-static \
	--docdir=%_defaultdocdir/%name
make %{?_smp_mflags} V=1

%check
%if %{with acl_tests}
    if ./setfacl -m u:`id -u`:rwx .; then
        make check || (cat test-suite.log ; false)
    else
        echo '*** ACLs are probably not supported by the file system,' \
             'the test-suite will NOT run ***'
    fi
%endif

%install
%make_install
rm -v %buildroot/%_libdir/lib%name.la
rm -rvf %buildroot/%_defaultdocdir/%name
%find_lang %name

%post -n %lname -p /sbin/ldconfig

%postun -n %lname -p /sbin/ldconfig

%files -f %name.lang
%license doc/COPYING
%doc doc/PORTING doc/extensions.txt doc/libacl.txt doc/CHANGES
%_bindir/chacl
%_bindir/getfacl
%_bindir/setfacl
%_mandir/man1/chacl.1
%_mandir/man1/getfacl.1
%_mandir/man1/setfacl.1
%_mandir/man5/acl.5

%files -n libacl-devel
%_includedir/acl/
%_includedir/sys/acl.h
%_libdir/libacl.so
%_mandir/man3/acl_add_perm.3
%_mandir/man3/acl_calc_mask.3
%_mandir/man3/acl_check.3
%_mandir/man3/acl_clear_perms.3
%_mandir/man3/acl_cmp.3
%_mandir/man3/acl_copy_entry.3
%_mandir/man3/acl_copy_ext.3
%_mandir/man3/acl_copy_int.3
%_mandir/man3/acl_create_entry.3
%_mandir/man3/acl_delete_def_file.3
%_mandir/man3/acl_delete_entry.3
%_mandir/man3/acl_delete_perm.3
%_mandir/man3/acl_dup.3
%_mandir/man3/acl_entries.3
%_mandir/man3/acl_equiv_mode.3
%_mandir/man3/acl_error.3
%_mandir/man3/acl_extended_fd.3
%_mandir/man3/acl_extended_file.3
%_mandir/man3/acl_extended_file_nofollow.3
%_mandir/man3/acl_free.3
%_mandir/man3/acl_from_mode.3
%_mandir/man3/acl_from_text.3
%_mandir/man3/acl_get_entry.3
%_mandir/man3/acl_get_fd.3
%_mandir/man3/acl_get_file.3
%_mandir/man3/acl_get_perm.3
%_mandir/man3/acl_get_permset.3
%_mandir/man3/acl_get_qualifier.3
%_mandir/man3/acl_get_tag_type.3
%_mandir/man3/acl_init.3
%_mandir/man3/acl_set_fd.3
%_mandir/man3/acl_set_file.3
%_mandir/man3/acl_set_permset.3
%_mandir/man3/acl_set_qualifier.3
%_mandir/man3/acl_set_tag_type.3
%_mandir/man3/acl_size.3
%_mandir/man3/acl_to_any_text.3
%_mandir/man3/acl_to_text.3
%_mandir/man3/acl_to_any_text.3
%_mandir/man3/acl_valid.3
%_libdir/pkgconfig/libacl.pc

%files -n %lname
%license doc/COPYING.LGPL
%_libdir/libacl.so.1
%_libdir/libacl.so.1.1.2301

%changelog
* Fri Apr  8 2022 Martin Liška <mliska@suse.cz>
- Disable -D_FORTIFY_SOURCE=3 for now
  as explained here: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=104964
* Sun May 16 2021 Dirk Müller <dmueller@suse.com>
- modernize spec-file (move license to licensedir)
* Wed May 12 2021 Ferdinand Thiessen <rpm@fthiessen.de>
- Update to version 2.3.1
  * Update German translation
  * getfacl: fix indent in --help output
  * getfacl: Add --one-file-system option, with this option getfacl
    will not cross mount points
  * Fix segfault on allocation failure
  * Avoid SIGSEGV with link-time optimisation enabled
- Use SourceUrls
* Tue Jan 26 2021 Dominique Leuenberger <dimstar@opensuse.org>
- Replace system-user-{bin,daemon} with user({bin,daemon}): be
  resilient to package name changes.
* Tue Sep  1 2020 Dirk Mueller <dmueller@suse.com>
- update url
* Sun Mar 17 2019 Jan Engelhardt <jengelh@inai.de>
- Update boilerplate descriptions for libacl-devel.
- Remove out-of-date comments for libattr.
- Remove old BuildRoot and %%defattr tags.
- Move library into the standard library directory.
* Thu Nov  8 2018 Cristian Rodríguez <crrodriguez@opensuse.org>
- libacl-devel used to require libattr-devel, but that is no longer
  the case, packages that relied on this indirect dependency to
  be present were fixed years ago.
* Thu Oct 11 2018 jeffm@suse.com
- Update to v2.2.53.
- Removed patches:
  * 0001-Install-the-libraries-to-the-appropriate-directory.patch
  * 0001-Use-OS-byteswapping-macros.patch
  * 0002-setfacl.1-fix-typo-inclu-de-include.patch
  * 0003-test-fix-insufficient-quoting-of.patch
  * 0004-Makefile-rename-configure.in-to-configure.ac.patch
  * 0005-Bad-markup-in-acl.5-page.patch
  * 0006-.gitignore-ignore-and-config.h.in.patch
  * 0007-Use-autoreconf-rather-than-autoconf-to-regenerate-th.patch
  * 0008-libacl-Make-sure-that-acl_from_text-always-sets-errn.patch
  * 0009-libacl-fix-SIGSEGV-of-getfacl-e-on-overly-long-group.patch
  * 0010-punt-debian-rpm-packaging-logic.patch
  * 0011-move-gettext-logic-into-misc.h.patch
  * 0012-test-make-running-parallel-out-of-tree-safe.patch
  * 0013-modernize-build-system.patch
  * 0014-po-regenerate-files-after-move.patch
  * 0015-build-drop-aclincludedir-use-pkgincludedir.patch
  * 0016-build-make-use-of-an-aux-dir-to-stow-away-helper-scr.patch
  * 0017-build-ship-a-pkgconfig-file-for-libacl.patch
  * 0018-read_acl_-comments-seq-rename-line-to-lineno.patch
  * 0019-read_acl_-comments-seq-switch-to-next_line.patch
  * 0020-telldir-return-value-and-seekdir-second-parameters-a.patch
  * 0021-mark-libmisc-funcs-as-hidden-so-they-are-not-exporte.patch
  * 0022-add-__acl_-prefixes-to-internal-symbols.patch
  * 0023-cp.test-Check-permissions-of-the-right-file.patch
  * 0024-libacl-acl_set_file-Remove-unnecesary-racy-check.patch
  * 0025-fix-compilation-with-latest-xattr-git.patch
  * 0026-getfacl-Fix-memory-leak.patch
  * 0027-Fix-the-display-block-nesting-in-acl.5.patch
  * 0028-setfacl-man-page-Minor-wording-improvements.patch
  * 0029-getfacl-Fix-minor-resource-leak.patch
  * 0030-Do-not-export-symbols-that-are-not-supposed-to-be-ex.patch
  * 0031-walk_tree-mark-internal-variables-as-static.patch
  * 0032-ignore-configure.lineno.patch
  * acl-2.2.52-tests.patch
* Sun Sep 24 2017 coolo@suse.com
- refresh acl-2.2.52-tests.patch to work with perl 5.26
* Sat May 20 2017 dimstar@opensuse.org
- BuildRequires gettext-tools-mini instead of gettext-tools: as
  acl is part of the bootstrap, we want to try to keep the dep
  chain as small as possible.
* Sun Apr 23 2017 jengelh@inai.de
- Remove --with-pic that's just for static libraries.
- Replace %%__-type macro indirections.
  Replace old $RPM_ by their macro equivalents for consistency.
  Make the macro style consistent across the file again.
* Mon Apr 17 2017 hendrikw@arcor.de
- reenable full Larg File Support for i586
* Wed Mar 29 2017 fvogt@suse.com
- Make it possible to disable tests (for Ring0)
- Add BuildRequires: system-user-daemon for the testsuite
* Mon Mar 13 2017 kukuk@suse.de
- Add BuildRequires for system user bin needed by test suite
* Wed Dec  2 2015 jeffm@suse.com
- Update to git snapshot dated 21 Sep 2015.
  - Added:
  * 0001-Install-the-libraries-to-the-appropriate-directory.patch
  * 0002-setfacl.1-fix-typo-inclu-de-include.patch
  * 0003-test-fix-insufficient-quoting-of.patch
  * 0004-Makefile-rename-configure.in-to-configure.ac.patch
  * 0005-Bad-markup-in-acl.5-page.patch
  * 0006-.gitignore-ignore-and-config.h.in.patch
  * 0007-Use-autoreconf-rather-than-autoconf-to-regenerate-th.patch
  * 0008-libacl-Make-sure-that-acl_from_text-always-sets-errn.patch
  * 0009-libacl-fix-SIGSEGV-of-getfacl-e-on-overly-long-group.patch
  * 0010-punt-debian-rpm-packaging-logic.patch
  * 0011-move-gettext-logic-into-misc.h.patch
  * 0012-test-make-running-parallel-out-of-tree-safe.patch
  * 0013-modernize-build-system.patch
  * 0014-po-regenerate-files-after-move.patch
  * 0015-build-drop-aclincludedir-use-pkgincludedir.patch
  * 0016-build-make-use-of-an-aux-dir-to-stow-away-helper-scr.patch
  * 0017-build-ship-a-pkgconfig-file-for-libacl.patch
  * 0018-read_acl_-comments-seq-rename-line-to-lineno.patch
  * 0019-read_acl_-comments-seq-switch-to-next_line.patch
  * 0020-telldir-return-value-and-seekdir-second-parameters-a.patch
  * 0021-mark-libmisc-funcs-as-hidden-so-they-are-not-exporte.patch
  * 0022-add-__acl_-prefixes-to-internal-symbols.patch
  * 0023-cp.test-Check-permissions-of-the-right-file.patch
  * 0024-libacl-acl_set_file-Remove-unnecesary-racy-check.patch
  * 0025-fix-compilation-with-latest-xattr-git.patch
  * 0026-getfacl-Fix-memory-leak.patch
  * 0027-Fix-the-display-block-nesting-in-acl.5.patch
  * 0028-setfacl-man-page-Minor-wording-improvements.patch
  * 0029-getfacl-Fix-minor-resource-leak.patch
  * 0030-Do-not-export-symbols-that-are-not-supposed-to-be-ex.patch
  * 0031-walk_tree-mark-internal-variables-as-static.patch
  * 0032-ignore-configure.lineno.patch
- Signficant spec file restructuring due to 0013-modernize-build-system.patch
- removed builddefs.in.diff
* Tue Sep 23 2014 jengelh@inai.de
- Reduce size of filelist by using wildcards;
  remove %%doc (some locations are always %%doc),
  remove %%attr (files already have proper permissions)
* Wed Nov 13 2013 sweet_f_a@gmx.de
- add acl-2.2.52-tests.patch and enable tests, check section taken
  from Fedora package
* Tue Jun 18 2013 coolo@suse.com
- remove gpg-offline calls from bootstrap package
* Sun Jun 16 2013 jengelh@inai.de
- Update to new upstream release 2.2.52
  * This release fixes a few build system issues that were found and
  merges in a tree walking bug fix.
- Remove acl-fiximplicit.patch (merged upstream),
  config-guess-sub-update.diff (no longer applies)
- Sync baselibs.conf with in-.spec obsoletes/provides.
* Tue Mar 19 2013 meissner@suse.com
- add gpg checking
* Fri Mar 15 2013 coolo@suse.com
- use source url
* Sat Feb  2 2013 dmueller@suse.com
- Add config-guess-sub-update.diff:
  update config.guess/sub to latest state for AArch64
* Wed Dec 26 2012 crrodriguez@opensuse.org
- Use OS byteswapping routines, application already Includes
  "endian.h" but then goes ahead defining ad-hoc equivalent
  functionality (0001-Use-OS-byteswapping-macros.patch)
* Wed May 30 2012 sweet_f_a@gmx.de
- remove useless automake deps
* Mon Feb 13 2012 coolo@suse.com
- patch license to follow spdx.org standard
* Wed Nov 30 2011 cfarrell@suse.com
- license update: GPL-2.0+;LGPL-2.1+
  SPDX format
* Wed Nov 30 2011 coolo@suse.com
- add automake as buildrequire to avoid implicit dependency
* Tue Sep 20 2011 crrodriguez@opensuse.org
- Fix provides/Obsoletes
* Fri Sep 16 2011 jengelh@medozas.de
- Implement shlib package (libacl1)
- Enable libacl-devel on all baselib arches
* Tue Apr 19 2011 bphilips@novell.com
- upgrade to 2.2.51
  - Test fixes
* Sat Apr 16 2011 bphilips@novell.com
- upgrade to 2.2.50
  - OPTIONS in man pages should be a section heading, not a subsection heading
  - Fix a typo in the setfacl man page
  - setfacl: Clarify that removing a non-existent acl entry is not an error
  - Prevent setfacl --restore from SIGSEGV on malformed restore file
  - setfacl: make sure that -R only calls stat(2) on symlinks when it needs to
  - libacl: fix potential null pointer dereference
  - setfacl: fix restore crash on malformed input
  - setfacl: print useful error from read_acl_comments
  - setfacl: changing owner and when S_ISUID should be set --restore fix
* Mon Jun 28 2010 jengelh@medozas.de
- use %%_smp_mflags
* Sat Dec 12 2009 jengelh@medozas.de
- add baselibs.conf as a source
- adjust baselibs.conf for SPARC
* Wed Nov 25 2009 meissner@suse.de
- readded incorrectly removed libattr-devel requires in -devel
* Mon Oct 26 2009 meissner@suse.de
- fixed implicit strchr() usage.
* Sun Sep 27 2009 crrodriguez@suse.de
- do not package static libraries
- fix -devel package dependencies
* Sat Aug  1 2009 bphilips@novell.com
- Version bump to 2.2.48
  - Document the new flags comments
  - Include the S_ISUID, S_ISGID, S_ISVTX flags in the getfacl output, and restore them with "setfacl --restore=file".
  - Make sure that getfacl -R only calls stat(2) on symlinks when it needs to
  - Stop quoting nonprintable characters in the getfacl output
  - Avoid unnecessary but destructive chown calls
  - Clarify license notice
* Fri Feb 13 2009 bphilips@novell.com
- fix setfacl for long utf8 filenames (rh#183181)
  - Return error status on setfacl failures (rh#368451)
  - getfacl/setfacl should support shortcode flags (rh#204087)
* Thu Jan  8 2009 bphilips@novell.com
- Added a number of unit test improvements
* Wed Dec 10 2008 olh@suse.de
- use Obsoletes: -XXbit only for ppc64 to help solver during distupgrade
  (bnc#437293)
* Tue Nov 11 2008 ro@suse.de
- SLE-11 uses PPC64 instead of PPC, adapt baselibs.conf
* Thu Oct 30 2008 olh@suse.de
- obsolete old -XXbit packages (bnc#437293)
* Fri Jul 11 2008 bphilips@suse.de
- Failure to recursively set/get ACLs on directories (bnc#404075)
- When invoked as ``setfacl -- ...'', setfacl segfaults (bnc#369425).
* Thu Apr 10 2008 ro@suse.de
- added baselibs.conf file to build xxbit packages
  for multilib support
* Sat Oct 27 2007 agruen@suse.de
- Don't exhaust the number of file descriptors in the path walking
  code, and make sure each directory is only visited once.
* Fri Oct 26 2007 agruen@suse.de
- A large jump to the current upstream version 2.2.45.
- Fix the upstream path walking code.
* Sat Mar 18 2006 agruen@suse.de
- Remove broken file /usr/lib[64]/libacl.la.
* Fri Mar 17 2006 agruen@suse.de
- Fix symlinks in the -devel package (149945, Nathan Scott).
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Fri Jan 13 2006 mjancar@suse.cz
- update to 2.2.34
* Tue Sep  6 2005 coolo@suse.de
- Fixing devel dependencies (the libtool check chokes on the symlinks,
  but it still is right)
* Fri Aug 26 2005 agruen@suse.de
- Update to version 2.2.31: Integrate a patch we had separately;
  additional stdin error handling in setfacl.
* Fri Aug 19 2005 kukuk@suse.de
- Move devel files from / to /usr
- Don't generate filelist dynamic (fix broken attr statements)
* Mon Apr 25 2005 meissner@suse.de
- Use RPM_OPT_FLAGS.
* Mon Feb 21 2005 agruen@suse.de
- Update to version 2.2.30. Several fixes.
* Thu Nov 11 2004 coolo@suse.de
- use %%find_lang
* Wed Aug 25 2004 agruen@suse.de
- #43472: Fix processing of the X pseudo permission in setfacl:
  Must not modify the sequence of commands directly or else only
  the first file is processed correctly, and X is not evaluated
  for any other file. Add test case for X pseudo permission.
- Remove support for relative permission changes; this
  non-standard feature was disabled since a while already.
- Bump version number to 2.2.25.
* Sun Jan 11 2004 adrian@suse.de
- build as user
* Thu Jan  1 2004 agruen@suse.de
- Update to version 2.2.21. Bug fix in directory tree walking
  code.
* Wed Oct 22 2003 kukuk@suse.de
- Fix provides for update case
* Thu Aug 28 2003 agruen@suse.de
- Fix a bug with error handling while walking directory trees.
* Wed Aug 27 2003 ro@suse.de
- fix patch depth in specfile
* Tue Aug 26 2003 agruen@suse.de
- Fix SIGSEGV if the quote function.
* Fri Aug 15 2003 agruen@suse.de
- Update to 2.2.15: Includes quoting of special characters in
  path and user names, and several minor fixes. (For details see
  doc/CHANGES in the tarball).
* Mon Jun 16 2003 ja@suse.cz
- File list fixed.
* Sun Apr  6 2003 agruen@suse.de
- Update to 2.2.7.
* Wed Feb 26 2003 agruen@suse.de
- Update to acl-2.2.3a, which has all our patches plus an
  additional malloc bug fix.
* Mon Feb 24 2003 agruen@suse.de
- Increment libattr library version to 1.1.0.
- Add symbol level versioning for libacl.
* Sat Feb  8 2003 agruen@suse.de
- Fix a long standing bug in acl_get_file() for Default ACLs (that
  probably was there from hour one), and another critical bug in
  the libacl entry pre-allocation patch (introduced on Jan 22).
* Tue Jan 28 2003 agruen@suse.de
- Fix inconsistent declarations for visibility("hidden") attributes
  ("config.h" was not always included).
- Fix a signedness warning in getfacl/user_group.c with a type
  cast.
* Wed Jan 22 2003 agruen@suse.de
- Update to acl-2.2.2
- Fix a memory leak in acl_init()
- Add memory pre-allocation support patch for libacl
- Add ACL copying functions patch
- Add visibility(hidden) patch that hides libacl internal functions
  from the outside.
- Let mls@suse.de add the following package alias in Autobuild
  for building packages against older releases:
  libacl-devel -> acl-devel [for <= 8.1]
* Tue Jan 21 2003 agruen@suse.de
- Remove (Prereq: /sbin/ldconfig) tag, and use %%run_ldconfig
  in %%post and %%postun instead.
- acl-devel was renamed to libacl-devel: add missing
  `Obsoletes: acl-devel' tag to libacl-devel.
* Sun Jan 19 2003 agruen@suse.de
- Fix a typo and add a clarification in the acl.5 manual page.
* Fri Dec 13 2002 schwab@suse.de
- Fix filelist generation.
* Fri Dec 13 2002 jderfina@suse.cz
- upgrading to version 2.1.1
- spliting acl to acl (binaries), libacl (libraries) and libacl-devel
  (development stuff). This spliting follows SGI's release.
* Thu Sep  5 2002 agruen@suse.de
- Update to 2.0.19 + additional corrections (see
  acl-2.0.19/doc/CHANGES).
* Thu Aug 15 2002 agruen@suse.de
- Remove the suse_update_config macro and the config.* stuff.
  (According to ro@suse.de this is not necessary.)
- Change the documentation path in builddefs.in instead of in
  configure.in.
- Update to version 2.0.17
* Thu Jun 20 2002 uli@suse.de
- fixed for lib64
* Thu Jun 20 2002 lmuelle@suse.de
- Remove DESTDIR patch, use DIST_ROOT of package instead
- Fix library location in the devel package
- Update to version 2.0.11
* Tue May  7 2002 sf@suse.de
- moved libs to %%{_lib} (they were in /lib _and_ /usr/lib before)
* Mon Feb 25 2002 ro@suse.de
- initial package (v2.0.0) (split from xfsprogs spec)
