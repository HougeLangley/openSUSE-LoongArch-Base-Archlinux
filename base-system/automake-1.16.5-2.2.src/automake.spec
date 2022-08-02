#
# spec file
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


# remove bogus Automake perl dependencies and provides
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}^perl\\(Automake::
%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}^perl\\(Automake::
%define flavor %{nil}
%if "%{flavor}" == "testsuite"
%define nsuffix -testsuite
%else
%define nsuffix %{nil}
%endif
Name:           automake%{nsuffix}
Version:        1.16.5
Release:        2.2
Summary:        A Program for Automatically Generating GNU-Style Makefile.in Files
# docs ~> GFDL, sources ~> GPLv2+, mkinstalldirs ~> PD and install-sh ~> MIT
License:        GFDL-1.3-or-later AND GPL-2.0-or-later AND SUSE-Public-Domain AND MIT
Group:          Development/Tools/Building
URL:            https://www.gnu.org/software/automake
Source0:        https://ftp.gnu.org/gnu/automake/automake-%{version}.tar.xz
Source1:        https://ftp.gnu.org/gnu/automake/automake-%{version}.tar.xz.sig
# taken from https://savannah.gnu.org/project/release-gpgkeys.php?group=automake&download=1
Source2:        automake.keyring
Source3:        automake-rpmlintrc
Patch2:         automake-require_file.patch
Patch3:         automake-1.13.4-fix-primary-prefix-invalid-couples-test.patch
Patch5:         0001-correct-parameter-parsing-in-test-driver-script.patch
Patch100:       automake-suse-vendor.patch
#BuildRequires:  autoconf >= 2.69
#BuildRequires:  bison
#BuildRequires:  gcc-c++
#BuildRequires:  gcc-fortran
#BuildRequires:  xz
#BuildRequires:  perl(Thread::Queue)
#BuildRequires:  perl(threads)
#Requires:       autoconf >= 2.69
#Requires:       perl
#Requires(post): info
#Requires(preun):info
#BuildArch:      noarch
#%if "%{flavor}" == "testsuite"
#BuildRequires:  cscope
#BuildRequires:  dejagnu
#BuildRequires:  etags
#BuildRequires:  expect
#BuildRequires:  flex
#BuildRequires:  gettext-tools
#BuildRequires:  libtool
#BuildRequires:  makedepend
#BuildRequires:  makeinfo
#BuildRequires:  pkgconfig
#BuildRequires:  python
#BuildRequires:  sharutils
#BuildRequires:  zip
#Requires:       expect
#Requires:       flex
#Requires:       libtool
#%if 0%{?suse_version} >= 1500
#BuildRequires:  vala
#BuildRequires:  pkgconfig(gobject-2.0)
#%endif
#%endif

%description
Automake is a tool for automatically generating "Makefile.in" files
from "Makefile.am" files.  "Makefile.am" is a series of "make" macro
definitions (with rules occasionally thrown in).  The generated
"Makefile.in" files are compatible with the GNU Makefile standards.

%prep
%setup -q -n automake-%{version}
%autopatch -p1

%build
sh bootstrap
%configure --docdir=%{_docdir}/%{name}
%make_build #%-j32

%if "%{flavor}" == "testsuite"
%check
# Some architectures can't keep up the pace.
%ifnarch alpha %{arm}
%make_build check
%endif

%install
%else

%install
%make_install
#mkdir %{buildroot}%{_sysconfdir}
#echo %{_prefix}/local/share/aclocal >%{buildroot}%{_sysconfdir}/aclocal_dirlist
#ln -s %{_sysconfdir}/aclocal_dirlist %{buildroot}%{_datadir}/aclocal/dirlist
install -m644 AUTHORS ChangeLog NEWS README THANKS %{buildroot}%{_docdir}/%{name}
# info's dir file is not auto ignored on some systems
rm -rf %{buildroot}%{_infodir}/dir
#name == automake
%endif

%post
%install_info --info-dir=%{_infodir} %{_infodir}/automake.info%{ext_info}

%preun
%install_info_delete --info-dir=%{_infodir} %{_infodir}/automake.info%{ext_info}

%if "%{flavor}" == ""
%files
%license COPYING
%doc %{_docdir}/%{name}
%{_bindir}/aclocal
%{_bindir}/aclocal-1.16
%{_bindir}/automake
%{_bindir}/automake-1.16
%{_infodir}/automake-history.info
%{_infodir}/automake.info
%{_infodir}/automake.info-1
%{_infodir}/automake.info-2
%{_mandir}/man1/aclocal.1
%{_mandir}/man1/aclocal-1.16.1
%{_mandir}/man1/automake.1
%{_mandir}/man1/automake-1.16.1
%{_datadir}/aclocal
%{_datadir}/aclocal-1.16
%{_datadir}/automake-1.16
%config %{_sysconfdir}/aclocal_dirlist
%endif

%changelog
* Tue May 24 2022 Dirk Müller <dmueller@suse.com>
- update automake.keyring: use release-team keyring
- don't reference source URL when the linked sources change over time
* Sat Oct 16 2021 Dirk Müller <dmueller@suse.com>
- update to 1.16.5:
  - PYTHON_PREFIX and PYTHON_EXEC_PREFIX are now set according to
    Python's sys.* values only if the new configure option
  - -with-python-sys-prefix is specified. Otherwise, GNU default values
    are used, as in the past. (The change in 1.16.3 was too incompatible.)
  - consistently depend on install-libLTLIBRARIES.
  - use const for yyerror declaration in bison/yacc tests.
  - Common top-level files can be provided as .md; the non-md version is
    used if both are present:
    AUTHORS ChangeLog INSTALL NEWS README README-alpha THANKS
  - CTAGS, ETAGS, SCOPE variables can be set via configure.
  - Silent make output for custom link commands.
  - New option "no-dist-built-sources" skips generating $(BUILT_SOURCES)
    before building the tarball as part of "make dist", that is,
    omits the dependency of $(distdir): $(BUILT_SOURCES).
  - automake output more reproducible.
  - test-driver less likely to clash with tests writing to the same file.
  - DejaGnu tests always use the directory name, testsuite/, for
    compatibility with the newer dejagnu-1.6.3 and with prior versions.
  - config.sub and config.guess updates include restoration of `...`
    for maximum portability.
- refresh automake-suse-vendor.patch
- drop fix-testsuite-failures-with-autoconf270.patch (upstream)
- drop automake-reproducible.patch (upstream)
* Fri Mar 12 2021 Dirk Müller <dmueller@suse.com>
- move license to licensedir
* Tue Feb 23 2021 Dirk Müller <dmueller@suse.com>
- make generated autoconf makefiles reproducible (bsc#1182604):
  add automake-reproducible.patch
* Sun Jan 17 2021 Dirk Müller <dmueller@suse.com>
- add fix-testsuite-failures-with-autoconf270.patch to fix compatibility
  with autoconf 2.70
* Tue Dec 29 2020 Dirk Müller <dmueller@suse.com>
- update to 1.16.3:
  - In the testsuite summary, the "for $(PACKAGE_STRING)" suffix
    can be overridden with the AM_TESTSUITE_SUMMARY_HEADER variable.
  - Python 3.10 version number no longer considered to be 3.1.
  - Broken links in manual fixed or removed, and new script
    contrib/checklinkx (a small modification of W3C checklink) added,
    with accompany target checklinkx to recheck urls.
  - install-exec target depends on $(BUILT_SOURCES).
  - valac argument matching more precise, to avoid garbage in DIST_COMMON.
  - Support for Vala in VPATH builds fixed so that both freshly-generated and
    distributed C files work, and operation is more reliable with or without
    an installed valac.
  - Dejagnu doesn't break on directories containing spaces.
  - new variable AM_DISTCHECK_DVI_TARGET, to allow overriding the
    "make dvi" that is done as part of distcheck.
  - install-sh tweaks:
    . new option -p to preserve mtime, i.e., invoke cp -p.
    . new option -S SUFFIX to attempt backup files using SUFFIX.
    . no longer unconditionally uses -f when rm is overridden by RMPROG.
    . does not chown existing directories.
  - Removed function up_to_date_p in lib/Automake/FileUtils.pm.
    We believe this function is completely unused.
  - Support for in-tree Vala libraries improved.
- rename automake-SuSE.patch to automake-suse-vendor.patch and refresh
- remove automake-testsuite-vala-gcc10.patch (upstream)
* Fri Jul 17 2020 Callum Farmer <callumjfarmer13@gmail.com>
- Fix name tag for multibuild
* Fri Jul 10 2020 Callum Farmer <callumjfarmer13@gmail.com>
- Add etags to BuildRequires for testsuite
- Add automake-testsuite-vala-gcc10.patch: fixes testsuite
* Sun Jul  5 2020 Callum Farmer <callumjfarmer13@gmail.com>
- Changed automake-SuSE.patch: updated for new version
- Update to 1.16.2. Changes since 1.16.1:
  * New features added
  - add zstd support and the automake option, dist-zstd.
  - support for Python 3: py-compile now supports both Python 3
    and Python 2; tests do not require .pyo files, and uninstall
    deletes __pycache__ correctly (automake bug #32088).
  * Miscellaneous changes
  - automake no longer requires a @setfilename in each .texi file
  * Bugs fixed
  - When cleaning the compiled python files, '\n' is not used anymore in the
    substitution text of 'sed' transformations.  This is done to preserve
    compatibility with the 'sed' implementation provided by macOS which
    considers '\n' as the 'n' character instead of a newline.
    (automake bug#31222)
  - For make tags, lisp_LISP is followed by the necessary space when
    used with CONFIG_HEADERS.
    (automake bug#38139)
  - The automake test txinfo-vtexi4.sh no longer fails when localtime
    and UTC cross a day boundary.
  - Emacsen older than version 25, which require use of
    byte-compile-dest-file, are supported again.
* Sun Mar 22 2020 Andreas Stieger <andreas.stieger@gmx.de>
- convert testsuite to singlespec
* Tue Nov 12 2019 Petr Vorel <pvorel@suse.cz>
- Add missing perl dependency (bsc#1156491).
* Tue Mar  5 2019 Dominique Leuenberger <dimstar@opensuse.org>
- Drop info requires: this is not actually true: automake works
  perfectly without the info tool present.
* Tue Jun 19 2018 schwab@suse.de
- Add pkgconfig(gobject-2.0) to BuildRequires for testsuite
* Fri May 18 2018 pth@suse.de
- Remove non-existing compress from BuildRequires.
* Fri May 18 2018 pth@suse.de
- Add gettext-tools, pkg-config. vala dejagnu, makeinfo, python and zip as
  BuildRequires for automake-testsuite to make testsuite complete and
  enable more tests.
* Thu May 10 2018 schwab@suse.de
- automake-SuSE.patch: fix variable syntax
* Wed Mar 21 2018 pth@suse.de
- Update to 1.16.1. Changes since 1.15.1:
  - 'install-sh' now ensures that nobody can cross privilege boundaries by
    pre-creating symlink on the directory inside "/tmp".
  - 'automake' does not depend on the 'none' subroutine of the List::Util
    module anymore to support older Perl version. (automake bug#30631)
  - A regression in AM_PYTHON_PATH causing the rejection of non literal
    minimum version parameter hasn't been fixed. (automake bug#30616)
  * Miscellaneous changes
  - When subdir-objects is in effect, Automake will now construct
    shorter object file names when no programs and libraries name
    clashes are encountered.  This should make the discouraged use of
    'foo_SHORTNAME' unnecessary in many cases.
  * Bugs fixed:
  - Automatic dependency tracking has been fixed to work also when the
    'subdir-object' option is used and some 'foo_SOURCES' definition
    contains unexpanded references to make variables, as in, e.g.:
    a_src = sources/libs/aaa
    b_src = sources/bbb
    foo_SOURCES = $(a_src)/bar.c $(b_src)/baz.c
    With such a setup, the created makefile fragment containing dependency
    tracking information will be correctly placed under the directories
    named 'sources/libs/aaa/.deps' and 'sources/bbb/.deps', rather than
    mistakenly under directories named (literally!) '$(src_a)/.deps' and
    '$(src_b)/.deps' (this was the first part of automake bug#13928).
    Notice that in order to fix this bug we had to slightly change the
    semantics of how config.status bootstraps the makefile fragments
    required for the dependency tracking to work: rather than attempting
    to parse the Makefiles via grep and sed trickeries only, we actually
    invoke 'make' on a slightly preprocessed version of those Makefiles,
    using a private target that is only meant to bootstrap the required
    makefile fragments.
  - The 'subdir-object' option no longer causes object files corresponding
    to source files specified with an explicit '$(srcdir)' component to be
    placed in the source tree rather than in the build tree.
    For example, if Makefile.am contains:
    AUTOMAKE_OPTIONS = subdir-objects
    foo_SOURCES = $(srcdir)/foo.c $(srcdir)/s/bar.c $(top_srcdir)/baz.c
    then "make all" will create 'foo.o' and 's/bar.o' in $(builddir) rather
    than in $(srcdir), and will create 'baz.o' in $(top_builddir) rather
    than in $(top_srcdir).
    This was the second part of automake bug#13928.
  - Installed 'aclocal' m4 macros can now accept installation directories
    containing '@' characters (automake bug#20903)
  - "./configure && make dist" no longer fails when a distributed file depends
    on one from BUILT_SOURCES.
  - When combining AC_LIBOBJ or AC_FUNC_ALLOCA with the
    "--disable-dependency-tracking" configure option in an out of source
    build, the build sub-directory defined by AC_CONFIG_LIBOBJ_DIR is now
    properly created.  (automake bug#27781)
  - The time printed by 'mdate-sh' is now using the UTC time zone to support
    the reproducible build effort.  (automake bug#20314)
  - The elisp byte-compilation rule now uses byte-compile-dest-file-function,
    rather than byte-compile-dest-file, which was obsoleted in 2009. We expect
    that Emacs-26 will continue to support the old function, but will complain
    loudly, and that Emacs-27 will remove support for it altogether.
- Build serially as a missing dependency makes parallel builds fail.
- Update the list of licenses.
* Sun Feb  4 2018 mail@bernhard-voelker.de
- Avoid bashisms in test-driver:
  * 0001-correct-parameter-parsing-in-test-driver-script.patch
  Use test's = operator instead of ==; use '[' instead of '[['.
  This avoids 'make check' failures of distribution tarballs (built on
  openSUSE) on platforms not supporting bashisms, e.g. NetBSD-7.1.
* Fri Oct 20 2017 jayvdb@gmail.com
- Add missing BuildRequires perl(Thread::Queue)
* Tue Jun 20 2017 mpluskal@suse.com
- Update to version 1.15.1:
  * The code has been adapted to remove a warning present since
    Perl 5.22 stating that "Unescaped left brace in regex is
    deprecated". This warning has become an hard error in Perl 5.26
  * The generated Makefiles do not rely on the obsolescent GZIP
    environment variable which was used for passing arguments to
    'gzip'.  Compatibility with old versions has been preserved.
  * Miscellaneous changes:
- Drop no longer needed patches:
  * automake-perl-5.22.patch
  * automake-fix-tests-gzip.patch
- Add keyring
- Small spec file cleanup
* Fri Feb 10 2017 bg@suse.com
- use vendor suse instead of IBM on s390x
* Sun Jun 26 2016 mpluskal@suse.com
- Fix tests with gzip-1.7 and later:
  * automake-fix-tests-gzip.patch
* Tue Jun 14 2016 Thomas.Blume@suse.com
- add 0001-correct-parameter-parsing-in-test-driver-script.patch
  make parameter parsing of test driver script matching the help
  text
* Tue Sep  1 2015 dimstar@opensuse.org
- Add automake-perl-5.22.patch: Fix test suite with perl 5.22 by
  silencing some warnings.
* Sun May 17 2015 meissner@suse.com
- move delete of info file to preun section
* Tue Feb 10 2015 pth@suse.de
- Update to 1.15:
  New in 1.15:
  * Improvements and refactorings in the install-sh script:
  - It has been modernized, and now makes the following assumptions
  * unconditionally*:
    (1) a working 'dirname' program is available;
    (2) the ${var:-value} shell parameters substitution works;
    (3) the "set -f" and "set +f" shell commands work, and, respectively,
    disable and enable shell globbing.
  - The script implements stricter error checking, and now it complains
    and bails out if any of the following expectations is not met:
    (1) the options -d and -t are never used together;
    (2) the argument passed to option -t is a directory;
    (3) if there are two or more SOURCEFILE arguments, the
    DESTINATION argument must be a directory.
  * Automake-generated testsuites:
  - The default test-driver used by the Automake-generates testsuites
    now appends the result and exit status of each "plain" test to the
    associated log file (automake bug#11814).
  - The perl implementation of the TAP testsuite driver is no longer
    installed in the Automake's scripts directory, and is instead just
    distributed as a "contrib" addition.  There should be no reason to
    use this implementation anyway in real packages, since the awk+shell
    implementation of the TAP driver (which is documented in the manual)
    is more portable and has feature parity with the perl implementation.
  - The rule generating 'test-suite.log' no longer risk incurring in an
    extra useless "make all" recursive invocation in some corner cases
    (automake bug#16302).
  * Distribution:
  - Automake bug#18286: "make distcheck" could sometimes fail to detect
    files missing from the distribution tarball, especially in those cases
    where both the generated files and their dependencies are explicitly
    in $(srcdir).  An important example of this are *generated* makefile
    fragments included at Automake time in Makefile.am; e.g.:
    ...
    $(srcdir)/fragment.am: $(srcdir)/data.txt $(srcdir)/preproc.sh
    cd $(srcdir) && $(SHELL) preproc.sh <data.txt >fragment.am
    include $(srcdir)/fragment.am
    ...
    If the use forgot to add data.txt and/or preproc.sh in the distribution
    tarball, "make distcheck" would have erroneously succeeded!  This issue
    is now fixed.
  - As a consequence of the previous change, "make distcheck" will run
    using '$(distdir)/_build/sub' as the build directory, rather than
    simply '$(distdir)/_build' (as it was the case for Automake 1.14 and
    earlier).  Consequently, the './configure' and 'make' invocations
    issued by the distcheck recipe now have $(srcdir) equal to '../..',
    rather than to just '..'.  Dependent and similar variables (e.g.,
    '$(top_srcdir)') are also changed accordingly.
    Thus, Makefiles that made assumptions about the exact values of the
    build and source directories used by "make distcheck" will have to
    be adjusted.  Notice that making such assumptions was a bad and
    unsupported practice anyway, since the exact locations of those
    directories should be considered implementation details, and we
    reserve the right to change them at any time.
  * Miscellaneous bugs fixed:
  - The expansion of AM_INIT_AUTOMAKE ends once again with a trailing
    newline (bug#16841).  Regression introduced in Automake 1.14.
  - We no longer risk to use '$ac_aux_dir' before it's defined (see
    automake bug#15981). Bug introduced in Automake 1.14.
  - The code used to detect whether the currently used make is GNU make
    or not (relying on the private macro 'am__is_gnu_make') no longer
    risks causing "Arg list too long" for projects using automatic
    dependency tracking and having a ton of source files (bug#18744).
  - Automake tries to offer a more deterministic output for generated
    Makefiles, in the face of the newly-introduced randomization for
    hash keys order in Perl 5.18.
  - In older Automake versions, if a user defined one single Makefile
    fragment (say 'foo.am') to be included via Automake includes in
    his main Makefile.am, and defined a custom make rule to generate that
    file from other data, Automake used to spuriously complain with some
    message like "... overrides Automake target '$(srcdir)/foo.am".
    This bug is now fixed.
  - The user can now extend the special .PRECIOUS target, the same way
    he could already do with the .MAKE .and .PHONY targets.
  - Some confusing typos have been fixed in the manual and in few warning
    messages (automake bug#16827 and bug#16997).
- Remove automake-fix-ac_aux_dir-used-before-initialized.patch as the
  change is incorporated now.
- Refresh automake-SuSE.patch and automake-require_file.patch so that
  they apply cleanly.
* Mon Oct  6 2014 gber@opensuse.org
- Add automake-fix-ac_aux_dir-used-before-initialized.patch in
  to fix the use of $ac_aux_dir before being initialized
* Mon Aug 25 2014 pth@suse.de
- Explicitely pass the directory name to setup so that the testsuite
  can run.
* Wed Feb  5 2014 jengelh@inai.de
- Update to new upstream release 1.14.1
  * The 'compile' script is now unconditionally required for all
  packages that perform C compilation
  * The AM_PROG_CC_C_O macro can still be called, albeit that
  should no longer be necessary.
  * The special Automake-time substitutions '%%reldir%%' and
  '%%canon_reldir%%' (and their short versions, '%%D%%' and '%%C%%'
  respectively) can now be used in an included Makefile fragment.
  The former is substituted with the relative directory of the
  included fragment (compared to the top-level including
  Makefile), and the latter with the canonicalized version of the
  same relative directory.
  * The 'shar' and 'compress' distribution formats are deprecated
* Tue Oct 29 2013 fcrozat@suse.com
- Add expect as BuildRequires/Requires for automake-testsuite.
* Fri Aug 16 2013 andreas.stieger@gmx.de
- fix tests on factory
  automake-1.13.4-fix-primary-prefix-invalid-couples-test.patch
* Mon Jun 17 2013 pth@suse.de
- Update to 1.13.4:
  - Fix a minor regression introduced in Automake 1.13.3: when two or more
    user-defined suffix rules were present in a single Makefile.am,
    automake would needlessly include definition of some make variables
    related to C compilation in the generated Makefile.in (bug#14560).
- Adapt automake-SuSE.patch to changed config.guess.
* Wed Jun 12 2013 pth@suse.de
- Update to 1.13.3:
  * Documentation fixes:
  - The documentation no longer mistakenly reports that the
    obsolete 'AM_MKDIR_PROG_P' macro and '$(mkdir_p)' make variable
    are going to be removed in Automake 2.0.
  * Bugs fixed:
  - Byte-compilation of Emacs lisp files could fail spuriously on
    Solaris, when /bin/ksh or /usr/xpg4/bin/sh were used as shell.
  - If the same user-defined suffixes were transformed into
    different Automake-known suffixes in different Makefile.am
    files in the same project, automake could get confused and
    generate inconsistent Makefiles (automake bug#14441).
    For example, if 'Makefile.am' contained a ".ext.cc:" suffix
    rule, and 'sub/Makefile.am' contained a ".ext.c:" suffix rule,
    automake would have mistakenly placed into 'Makefile.in' rules
    to compile "*.c" files into object files, and into
    'sub/Makefile.in' rules to compile "*.cc" files into object
    files --- rather than the other way around.  This is now fixed.
  - Several spurious failures have been fixed (they hit especially
    MinGW/MSYS builds).  See automake bugs #14493, #14494, #14495,
    [#14498], #14499, #14500, #14501, #14517 and #14528.
  - Some other minor miscellaneous changes and fixlets.
  - Patches updated to they apply cleanly and with no offset.
* Tue May 28 2013 pth@suse.de
- Remove aclocal-am_ac.patch and aclocal-am_ac.sh as they aren't
  needed anymore and instead cause havok.
* Mon May 27 2013 pth@suse.de
- Update to 1.13.2 (for the full change log please see the file NEWS
  in the package documentation):
  * Obsolescent features:
  - Use of suffix-less info files (that can be specified through the
    '@setfilename' macro in Texinfo input files) is discouraged, and
    its use will raise warnings in the 'obsolete' category.
  - Use of Texinfo input files with '.txi' or '.texinfo' extensions
    is discouraged, and its use will raise warnings in the 'obsolete'
    category.  You are advised to simply use the '.texi' extension
    instead.
  * Documentation fixes:
  - The long-deprecated but still supported two-arguments invocation form
    of AM_INIT_AUTOMAKE is documented once again.
  * Bugs fixed:
  - When the 'ustar' option is used, the generated configure script no
    longer risks hanging during the tests for the availability of the
    'pax' utility, even if the user running configure has a UID or GID
    that requires more than 21 bits to be represented.
  - The obsolete macros AM_CONFIG_HEADER or AM_PROG_CC_STDC work once
    again, as they did in Automake 1.12.x (albeit printing runtime
    warnings in the 'obsolete' category).
  - aclocal will no longer error out if the first local m4 directory
    (as specified by the '-I' option or the 'AC_CONFIG_MACRO_DIRS' or
    'AC_CONFIG_MACRO_DIR' macros) doesn't exist; it will merely report
    a warning in the 'unsupported' category.
  - aclocal will no longer consider directories for extra m4 files more
    than once, even if they are specified multiple times.
  - Analysis of make flags in Automake-generated rules has been made more
    robust, and more future-proof.
- Adapt automake-SUSE.patch to the changed sources.
* Mon Apr 29 2013 mmeister@suse.com
- add a script to replace obsolete macros in configure.*
- call it from aclocal to avoid having to patch hundreds of packages
* Wed Mar 20 2013 mmeister@suse.com
- Added url as source.
  Please see http://en.opensuse.org/SourceUrls
* Tue Feb 19 2013 p.drouand@gmail.com
- Update to version 1.13.1:
  * Bugs fixed:
  - Use of the obsolete macros AM_CONFIG_HEADER or AM_PROG_CC_STDC now
    causes a clear and helpful error message, instead of obscure ones
    (issue introduced in Automake 1.13).
- Remove config-guess-sub-update.diff; config.guess and config.sub are
  not included anymore in /lib
- Remove
- Clean the specfile; remove useless conditionnal macros
- Automake now provide manfiles by default and help2man is not required
  anymore
* Sat Feb  2 2013 dmueller@suse.com
- update config.guess/sub to the latest state
* Thu Sep 13 2012 pth@suse.de
- Run pre_checkin.sh to sync automake-testsuite pec and .changes.
* Tue Sep 11 2012 p.drouand@gmail.com
- Update to 1.12.3:
  - reworks and reshuffles the Automake testsuite a bit; fixing some
    weaknesses and spurious failures in the process, but also, likely,
    introducing new ones;
  - introduces initial support for automatic dependency tracking with
    the Portland Group C/C++ compilers (thanks to Dave Goodell and
    Jeff A. Daily);
  - fixes several long-standing bugs and limitations in the 'ylwrap'
    script (thanks to Akim Demaille); among the other things, the
    long-standing PR/491 and automake bug#7648 are now fixed.
- Remove automake-add-mkdir_p-temporarly.patch:
  * Only temporary hack for openSUSE 12.2, now it is time to remove it
* Wed Jul  4 2012 coolo@suse.com
- make sure we still define $(mkdir_p) for the time being
* Wed Jun 27 2012 tom.mbrt@googlemail.com
- Update to 1.12.1:
  Bugs fixed in 1.12.1:
  - Several weaknesses in Automake's own build system and test suite
    have been fixed.
  - Aclocal works correctly with perl 5.16.0 (automake bug#11543).
  - Starting from either the next minor version (1.12.2) or the next major
  version (1.13), Automake will start warning if 'configure.in' is used
  instead of 'configure.ac' as the Autoconf input.  Future versions of
  Automake will drop support for 'configure.in' altogether.
* Fri May  4 2012 pth@suse.de
- Run pre_checkin.sh manually.
* Thu Apr 26 2012 pth@suse.de
- Update to 1.12:
  * Changes to Yacc and Lex support:
  - C source and header files derived from non-distributed Yacc
    and/or Lex sources are now removed by a simple "make clean"
    (while they were previously removed only by "make
    maintainer-clean").
  - Slightly backward-incompatible change, relevant only for use of
    Yacc with C++: the extensions of the header files produced by the
    Yacc rules are now modelled after the extension of the
    corresponding sources.  For example, yacc files named "foo.y++"
    and "bar.yy" will produce header files named "foo.h++" and
    "bar.hh" respectively, where they would have previously produced
    header files named simply "foo.h" and "bar.h".  This change
    offers better compatibility with 'bison -o'.
  * Miscellaneous changes:
  - The AM_PROG_VALAC macro now causes configure to exit with status
    77, rather than 1, if the vala compiler found is too old.
  - The build system of Automake itself now avoids the use of make
    recursion as much as possible.
  - Automake now prefers to quote 'like this' or "like this", rather
    than `like this', in diagnostic message and generated Makefiles,
    to accommodate the new GNU Coding Standards recommendations.
  - Automake has a new option '--print-libdir' that prints the path
    of the directory containing the Automake-provided scripts and
    data files.
  - The 'dist' and 'dist-all' targets now can run compressors in
  - parallel.
  - The rules to create pdf, dvi and ps output from Texinfo files now
    works better with modern 'texi2dvi' script, by explicitly passing
    it the '--clean' option to ensure stray auxiliary files are not
    left to clutter the build directory.
  - Automake can now generate silenced rules for texinfo outputs.
  - Some auxiliary files that are automatically distributed by
    Automake (e.g., 'install-sh', or the 'depcomp' script for
    packages compiling C sources) might now be listed in the
    DIST_COMMON variable in many Makefile.in files, rather than in
    the top-level one.
  - Messages of types warning or error from 'automake' and 'aclocal'
    are now prefixed with the respective type, and presence of
  - Werror is noted.
  - Automake's early configure-time sanity check now tries to avoid
    sleeping for a second, which slowed down cached configure runs
    noticeably.  In that case, it will check back at the end of the
    configure script to ensure that at least one second has passed,
    to avoid time stamp issues with makefile rules rerunning
    autotools programs.
  - The warnings in the category 'extra-portability' are now enabled
    by '-Wall'.  In previous versions, one has to use
    '-Wextra-portability' to enable them.
  - Various minor bugfixes for recent or long-standing bugs.
  For a more detailed list see the file NEWS in the package
  documentation.
* Wed Apr 18 2012 pth@suse.de
- Update to 1.11.5:
  Bugs fixed in 1.11.5:
  * Bugs introduced by 1.11.3:
  - Vala files with '.vapi' extension are now recognized and
    handled correctly again.
  - Vala support work again for projects that contain some program
    built from '.vala' (and possibly '.c') sources and some other
    program built from '.c' sources *only*.
* Fri Apr  6 2012 tabraham@novell.com
- Update to 1.11.4
  * WARNING - future backward-incompatibilities:
  - The support for the "obscure" multilib feature has been deprecated,
    and will be moved out of the automake core in the next major Automake
    release (1.12).
  - The support for ".log -> .html" conversion and the check-html and
    recheck-html targets will be removed in the next major Automake
    release (1.12).
  - The obsolescent AM_WITH_REGEX  macro has been deprecated (since the
    GNU rx library has been decommissioned), and will be removed in the
    next major Automake release (1.12).
  - The `lzma' compression format for distribution archives has been
    deprecated in favor of `xz' and `lzip', and will be removed in the
    next major Automake release (1.12).
  - The `--acdir' option of aclocal is deprecated, and will probably be
    removed in the next major Automake release (1.12).
  - The exact order in which the directories in the aclocal macro
    search path are looked up is probably going to be changed in the
    next Automake release (1.12).
  - The Automake support for automatic de-ANSI-fication will be removed
    in the next major Automake release (1.12).
  - Starting from the next Automake release (1.12), warnings in the
    `extra-portability' category will be enabled by `-Wall' (right now,
    one has to use `-Wextra-portability' explicitly).
  * Misc changes:
  - The 'ar-lib' script now ignores the "s" (symbol index) and "S" (no
    symbol index) modifiers as well as the "s" action, as the symbol index
    is created unconditionally by Microsoft lib.  Also, the "q" (quick)
    action is now a synonym for "r" (replace).  Also, the script has been
    ignoring the "v" (verbose) modifier already since Automake 1.11.3
  - When the 'compile' script is used to wrap MSVC, it now accepts an
    optional space between the -I, -L and -l options and their respective
    arguments, for better POSIX compliance
  - There is an initial, experimental support for automatic dependency
    tracking with tcc (the Tiny C Compiler).  Its associated depmode is
    currently recognized as "icc" (but this and other details are likely
    to change in future versions)
  - Automatic dependency tracking now works also with the IBM XL C/C++
    compilers, thanks to the new new depmode 'xlc'
  * Bugs fixed:
  - A definition of 'noinst_PYTHON' before 'python_PYTHON' (or similar)
    don't cause spurious failures upon "make install" anymore
  - The user can now instruct the 'uninstall-info' rule not to update
    the '${infodir}/dir' file by exporting the environment variable
    'AM_UPDATE_INFO_DIR' to the value "no".  This is done for consistency
    with how the 'install-info' rule operates since automake 1.11.2.
  * Long standing bugs:
  - It is now possible for a foo_SOURCES variable to hold Vala sources
    together with C header files, as well as with sources and headers for
    other supported languages (e.g., C++).  Previously, only mixing C and
    Vala sources was supported
  - If "aclocal --install" is used, and the first directory specified with
    '-I' is non-existent, aclocal will now create it before trying to copy
    files in it
  - An empty declaration of a "foo_PRIMARY" don't cause anymore the
    generated install rules to create an empty $(foodir) directory;
    for example, if Makefile.am contains something like:
    pkglibexec_SCRIPTS =
    if FALSE
    pkglibexec_SCRIPTS += bar.sh
    endif
    the $(pkglibexec) directory will not be created upon "make install".
- Changes from 1.11.3
  - Automake's own build system is more silent by default, making use of
    the 'silent-rules' option
  - The master copy of the `gnupload' script is now maintained in gnulib,
    not in automake
  - The `missing' script doesn't try to wrap calls to `tar' anymore
  - "make dist" doesn't wrap `tar' invocations with the `missing' script
    anymore.  Similarly, the obsolescent variable `$(AMTAR)' (which you
    shouldn't be using BTW ;-) does not invoke the missing script anymore
    to wrap tar, but simply invokes the `tar' program itself
  - "make dist" can now create lzip-compressed tarballs
  - In the Automake info documentation, the Top node and the nodes about
    the invocation of the automake and aclocal programs have been renamed;
    now, calling "info automake" will open the Top node, while calling
    "info automake-invocation" and "info aclocal-invocation" will access
    the nodes about the invocation of respectively automake and aclocal
  - Automake is now distributed as a gzip-compressed and an xz-compressed
    tarball.  Previously, bzip2 was used instead of xz
  - The last relics of Python 1.5 support have been removed from the
    AM_PATH_PYTHON macro
  - For programs and libraries, automake now detects EXTRA_foo_DEPENDENCIES
    and adds them to the normal list of dependencies, but without
    overwriting the foo_DEPENDENCIES variable, which is normally computed
    by automake
  * Bugs fixed:
  - Automake now correctly recognizes the prefix/primary combination
    `pkglibexec_SCRIPTS' as valid
  - The parallel-tests harness doesn't trip anymore on sed implementations
    with stricter limits on the length of input lines (problem seen at
    least on Solaris 8)
  * Long standing bugs:
  - The "deleted header file problem" for *.am files is avoided by stub
    rules.  This allows `make' to trigger a rerun of `automake' also if
    some previously needed `.am' file has been removed
  - The `silent-rules' option now generates working makefiles even
    for the uncommon `make' implementations that do not support the
    nested-variables extension to POSIX 2008.  For such `make'
    implementations, whether a build is silent is determined at
    configure time, and cannot be overridden at make time with
    `make V=0' or `make V=1'
  - Vala support now works better in VPATH setups
- Changes from 1.11.2
  * Changes to aclocal:
  - The `--acdir' option is deprecated.  Now you should use the new options
    `--automake-acdir' and `--system-acdir' instead.
  - The `ACLOCAL_PATH' environment variable is now interpreted as a
    colon-separated list of additional directories to search after the
    automake internal acdir (by default ${prefix}/share/aclocal-APIVERSION)
    and before the system acdir (by default ${prefix}/share/aclocal).
  * Misc changes:
  - The Automake support for automatic de-ANSI-fication has been
    deprecated.  It will probably be removed in the next major Automake
    release (1.12).
  - The `lzma' compression scheme and associated automake option `dist-lzma'
    is obsoleted by `xz' and `dist-xz' due to upstream changes.
  - You may adjust the compression options used in dist-xz and dist-bzip2.
    The default is now merely -e for xz, but still -9 for bzip;  you may
    specify a different level via the XZ_OPT and BZIP2 envvars respectively.
    E.g., "make dist-xz XZ_OPT=-7" or "make dist-bzip2 BZIP2=-5"
  - The `compile' script now converts some options for MSVC for a better
    user experience.  Similarly, the new `ar-lib' script wraps Microsoft lib.
  - The py-compile script now accepts empty arguments passed to the options
    `--destdir' and `--basedir', and complains about unrecognized options.
    Moreover, a non-option argument or a special `--' argument terminates
    the list of options.
  - A developer that needs to pass specific flags to configure at "make
    distcheck" time can now, and indeed is advised to, do so by defining
    the developer-reserved makefile variable AM_DISTCHECK_CONFIGURE_FLAGS,
    instead of the old DISTCHECK_CONFIGURE_FLAGS.
    The DISTCHECK_CONFIGURE_FLAGS variable should now be reserved for the
    user; still, the old Makefile.am files that used to define it will
    still continue to work as before.
  - New macro AM_PROG_AR that looks for an archiver and wraps it in the new
    'ar-lib' auxiliary script if the selected archiver is Microsoft lib.
    This new macro is required for LIBRARIES and LTLIBRARIES when automake
    is run with -Wextra-portability and -Werror.
  - When using DejaGnu-based testsuites, the user can extend the `site.exp'
    file generated by automake-provided rules by defining the special make
    variable `$(EXTRA_DEJAGNU_SITE_CONFIG)'.
  - The `install-info' rule can now be instructed not to create/update
    the `${infodir}/dir' file, by exporting the new environment variable
    `AM_UPDATE_INFO_DIR' to the value "no".
  * Bugs fixed:
  - When the parallel-tests driver is in use, automake now explicitly
    rejects invalid entries and conditional contents in TEST_EXTENSIONS,
    instead of issuing confusing and apparently unrelated error messages
    (e.g., "non-POSIX variable name", "bad characters in variable name",
    or "redefinition of TEST_EXTENSIONS), or even, in some situations,
    silently producing broken `Makefile.in' files
  - The `silent-rules' option now truly silences all compile rules, even
    when dependency tracking is disabled.  Also, when `silent-rules' is
    not used, `make' output no longer contains spurious backslash-only
    lines, thus once again matching what Automake did before 1.11.
  - The AM_COND_IF macro also works if the shell expression for the
    conditional is no longer valid for the condition.
  * Long standing bugs:
  - The order of Yacc and Lex flags is fixed to be consistent with other
    languages: $(AM_YFLAGS) comes before $(YFLAGS), and $(AM_LFLAGS) before
    $(LFLAGS), so that the user variables override the developer variables.
  - "make distcheck" now correctly complains also when "make uninstall"
    leaves one and only one file installed in $(prefix).
  - A "make uninstall" issued before a "make install", or after a mere
    "make install-data" or a mere "make install-exec" does not spuriously
    fail anymore.
  - Automake now warns about more primary/directory invalid combinations,
    such as "doc_LIBRARIES" or "pkglib_PROGRAMS".
  - Rules generated by Automake now try harder to not change any files when
    `make -n' is invoked.  Fixes include compilation of Emacs Lisp, Vala, or
    Yacc source files and the rule to update config.h.
  - Several scripts and the parallel-tests testsuite driver now exit with
    the right exit status upon receiving a signal.
  - A per-Makefile.am setting of -Werror does not erroneously carry over
    to the handling of other Makefile.am files.
  - The code for automatic dependency tracking works around a Solaris
    make bug triggered by sources containing repeated slashes when the
    `subdir-objects' option was used.
  - The makedepend and hp depmodes now work better with VPATH builds.
  - Java sources specified with check_JAVA are no longer compiled for
    "make all", but only for "make check".
  - An usage like "java_JAVA = foo.java" will now cause Automake to warn
    and error out if `javadir' is undefined, instead of silently producing
    a broken Makefile.in.
  - aclocal and automake now honour the configure-time definitions of
    AUTOCONF and AUTOM4TE when they spawn autoconf or autom4te processes.
  - The `install-info' recipe no longer tries to guess whether the
    `install-info' program is from Debian or from GNU, and adaptively
    change its behaviour; this has proven to be frail and easy to
    regress.
* Tue Dec 20 2011 coolo@suse.com
- add autoconf as buildrequire to avoid implicit dependency
* Sun Dec 18 2011 sweet_f_a@gmx.de
- correct license and style (prepare_spec)
- minor build fixes, avoid deprecated macros to be more portable
* Sat Sep 17 2011 jengelh@medozas.de
- Remove redundant tags/sections from specfile
* Mon Jun 28 2010 jengelh@medozas.de
- use %%_smp_mflags
* Fri Dec 11 2009 pth@suse.de
- Update to 1.11.1 (bnc#559815):
  - The `parallel-tests' test driver works around a GNU make 3.80
    bug with trailing white space in the test list
    (`TESTS = foo $(EMPTY)').
  * Long standing bugs:
  - The testsuite does not try to change the mode of `ltmain.sh'
    files from a Libtool installation (symlinked to test
    directories) any more.
  - AM_PROG_GCJ uses AC_CHECK_TOOLS to look for `gcj' now, so
    that prefixed tools are preferred in a cross-compile setup.
  - The distribution is tarred up with mode 755 now by the
    `dist*' targets.  This fixes a race condition where untrusted
    users could modify files in the $(PACKAGE)-$(VERSION) distdir
    before packing if the toplevel build directory was
    world-searchable.  This is CVE-2009-4029.
- Make automake a noarch package.
  Sun Dec  6 18:02:39 CET 2009 - jengelh
- enable parallel building
* Wed Aug 26 2009 coolo@novell.com
- rediff to avoid fuzz
* Fri Jul 10 2009 jansimon.moeller@opensuse.org
- Disable the testsuite also for ARM as it blocks/stalls the worker.
* Sun Jun 21 2009 coolo@novell.com
- add empty %%install section to testsuite to fix build
* Tue Jun 16 2009 coolo@novell.com
- split test suit into own package (new policy for bootstrap)
* Fri May 29 2009 puzel@suse.cz
- update to automake-1.11
  - noteworthy changes:
  - require autoconf-2.62
  - The autoconf version check implemented by aclocal in aclocal.m4
    (and new in Automake 1.10) is degraded to a warning.  This helps
  - The automake program can run multiple threads for creating most
  Makefile.in files concurrently in the common case where the Autoconf
  versions used are compatible.
  - Libtool generic flags are now passed to the install and uninstall
    modes as well.
  - distcheck works with Libtool 2.x even when LT_OUTPUT is used, as
    config.lt is removed correctly now.
  - subdir-object mode works now with Fortran (F77, FC, preprocessed
    Fortran, and Ratfor).
  - For files with extension .f90, .f95, .f03, or .f08, the flag
  $(FCFLAGS_f[09]x) computed by AC_FC_SRCEXT is now used in compile rules.
  - Files with extension .sx are also treated as preprocessed assembler.
  - The default source file extension (.c) can be overridden with
    AM_DEFAULT_SOURCE_EXT now.
  - Python 3.0 is supported now, Python releases prior to 2.0 are no
    longer supported.
  - AM_PATH_PYTHON honors python's idea about the site directory.
  - "make dist" can now create xz-compressed tarballs,
    as well as (deprecated?) lzma-compressed tarballs.
  - `automake --add-missing' will by default install the GPLv3 file as
    COPYING if it is missing.
  - for full changelog please see /usr/share/doc/packages/automake/NEWS
- remove automake-fix_check10.patch (fixed upstream)
- add automake-11.1-skip-specflg10-without-g++.patch (from upstream git)
* Thu Apr 30 2009 pth@suse.de
- Add upstream post 1.10.2 patch to fix the failing check10.test.
* Wed Apr 29 2009 pth@suse.de
- Rediff to sync the patches (automake-require_file.patch was off
  by ~ 500 lines). Update the reference to bugzilla for this patch.
* Wed Mar 11 2009 pth@suse.de
- Update to 1.10.2:
  * Rebuild rules now also work for a removed `subdir/Makefile.in' in
    an otherwise up to date tree.
  * Work around AIX sh quoting issue in AC_PROG_CC_C_O, leading to
    unnecessary use of the `compile' script.
  * `config.status --file=Makefile depfiles' now also works with the
    extra quoting used internally by Autoconf 2.62 and newer
    (it used to work only without the `--file=' bit).
  * distcheck works with Libtool 2.x even when LT_OUTPUT is used, as
    config.lt is removed correctly now.
  * The manual is now distributed under the terms of the GNU FDL 1.3.
  * When `automake --add-missing' causes the COPYING file to be installed,
    it will also warn that the license file should be added to source
    control.
- Add bison again.
- Pass docdir on to configure.
- Add a rpmlintrc file
* Wed Mar  4 2009 pth@suse.de
- Prefix patches with package name.
* Mon Jan 28 2008 schwab@suse.de
- Revert last change.
* Sat Jan 26 2008 aj@suse.de
- Add bison as buildrequirs for the testsuite.
* Tue Jan 22 2008 schwab@suse.de
- Update to automake 1.10.1.
  * Automake development is done in a git repository on Savannah now, see
    http://git.sv.gnu.org/gitweb/?p=automake.git
    A read-only CVS mirror is provided at
    cvs -d :pserver:anonymous@pserver.git.sv.gnu.org:/automake.git \
    checkout -d automake HEAD
  * "make dist" can now create lzma-compressed tarballs.
  * `automake --add-missing' will by default install the GPLv3 file as
    COPYING if it is missing.  Note that Automake will never overwrite
    an existing COPYING file, even when the `--force-missing' option is
    used.  Further note that Automake 1.10.1 is still licensed under GPLv2+.
  * Libtool generic flags are now passed to the install and uninstall
    modes as well.
  * Files with extension .sx are also treated as preprocessed assembler.
  * install-sh now has an BSD-like option `-C' to preserve modification
    times of unchanged files upon installation.
  * Fix aix dependency tracking for libtool objects.
  * The signal handling of aclocal has been improved.
  * Targets beginning with a digit are now recognized correctly.
  * All directories `.libs'/`_libs' used by libtool are cleaned now,
    not only those in which libraries are built.
  * Fix output of dummy dependency files in presence of post-processed
    Makefile.in's again, but also cope with long lines.
  * $(EXEEXT) is automatically appended to filenames of XFAIL_TESTS
    that have been declared as programs in the same Makefile.
    This is for consistency with the analogous change to TESTS in 1.10.
  * The autoconf version check implemented by aclocal in aclocal.m4
    (and new in Automake 1.10) is degraded to a warning.  This helps
    in the common case where the Autoconf versions used are compatible.
  * Fix order of standard includes to again be `-I. -I$(srcdir)',
    followed by directories containing config headers.
* Fri Nov 23 2007 schwab@suse.de
- Fix last change.
* Mon Nov 12 2007 dmueller@suse.de
- require the autoconf version it was build against
* Thu Oct 11 2007 schwab@suse.de
- Add lzma support.
* Mon Jan 29 2007 sbrabec@suse.cz
- Removed references to /opt/gnome.
* Sun Oct 15 2006 schwab@suse.de
- Update to automake 1.10.
  * Version requirements:
  - Autoconf 2.60 or greater is required.
  - Perl 5.6 or greater is required.
  * Changes to aclocal:
  - aclocal now also supports -Wmumble and -Wno-mumble options.
  - `dirlist' entries (for the aclocal search path) may use shell
    wildcards such as `*', `?', or `[...]'.
  - aclocal supports an --install option that will cause system-wide
    third-party macros to be installed in the local directory
    specified with the first -I flag.  This option also uses #serial
    lines in M4 files to upgrade local macros.
    The new aclocal options --dry-run and --diff help to review changes
    before they are installed.
  - aclocal now outputs an autoconf version check in aclocal.m4 in
    projects using automake.
    For a few years, automake and aclocal have been calling autoconf
    (or its underlying engine autom4te) to accurately retrieve the
    data they need from configure.ac and its siblings.  Doing so can
    only work if all autotools use the same version of autoconf.  For
    instance a Makefile.in generated by automake for one version of
    autoconf may stop working if configure is regenerated with another
    version of autoconf, and vice versa.
    This new version check ensures that the whole build system has
    been generated using the same autoconf version.
  * Support for new Autoconf macros:
  - The new AC_REQUIRE_AUX_FILE Autoconf macro is supported.
  - If `subdir-objects' is set, and AC_CONFIG_LIBOBJ_DIR is specified,
    $(LIBOBJS), $(LTLIBOBJS), $(ALLOCA), and $(LTALLOCA) can be used
    in different directories.  However, only one instance of such a
    library objects directory is supported.
  * Change to Libtool support:
  - Libtool generic flags (those that go before the --mode=MODE option)
    can be specified using AM_LIBTOOLFLAGS and target_LIBTOOLFLAGS.
  * Yacc and Lex changes:
  - The rebuild rules for distributed Yacc and Lex output will avoid
    overwriting existing files if AM_MAINTAINER_MODE and maintainer-mode
    is not enabled.
  - ylwrap is now always used for lex and yacc source files,
    regardless of whether there is more than one source per directory.
  * Languages changes:
  - Preprocessed assembler (*.S) compilation now honors CPPFLAGS,
    AM_CPPFLAGS and per-target _CPPFLAGS, and supports dependency
    tracking, unlike non-preprocessed assembler (*.s).
  - subdir-object mode works now with Assembler.  Automake assumes
    that the compiler understands `-c -o'.
  - Preprocessed assembler (*.S) compilation now also honors
    $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES).
  - Improved support for Objective C:
  - Autoconf's new AC_PROG_OBJC will enable automatic dependency tracking.
  - A new section of the manual documents the support.
  - New support for Unified Parallel C:
  - AM_PROG_UPC looks for a UPC compiler.
  - A new section of the manual documents the support.
  - Per-target flags are now correctly handled in link rules.
    For instance maude_CFLAGS correctly overrides AM_CFLAGS; likewise
    for maude_LDFLAGS and AM_LDFLAGS.  Previous versions bogusly
    preferred AM_CFLAGS over maude_CFLAGS while linking, and they
    used both AM_LDFLAGS and maude_LDFLAGS on the same link command.
    The fix for compiler flags (i.e., using maude_CFLAGS instead of
    AM_CFLAGS) should not hurt any package since that is how _CFLAGS
    is expected to work (and actually works during compilation).
    However using maude_LDFLAGS "instead of" AM_LDFLAGS rather than
    "in addition to" breaks backward compatibility with older versions.
    If your package used both variables, as in
  AM_LDFLAGS = common flags
  bin_PROGRAMS = a b c
  a_LDFLAGS = more flags
  ...
    and assumed *_LDFLAGS would sum up, you should rewrite it as
  AM_LDFLAGS = common flags
  bin_PROGRAMS = a b c
  a_LDFLAGS = $(AM_LDFLAGS) more flags
  ...
    This new behavior of *_LDFLAGS is more coherent with other
    per-target variables, and the way *_LDFLAGS variables were
    considered internally.
  * New installation targets:
  - New targets mandated by GNU Coding Standards:
  install-dvi
  install-html
  install-ps
  install-pdf
    By default they will only install Texinfo manuals.
    You can customize them with *-local variants:
  install-dvi-local
  install-html-local
  install-ps-local
  install-pdf-local
  - The undocumented recursive target `uninstall-info' no longer exists.
    (`uninstall' is in charge of removing all possible documentation
    flavors, including optional formats such as dvi, ps, or info even
    when `no-installinfo' is used.)
  * Miscellaneous changes:
  - Automake no longer complains if input files for AC_CONFIG_FILES
    are specified using shell variables.
  - clean, distribution, or rebuild rules are normally disabled for
    inputs and outputs of AC_CONFIG_FILES, AC_CONFIG_HEADERS, and
    AC_CONFIG_LINK specified using shell variables.  However, if these
    variables are used as ${VAR}, and AC_SUBSTed, then Automake will
    be able to output rules anyway.
    (See the Automake documentation for AC_CONFIG_FILES.)
  - $(EXEEXT) is automatically appended to filenames of TESTS
    that have been declared as programs in the same Makefile.
    This is mostly useful when some check_PROGRAMS are listed in TESTS.
  - `-Wportability' has finally been turned on by default for `gnu' and
    `gnits' strictness.  This means, automake will complain about %%-rules
    or $(GNU Make functions) unless you switch to `foreign' strictness or
    use `-Wno-portability'.
  - Automake now uses AC_PROG_MKDIR_P (new in Autoconf 2.60), and uses
    $(MKDIR_P) instead of $(mkdir_p) to create directories.  The
    $(mkdir_p) variable is still defined (to the same value as
    $(MKDIR_P)) but should be considered obsolete.  If you are using
    $(mkdir_p) in some of your rules, please plan to update them to
    $(MKDIR_P) at some point.
  - AM_C_PROTOTYPES and ansi2knr are now documented as being obsolete.
    They still work in this release, but may be withdrawn in a future one.
  - Inline compilation rules for gcc3-style dependency tracking are
    more readable.
  - Automake installs a "Hello World!" example package in $(docdir).
    This example is used throughout the new "Autotools Introduction"
    chapter of the manual.
* Mon Aug 21 2006 sbrabec@suse.cz
- Removed dirlist.d support, use hardwired path instead.
* Mon Jul 31 2006 schwab@suse.de
- Remove obsolete patch.
* Mon May 15 2006 schwab@suse.de
- Import latest versions of config.{guess,sub}.
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Mon Jul 11 2005 schwab@suse.de
- Update to automake 1.9.6.
* Sun May  8 2005 schwab@suse.de
- Some architectures can't keep up the pace.
* Sat May  7 2005 matz@suse.de
- Split away an automake-check package, which does the make check.
* Sun Feb 13 2005 schwab@suse.de
- Update to automake 1.9.5.
* Fri Jan 14 2005 schwab@suse.de
- Fix require_file_internal to handle file names with directories
  (bnc#64822).
* Wed Jan 12 2005 schwab@suse.de
- Update to automake 1.9.4.
* Thu Nov 25 2004 ro@suse.de
- incremental fix for py-compile
* Fri Nov 19 2004 schwab@suse.de
- Fix py-compile to avoid putting $(DESTDIR) in the output.
* Mon Nov  1 2004 schwab@suse.de
- Update to automake 1.9.3.
* Fri Oct  8 2004 schwab@suse.de
- Update to automake 1.9.2.
* Mon Aug 30 2004 schwab@suse.de
- Fix $PATH_PATTERN.
* Tue Aug 17 2004 schwab@suse.de
- Fix handling of subdir-objects.
* Thu Aug 12 2004 schwab@suse.de
- Update to automake 1.9.1.
* Thu Jul 29 2004 schwab@suse.de
- Update to automake 1.9.
* Mon Jul 19 2004 schwab@suse.de
- Fix quoting.
* Sat Jul 17 2004 schwab@suse.de
- Update to automake 1.8d (1.9 release candidate).
* Mon May 17 2004 schwab@suse.de
- Update to automake 1.8.5.
* Tue May  4 2004 schwab@suse.de
- Update to automake 1.8.4.
* Sun Mar  7 2004 schwab@suse.de
- Update to automake 1.8.3.
* Sat Jan 17 2004 schwab@suse.de
- Fix race condition in testsuite.
* Tue Jan 13 2004 schwab@suse.de
- Update to automake 1.8.2.
* Mon Jan 12 2004 schwab@suse.de
- Update to automake 1.8.1.
* Thu Jan  8 2004 schwab@suse.de
- Fix use of undefined value.
* Thu Dec 11 2003 schwab@suse.de
- Update to automake 1.8.
* Mon Nov 10 2003 schwab@suse.de
- Update to automake 1.7.9.
* Tue Oct  7 2003 schwab@suse.de
- Update to automake 1.7.8.
* Mon Sep  8 2003 schwab@suse.de
- Update to automake 1.7.7.
* Wed Jul 16 2003 sbrabec@suse.cz
- Added support for /usr/share/aclocal/dirlist.
* Fri Jul 11 2003 schwab@suse.de
- Update to automake 1.7.6.
* Tue Jun 10 2003 schwab@suse.de
- Update to automake 1.7.5.
* Mon May 12 2003 schwab@suse.de
- Add %%defattr.
* Fri Apr 25 2003 schwab@suse.de
- Update to automake 1.7.3.
* Thu Apr 24 2003 ro@suse.de
- fix install_info --delete call and move from preun to postun
* Mon Apr  7 2003 schwab@suse.de
- Only delete info entries when removing last version.
* Thu Feb  6 2003 schwab@suse.de
- Use %%install_info.
* Mon Jan 20 2003 schwab@suse.de
- Fix python macros properly.
* Fri Dec  6 2002 schwab@suse.de
- Update to automake 1.7.2.
  * Many bug fixes.
* Thu Nov 21 2002 schwab@suse.de
- Fix ansi2knr option.
* Mon Nov 18 2002 ro@suse.de
- use /.buildenv like /etc/SuSE-release
* Fri Sep 27 2002 schwab@suse.de
- Update to automake 1.7.
* Tue Sep 17 2002 ro@suse.de
- removed bogus self-provides
* Mon Aug  5 2002 schwab@suse.de
- Update to automake 1.6.3.
  * Support for AM_INIT_GETTEXT([external])
  * Bug fixes
* Thu Jun 20 2002 schwab@suse.de
- Fix python macros for lib64.
* Sat Jun 15 2002 schwab@suse.de
- Update to automake 1.6.2.
  * Bug fix release.
* Fri Apr 12 2002 schwab@suse.de
- Update to automake 1.6.1.
* Fri Mar 29 2002 schwab@suse.de
- Fix typo check.
- Disable libtool vs. normal check.
- Make dependency generation work with KDE.
* Mon Mar 11 2002 schwab@suse.de
- Add versioned links to automake and aclocal.
* Thu Mar  7 2002 schwab@suse.de
- Update to automake 1.6.
* Wed Jan 23 2002 schwab@suse.de
- Fix nonportable test option in config.guess.
* Sun Dec 16 2001 adrian@suse.de
- fix config.guess to recognize SGI mips systems as big endian systems
- bzip2 sources
* Mon Aug 27 2001 schwab@suse.de
- Update to automake 1.5.
* Thu Aug  9 2001 ro@suse.de
- fixed problem when installing lisp files
* Thu Jul 19 2001 schwab@suse.de
- Update to automake 1.4-p5.
* Tue Jun 12 2001 olh@suse.de
- recognize ppc64
* Tue Jun 12 2001 olh@suse.de
- fix typo in automake-1.4-SuSE.patch
* Mon Jun 11 2001 schwab@suse.de
- Recognize AC_PROG_LIBTOOL as well as AM_PROG_LIBTOOL.
* Mon Jun 11 2001 schwab@suse.de
- Update to automake 1.4-p4.
* Sat May 26 2001 schwab@suse.de
- Update to automake 1.4-p2.
* Wed May  9 2001 schwab@suse.de
- Update to automake 1.4-p1.
* Fri May  4 2001 schwab@suse.de
- Fix automake script for libtool 1.4.
* Fri Mar 30 2001 schwab@suse.de
- config.sub: don't try to fill missing parts by looking at the host
  system.
* Thu Feb 15 2001 schwab@suse.de
- Update config.{guess,sub} to latest version.
* Wed Sep 13 2000 schwab@suse.de
- Add bzip2 patch from kkaempf@suse.de.
* Mon Aug 21 2000 werner@suse.de
- Use vendor within config.sub even for s390
* Mon May  1 2000 kukuk@suse.de
- Use mandir und infodir macro
* Wed Mar 29 2000 bk@suse.de
- updated config.guess and config.sub for s390
* Wed Mar  1 2000 werner@suse.de
- Add arm/ppc patch from teTeX sources
- Make VENDOR=suse if /etc/SuSE-release exists, remove `-gnu', and
  use $VERNDOR for all Linux architectures.
* Tue Feb 15 2000 schwab@suse.de
- Update config.{guess,sub} to latest version.
* Thu Jan 20 2000 kukuk@suse.de
- Move /usr/{info,man} -> /usr/share/{info,man}
* Mon Sep 13 1999 bs@suse.de
- ran old prepare_spec on spec file to switch to new prepare_spec.
* Thu Aug 26 1999 kukuk@suse.de
- Add automake.1, aclocal.1 and other documentation
- Add make check to build section
* Fri Feb 26 1999 florian@suse.de
- update to 1.4
* Fri Jun 19 1998 ro@suse.de
- update to 1.3 using dif from jurix
* Wed Jun 25 1997 florian@suse.de
- update to version 1.2
* Thu Jan  2 1997 florian@suse.de
  new version 1.0
