#
# spec file for package attr
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


%define lname	libattr1
Name:           attr
Version:        2.5.1
Release:        1.21
Summary:        Commands for Manipulating Extended Attributes
License:        GPL-2.0-or-later AND LGPL-2.1-or-later
Group:          System/Filesystems
URL:            https://savannah.nongnu.org/projects/attr/
Source:         https://download-mirror.savannah.gnu.org/releases/attr/attr-%{version}.tar.gz
Source2:        https://download-mirror.savannah.gnu.org/releases/attr/attr-%{version}.tar.gz.sig
Source3:        %{name}.keyring
Source99:       baselibs.conf
#BuildRequires:  pkgconfig
Conflicts:      xfsdump < 2.0.0

%description
A set of tools for manipulating extended attributes on file system
objects, in particular getfattr(1) and setfattr(1). An attr(1) command
is also provided, which is largely compatible with the SGI IRIX tool of
the same name.

%package -n %{lname}
Summary:        A dynamic library for filesystem extended attribute support
Group:          System/Libraries
Obsoletes:      libattr < %{version}-%{release}
Provides:       libattr = %{version}-%{release}

%description -n %{lname}
This package contains the libattr.so dynamic library, which contains
the extended attribute library functions.

%package -n libattr-devel
Summary:        Header files for libattr
Group:          Development/Libraries/C and C++
Requires:       %{lname} = %{version}
Requires:       glibc-devel
Provides:       attr-devel = %{version}-%{release}
Obsoletes:      attr-devel < %{version}-%{release}

%description -n libattr-devel
This package contains the libraries and header files needed to develop
programs which make use of extended attributes. For Linux programs, the
documented system call API is the recommended interface, but an SGI
IRIX compatibility interface is also provided.

%package -n libattr-devel-static
Summary:        Static libraries for libattr development
Group:          Development/Libraries/C and C++
Provides:       libattr-devel:%{_libdir}/libattr.a
Requires:       libattr-devel = %version

%description -n libattr-devel-static
This package contains the static library of libattr which is needed for
staticallly linking to programs that make use of extended attributes.

%prep
%setup -q

%build
%global _lto_cflags %{_lto_cflags} -ffat-lto-objects
%configure \
    --enable-static \
    --disable-silent-rules
make %{?_smp_mflags}

%install
%make_install
# remove libtool archives
find %{buildroot} -type f -name "*.la" -delete -print
# handle docs on our own
rm -rf %{buildroot}/%{_datadir}/doc/%{name}
%find_lang %{name}

%check
make %{?_smp_mflags} check

%post -n %{lname} -p /sbin/ldconfig
%postun -n %{lname} -p /sbin/ldconfig

%files -f %{name}.lang
%license doc/COPYING*
%doc doc/CHANGES doc/PORTING
%{_mandir}/man1/attr.1
%{_mandir}/man1/getfattr.1
%{_mandir}/man1/setfattr.1
%{_bindir}/attr
%{_bindir}/getfattr
%{_bindir}/setfattr

%files -n libattr-devel
%{_includedir}/attr/
%{_libdir}/pkgconfig/libattr.pc
%{_libdir}/libattr.so
%{_mandir}/man3/attr_get.3
%{_mandir}/man3/attr_getf.3
%{_mandir}/man3/attr_list.3
%{_mandir}/man3/attr_listf.3
%{_mandir}/man3/attr_multi.3
%{_mandir}/man3/attr_multif.3
%{_mandir}/man3/attr_remove.3
%{_mandir}/man3/attr_removef.3
%{_mandir}/man3/attr_set.3
%{_mandir}/man3/attr_setf.3

%files -n libattr-devel-static
%defattr(-,root,root)
%{_libdir}/libattr.a

%files -n %{lname}
%license doc/COPYING*
%{_libdir}/libattr.so.1
%{_libdir}/libattr.so.1.1.2501
%config %{_sysconfdir}/xattr.conf

