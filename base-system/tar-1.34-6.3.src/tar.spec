#
# spec file for package tar
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


# For correct subpackages docs installation into tar doc directory
%global _docdir_fmt %{name}
Name:           tar
Version:        1.34
Release:        6.3
Summary:        GNU implementation of ((t)ape (ar)chiver)
License:        GPL-3.0-or-later
Group:          Productivity/Archiving/Backup
URL:            https://www.gnu.org/software/tar/
Source0:        https://ftp.gnu.org/gnu/tar/%{name}-%{version}.tar.xz
Source1:        https://ftp.gnu.org/gnu/tar/%{name}-%{version}.tar.xz.sig
# http://wwwkeys.pgp.net:11371/pks/lookup?op=get&search=0x3602B07F55D0C732
Source2:        %{name}.keyring
Patch0:         %{name}-wildcards.patch
Patch1:         %{name}-backup-spec-fix-paths.patch
Patch2:         paxutils-rtapelib_mtget.patch
# don't print warning about zero blocks
# the patch is used in Fedora and Debian
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=235820
Patch3:         %{name}-ignore_lone_zero_blocks.patch
# The next patch is disabled because it causes a regression:
#https://bugzilla.opensuse.org/show_bug.cgi?id=918487
Patch4:         %{name}-recursive--files-from.patch
Patch5:         add_readme-tests.patch
Patch6:         tar-PIE.patch
Patch7:         tests-skip-time01-on-32bit-time_t.patch
#BuildRequires:  automake >= 1.15
#BuildRequires:  libacl-devel
#BuildRequires:  libselinux-devel
Recommends:     %{name}-rmt = %{version}
Recommends:     mt
Recommends:     xz
Recommends:     zstd
Provides:       base:/bin/tar

%description
GNU Tar is an archiver program. It is used to create and manipulate files
that are actually collections of many other files; the program provides
users with an organized and systematic method of controlling a large amount
of data. Despite its name, that is an acronym of "tape archiver", GNU Tar
is able to direct its output to any available devices, files or other programs,
it may as well access remote devices or files.

%package backup-scripts
Summary:        Backup scripts
Group:          Productivity/Archiving/Backup
Requires:       %{name} = %{version}
BuildArch:      noarch

%description backup-scripts
Shell scripts for system backup/restore

%package tests
Summary:        Tests for the package
Group:          Development/Tools/Other
Requires:       %{name} = %{version}

%description tests
Upstream testsuite for the package

%package rmt
Summary:        Remote tape drive control server by GNU
Group:          Productivity/Archiving/Backup
Requires(post): update-alternatives
Requires(postun):update-alternatives
Provides:       rmt

%description rmt
Provides remote access to files and devices for tar, cpio
and similar backup utilities

%package doc
Summary:        Documentation files for GNU tar
Group:          Documentation/Man
Requires:       %{name} = %{version}
BuildArch:      noarch

%description doc
GNU Tar is an archiver program. It is used to create and manipulate files
that are actually collections of many other files; the program provides
users with an organized and systematic method of controlling a large amount
of data. Despite its name, that is an acronym of "tape archiver", GNU Tar
is able to direct its output to any available devices, files or other programs,
it may as well access remote devices or files.

%package lang
Summary:	Translations for package tar
Group:		Documentation/Man
Requires:	%{name} = %{version}
BuildArch:	noarch

%description lang
Provides translations for the "tar" package.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
#%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
%define my_cflags -W -Wall -Wpointer-arith -Wstrict-prototypes -Wformat-security -Wno-unused-parameter -fPIE
export CFLAGS="%{optflags} %{my_cflags}"
export RSH=%{_bindir}/ssh
export DEFAULT_ARCHIVE_FORMAT="POSIX"
export DEFAULT_RMT_DIR=%{_bindir}
autoreconf -fi
%configure \
	gl_cv_func_linkat_follow="yes" \
	--enable-backup-scripts \
	--disable-silent-rules \
	--program-transform-name='s/^rmt$/gnurmt/'
%make_build LDFLAGS="-pie"
cd tests
%make_build genfile
mkdir bin
mv genfile bin
cd -

%check
%if !0%{?qemu_user_space_build:1}
# Checks disabled in qemu because of races happening when we emulate
# multi-threaded programs
%make_build check || { cat tests/testsuite.log; exit 1; }
%endif

