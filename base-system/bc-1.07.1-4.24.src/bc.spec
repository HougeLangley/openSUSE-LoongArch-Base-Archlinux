#
# spec file for package bc
#
# Copyright (c) 2020 SUSE LLC
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


Name:           bc
Version:        1.07.1
Release:        4.24
Summary:        GNU Command Line Calculator
License:        GPL-2.0-or-later
Group:          Productivity/Scientific/Math
URL:            https://www.gnu.org/software/bc/
Source0:        https://ftp.gnu.org/gnu/bc/bc-%{version}.tar.gz
Source1:        https://ftp.gnu.org/gnu/bc/bc-%{version}.tar.gz.sig
Source2:        %{name}.keyring
# Correct return value after 'q' [bsc#1129038]
Patch2:         bc-dc-correct-return-value.patch
#BuildRequires:  bison
#BuildRequires:  ed
#BuildRequires:  flex
#BuildRequires:  makeinfo
#BuildRequires:  ncurses-devel
#BuildRequires:  readline-devel
#Requires(post): %{install_info_prereq}
#Requires(preun): %{install_info_prereq}

%description
bc is an interpreter that supports numbers of arbitrary precision and
the interactive execution of statements. The syntax has some
similarities to the C programming language. A standard math library is
available through command line options. When used, the math library is
read in before any other input files. bc then reads in all other files
from the command line, evaluating their contents. Then bc reads from
standard input (usually the keyboard).

The dc program is also included. dc is a calculator that supports
reverse-polish notation and allows unlimited precision arithmetic.
Macros can also be defined. Normally, dc reads from standard input but
can also read in files specified on the command line. A calculator with
reverse-polish notation saves numbers to a stack. Arguments to
mathematical operations (operands) are "pushed" onto the stack until
the next operator is read in, which "pops" its arguments off the stack
and "pushes" its results back onto the stack.

%prep
%setup -q
%patch2 -p1

%build
%configure \
  --with-readline \
  --without-libedit
make %{?_smp_mflags}

%install
%make_install

%post
%install_info --info-dir=%{_infodir} %{_infodir}/bc.info%{ext_info}
%install_info --info-dir=%{_infodir} %{_infodir}/dc.info%{ext_info}

%preun
%install_info_delete --info-dir=%{_infodir} %{_infodir}/bc.info%{ext_info}
%install_info_delete --info-dir=%{_infodir} %{_infodir}/dc.info%{ext_info}

%files
%defattr(-,root,root)
%license COPYING.LIB COPYING
%doc NEWS README FAQ
%{_bindir}/bc
%{_bindir}/dc
%{_infodir}/bc.info
%{_infodir}/dc.info
%{_infodir}/dir
%{_mandir}/man1/bc.1
%{_mandir}/man1/dc.1