%changelog
* Mon Mar 22 2021 Dirk Müller <dmueller@suse.com>
- update to 2.5.1:
  * Fix libtool library versioning regression
  * Update po files and German translation
  * getfattr: Add --one-file-system option
  * Move struct stat into struct walk_tree_args
  * Move list of open directories into struct walk_tree_args
  * Move walk_tree_rec arguments into a separate struct
  * xattr.conf: Indicate afs metadata xattrs should be skipped when copying
  * Fix typos in manual pages
  * getfattr.1: by default only user namespace attributes are dumped
  * Enable large-file support on systems that do not enable it by default
  * test: escape left brace in a regex in test/run
- drop 0001-attr-2.4.48-test-suite-perl.patch (upstream)
* Fri Aug  2 2019 Martin Liška <mliska@suse.cz>
- Use FAT LTO objects in order to provide proper static library.
* Tue Sep 11 2018 dmueller@suse.com
- update description for libattr-devel-static to make it less
  boilerplate
* Wed Sep  5 2018 schwab@suse.de
- Add libattr-devel-static subpackage
* Sat Aug 25 2018 jengelh@inai.de
- Replace unspecific boilerplate summary from years ago.
* Mon Aug 13 2018 tchvatal@suse.com
- Remove obsolete Obsolete lines
- Drop static subpackage, nothing in TW depends on it Deb/RH do not
  provide it either
- Rely on simple upstream make install target
- Run tests
- Update to 2.4.48:
  * Provide default xattr.conf
  * Update buildsystem to reflect current autotools state
  * Small test updates
  * Remove various deprecated sections like attr/attr.h
- Update keyring, Mike Frysinger released this version
- Add patch to have tests working with newer perls:
  * 0001-attr-2.4.48-test-suite-perl.patch