%install
%make_install DESTDIR=%{buildroot}
mkdir %{buildroot}/bin
mv %{buildroot}%{_mandir}/man8/gnurmt.8 %{buildroot}%{_mandir}/man1/gnurmt.1
install -D -m 644 scripts/backup-specs %{buildroot}%{_sysconfdir}/backup/backup-specs
# For avoiding file conflicts with dump/restore
mv %{buildroot}%{_sbindir}/restore %{buildroot}%{_sbindir}/restore.sh
rm -f %{buildroot}%{_infodir}/dir
install -D -m 644 -t %{buildroot}%{_docdir}/%{name} README* ABOUT-NLS AUTHORS NEWS THANKS \
							ChangeLog TODO
install -d -m 755 %{buildroot}%{_localstatedir}/lib/tests
cp -r tests %{buildroot}%{_localstatedir}/lib/tests/tar
rm %{buildroot}%{_localstatedir}/lib/tests/tar/*.{c,h,o}
rm %{buildroot}%{_localstatedir}/lib/tests/tar/package.m4
rm %{buildroot}%{_localstatedir}/lib/tests/tar/{atconfig,atlocal,Makefile}*
# Alternatives system
mkdir -p %{buildroot}%{_sysconfdir}/alternatives
ln -sf %{_sysconfdir}/alternatives/rmt %{buildroot}%{_bindir}/rmt
ln -sf %{_sysconfdir}/alternatives/rmt.1%{ext_man} %{buildroot}%{_mandir}/man1/rmt.1%{ext_man}
%if !0%{?usrmerged}
mkdir -p %{buildroot}/bin
ln -s %{_bindir}/%{name} %{buildroot}/bin
%endif
%find_lang %{name}

%post rmt
%{_sbindir}/update-alternatives --force \
    --install %{_bindir}/rmt rmt %{_bindir}/gnurmt 10 \
    --slave %{_mandir}/man1/rmt.1%{ext_man} rmt.1%{ext_man} %{_mandir}/man1/gnurmt.1%{ext_man}

%postun rmt
if [ ! -f %{_bindir}/gnurmt ] ; then
   "%{_sbindir}/update-alternatives" --remove rmt %{_bindir}/gnurmt
fi

%files backup-scripts
%{_sbindir}/backup
%{_sbindir}/restore.sh
%{_libexecdir}/backup.sh
%{_libexecdir}/dump-remind
%dir %{_sysconfdir}/backup
%config(noreplace) %{_sysconfdir}/backup/backup-specs

%files lang -f %{name}.lang

%files tests
%{_localstatedir}/lib/tests
%{_docdir}/%{name}/README-tests

%files rmt
%ghost %{_bindir}/rmt
%{_bindir}/gnurmt
%ghost %{_mandir}/man1/rmt.1%{ext_man}
%{_mandir}/man1/gnurmt.1
%ghost %{_sysconfdir}/alternatives/rmt
%ghost %{_sysconfdir}/alternatives/rmt.1%{ext_man}

%files doc
%dir %{_docdir}/%{name}
%{_docdir}/%{name}/NEWS
%{_docdir}/%{name}/README
%{_docdir}/%{name}/ABOUT-NLS
%{_docdir}/%{name}/AUTHORS
%{_docdir}/%{name}/THANKS
%{_docdir}/%{name}/ChangeLog
%{_docdir}/%{name}/TODO
%{_infodir}/%{name}.info
%{_infodir}/%{name}.info-1
%{_infodir}/%{name}.info-2

%files
%license COPYING
%if !0%{?usrmerged}
/bin/%{name}
%endif
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1

%changelog
* Wed Apr 13 2022 William Brown <william.brown@suse.com>
- Add recommends to zstd, a modern fast compression type.
* Thu Oct 14 2021 Bernhard Voelker <mail@bernhard-voelker.de>
- tests-skip-time01-on-32bit-time_t.patch: Add patch to skip test
  'tests/time01.at' on platforms with 32-bit time_t for now.
- tar.spec: Reference it.
  (%%check): Output the testsuite.log in case the testsuite failed.
* Fri Oct  8 2021 Danilo Spinella <danilo.spinella@suse.com>
- The following issues have already been fixed in this package but
  weren't previously mentioned in the changes file:
  * bsc#1181131, CVE-2021-20193
  * bsc#1120610
* Wed Jun  9 2021 Wolfgang Frisch <wolfgang.frisch@suse.com>
- Link /var/lib/tests/tar/bin/genfile as Position-Independent Executable
  (bsc#1184124).
  + tar-PIE.patch
* Sun Feb 14 2021 Andreas Stieger <andreas.stieger@gmx.de>
- GNU tar 1.34:
  * Fix extraction over pipe
  * Fix memory leak in read_header
  * Fix extraction when . and .. are unreadable
  * Gracefully handle duplicate symlinks when extracting
  * Re-initialize supplementary groups when switching to user
    privileges
* Sat Jan  9 2021 Andreas Stieger <andreas.stieger@gmx.de>
- GNU tar 1.33:
  * POSIX extended format headers do not include PID by default
  * --delay-directory-restore works for archives with reversed
    member ordering
  * Fix extraction of a symbolic link hardlinked to another
    symbolic link
  * Wildcards in exclude-vcs-ignore mode don't match slash
  * Fix the --no-overwrite-dir option
  * Fix handling of chained renames in incremental backups
  * Link counting works for file names supplied with -T
  * Accept only position-sensitive (file-selection) options in file
    list files
- remove deprecated texinfo packaging macros
* Mon Oct 19 2020 Ludwig Nussel <lnussel@suse.de>
- prepare usrmerge (boo#1029961)
* Fri Apr  3 2020 Dominique Leuenberger <dimstar@opensuse.org>
- Drop Requires(pre) info in the preamble: the main package does
  not contain any info files, and has not even a pre script. The
  - doc subpackage already has the correct deps.
* Fri Jan 31 2020 Bjørn Lie <bjorn.lie@gmail.com>
- No longer recommend -lang: supplements are in use.
* Mon Mar 25 2019 Kristýna Streitová <kstreitova@suse.com>
- update to version 1.32
  * Fix the use of --checkpoint without explicit --checkpoint-action
  * Fix extraction with the -U option
  * Fix iconv usage on BSD-based systems
  * Fix possible NULL dereference (savannah bug #55369)
    [bsc#1130496] [CVE-2019-9923]
  * Improve the testsuite
- remove tar-1.31-tests_dirrem.patch and
  tar-1.31-racy_compress_tests.patch that are no longer needed
  (applied usptream)
* Fri Mar 15 2019 Cristian Rodríguez <crrodriguez@opensuse.org>
- Remove libattr-devel from buildrequires, tar no longer uses
  it but finds xattr functions in libc.
* Thu Feb 14 2019 kstreitova@suse.com
- update to version 1.31
  * Fix heap-buffer-overrun with --one-top-level, bug introduced
    with the addition of that option in 1.28
  * Support for zstd compression
  * New option '--zstd' instructs tar to use zstd as compression
    program. When listing, extractng and comparing, zstd compressed
    archives are recognized automatically. When '-a' option is in
    effect, zstd compression is selected if the destination archive
    name ends in '.zst' or '.tzst'.
  * The -K option interacts properly with member names given in the
    command line. Names of members to extract can be specified along
    with the "-K NAME" option. In this case, tar will extract NAME
    and those of named members that appear in the archive after it,
    which is consistent with the semantics of the option. Previous
    versions of tar extracted NAME, those of named members that
    appeared before it, and everything after it.
  * Fix CVE-2018-20482 - When creating archives with the --sparse
    option, previous versions of tar would loop endlessly if a
    sparse file had been truncated while being archived.
- remove the following patches (upstreamed)
  * tar-1.30-tests-difflink.patch
  * tar-1.30-tests_dirrem_race.patch
- refresh add_readme-tests.patch
- add tar-1.31-tests_dirrem.patch to fix expected output in dirrem
  tests
- add tar-1.31-racy_compress_tests.patch to fix compression tests
* Fri May 11 2018 kstreitova@suse.com
- add tar-1.30-tests_dirrem_race.patch to fix race in dirrem01 and
  dirrem02 tests that were passing/failing randomly because of that
- run spec-cleaner
- renumber patches
* Tue Apr  3 2018 kukuk@suse.de
- Use %%license instead of %%doc [bsc#1082318]
* Thu Jan  4 2018 kstreitova@suse.com
- add tar-1.30-tests-difflink.patch to fix difflink.at test
  (https://www.mail-archive.com/bug-tar@gnu.org/msg05440.html)
* Mon Dec 18 2017 avindra@opensuse.org
- GNU tar 1.30:
  * Member names containing '..' components are now skipped when
    extracting.
  * Report erroneous use of position-sensitive options.
  * --numeric-owner now affects private headers too.
  * Fixed the --delay-directory-restore option
  * The --warnings=failed-read option
  * The --warnings=none option now suppresses all warnings
  * Fix reporting of hardlink mismatches during compare
- cleanup with spec-cleaner
- switch all urls to https
- drop upstreamed patches
  * add-return-values-to-backup-scripts.patch
  * tar-1.29-extract_pathname_bypass.patch
- rebase add_readme-tests.patch
* Thu Apr 20 2017 kstreitova@suse.com
- remove tar-1.26-remove_O_NONBLOCK.patch as this issue was fixed
  in tar 1.27 (commit 03858cf583ce299b836d8a848967ce290a6bf303)
* Mon Apr  3 2017 svalx@svalx.net
- Use update-alternatives according to current documentation
* Mon Mar 27 2017 svalx@svalx.net
- Disable tar-1.26-remove_O_NONBLOCK.patch - this issue has been
  fixed in tar-1.27
- backup-scripts subpackage change to noarch
- Change rpm group of tar-tests to Development/Tools/Other
- Enable rmt building, change package description
- Switch rmt to alternatives system
- Separate rmt subpackage - it can be used by different archiving
  tools as a dedicated program
- Change rmt path to /usr/bin folder - it can be used by non privileged
  users for backup purposes. Security is controlled by access rights to
  the targets and remote shell.
- Separate doc subpackage
- Remove conditions for old SUSE builds and lang subpackage
- Rename restore script to restore.sh for avoiding file conflicts
  with dump/restore
* Thu Mar 23 2017 kstreitova@suse.com
- move binaries from /bin to /usr/bin [bsc#1029977]
  * refresh tar-backup-spec-fix-paths.patch to change path of the
    tar binary from TAR=/bin/tar to TAR=/usr/bin/tar
- use spec-cleaner
* Thu Dec 15 2016 vcizek@suse.com
- update tar-1.29-extract_pathname_bypass.patch to the upstream
  one that fixes POINTYFEATHER issue but it doesn't limit append or
  create operations as the initial patch did [bsc#1012633]
  [CVE-2016-6321]
* Tue Nov  8 2016 kstreitova@suse.com
- add tar-1.29-extract_pathname_bypass.patch to fix POINTYFEATHER
  vulnerability - GNU tar archiver can be tricked into extracting
  files and directories in the given destination, regardless of the
  path name(s) specified on the command line [bsc#1007188]
  [CVE-2016-6321]
* Sat May 28 2016 astieger@suse.com
- GNU tar 1.29:
  * New options: --verbatim-files-from, --no-verbatim-files-from
  * --null option reads file names verbatim
  * New options: --owner-map=FILE and --group-map=FILE
  * New option --clamp-mtime
  * Deprecated --preserve option removed
  * Sparse file detection - now uses SEEK_DATA/SEEK_HOLE on
    systems that support it. This allows for considerable speed-up
    in sparse-file detection. New option --hole-detection for
    algorithm selection.
* Wed Mar 23 2016 svalx@svalx.net
- Add add-return-values-to-backup-scripts.patch
* Mon Apr 13 2015 vcizek@suse.com
- Revert tar-recursive--files-from.patch because it causes regression
  (bnc#918487, bnc#919233)
* Mon Feb  9 2015 vcizek@suse.com
- extract files recursively with --files-from (bnc#913058)
  * added tar-recursive--files-from.patch
- call autoreconf in %%prep
* Sun Dec 21 2014 meissner@suse.com
- build with PIE
* Thu Nov 20 2014 andreas.stieger@gmx.de
- compile in ACLs, Xattr and selinux support [boo#906413]
* Fri Aug 29 2014 jengelh@inai.de
- Improve on RPM group classification
* Sat Aug  2 2014 andreas.stieger@gmx.de
- GNU tar 1.28:
  * New --checkpoint-action=totals
  * Extended checkpoint format specification
  * New option --one-top-level
  * New option --sort
  * New exclusion options:
  - -exclude-ignore=FILE
  - -exclude-ignore-recursive=FILE
  - -exclude-vcs-ignores
  * refuses to read input from and write output to a tty
- packaging changes:
  * adjust patch for context change: add_readme-tests.patch
  * remove patch applied upstream:
    tar-fix_eternal_loop_in_handle_option.patch
* Mon Jul 28 2014 vcizek@suse.com
- don't print lone zero blocks warning (bnc#881863)
  * there are many tar implementations around that create invalid
    archives with a zero block in the middle
  * https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=235820
  * added tar-ignore_lone_zero_blocks.patch from Fedora
* Wed Mar 26 2014 vcizek@suse.com
- fix an infinite loop in handle_option (bnc#867919 and bnc#870422)
  * added tar-fix_eternal_loop_in_handle_option.patch
* Tue Jan  7 2014 llipavsky@suse.com
- add tests subpackage.
  * It is the same testsuite that is run during make check.
  * It is now possible to run it in real system to verify that
    nothing is broken by incompatible libraries, etc.
- add add_readme-tests.patch: README for testsuite
* Tue Nov 19 2013 andreas.stieger@gmx.de
- update to 1.27.1
  * Fix unquoting of file names obtained via the -T option.
  * Fix GNU long link header timestamp (backward compatibility).
  * Fix extracting sparse members from star archives.
* Thu Oct 24 2013 andreas.stieger@gmx.de
- update to 1.27
- bug fixes:
  * PAX-format sparse archive files no longer restricted to 8 GiB.
  * adjust diagnostics and output to GNU coding
- new features:
  * The --owner and --group options now accept numeric IDs
  * restore traditional functionality of --keep-old-files and
  - -skip-old-files, treat existing file as errors for the former
  * --warning=existing-file gives verbose notice for this
  * Support for POSIX ACLs, extended attributes and SELinux context
  - -xattrs, --acls and --selinux and their `--no-' counterparts
  - -xattrs-include and --xattrs-exclude allows selective control
  * Any option taking a command name as its argument now accepts a
    full command line as well:
  - -checkpoint-action=exec
  - I, --use-compress-program
  - F, --info-script
  - -to-command
  * environment variables supplied to such commands can now be used
    in the command line itself
  * New warning control option --warning=[no-]record-size controls
    display of actual record size, if it differs from the default
  * New command line option --keep-directory-symlink to disable
    default behaviour that unlinks exising symbolic link for an
    extracted directory of the corresponding name
- packaging changes:
  * drop tar-1.26-stdio.in.patch, committed upstream
  * drop config-guess-sub-update.patch, newer version in upstream
  * verify source signature
* Thu Aug 22 2013 vcizek@suse.com
- added fix for paxutils rtapelib which is bundled with tar.
  the very same fix was added to cpio too (bnc#658031)
  * paxutils-rtapelib_mtget.patch
* Fri Apr  5 2013 idonmez@suse.com
- Add Source URL, see https://en.opensuse.org/SourceUrls
* Sat Feb  2 2013 schwab@suse.de
- Add config-guess-sub-update.patch:
  Update config.guess/sub for aarch64
* Tue Jul 17 2012 aj@suse.de
- Fix build failure with undefined gets (glibc 2.16).
* Wed May 30 2012 sweet_f_a@gmx.de
- avoid automake dependency
* Fri Apr 20 2012 crrodriguez@opensuse.org
- disable 'runtime checks' in m4/*.m4 that override
  system calls with custom implementations to workaround
  very old kernel/libc bugs (dating 2003-2009)
  we do not ship those buggy components nowdays.
* Fri Apr 20 2012 crrodriguez@opensuse.org
- Switch to default archive type to POSIX.1-2001, which is ten years
  old and has no limits on filesize,filename length etc.
* Mon Dec 19 2011 tcech@suse.cz
- tar-1.26-remove_O_NONBLOCK.patch:
  don't use O_NONBLOCK as a flag for read,
  when file is offline, read with O_NONBLOCK returns EAGAIN,
  but tar doesn't handle it
  (bnc#737331)
* Sun Oct 30 2011 dmueller@suse.de
- disable testsuite on qemu build
* Wed Oct  5 2011 sweet_f_a@gmx.de
- minor portability fixes
* Thu Sep 29 2011 sweet_f_a@gmx.de
- spec cleaner, avoid some deprecated macros
- fix non-utf8-spec-file
- fix macro-in-comment
- enable make check
- remove upstream-fixed/obsolete patches (fortifysourcessigabrt,
  disable-listed02-test, disable_languages)
- call help2man inside specfile instead of paching tar's build chain
* Tue Mar 15 2011 puzel@novell.com
- update to tar-1.26
  * Fix the --verify option, which broke in version 1.24.
  * Fix storing long sparse file names in PAX archives.
  * Fix correctness of --atime-preserve=replace
  * tar --atime-preserve=replace no longer tries to restore atime of
    zero-sized files.
  * Fix bug with --one-file-system --listed-incremental
* Wed Nov 24 2010 puzel@novell.com
- fix tar-backup-scripts (bnc#654199)
- add tar-backup-spec-fix-paths.patch
- cleanup spec
* Tue Nov  9 2010 puzel@novell.com
- update to tar-1.25
  * Fix extraction of empty directories with the -C option in effect.
  * Fix extraction of device nodes.
  * Make sure name matching occurs before eventual name transformation.
  * Fix the behavior of tar -x --overwrite on hosts lacking O_NOFOLLOW.
  * Support alternative decompression programs.
- update to tar-1.24
  * The new --full-time option instructs tar to output file
    time stamps to the full resolution.
  * More reliable directory traversal when creating archives
  * When extracting symbolic links, tar now restores attributes
    such as last-modified time and link permissions, if the
    operating system supports this.
  * The --dereference (-h) option now applies to files that are
    copied into or out of archives, independently of other options.
  * When receiving SIGPIPE, tar would exit with error status and
    "write error" diagnostics.
- disable-silent-rules
- updated tar-fortifysourcessigabrt.patch
* Mon Jun 28 2010 jengelh@medozas.de
- use %%_smp_mflags
* Fri Mar 12 2010 mseben@novell.com
- updated to version 1.23
  * Improved record size autodetection
  * Use of lseek on seekable archives
  * New command line option --warning
  * New command line option --level
  * Improved behavior if some files were removed during incremental dumps
  * Modification times of PAX extended headers
  * Time references in the --pax-option argument
  * Augmented environment of the --to-command script
  * Fix handling of hard link targets by -c --transform
  * Fix hard links recognition with -c --remove-files
  * Fix restoring files from backup (debian bug #508199)
  * Correctly restore modes and permissions on existing directories
  * The --remove-files option removes files only if they were succesfully stored in the archive
  * Fix storing and listing of the volume labels in POSIX format
  * Improve algorithm for splitting long file names (ustar format)
  * Fix possible memory overflow in the rmt client code (CVE-2010-0624)
- deprecated heap_overflow_in_rtapelib.patch
* Wed Mar  3 2010 mseben@novell.com
- added heap_overflow_in_rtapelib.patch fix possible heap overflow in
  rtapelib.c (bnc#579475)
* Tue Feb  2 2010 mseben@novell.com
- updated to version 1.22
  * Support for xz compression (--xz option)
  * Short option -J is reassigned as a shortcut for --xz
  * The option -I is a shortcut for --use-compress-program
  * The --no-recursive option works with --incremental
- deprecated recognize_xz.patch
- created tar-backup-scripts subpackage (bnc#574688)
* Sun Dec  6 2009 jengelh@medozas.de
- enable parallel building
* Fri Dec  4 2009 meissner@suse.de
- fixed FORTIFY_SOURCE=2 issue with gcc 4.5.
* Sun Aug 30 2009 aj@suse.de
- recommend not require language subpackage
* Tue Mar  3 2009 pth@suse.de
- Recognize .xz as lzma archive.
* Wed Feb 11 2009 coolo@suse.de
- update to version 1.21
  * New short option -J - A shortcut for --lzma.
  * New option --lzop
  * Compressed format recognition
  * Using --exclude-vcs handles also files used internally by
    Bazaar, Mercurial and Darcs.
- split out language subpackage
- recommend xz instead of the old name of lzma
* Wed Nov 19 2008 mkoenig@suse.de
- fix incremental backup with wildcard option [bnc#445411]
* Mon Jun 23 2008 mkoenig@suse.de
- update to version 1.20:
  * new options: --auto-compress, --lzma, --hard-dereference,
  - -checkpoint-action, --(no-)check-device, --transform
  * Add recommends tag for lzma
- removed patches:
  tar-gcc43.patch
  tar-1.19-update_flag.patch
* Fri Mar 28 2008 mkoenig@suse.de
- apply upstream patch to avoid error message when updating
  an archive that does not exist [bnc#347525]
* Wed Nov 14 2007 mkoenig@suse.de
- update to version 1.19
  * New option --exclude-vcs
  * --exclude-tag and --exclude-cache options now work under
    incremental archives
  * Fix handling of renamed files in listed incremental archives
  * Fix --version output
  * Recognition of broken archives
- merged patches:
  tar-1.15.1-CVE-2001-1267.patch
  tar-1.17-paxlib-owl-alloca.patch
* Fri Oct  5 2007 mkoenig@suse.de
- update to version 1.18
  Licensed under the GPLv3
- merged patches:
  tar-1.17-testsuite12.patch
* Mon Oct  1 2007 mkoenig@suse.de
- fix build with gcc-4.3
* Fri Aug 31 2007 mkoenig@suse.de
- fixed another directory traversal vulnerability, CVE-2001-1267,
  CVE-2002-0399, [#29973]
* Mon Aug 20 2007 mkoenig@suse.de
- use correct patch for paxlib stack overflow [#301416]
* Fri Aug 17 2007 lmichnovic@suse.cz
- upstream fix: use of alloca can cause stack overflow
  (paxlib-owl-alloca.patch)
* Thu Jun 21 2007 mkoenig@suse.de
- update to version 1.17:
  * Fix archivation of sparse files in posix mode
  * Fix operation of --verify --listed-incremental
  * Fix --occurence
  * Scope of --transform and --strip-components options
  * End-of-volume script can send the new volume name to tar
- remove patch (fixed upstream)
  tar-1.6.1-futimens.patch
- fix test 12
  tar-1.17-testsuite12.patch
* Tue May 22 2007 mkoenig@suse.de
- fix build
* Tue May 15 2007 coolo@suse.de
- use %%find_lang
* Wed Jan 24 2007 mkoenig@suse.de
- update to version 1.16.1:
  * tar-1.16-CVE-2006-6097.patch merged upstream
  * tar-1.16-xheader_unused.patch merged upstream
  * New option --exclude-tag
  * The --exclude-cache option excludes directories that
    contain the CACHEDIR.TAG file from being archived
  * Race conditions have been fixed that in some cases briefly
    allowed files extracted by 'tar -x --same-owner' to be
    accessed by users that they shouldn't have been.
* Tue Dec  5 2006 mkoenig@suse.de
- update to version 1.16:
  Bugfixes:
  * Avoid running off file descriptors when using multiple -C options.
  * tar --index-file=FILE --file=- sent the archive to FILE, and
    the listing to stderr.
  * Detect attempts to update compressed archives.
  * Allow non-option arguments to be interspersed with options.
  * Previous version created invalid archives when files shrink
    during reading.
  * Compare mode (tar d) hanged when trying to compare file contents.
  * Previous versions in certain cases failed to restore directory
    modification times.
  New features:
  * New option --mtime allows to set modification times
  * New option --transform allows to transform file names before
    storing
  * --strip-components option works when deleting and comparing.
  * New option --show-transformed-names
  * Short option -l is now an alias of --check-links option,
    which complies with UNIX98
  * The --checkpoint option takes an optional argument specifying
    the number of records between the two successive checkpoints.
  * The --totals option can be used with any tar operation
  * Any number of -T (--files-from) options may be used in the
    command line.
  * List files containing null-separated file names are detected
    and processed automatically.
  * New option --no-unquote disables the unquoting of input file
    names.
  * New option --test-label tests the archive volume label.
  * New option --show-stored-names.
  * New option --to-command pipes the contents of archive members
    to the specified command.
  * New option --atime-preserve=system
  * New option --delay-directory-restore
  * New option --restrict prohibits use of some potentially harmful
    tar options.
  * New options --quoting-style and --quote-chars control the way
    tar quotes member names on output.
  * Better support for full-resolution time stamps.
  Incompatible changes:
  * tar no longer uses globbing by default
- remove unused variable [#223847]
- create man page via help2man
- remove support for mangled names, due to security reasons
  CVE-2006-6097 [#223185]
* Mon Jul 24 2006 rguenther@suse.de
- Do not build-depend on rsh, but provide the RSH environment.
* Mon Feb 27 2006 kssingvo@suse.de
- fixed buffer overflow issue CVE-2006-0300 (bugzilla#151516)
- not affected: traversal bug CVE-2005-1918 (bugzilla#145081)
* Sat Feb 18 2006 aj@suse.de
- Fix build.
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Thu Sep  1 2005 mmj@suse.de
- Add patch from upstream for fixing sparse files > 4GB [#114540]
* Fri Jun 24 2005 schwab@suse.de
- Fix broken test.
* Fri Apr  8 2005 uli@suse.de
- ignore test suite fails on ARM
* Wed Mar  9 2005 mmj@suse.de
- Make gcc4 happy
* Tue Feb  1 2005 mmj@suse.de
- Disable test that breaks on reiserfs due to that filesystems
  limitations. Tar works fine on reiserfs.
* Tue Dec 21 2004 mmj@suse.de
- Update to 1.15.1 which fixes a bug introduced in 1.15 which caused
  tar to refuse to extract files from standard input.
* Tue Dec 21 2004 mmj@suse.de
- Update to tar-1.15 including:
- Features:
  o Compressed archives are recognised automatically, it is no
    longer necessary to specify -Z, -z, or -j options to read
    them.  Thus, you can now run `tar tf archive.tar.gz'.
  o When restoring incremental dumps, --one-file-system option
    prevents directory hierarchies residing on different devices
    from being purged. With the previous versions of tar it was
    dangerous to create incremental dumps with --one-file-system
    option, since they would recursively remove mount points when
    restoring from the back up. This change fixes the bug.
  o Renamed --strip-path to --strip-components for consistency with
    the GNU convention.
  o Skipping archive members is sped up if the archive media supports
    seeks.
  o Restore script starts restoring only if it is given --all (-a)
    option, or some patterns. This is to prevent accidental restores.
  o `tar --verify' prints a warning if during archive creation some of
    the file names had their prefixes stripped off.
  o New option --exclude-caches instructs tar to exclude cache
    directories automatically on archive creation. Cache directories
    are those containing a standardized tag file, as specified at:
    http://www.brynosaurus.com/cachedir/spec.html
  o New configure option --with-rmt allows to specify full path
    name to the `rmt' utility. This supercedes DEFAULT_RMT_COMMAND
    variable introduced in version 1.14
  o New configure variable DEFAULT_RMT_DIR allows to specify the
    directory where to install `rmt' utility. This is necessary
    since modifying --libexecdir as was suggested for version 1.14
    produced a side effect: it also modified installation prefix
    for backup scripts (if --enable-backup-scripts was given).
- Bugfixes:
  o Fixed flow in recognizing files to be included in incremental dumps.
  o Correctly recognize sparse archive members when used with -T option.
  o GNU multivolume headers cannot store filenames longer than
    100 characters.  Do not allow multivolume archives to begin
    with such filenames.
  o If a member with link count > 2 was stored in the archive twice,
    previous versions of tar were not able to extract it, since they
    were trying to link the file to itself, which always failed and
    lead to removing the already extracted copy. Preserve the first
    extracted copy in such cases.
  o Restore script was passing improper argument to tar --listed
    option (which didn't affect the functionality, but was
    logically incorrect).
  o Fixed verification of created archives.
  o Fixed unquoting of file names containing backslash escapes (previous
    versions failed to recognize \a and \v).
  o When attempting to delete a non-existing member from the
    archive, previous versions of tar used to overwrite last
    archive block with zeroes.
* Mon Aug  9 2004 mmj@suse.de
- Add patch from snwint with long filename fix [#43538]
* Sun May 30 2004 mmj@suse.de
- Update to 1.14 which is the first stable release of tar
  since 1999.
* Thu Apr 15 2004 mmj@suse.de
- Fix detection of remote paths [#38709]. Thanks Jürgen!
* Tue Apr 13 2004 mmj@suse.de
- Update to 1.13.94 including fix for [#16531]
* Sat Jan 10 2004 adrian@suse.de
- build as user
* Fri Jun 20 2003 ro@suse.de
- build with current gettext
* Thu May 15 2003 pthomas@suse.de
- Remove unneeded files from build root.
- Add autoconf tests to properly guard K&R prototypes
- Clean up signed/unsigned compares.
* Thu Apr 24 2003 ro@suse.de
- fix install_info --delete call and move from preun to postun
* Fri Feb  7 2003 ro@suse.de
- added install_info macros
* Mon Nov 18 2002 ro@suse.de
- add AM_GNU_GETTEXT_VERSION to configure.ac
* Thu Aug  1 2002 ro@suse.de
- add acinclude.m4 with missing macros
* Tue Jun  4 2002 pthomas@suse.de
- Make tar a package of its own.
- Update to tar-1.13.25.
- Make tar man page a seperate file instead of part of the patch.
- Patch de.po to reflect the addition of the --bunzip2 parameter
- Use AC_LIBOBJ instead of LIBOBJS
* Wed May 22 2002 olh@suse.de
- allow build as user, use buildroot
* Fri Feb  8 2002 werner@suse.de
- Fix bug #12797: back to builtin behaviour, the widly used -I for
  bunzip2 can be reenabled with the environment var TAROLDOPT4BZIP2
* Mon Dec 17 2001 werner@suse.de
- draht@suse.de: package rsh is needed for build of tar(1) to
  enable rsh remote command execution.
  two successive execl() calls to /usr/bin/rsh with different
  args/remote commands do not make sense since the first execl() is
  successful if /usr/bin/rsh exists. Check for existence of /etc/rmt
  on the remote side and execute it, else exec /sbin/rmt . (#12605)
- Use one contstant string for command line
* Tue Nov 20 2001 werner@suse.de
- Add rsh to needeforbuild to be sure that remote shell for remote
  backup will be found.
* Wed Aug  1 2001 werner@suse.de
- Make /etc/rmt versus /sbin/rmt switch dynamic.
* Tue Mar 27 2001 werner@suse.de
- Fix man page of tar (#6741)
* Thu Dec 14 2000 werner@suse.de
- Update to tar 1.13.18
  * should avoid some crashes
  * avoid exclude file list problem
* Fri Nov 26 1999 kukuk@suse.de
- Add tar.1 to file list
- Remove obsolete entries from file list
- Build tar with locale support
