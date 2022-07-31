#
# spec file for package autogen
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


%define         libname libopts25
Name:           autogen
Version:        5.18.16
Release:        7.3
Summary:        Automated Text File Generator
License:        GPL-3.0-or-later
Group:          Development/Tools/Building
URL:            https://www.gnu.org/software/autogen/
Source0:        https://ftp.gnu.org/gnu/autogen/rel%{version}/%{name}-%{version}.tar.xz
Patch1:         autogen-build_ldpath.patch
# PATCH-FIX-UPSTREAM -- https://savannah.gnu.org/support/index.php?109234 boo#1021353
Patch2:         autogen-catch-race-error.patch
# PATCH-FIX-UPSTREAM don't make programs uninstallable
Patch3:         installable-programs.patch
# PATCH-FIX-UPSTREAM
Patch4:         sprintf-overflow.patch
# PATCH-FIX-UPSTREAM -- https://sourceforge.net/p/autogen/bugs/193/#5844
Patch5:         gcc9-fix-wrestrict.patch
# PATCH-FIX-UPSTREAM Allow building with guile 3.0
Patch6:         guile-version.patch
Patch7:         autogen-avoid-GCC-code-analysis-bug.patch
#BuildRequires:  fdupes
#BuildRequires:  guile-devel
#BuildRequires:  makeinfo
#BuildRequires:  pkgconfig >= 0.9.0
#BuildRequires:  pkgconfig(libxml-2.0)
#Requires(post): %{install_info_prereq}
#Requires(preun):%{install_info_prereq}

%description
AutoGen is a tool designed for generating program files that contain
repetitive text with varied substitutions.  Its goal is to simplify the
maintenance of programs that contain large amounts of repetitious text.
This is especially valuable if there are several blocks of such text that
must be kept synchronized in parallel tables.

%package -n %{libname}
Summary:        Shared library libopts
Group:          System/Libraries

%description -n %{libname}
AutoOpts is a tool that virtually eliminates the hassle of processing
options and keeping man pages, info docs and usage text up to date.  This
package allows you to specify several program attributes, thousands of
option types and many option attributes.  From this, it then produces all
the code necessary to parse and handle the command line and configuration
file options, and the documentation that should go with your program as
well.

This package contains shared library libopts

%package -n autoopts
Summary:        Automated Option Processing
Group:          Development/Languages/C and C++
Requires:       %{libname} = %{version}-%{release}
Requires:       autogen
Obsoletes:      %{libname}-devel < %{version}-%{release}
Provides:       autogen:/usr/bin/autoopts-config
Provides:       libopts-devel

%description -n autoopts
AutoOpts is a tool that virtually eliminates the hassle of processing
options and keeping man pages, info docs and usage text up to date.  This
package allows you to specify several program attributes, thousands of
option types and many option attributes.  From this, it then produces all
the code necessary to parse and handle the command line and configuration
file options, and the documentation that should go with your program as
well.

%prep
%autosetup -p1
touch aclocal.m4 configure Makefile.in config-h.in

%build
%configure \
	--enable-timeout=70 \
	--disable-static \
	--with-pic
make %{?_smp_mflags}

%install
export MAN_PAGE_DATE=$(date -u -d @${SOURCE_DATE_EPOCH:-$(date +%s)} -I)
%make_install
find %{buildroot} -type f -name "*.la" -delete -print
#%fdupes -s %{buildroot}%{_datadir}

%check
make %{?_smp_mflags} check VERBOSE=1

%post
%install_info --info-dir=%{_infodir} %{_infodir}/autogen.info%{ext_info}

%preun
%install_info_delete --info-dir=%{_infodir} %{_infodir}/autogen.info%{ext_info}

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files
%doc NEWS
%license COPYING
%{_bindir}/autogen
%{_bindir}/columns
%{_bindir}/getdefs
%{_bindir}/xml2ag
%{_mandir}/man1/autogen.1
%{_mandir}/man1/columns.1
%{_mandir}/man1/getdefs.1
%{_mandir}/man1/xml2ag.1
%exclude %{_mandir}/man1/autoopts-config.1
%{_infodir}/autogen.info
%{_infodir}/autogen.info-1
%{_infodir}/autogen.info-2
%{_infodir}/dir
%dir %{_datadir}/autogen
%{_datadir}/autogen/fsm-trans.tlib
%{_datadir}/autogen/fsm-macro.tlib