%changelog
* Thu Oct 15 2020 pgajdos@suse.com
- fix [bsc#1177579] -- wrong clamping of hexadecimal digits in dc
- deleted patches
  - bc-1.06-dc_ibase.patch (upstreamed)
* Wed Aug 28 2019 kukuk@suse.de
- Use %%license instead of %%doc [bsc#1082318]
- Cleanup %%doc section
* Wed Mar 13 2019 pgajdos@suse.com
- added patches
  Correct return value after 'q' [bsc#1129038]
  + bc-dc-correct-return-value.patch
* Mon Apr 10 2017 mpluskal@suse.com
- Update to version 1.07.1:
  * Fixed ibase extension causing problems for read()
  * Fixed parallel make problem.
  * Fixed dc "Q" comanmd bug.
- Changes for version 1.07:
  * Added void functions.
  * fixes bug in load_code introduced by mathlib string storage in 1.06.
  * fix to get long options working.
  * signal code clean-up.
  * fixed a bug in the AVL tree routines.
  * fixed math library to work properly when called with ibase not 10.
  * fixed a symbol table bug when using more than 32 names.
  * removed a double free.
  * Added base 17 to 36 for ibase.
  * Fixed some memory leaks.
  * Various small tweaks and doc bug fixes.
- Drop no longer needed patches:
  * bc-1.06.95-memleak.patch
  * bc-1.06.95-matlib.patch
  * bc-1.06.95-sigintmasking.patch
- Refresh bc-1.06-dc_ibase.patch
- Add gpg signature
* Mon Mar 16 2015 mpluskal@suse.com
- Update url
- Correct info files scriplets and dependencies
* Fri Nov 28 2014 tchvatal@suse.com
- Clean up with spec-cleaner
- Add ncurses-devel as it is inherited from readline
- Explicitely pass without-libedit if we decide to switch for
  it at some point
* Mon Sep 17 2012 idonmez@suse.com
- Add BuildRequires on makeinfo to fix Factory build
* Thu May 31 2012 sweet_f_a@gmx.de
- update to upstream alpha 1.06.95 (2006-09-05), in use in other
  major distros for quite a long time (Debian, Fedora, Ubuntu, ...)
- add patches from Fedora
- automake dependency removed
* Wed Nov 30 2011 coolo@suse.com
- add automake as buildrequire to avoid implicit dependency
* Thu Dec 27 2007 schwab@suse.de
- Fix last change.
- Fix detection of empty opt_expression in the parser.
* Tue Jun 12 2007 pgajdos@suse.cz
- repared acceptance of some long commandline options
  [#282747]
* Thu Mar 29 2007 rguenther@suse.de
- add flex BuildRequires
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Mon Sep 19 2005 mmj@suse.de
- fix strict aliasing issues
* Thu Jul  7 2005 mmj@suse.de
- add missing decls
* Mon Aug 30 2004 postadal@suse.cz
- fixed for new flex
* Sun Jan 11 2004 adrian@suse.de
- build as user
* Tue Jul 22 2003 schwab@suse.de
- Fix unbalanced identifier tree.
* Thu Apr 24 2003 ro@suse.de
- fix install_info --delete call and move from preun to postun
* Thu Feb  6 2003 kukuk@suse.de
- Use install-info macros
- Fix bc.info (add dir entry)
* Wed Nov 20 2002 postadal@suse.cz
- returned the recompilation of libmath.h and fixed the problematic
  part which caused segmentation fault on 64bit archs [#21697]
* Mon Oct  7 2002 postadal@suse.cz
- removed recompilation of libmath.h [#20241]
* Wed Aug  7 2002 uli@suse.de
- build with -O0 on x86-64 (bug #17231)
* Thu Apr 12 2001 cihlar@suse.cz
- fixed to compile
* Thu Feb 22 2001 ro@suse.de
- added readline/readline-devel to neededforbuild (split from bash)
* Tue Dec  5 2000 cihlar@suse.cz
- added ed to neededforbuild
- fixed to recompile libmath.h
* Mon Oct 30 2000 cihlar@suse.cz
- update to version 1.6
- added BuildRoot
- bzipped sources
* Tue Sep 26 2000 schwab@suse.de
- Fix overflow bug in bc scanner.
* Fri Mar 10 2000 kasal@suse.de
- specfile cleanup
* Fri Feb 25 2000 kukuk@suse.de
- Use _infodir/_mandir, add group tag
* Thu Nov 25 1999 kukuk@suse.de
- Remove termcap from needforbuild
* Fri Nov 12 1999 kukuk@suse.de
- Fix Include paths
* Mon Sep 13 1999 bs@suse.de
- ran old prepare_spec on spec file to switch to new prepare_spec.
* Fri Aug 27 1999 fehr@suse.de
- chaged to new version 1.05a
* Wed Jul 21 1999 garloff@suse.de
- added -d to YFLAGS to prevent problem when bison changes
* Tue Sep 22 1998 ro@suse.de
- dont try to include posix_lim2.h for glibc
* Fri Dec 12 1997 florian@suse.de
- add many bug-fixes from gnu.utils.bug
* Fri Oct 10 1997 florian@suse.de
- update to 1.04 and fix rpm spec file
* Thu Jan  2 1997 florian@suse.de
- add some bug-fixes