* Tue Mar 20 2018 kukuk@suse.de
- Use %%license instead of %%doc [bsc#1082318]
* Mon May 11 2015 pgajdos@suse.com
- remove man5/attr.5, it is now part of man-pages
  http://lwn.net/Articles/643559/
* Tue Sep 23 2014 jengelh@inai.de
- Reduce size of filelist by using wildcards;
  remove %%doc (some locations are always %%doc),
  remove %%attr (files already have proper permissions)
* Tue Jun 18 2013 coolo@suse.com
- remove gpg-offline from bootstrap packages
* Sun Jun 16 2013 jengelh@inai.de
- Update to new upstream release 2.4.47
  * This release fixes two functional bugs related to tree walking
  and the return code from getfattr. Also, a number of build system
  problems were fixed.
- Remove config-guess-sub-update.patch (no longer applies),
  attr-syscalls.patch (resolved differently upstream),
  builddefs.in.diff (replaced by logic in specfile)
- Signature verification
* Wed Mar 20 2013 mmeister@suse.com
- Added url as source.
  Please see http://en.opensuse.org/SourceUrls
* Tue Feb  5 2013 schwab@suse.de
- Remove unused autoconf and automake build requires
* Sat Feb  2 2013 schwab@suse.de
- Add attr-syscalls.patch:
  Define attr syscall numbers for aarch64
* Sat Feb  2 2013 schwab@suse.de
- Add config-guess-sub-update.patch:
  Update confg.guess/sub for aarch64
* Fri Feb  1 2013 coolo@suse.com
- update license to new format
* Tue Dec 20 2011 coolo@suse.com
- add autoconf as buildrequire to avoid implicit dependency
* Fri Oct 14 2011 afaerber@suse.com
- Add libattr-devel-static package
* Fri Sep 16 2011 jengelh@medozas.de
- Enable libattr-devel for all baselib arches
- Implement shlib package (libattr1)
* Wed May 18 2011 coolo@novell.com
- make shared library executable
* Tue Apr 19 2011 bphilips@novell.com
- upgrade to 2.4.46
  - Fix tests
* Sat Apr 16 2011 bphilips@novell.com
- upgrade to 2.4.45
  - OPTIONS in man pages should be a section heading, not a subsection heading
  - getfattr: encode NULs properly with --encoding=text
  - setfattr.1: document supported encodings of values
  - convert the man pages into html
  - attr_parse_attr_conf: eliminate a double free
  - attr_parse_attr_conf: eliminate a memory leak
  - quote: pull in string.h for strchr prototype
  - libattr: fix memory leak in attr_copy_action()
* Mon Jun 28 2010 jengelh@medozas.de
- use %%_smp_mflags
* Sat Dec 12 2009 jengelh@medozas.de
- add baselibs.conf as a source
- adjust baselibs.conf for SPARC
* Mon Oct 26 2009 meissner@suse.de
- fixed implicit strchr() call
* Sun Sep 27 2009 crrodriguez@suse.de
- do not package static libraries
- fix -devel package dependencies
* Sat Aug  1 2009 bphilips@novell.com
- Version bump to 2.4.44
  - Stop quoting nonprintable characters in the getfattr output
  - More license updates
* Fri Feb 13 2009 bphilips@suse.de
- Improve unit test harness
* Tue Jan  6 2009 bphilips@suse.de
- Fix tests and add make target
- Version bump to get fix for getfattr -P bnc#457660
* Wed Dec 10 2008 olh@suse.de
- use Obsoletes: -XXbit only for ppc64 to help solver during distupgrade
  (bnc#437293)
* Tue Nov 11 2008 ro@suse.de
- SLE-11 uses PPC64 instead of PPC, adapt baselibs.conf
* Thu Oct 30 2008 olh@suse.de
- obsolete old -XXbit packages (bnc#437293)
* Thu Apr 10 2008 ro@suse.de
- added baselibs.conf file to build xxbit packages
  for multilib support
* Sat Oct 27 2007 agruen@suse.de
- Don't exhaust the number of file descriptors in the path walking
  code, and make sure each directory is only visited once.
* Fri Oct 26 2007 agruen@suse.de
- A large jump to the current upstream version 2.4.39.
- Fix the upstream path walking code.
- Remove the ea-conv script; this is not relevant anymore since
  years.
* Wed Apr 25 2007 agruen@suse.de
- Fix the permissions of /etc/xattr.conf.
* Mon Oct 16 2006 agruen@suse.de
- Ignore Beagle index data when copying files.
* Wed Oct  4 2006 agruen@suse.de
- /etc/xattr.conf: Allow to configure which attributes to skip
  when copying, and which attributes contain file permissions.
* Sat Mar 18 2006 aj@suse.de
- Remove .la package that was introduced in last change and breaks
  build of many packages.
* Fri Mar 17 2006 agruen@suse.de
- Fix symlinks in the -devel package (149945, Nathan Scott).
* Tue Mar  7 2006 agruen@suse.de
- xfs-cmds-25263a-fix-list_attr-segfault: Fix a possible segfault
  in the attr_list compat function (155746).
* Sat Feb 18 2006 agruen@suse.de
- Add xfs-cmds-25211a-skip-DMF-attributes-on-copy-also patch from
  SGI (151782).
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Fri Jan 13 2006 mjancar@suse.cz
- update to 2.4.28
  * Implement the IRIX list_attr interfaces
* Wed Nov  2 2005 schwab@suse.de
- Use RPM_OPT_FLAGS.
* Fri Aug 26 2005 agruen@suse.de
- Update to version 2.4.24: integrates two patches we had
  separately before; add a missing space in an error message;
  an error path fix in setfattr. No API/ABI changes in libattr.
* Fri Aug 19 2005 kukuk@suse.de
- Move devel files from / to /usr
- Don't generate filelist dynamic (fix broken attr statements)
* Mon Jun  6 2005 agruen@suse.de
- Bump version number to 2.4.23.
* Thu Jun  2 2005 agruen@suse.de
- reduce-verboseness.diff: attr_copy_{fd,file}: Don't report an
  error for each attribute copy that fails with ENOSYS, but report
  such failures only once (85646).
* Mon Feb 21 2005 agruen@suse.de
- Update to version 2.4.22. Various fixes.
* Fri Aug 13 2004 mjancar@suse.cz
- update to 2.4.16
* Tue Jan 27 2004 kukuk@suse.de
- Don't include man2/*xattr.2 manual pages, use the copy from
  the man-pages package (so we have documentation for the glibc
  functions, too).
* Sat Jan 10 2004 adrian@suse.de
- build as user
* Thu Jan  1 2004 agruen@suse.de
- Update to version 2.4.12. Bug fix in directory tree walking
  code.
* Wed Oct 22 2003 kukuk@suse.de
- Fix provides/requires for update case
* Thu Aug 28 2003 agruen@suse.de
- Fix a bug with error handling while walking directory trees.
* Wed Aug 27 2003 ro@suse.de
- fix patch-depth in specfile
* Tue Aug 26 2003 agruen@suse.de
- Fix SIGSEGV if the quote function.
* Fri Aug 15 2003 agruen@suse.de
- Update to 2.4.8: Fixes SIGSEGV if the quote/unquote functions
  are passed NULL arguments.
* Sat Jul 26 2003 agruen@suse.de
- Update to 2.4.6 + additional patch to be merged upstream.
* Mon Jun 16 2003 jderfina@suse.cz
- File list fixed.
* Wed Apr 16 2003 jderfina@suse.cz
- Update to 2.4.2
* Sun Apr  6 2003 agruen@suse.de
- Update to 2.4.1.
* Thu Feb 27 2003 agruen@suse.de
- Fix broken attr_copy_check_permissions() function.
* Wed Feb 26 2003 agruen@suse.de
- Update to attr-2.4.0 which has our patches integrated.
* Mon Feb 24 2003 agruen@suse.de
- Increment libattr library version to 1.1.0.
- Fix [#24244] (prevent accidental acl copying on xfs).
- Add symbol level versioning for libattr.
* Thu Feb 13 2003 agruen@suse.de
- Fix an interface declaration in in the error_context.h header.
* Wed Jan 22 2003 agruen@suse.de
- Update to attr-2.2.0
- Add EA copying functions patch
- Let mls@suse.de add the following package alias in Autobuild
  for building packages against older releases:
  libattr-devel -> attr-devel [for <= 8.1]
* Tue Jan 21 2003 agruen@suse.de
- Remove (Prereq: /sbin/ldconfig) tag, and use %%run_ldconfig
  in %%post and %%postun instead.
- attr-devel was renamed to libattr-devel: add missing
  `Obsoletes: attr-devel' tag to libattr-devel.
* Fri Dec 13 2002 schwab@suse.de
- Fix filelist generation.
* Thu Dec 12 2002 jderfina@suse.cz
- upgrading to version 2.1.1
- spliting attr to attr (binaries), libattr (libraries, only this package is
  needed for other packages) and libattr-devel (development stuff). This
  spliting follows SGI's release.
* Thu Sep  5 2002 agruen@suse.de
- Update to version 2.0.11: Adds support for m68k and alpha, minor
  corrections (see attr-2.0.11/doc/CHANGES for details).
* Thu Aug 15 2002 agruen@suse.de
- Remove the suse_update_config macro and the config.* stuff.
  (According to ro@suse.de this is not necessary.)
- Change the documentation path in builddefs.in instead of in
  configure.in.
- Update to version 2.0.9
* Thu Jun 20 2002 lmuelle@suse.de
- Remove DESTDIR patch, use DIST_ROOT of package instead
- Update to version 2.0.8
* Wed Jun 12 2002 ro@suse.de
- fix for ppc64 (it's called powerpc64 in configure)
* Tue May 21 2002 coolo@suse.de
- build also on archs without xattr syscalls
* Mon May 13 2002 sf@suse.de
- changed configure.in to use */lib64 as pkg_slib_dir and
  pkg_lib_dir on architectures with lib and lib64
* Wed Apr 24 2002 mls@suse.de
- support for mips architecture
* Mon Feb 25 2002 ro@suse.de
- initial package (split from xfstools spec)