%files -n %{libname}
%{_libdir}/libopts.so.25
%{_libdir}/libopts.so.25.17.1

%files -n autoopts
%{_bindir}/autoopts-config
%{_libdir}/libopts.so
%{_includedir}/autoopts/options.h
%{_includedir}/autoopts/usage-txt.h
%{_mandir}/man1/autoopts-config.1
%{_mandir}/man3/ao_string_tokenize.3
%{_mandir}/man3/configFileLoad.3
%{_mandir}/man3/optionFileLoad.3
%{_mandir}/man3/optionFindNextValue.3
%{_mandir}/man3/optionFindValue.3
%{_mandir}/man3/optionFree.3
%{_mandir}/man3/optionGetValue.3
%{_mandir}/man3/optionLoadLine.3
%{_mandir}/man3/optionMemberList.3
%{_mandir}/man3/optionNextValue.3
%{_mandir}/man3/optionOnlyUsage.3
%{_mandir}/man3/optionPrintVersion.3
%{_mandir}/man3/optionPrintVersionAndReturn.3
%{_mandir}/man3/optionProcess.3
%{_mandir}/man3/optionRestore.3
%{_mandir}/man3/optionSaveFile.3
%{_mandir}/man3/optionSaveState.3
%{_mandir}/man3/optionUnloadNested.3
%{_mandir}/man3/optionVersion.3
%{_mandir}/man3/strequate.3
%{_mandir}/man3/streqvcmp.3
%{_mandir}/man3/streqvmap.3
%{_mandir}/man3/strneqvcmp.3
%{_mandir}/man3/strtransform.3
%{_libdir}/autogen
%{_datadir}/aclocal/autoopts.m4
%{_datadir}/autogen
%exclude %{_datadir}/autogen/fsm-trans.tlib
%exclude %{_datadir}/autogen/fsm-macro.tlib
%{_libdir}/pkgconfig/autoopts.pc

%changelog
* Tue Apr 19 2022 Martin Liška <mliska@suse.cz>
- Add upstream patch autogen-avoid-GCC-code-analysis-bug.patch
  in order to support -D_FORTIFY_SOURCE=3 with GCC 12.
- Use autosetup.
* Wed Jun 10 2020 Bernhard Wiedemann <bwiedemann@suse.com>
- Set MAN_PAGE_DATE to normalize man page date (boo#1047218)
* Mon May 11 2020 Andreas Schwab <schwab@suse.de>
- Increase default timeout
- Run testsuite in verbose mode
* Mon Mar 23 2020 Andreas Schwab <schwab@suse.de>
- guile-version.patch: Allow all patchlevel versions of guile 3.0
* Tue Jan 21 2020 Andreas Schwab <schwab@suse.de>
- guile-version.patch: Allow building with guile 3.0
* Mon Mar 25 2019 Martin Liška <mliska@suse.cz>
- Add gcc9-fix-wrestrict.patch in order to fix
  bsc#1125772.
* Thu Nov 22 2018 schwab@suse.de
- Remove invalid signature file and keyring
* Wed Nov 21 2018 <jbrielmaier@suse.de>
- BuildRequire guile-devel to make transistion to Guile 2.2 smooth
* Tue Oct 16 2018 schwab@suse.de
- Update to version 5.8.16
  - Enable compiling with Guile 2.2
- autogen-guile-2.2.patch: removed
- installable-programs.patch: don't make programs uninstallable
- Rediff remaining patches
* Tue Jul 31 2018 schwab@suse.de
- Don't require libopts-devel from autogen
- Rename libopts-devel to autoopts
- Move all autoopts related files to autoopts
- Don't run autoreconf
- Don't remove -Werror
- sprintf-overflow.patch: Fix sprintf overflow
- autogen-guile-2.2.patch: properly add support for guile 2.2
- autogen-constant-timeout.patch: remove, use --enable-timeout
  instead
* Fri Jul 20 2018 mpluskal@suse.com
- Update to version 5.8.14:
  * several configury fixes to enable cross platform building.
  * fompletion of a change in "char-mapper" to enable bootstrapping
  * Guile 1.8 support was removed
  * Replace AG_SCM_STR02SCM with scm_from_latin1_string this breaks
    Guile 1.8.
  * adaptations for cross compiling
  * no more generating autoconf macros
  * fix internal implementation of forking off autogen in xml2ag
  * when calling abort() causes problems, exit() can now be called
    (via an option) instead.
  * add support for nanosecond precision in file times
  * suppress dumb warnings about embedded NUL bytes in formats.
- Refresh patches
- Drop not applying autogen-reproducible-tar.patch
* Tue Mar 27 2018 dimstar@opensuse.org
- Explicitly call autoreconf: various patches touch the build
  system, which results in an implicit call. That in turn only
  works as long as the automake/autconf version is the same as used
  when originally bootrapping the tarball.
* Wed Aug 23 2017 bwiedemann@suse.com
- Add autogen-reproducible-tar.patch to make .tar.gz build reproducible
  ( https://sourceforge.net/p/autogen/bugs/182/ )
- Add autogen-constant-timeout.patch to make build reproducible (boo#1041534)
- Set MAN_PAGE_DATE to not include build date into man pages (boo#1047218)
* Tue Jul  4 2017 tchvatal@suse.com
- Add patch to build with guile 2.2:
  * autogen-guile-2.2.patch
* Wed Feb 22 2017 bwiedemann@suse.com
- Add autogen-catch-race-error.patch (boo#1021353)
* Sun Jan  8 2017 mpluskal@suse.com
- Update to version 5.8.12:
  * several configury fixes to enable cross platform building.
  * fompletion of a change in "char-mapper" to enable bootstrapping
* Mon Jun 27 2016 astieger@suse.com
- GNU autogen 5.18.10:
  * NUL terminate CGI definitions text
- GNU autogen 5.18.9:
  * When parsing CGI, do not allow spaces to be lost
  * In producing usage text, check more rigorously that
    option "values" are really not flag characters.
- GNU autogen 5.18.8:
  * Ensure testing vars start as unset for testing
  * happy new year & de-uglifications
- update download URL and usptream signing key
* Thu May  5 2016 mpluskal@suse.com
- Rename devel package to libopts-devel
- Add corresponding obsoletion
* Tue May  3 2016 mpluskal@suse.com
- Fix typo in preun script
* Tue Apr 19 2016 mpluskal@suse.com
- Split shared libraries (boo#976068)
- Move info handling to preun section
- Do not ship .la file
* Mon Dec  7 2015 mpluskal@suse.com
- Update to 5.18.7
  * {AG,CL,GD}exe environment variables may be set to force
  bootstrapping with a particular release.
  * MAN_PAGE_DATE can be used with various man page docs to
  override the current date default.
  * project may now be bootstrapped and built in the source
  directory with no ill effect.
  * AutoGen as a daemon will never happen.  Last vestiges gone.
  * templates may now obtain the most recent source modification
  time with "(max-file-time)"
* Wed Sep 16 2015 mpluskal@suse.com
- Update to 5.18.6
  * {AG,CL,GD}exe environment variables may be set to force
    bootstrapping with a particular release.
  * MAN_PAGE_DATE can be used with various man page docs to
    override the current date default.
  * project may now be bootstrapped and built in the source
    directory with no ill effect.
  * AutoGen as a daemon will never happen.  Last vestiges gone.
  * templates may now obtain the most recent source modification
    time with "(max-file-time)"
* Thu May 21 2015 schwab@suse.de
- No longer call autoreconf
* Thu May 21 2015 mpluskal@suse.com
- Update info files dependencies
- Refresh partially upstreamed autogen-build_ldpath.patch
- Update to 5.18.5
  * Guile 1.6 is now obsolete.  1.7/8 or newer from now on.
    Fixed issues with Guile managed locale string processing.
    (It keeps getting better and better all the time and I
    must keep adjusting over and over all the time.)
  * more Guile-config somersaults
    config/misc.def: sometimes, "pkg-config --cflags-only-I" yields
    multiple directories for Guile and that incantation is the only
    way to find libguile/version.h and that header is the only way
    to determine the micro version and the micro version is the best
    way to check for certain types of breakage.  (Testing is too
    convoluted.)
  * for-each handler functions may now be able to free (or not)
    the file text via the "handler-frees" attribute.
* Mon Mar  2 2015 mpluskal@suse.com
- Remove upsteamed patch:
  * autoopts-remove-stupid-set-e.patch
  * agen5-testsuite.patch
- Cleanup spec file with spec-cleaner
- Use url for source
- Add gpg signature
- Update to 5.18.4
  * Do Not Edit (dne) warning:  the default of printing a date in
    the warning has now changed to not doing so.  The "-d" option
    to suppress the date is now deprecated (ignored).  A new
    option, "-D" will cause the date to be included.  The
    environment variable, "AUTOGEN_DNE_DATE" overrides everything.
  * The RETURN function was not completely implemented and only
    partially worked.  It is working now.
  * optionPrintVersionAndReturn() is a new function for applications
    that wish to extend the behavior of the "--version" option.
  * mdoc and man pages have been greatly improved.
  * libopts tear-off library used stdnoreturn.h and now includes
    infrastructure for systems deficient in that area
  * new function: insert-file  It will simply insert the contents
    of a file (or list of files) into the output stream.
* Fri Jul  4 2014 schwab@suse.de
- agen5-testsuite.patch: fix spurious testsuite failure
* Thu Jul  3 2014 schwab@suse.de
- Update to 5.18.3
  * ATTRIBUTE_FORMAT_ARG is a configured attribute that wraps
    __attribute__((__format_arg__(n))) procedure declaration attributes.
    To configure it, the ag_macros.m4 has a new macroo,
    AG_COMPILE_FORMAT_ARG (which is a compile only test probe).
  * Auto-edit Guile headers that depend upon configure values
    most especially:  noreturn
    but check for "ptrdiff_t" in our configure too, so that Guile does
    not create its own duplicate definition.
  * Abort from the failing function so that stack traces are useful
  * The libopts m4 configure code must configure the libopts/Makefile
  * Happy 2014 New Year
  * make sure library option handling code does nothing when the
    library is just trying to get information about an option.
  * Only apply texi2mdoc when it is needed.
  * The aoGetsText() emitted i18n helper function needs its argument
    to have the "format_arg" attribute.
  * documentation clarifications
  * properly create generated main procedures from user supplied code.
  * ChangeLog files have been removed from GIT sources
    (though still obtainable with tagged checkouts).
  * LIBGUILE_PATH is not needed and its derivation is wrong on
    where binaries and libraries have different prefixes.
  * fixed char casting issue that shows in UTF-8 files
  * fixed installation error for str2init
  * fixed failure handling in the usage template
  * fix broken flag values for auto-supported options
  * various tweaks to make Coverity happy.
  * allow the fatal error message functions to be tagged "noreturn"
    and incorporate sysnoreturn.h technology into AutoGen.
  * --save-opts documentation cleanup
  * optionMemberList() will return an allocated string containing
    the names of the bits set in the option.
  * tab stripped "here strings" include stripping the backslash
    escape character when it precedes any whitespace character.
- autoopts-remove-stupid-set-e.patch: remove stupid use of set -e
- autogen-setfilename.patch: remove
- autogen-build_ldpath.patch: regenerate
- run testsuite
* Tue Apr 16 2013 pth@suse.de
- Update to 5.16.2:
  * Coverity cleanups
  * evade Guile issue on BSD platform.
  * avoid emitting non-error messages to stderr
- Adapt autogen-build_ldpath.patch to the changed sources.
* Sat Mar  2 2013 seife+obs@b1-systems.com
- fix build with automake-1.13.1
- add explicit makeinfo buildrequires, it is required to build
* Sat Jul 14 2012 crrodriguez@opensuse.org
- Fix source URL, this update must reach 12.2 because
  autogen was generating broken C code that segfaults
  with fortify source.
* Tue May 22 2012 crrodriguez@opensuse.org
- Update to version 5.16
  * Changes, many see http://autogen.sourceforge.net/announce.html.
* Fri Sep 30 2011 coolo@suse.com
- add libtool as buildrequire to make the spec file more reliable
* Sat Sep 17 2011 jengelh@medozas.de
- Remove redundant tags/sections from specfile
- Use %%_smp_mflags for parallel build
* Tue Aug  2 2011 aj@suse.de
- Remove download source service.
* Mon Jul 25 2011 pgajdos@novell.com
- require pkg-config for build to detect guile-2.0
* Wed Mar  9 2011 coolo@novell.com
- update to 5.11.8:
  * many, many changes - see NEWS and ChangeLog
* Mon Sep 13 2010 pth@suse.de
- Add patch from dnh@opensuse.org to fix building the documentation
  with an uninstalled libopts.
* Thu Sep  9 2010 pth@suse.de
- Update to 5.11.1:
  * Fix (kill) orphaned shell program
  * add file-next-line functions to facilitate #line "C" directives
  * simplify some snprintfv code
  * implement dependency generation in autogen output.
  * fix up fmemopen()
  * Fixes for unusual shell programs
  * Remove guile option code
* Wed Apr  1 2009 crrodriguez@suse.de
- disable static libraries but keep "la" files, package uses
  libltdl
* Mon Jan 12 2009 schwab@suse.de
- Update to autogen 5.9.7.
  * several cleanups.
  * "more-help" is only supported with libopts is in use at run time.
    Allow for it to be expunged from the documentation.
  * Add a #define for the configured shell to config.h
  * add --used-defines to autogen.  You can now find out all the names
    that autogen looked up during processing.  That will include computed
    names and values passed to macros by name and it won't include names
    only referenced in sections of a template that were not processed.
    But it helps in documenting a template anyway.
* Mon Nov 17 2008 schwab@suse.de
- Update to autogen 5.9.6.
  * Hierarchically valued options can now be stored with ``--save-opt'' option
  * option state may now be "reset".  This is indistinguishable from the
    compiled state.  If option state is "saved" later, such an option will
    not appear in the save file.
  * there is a new option argument type:  time.  Its argument string
    represents years (?!), months, weeks, days, hours, minutes and seconds.
    The value seen by the program is an integer number of seconds.
    (This is not a date/time.)  The duration of a year is always 365 days
    and the duration of a month is always 30 days.
  * various obscure cleanups.
* Mon Jan  7 2008 schwab@suse.de
- Update to autogen 5.9.5.
  * integer number arguments may now have their values suffixed with
    one of the letters k/K/m/M/g/G/t/T to signify scaling by powers
    of 1000 (lower case) or 1024 (upper case).  Specify, "scaled".
  * AutoOpts "arg-type" may now be set to "file".  Existence of the directory
    portion of the name will be checked.  The existence (or not) of the actual
    file may also be checked.  Finally, the file may be pre-opened with either
    "fopen(3C)" or "open(2)".
  * The "columns" program now accepts a "--fill" option to cause it to fill
    text instead of filling columns.
  * The tests should no longer indirectly reference installed versions of
    the binaries.  They should all work out of the build directories.
* Mon Oct  8 2007 schwab@suse.de
- Update to autogen 5.9.3.
  * libopts requires strsignal, so the config test has been moved.
  * fixed ``--save'' option bug
  * programs may now choose to have config files kept in cannonical form
    ("C" locale), even if long option names are translated.  The option
    definition file must contain ``no-xlate = opt-cfg;'' or
    ``no-xlate = opt;''  See the documentation for details.
* Mon Jul 30 2007 schwab@suse.de
- Update to autogen 5.9.2.
  * GNU GPL v3 is now emitted with the "gpl" and "lgpl" functions.
  * usage.tpl template has been added.
  * getopt.tpl uses this template for constructing its usage string.
  * if "short-usage" or "full-usage" can be used to specify the form
    of the usage text:
  * not supplied -> compute it at run time
  * supplied, but empty -> use "usage.tpl" to compute it
  * is a variable name -> insert into option structure
  * is text -> emit the text and point to it from option structure
* Mon May  7 2007 schwab@suse.de
- Update to autogen 5.9.1.
  * getopt.tpl template is fixed to not require the internal header
    autoopts/autoopts.h.
  * MAXPATHLEN will use _MAX_PATH on Windows platforms
  * new libopts configuration option: --disable-optional-args This will #define
    NO_OPTIONAL_OPT_ARGS in config.h and cause the built library to ignore the
    OPTST_ARG_OPTIONAL bit in an option descriptor.  autoopts generated code
    compiled with NO_OPTIONAL_OPT_ARGS #defined will never have that bit set in
    the option descriptors either.  If libopts has been so configured, then the
    installed options.h header will contain: #define NO_OPTIONAL_OPT_ARGS 1 so
    that client code will generally be compiled with that flag set.
    The OPTST_ARG_OPTIONAL bit is ignored regardless.
  * Fixed up --load-opts environment variable processing.  You can
    now correctly suppress config file loading with either:
    PROGRAM_LOAD_OPTS=no
    PROGRAM=--no-load-opts
  * added new auto-supported option, --usage.  It is incorporated
    by specifying ``usage-opt;'' in the option definitions file.
  * libopts now uses several exit codes from sysexits.h:
    EX_NOINPUT  (66) - a specified config file cannot be found
    EX_SOFTWARE (70) - libopts error - please file a bug report
    EX_CONFIG   (78) - a NULL option descriptor was passed in - user bug
* Sun Feb 18 2007 schwab@suse.de
- Update to autogen 5.9.
  * a script for producing Debian packages is included
  * including of templates and definitions now works more like
    ``#include "foo"'' instead of ``#include <foo>''.
  * fixed sizeof(int) != sizeof(size_t) bug.
  * fixed incorrect argument number format string
* Mon Jan 29 2007 schwab@suse.de
- Update to autogen 5.8.9.
  * GREP is now a configurable.  (Sheesh!)
  * options with hierarchical structure (nested values) had some
    bugs in the config file parsing code.  Fixed.
  * Since YACC is not used any more, it is no longer required. :)
* Sun Oct 15 2006 schwab@suse.de
- Update to autogen 5.8.7.
  * Tweaks for Windows' compat/windows-config.h
  * new string-table convenience functions:  string-table-add-ref and
    string-table-size
  * fixed a value referencing bug in enumeration arg handling
    (seen on platforms where sizeof(int) != sizeof(void*)).
* Fri Oct 13 2006 aj@suse.de
- add guile-devel buildrequires.
* Thu Oct 12 2006 ro@suse.de
- added gmp-devel to buildrequires (guile)
* Mon Oct  9 2006 schwab@suse.de
- Update to autogen 5.8.6.
  * AutoOpts code presumed that there were no #defines for the option
    names.  You can now force aside such conflicts.
  * AutoOpts generated code unconditionally #includes limits.h and stdint.h.
  * aliased pointer cleanups should allow higher optimization of code.
  * The installation of the tear-off libopt library is now optional
    to the installers of client projects.
* Mon May 15 2006 schwab@suse.de
- Update to autogen 5.8.5.
  * ag-fprintf will now allow you to emit text into a suspended output stream.
  * string tables have been implemented as a scheme function.  This makes it
    very easy to produce an array of characters containing NUL termintaed
    strings and have these string offsets (indexes) available for indexing into
    the string arrays.
  * The libopts code will omit Windows-unfriendly code if the compile defines
    _WIN32 and does not define __CYGWIN__.
  * suffix specifications in the pseudo macro may now construct an output
    file name format string using scheme code, a la:
    [= autogen5 template
    h=(string-append (getenv "TMPDIR") "/%%s-hdr.h")  =]
    The "%%s" will still be replaced by the base name.
  * the scheme function "version-compare" will allow you to compare
    two dotted version numbers.  These can be your own versions or
    that of autogen.  The scheme variable ``autogen-version'' has been
    around for a long time and may be used as one of the arguments.
  * #assert is now active in definition files.  If the text begins
    with a back quote, it is handed off to the shell for processing.
    If an open parenthesis, it is handed off to Guile.  If it is
    anything else, it is ignored.
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Sun Jan 15 2006 schwab@suse.de
- Run %%install_info.
* Fri Jan 13 2006 schwab@suse.de
- Update to autogen 5.8.1.
* Tue Jan 10 2006 schwab@suse.de
- Run ldconfig in %%post.
* Mon Jan  9 2006 schwab@suse.de
- Update to autogen 5.8.
* Fri Oct 14 2005 schwab@suse.de
- Fix strict-aliasing bugs.
* Tue Oct 11 2005 schwab@suse.de
- Update to autogen 5.7.3.
* Tue Aug  2 2005 schwab@suse.de
- Update to autogen 5.7.2.
* Fri Apr 29 2005 schwab@suse.de
- Update to autogen 5.7.
* Tue Mar 29 2005 schwab@suse.de
- Update to autogen 5.6.6.
* Mon Jan 10 2005 schwab@suse.de
- Update to autogen 5.6.5.
* Thu Nov 11 2004 ro@suse.de
- fixed file list
* Sat Nov  6 2004 schwab@suse.de
- Initial version 5.6.4.
