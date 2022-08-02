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


# there are more fancy ways to define a package name using magic
# macros but OBS and the bots that rely on parser information from
# OBS can't deal with all of them
%global flavor %{nil}
%if "%{flavor}" != ""
%define psuffix -%{flavor}
%else
%define psuffix %{nil}
%endif
Name:           coreutils%{psuffix}
Version:        9.1
Release:        2.3
Summary:        GNU Core Utilities
License:        GPL-3.0-or-later
Group:          System/Base
URL:            https://www.gnu.org/software/coreutils/
Source0:        https://ftp.gnu.org/gnu/coreutils/coreutils-%{version}.tar.xz
Source1:        https://ftp.gnu.org/gnu/coreutils/coreutils-%{version}.tar.xz.sig
Source2:        https://savannah.gnu.org/project/release-gpgkeys.php?group=coreutils&download=1&file=./coreutils.keyring
Source3:        baselibs.conf
Patch1:         coreutils-remove_hostname_documentation.patch
Patch3:         coreutils-remove_kill_documentation.patch
Patch4:         coreutils-i18n.patch
Patch8:         coreutils-sysinfo.patch
Patch16:        coreutils-invalid-ids.patch
# OBS / RPMLINT require /usr/bin/timeout to be built with the -fpie option.
Patch100:       coreutils-build-timeout-as-pie.patch
# There is no network in the build root so make the test succeed
Patch112:       coreutils-getaddrinfo.patch
# Assorted fixes
Patch113:       coreutils-misc.patch
# Skip 2 valgrind'ed sort tests on ppc/ppc64 which would fail due to
# a glibc issue in mkstemp.
Patch300:       coreutils-skip-some-sort-tests-on-ppc.patch
Patch301:       coreutils-skip-gnulib-test-tls.patch
# tests: shorten extreme-expensive factor tests
Patch303:       coreutils-tests-shorten-extreme-factor-tests.patch
# Stop using Python 2.x
Patch304:       coreutils-use-python3.patch
Patch500:       coreutils-disable_tests.patch
Patch501:       coreutils-test_without_valgrind.patch
# Downstream patch to skip a test failing on OBS.
# tests: skip tests/rm/ext3-perf.sh temporarily as it hangs on OBS.
Patch810:       coreutils-skip-tests-rm-ext3-perf.patch
# Upstream patch - remove with version >9.1:
Patch850:       gnulib-simple-backup-fix.patch
#BuildRequires:  automake
#BuildRequires:  gmp-devel
#BuildRequires:  libacl-devel
#BuildRequires:  libattr-devel
#BuildRequires:  libcap-devel
#BuildRequires:  libselinux-devel
#BuildRequires:  makeinfo
#BuildRequires:  perl
#BuildRequires:  xz
#%if 0%{?suse_version} > 1320
#BuildRequires:  gcc-PIE
#%endif
#%if "%{name}" == "coreutils-testsuite"
#BuildRequires:  acl
#BuildRequires:  gdb
#BuildRequires:  perl-Expect
#BuildRequires:  python
#BuildRequires:  python3
#BuildRequires:  python3-pyinotify
#BuildRequires:  strace
#BuildRequires:  timezone
## Some tests need the 'bin' user.
#BuildRequires:  user(bin)
#%ifarch %{ix86} x86_64 ppc ppc64 s390x armv7l armv7hl
#BuildRequires:  valgrind
#%endif
#%endif
%if "%{name}" == "coreutils" || "%{name}" == "coreutils-single"
Provides:       fileutils = %{version}
Provides:       mktemp = %{version}
Provides:       sh-utils = %{version}
Provides:       stat = %{version}
Provides:       textutils = %{version}
%if "%{name}" == "coreutils-single"
Conflicts:      coreutils
Provides:       coreutils = %{version}-%{release}
%endif
%endif

# ================================================
%description
These are the GNU core utilities.  This package is the union of
the GNU fileutils, sh-utils, and textutils packages.

  [ arch b2sum base32 base64 basename basenc cat chcon chgrp chmod chown chroot
  cksum comm cp csplit cut date dd df dir dircolors dirname du echo env expand
  expr factor false fmt fold groups head hostid id install join
  link ln logname ls md5sum mkdir mkfifo mknod mktemp mv nice nl nohup
  nproc numfmt od paste pathchk pinky pr printenv printf ptx pwd readlink
  realpath rm rmdir runcon seq sha1sum sha224sum sha256sum sha384sum sha512sum
  shred shuf sleep sort split stat stdbuf stty sum sync tac tail tee test
  timeout touch tr true truncate tsort tty uname unexpand uniq unlink
  uptime users vdir wc who whoami yes

%package doc
Summary:        Documentation for the GNU Core Utilities
Group:          Documentation/Man
Supplements:    (coreutils and patterns-base-documentation)
Supplements:    (coreutils-single and patterns-base-documentation)
Provides:       coreutils:%{_infodir}/coreutils.info.gz
BuildArch:      noarch

%description doc
This package contains the documentation for the GNU Core Utilities.

# ================================================
%package -n coreutils-lang
Summary:	Translations for package coreutils
Group:		Documentation/Man
Requires:	%{name} = %{version}
BuildArch:	noarch

%description -n coreutils-lang
Provides translations for the "coreutils" package.

%prep
%setup -q -n coreutils-%{version}
%patch4 -p1
%patch1
%patch3
%patch8
%patch16
#
%if 0%{?suse_version} <= 1320
%patch100
%endif
%patch112
%patch113

%patch300

%ifarch %{ix86} x86_64 ppc ppc64
%patch301
%endif

%patch303
%patch304
%patch500
%patch501

%patch810
%patch850

# ================================================
%build
%if 0%{?suse_version} >= 1200
AUTOPOINT=true autoreconf -fi
%endif
export CFLAGS="%{optflags}"
%configure --libexecdir=%{_libdir} \
           --enable-install-program=arch \
	   --enable-no-install-program=kill \
%if "%{name}" == "coreutils-single"
           --enable-single-binary \
           --without-openssl \
           --without-gmp \
%endif
           DEFAULT_POSIX2_VERSION=200112 \
           alternative=199209

%make_build -C po update-po

# Regenerate manpages
touch man/*.x

%make_build -j32 all

# make sure that parse-datetime.{c,y} ends up in debuginfo (rh#1555079)
ln -v lib/parse-datetime.{c,y} .

# ================================================
#%check
#%if "%{name}" == "coreutils-testsuite"
#  # Make our multi-byte test for sort executable
#  chmod a+x tests/misc/sort-mb-tests.sh
#  # Avoid parallel make, because otherwise some timeout based tests like
#  # rm/ext3-perf may fail due to high CPU or IO load.
#  %make_build check-very-expensive \
#    && install -d -m 755 %{buildroot}%{_docdir}/%{name} \
#    && xz -c tests/test-suite.log \
#         > %{buildroot}%{_docdir}/%{name}/test-suite.log.xz
#%else
#  # Run the shorter check otherwise.
#  %make_build check
#%endif

# ================================================
%install
%if "%{name}" == "coreutils" || "%{name}" == "coreutils-single"
make install DESTDIR=%{buildroot} pkglibexecdir=%{_libdir}/%{name}

echo '.so man1/test.1' > %{buildroot}/%{_mandir}/man1/\[.1
%if "%{name}" == "coreutils"
%find_lang coreutils
# add LC_TIME directories to lang package
awk '/LC_TIME/ {a=$2; gsub(/\/[^\/]+\.mo/,"", a); print "%%dir", a} {print}' < coreutils.lang > tmp
mv tmp coreutils.lang
%else
rm -rf %{buildroot}%{_mandir}
rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_datadir}/locale
> coreutils.lang
%endif
%endif
rm -rf %{buildroot}%{_infodir}/dir

# ================================================
%post
%if "%{name}" == "coreutils" || "%{name}" == "coreutils-single"
%{?regenerate_initrd_post}
%endif

# ================================================
%posttrans
%if "%{name}" == "coreutils" || "%{name}" == "coreutils-single"
%{?regenerate_initrd_posttrans}
%endif

# ================================================
%files
%if "%{name}" == "coreutils" || "%{name}" == "coreutils-single"

%license COPYING
%doc NEWS README THANKS
%{_bindir}/.
%{_libdir}/%{name}

%if "%{name}" == "coreutils"
%files lang -f coreutils.lang

%files doc
%{_infodir}/coreutils.info
%{_mandir}/man1/.
%endif

%else

# test-suite
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/test-suite.log.xz

%endif

# ================================================

%changelog
* Tue Apr 26 2022 Dirk Müller <dmueller@suse.com>
- remove builddisabled conditions for rings - will be done now as
  BuildFlags: excludebuilds
* Sun Apr 24 2022 Bernhard Voelker <mail@bernhard-voelker.de>
- gnulib-simple-backup-fix.patch: Add patch to make simple backups in correct
  directory; broken in 9.1.  See https://bugs.gnu.org/55029
* Thu Apr 21 2022 Dirk Müller <dmueller@suse.com>
- update to 9.1:
  * chmod -R no longer exits with error status when encountering symlinks.
    All files would be processed correctly, but the exit status was incorrect.
  * If 'cp -Z A B' checks B's status and some other process then removes B,
    cp no longer creates B with a too-generous SELinux security context
    before adjusting it to the correct value.
  * 'cp --preserve=ownership A B' no longer ignores the umask when creating B.
    Also, 'cp --preserve-xattr A B' is less likely to temporarily chmod u+w B.
  * 'id xyz' now uses the name 'xyz' to determine groups, instead of xyz's uid.
  * 'ls -v' and 'sort -V' no longer mishandle corner cases like "a..a" vs "a.+"
    or lines containing NULs.  Their behavior now matches the documentation
    for file names like ".m4" that consist entirely of an extension,
    and the documentation has been clarified for unusual cases.
  * 'mv -T --backup=numbered A B/' no longer miscalculates the backup number
    for B when A is a directory, possibly inflooping.
  * cat now uses the copy_file_range syscall if available, when doing
    simple copies between regular files.  This may be more efficient, by avoiding
    user space copies, and possibly employing copy offloading or reflinking.
  * chown and chroot now warn about usages like "chown root.root f",
    which have the nonstandard and long-obsolete "." separator that
    causes problems on platforms where user names contain ".".
    Applications should use ":" instead of ".".
  * cksum no longer allows abbreviated algorithm names,
    so that forward compatibility and robustness is improved.
  * date +'%%-N' now suppresses excess trailing digits, instead of always
    padding them with zeros to 9 digits.  It uses clock_getres and
    clock_gettime to infer the clock resolution.
  * dd conv=fsync now synchronizes output even after a write error,
    and similarly for dd conv=fdatasync.
  * dd now counts bytes instead of blocks if a block count ends in "B".
    For example, 'dd count=100KiB' now copies 100 KiB of data, not
    102,400 blocks of data.  The flags count_bytes, skip_bytes and
    seek_bytes are therefore obsolescent and are no longer documented,
    though they still work.
  * ls no longer colors files with capabilities by default, as file-based
    capabilties are very rarely used, and lookup increases processing per file by
    about 30%%.  It's best to use getcap [-r] to identify files with capabilities.
  * ls no longer tries to automount files, reverting to the behavior
    before the statx() call was introduced in coreutils-8.32.
  * stat no longer tries to automount files by default, reverting to the
    behavior before the statx() call was introduced in coreutils-8.32.
    Only `stat --cached=never` will continue to automount files.
  * timeout --foreground --kill-after=... will now exit with status 137
    if the kill signal was sent, which is consistent with the behavior
    when the --foreground option is not specified.  This allows users to
    distinguish if the command was more forcefully terminated.
  * dd now supports the aliases iseek=N for skip=N, and oseek=N for seek=N,
    like FreeBSD and other operating systems.
  * dircolors takes a new --print-ls-colors option to display LS_COLORS
    entries, on separate lines, colored according to the entry color code.
  * dircolors will now also match COLORTERM in addition to TERM environment
    variables.  The default config will apply colors with any COLORTERM set.
  * cp, mv, and install now use openat-like syscalls when copying to a directory.
  * This avoids some race conditions and should be more efficient.
  * The new 'date' option --resolution outputs the timestamp resolution.
  * With conv=fdatasync or conv=fsync, dd status=progress now reports
    any extra final progress just before synchronizing output data,
    since synchronizing can take a long time.
  * printf now supports printing the numeric value of multi-byte characters.
  * sort --debug now diagnoses issues with --field-separator characters
    that conflict with characters possibly used in numbers.
  * 'tail -f file | filter' now exits on Solaris when filter exits.
  * root invoked coreutils, that are built and run in single binary mode,
    now adjust /proc/$pid/cmdline to be more specific to the utility
    being run, rather than using the general "coreutils" binary name.
- coreutils-i18n.patch: Re-sync the patch with Fedora.
- drop coreutils-chmod-fix-exit-status-ign-symlinks.patch (upstream)
* Mon Oct  4 2021 Bernhard Voelker <mail@bernhard-voelker.de>
- coreutils-i18n.patch: Re-sync the patch with Fedora.
  Refresh the patch, adding a hunk to link the expand+unexpand tools
  against lib/mbfile.c, thus fixing build problems with clang
  (see https://src.fedoraproject.org/rpms/coreutils/c/f4a53e34).
* Fri Oct  1 2021 Dirk Müller <dmueller@suse.com>
- spec file cleanups (spec-cleaner run)
* Thu Sep 30 2021 Bernhard Voelker <mail@bernhard-voelker.de>
- coreutils-skip-tests-rm-ext3-perf.patch: Add patch to skip the test
  'tests/rm/ext3-perf.sh' temporarily as it hangs on OBS.
* Sun Sep 26 2021 Bernhard Voelker <mail@bernhard-voelker.de>
- Update to 9.0:
  * Noteworthy changes in release 9.0 (2021-09-24) [stable]
  * * Bug fixes
  chmod -v no longer misreports modes of dangling symlinks.
  [bug introduced in coreutils-5.3.0]
  cp -a --attributes-only now never removes destination files,
  even if the destination files are hardlinked, or the source
  is a non regular file.
  [bug introduced in coreutils-8.6]
  csplit --suppress-matched now elides the last matched line
  when a specific number of pattern matches are performed.
  [bug introduced with the --suppress-matched feature in coreutils-8.22]
  df no longer outputs duplicate remote mounts in the presence of bind mounts.
  [bug introduced in coreutils-8.26]
  df no longer mishandles command-line args that it pre-mounts
  [bug introduced in coreutils-8.29]
  du no longer crashes on XFS file systems when the directory hierarchy is
  heavily changed during the run.
  [bug introduced in coreutils-8.25]
  env -S no longer crashes when given unusual whitespace characters
  [bug introduced in coreutils-8.30]
  expr no longer mishandles unmatched \(...\) in regular expressions.
  [bug introduced in coreutils-6.0]
  ls no longer crashes when printing the SELinux context for unstatable files.
  [bug introduced in coreutils-6.9.91]
  mkdir -m no longer mishandles modes more generous than the umask.
  [bug introduced in coreutils-8.22]
  nl now handles single character --section-delimiter arguments,
  by assuming a second ':' character has been specified, as specified by POSIX.
  [This bug was present in "the beginning".]
  pr again adjusts tabs in input, to maintain alignment in multi column output.
  [bug introduced in coreutils-6.9]
  rm no longer skips an extra file when the removal of an empty directory fails.
  [bug introduced by the rewrite to use fts in coreutils-8.0]
  split --number=K/N will again correctly split chunk K of N to stdout.
  Previously a chunk starting after 128KiB, output the wrong part of the file.
  [bug introduced in coreutils-8.26]
  tail -f no longer overruns a stack buffer when given too many files
  to follow and ulimit -n exceeds 1024.
  [bug introduced in coreutils-7.5]
  tr no longer crashes when using --complement with certain
  invalid combinations of case character classes.
  [bug introduced in coreutils-8.6]
  basenc --base64 --decode no longer silently discards decoded characters
  on (1024*5) buffer boundaries
  [bug introduced in coreutils-8.31]
  * * Changes in behavior
  cp and install now default to copy-on-write (COW) if available.
  cp, install and mv now use the copy_file_range syscall if available.
  Also, they use lseek+SEEK_HOLE rather than ioctl+FS_IOC_FIEMAP on sparse
  files, as lseek is simpler and more portable.
  On GNU/Linux systems, ls no longer issues an error message on a
  directory merely because it was removed.  This reverts a change
  that was made in release 8.32.
  ptx -T no longer attempts to substitute old-fashioned TeX escapes
  for 8-bit non-ASCII alphabetic characters.  TeX indexes should
  instead use '\usepackage[latin1]{inputenc}' or equivalent.
  stat will use decomposed (major,minor) device numbers in its default format.
  This is less ambiguous, and more consistent with ls.
  sum [-r] will output a file name, even if only a single name is passed.
  This is consistent with sum -s, cksum, and other sum(1) implementations.
  * * New Features
  cksum now supports the -a (--algorithm) option to select any
  of the existing sum, md5sum, b2sum, sha*sum implementations etc.
  cksum now subsumes all of these programs, and coreutils
  will introduce no future standalone checksum utility.
  cksum -a now supports the 'sm3' argument, to use the SM3 digest algorithm.
  cksum --check now supports auto detecting the digest type to use,
  when verifying tagged format checksums.
  expr and factor now support bignums on all platforms.
  ls --classify now supports the "always", "auto", or "never" flags,
  to support only outputting classifier characters if connected to a tty.
  ls now accepts the --sort=width option, to sort by file name width.
  This is useful to more compactly organize the default vertical column output.
  ls now accepts the --zero option, to terminate each output line with
  NUL instead of newline.
  nl --line-increment can now take a negative number to decrement the count.
  stat supports more formats for representing decomposed device numbers.
  %%Hd,%%Ld and %%Hr,%%Lr will output major,minor device numbers and device types
  respectively.  %%d corresponds to st_dev and %%r to std_rdev.
  * * Improvements
  cat --show-ends will now show \r\n as ^M$.  Previously the \r was taken
  literally, thus overwriting the first character in the line with '$'.
  cksum [-a crc] is now up to 4 times faster by using a slice by 8 algorithm,
  and at least 8 times faster where pclmul instructions are supported.
  A new --debug option will indicate if pclmul is being used.
  md5sum --check now supports checksum files with CRLF line endings.
  This also applies to cksum, sha*sum, and b2sum.
  df now recognizes these file systems as remote:
  acfs, coda, fhgfs, gpfs, ibrix, ocfs2, and vxfs.
  rmdir now clarifies the error if a symlink_to_dir/ has not been traversed.
  This is the case on GNU/Linux systems, where the trailing slash is ignored.
  stat and tail now know about the "devmem", "exfat", "secretmem", "vboxsf",
  and "zonefs" file system types.  stat -f -c%%T now reports the file system
  type, and tail -f uses polling for "vboxsf" and inotify for the others.
  timeout now supports sub-second timeouts on macOS.
  wc is up to 5 times faster when counting only new line characters,
  where avx2 instructions are supported.
  A new --debug option will indicate if avx2 is being used.
- Remove patches which are included in the new upstream version now:
  * coreutils-gnulib-disable-test-float.patch
  * coreutils-ls-restore-8.31-behavior-on-removed-dirs.patch
  * coreutils-tests-fix-FP-in-ls-stat-free-color.patch
  * gnulib-test-avoid-FP-perror-strerror.patch
- coreutils-i18n.patch: Refresh patch.  Also patch 'tests/Coreutils.pm' used
  by perl-based tests to allow longer test names ... which the i18n tests with
  their "-mb" suffix have.
- coreutils-chmod-fix-exit-status-ign-symlinks.patch: Add upstream patch to
  fix a regression with the exit code of chmod introduced in 9.0.
- coreutils.spec:
  * Version: bump version.
  * Remove the above removed patches.
  * Reference the above new patch.
* Thu Apr 29 2021 Callum Farmer <gmbr3@opensuse.org>
- Use new packageand format
* Fri Apr 23 2021 Bernhard Voelker <mail@bernhard-voelker.de>
- coreutils-tests-fix-FP-in-ls-stat-free-color.patch: Add upstream patch
  to avoid FP in testsuite.
- coreutils.spec:
  - Reference the above patch.
  - Change keyring URL to new GNU coreutils Group Release Keyring.
- coreutils.keyring: Update with the Group Release Keyring.
* Fri Oct 16 2020 Ludwig Nussel <lnussel@suse.de>
- prepare usrmerge (boo#1029961)
* Mon Aug 31 2020 Bernhard Voelker <mail@bernhard-voelker.de>
- gnulib-test-avoid-FP-perror-strerror.patch: Add patch to
  avoid false-positive error in gnulib tests 'test-perror2' and
  'test-strerror_r', visible on armv7l.
- coreutils.spec: Reference the patch.
* Thu Jul 16 2020 Dominique Leuenberger <dimstar@opensuse.org>
- Drop suse-module-tools BuildRequires: this was used for the macro
  regenerate_initrd_post/posttrans, which have been moved to
  rpm-config-SUSE in Jan 2019.
* Sat Jun 13 2020 Bernhard Voelker <mail@bernhard-voelker.de>
- coreutils-gnulib-disable-test-float.patch: Add patch to temporarily
  disable the gnulib test 'test-float' failing on ppc and ppc64le.
- coreutils.spec: Reference the patch.  While at it, avoid conditional
  Patch and Source entries as that break cross-platform builds from
  source RPMs.
* Mon May  4 2020 Dirk Mueller <dmueller@suse.com>
- add coreutils-use-python3.patch to minimally port away from
  python 2.x use of pyinotify in the testsuite
* Mon Mar  9 2020 Bernhard Voelker <mail@bernhard-voelker.de>
- Update to 8.32:
  * Noteworthy changes in release 8.32 (2020-03-05) [stable]
  * * Bug fixes
  cp now copies /dev/fd/N correctly on platforms like Solaris where
  it is a character-special file whose minor device number is N.
  [bug introduced in fileutils-4.1.6]
  dd conv=fdatasync no longer reports a "Bad file descriptor" error
  when fdatasync is interrupted, and dd now retries interrupted calls
  to close, fdatasync, fstat and fsync instead of incorrectly
  reporting an "Interrupted system call" error.
  [bugs introduced in coreutils-6.0]
  df now correctly parses the /proc/self/mountinfo file for unusual entries
  like ones with '\r' in a field value ("mount -t tmpfs tmpfs /foo$'\r'bar"),
  when the source field is empty ('mount -t tmpfs "" /mnt'), and when the
  filesystem type contains characters like a blank which need escaping.
  [bugs introduced in coreutils-8.24 with the introduction of reading
  the /proc/self/mountinfo file]
  factor again outputs immediately when stdout is a tty but stdin is not.
  [bug introduced in coreutils-8.24]
  ln works again on old systems without O_DIRECTORY support (like Solaris 10),
  and on systems where symlink ("x", ".") fails with errno == EINVAL
  (like Solaris 10 and Solaris 11).
  [bug introduced in coreutils-8.31]
  rmdir --ignore-fail-on-non-empty now works correctly for directories
  that fail to be removed due to permission issues.  Previously the exit status
  was reversed, failing for non empty and succeeding for empty directories.
  [bug introduced in coreutils-6.11]
  'shuf -r -n 0 file' no longer mistakenly reads from standard input.
  [bug introduced with the --repeat feature in coreutils-8.22]
  split no longer reports a "output file suffixes exhausted" error
  when the specified number of files is evenly divisible by 10, 16, 26,
  for --numeric, --hex, or default alphabetic suffixes respectively.
  [bug introduced in coreutils-8.24]
  seq no longer prints an extra line under certain circumstances (such as
  'seq -f "%%g " 1000000 1000000').
  [bug introduced in coreutils-6.10]
  * * Changes in behavior
  Several programs now check that numbers end properly.  For example,
  'du -d 1x' now reports an error instead of silently ignoring the 'x'.
  Affected programs and options include du -d, expr's numeric operands
  on non-GMP builds, install -g and -o, ls's TABSIZE environment
  variable, mknod b and c, ptx -g and -w, shuf -n, and sort --batch-size
  and --parallel.
  date now parses military time zones in accordance with common usage:
    "A" to "M"  are equivalent to UTC+1 to UTC+12
    "N" to "Y"  are equivalent to UTC-1 to UTC-12
    "Z" is "zulu" time (UTC).
  For example, 'date -d "09:00B" is now equivalent to 9am in UTC+2 time zone.
  Previously, military time zones were parsed according to the obsolete
  rfc822, with their value negated (e.g., "B" was equivalent to UTC-2).
  [The old behavior was introduced in sh-utils 2.0.15 ca. 1999, predating
  coreutils package.]
  ls issues an error message on a removed directory, on GNU/Linux systems.
  Previously no error and no entries were output, and so indistinguishable
  from an empty directory, with default ls options.
  uniq no longer uses strcoll() to determine string equivalence,
  and so will operate more efficiently and consistently.
  * * New Features
  ls now supports the --time=birth option to display and sort by
  file creation time, where available.
  od --skip-bytes now can use lseek even if the input is not a regular
  file, greatly improving performance in some cases.
  stat(1) supports a new --cached= option, used on systems with statx(2)
  to control cache coherency of file system attributes,
  useful on network file systems.
  * * Improvements
  stat and ls now use the statx() system call where available, which can
  operate more efficiently by only retrieving requested attributes.
  stat and tail now know about the "binderfs", "dma-buf-fs", "erofs",
  "ppc-cmm-fs", and "z3fold" file systems.
  stat -f -c%%T now reports the file system type, and tail -f uses inotify.
  * * Build-related
  gzip-compressed tarballs are distributed once again
- Refresh patches:
  * coreutils-disable_tests.patch
  * coreutils-getaddrinfo.patch
  * coreutils-i18n.patch
  * coreutils-invalid-ids.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-skip-gnulib-test-tls.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
- coreutils-i18n.patch:
  * uniq: remove collation handling as required by newer POSIX; see
  - https://git.savannah.gnu.org/cgit/coreutils.git/commit/?id=8e81d44b5
  - https://www.austingroupbugs.net/view.php?id=963
- coreutils-ls-restore-8.31-behavior-on-removed-dirs.patch:
  * Add patch for 'ls' to restore 8.31 behavior on removed directories.
- coreutils.spec:
  * Version: bump version.
  * %%check: re-enable regular 'make check' for non-multibuild package.
  * reference the above new patch.
- coreutils.keyring:
  * Update from upstream (Savannah).
* Tue Jan 28 2020 Ludwig Nussel <lnussel@suse.de>
- disable single and testsuite builds in rings/staging
- remove duplicate "coreutils" in flavor to make it look nicer in OBS
* Mon Jan 20 2020 Bernhard Voelker <mail@bernhard-voelker.de>
- minor: remove obsolete comment in spec file.
* Thu Jan  9 2020 Ludwig Nussel <lnussel@suse.de>
- switch to multibuild
- add coreutils-single subpackage that contains a single binary coreutils tool
  similar to busybox
- package LC_CTIME directories also in lang package
- split off doc package
- remove info macros, handled by file trigger nowadays
* Thu Sep 19 2019 Ludwig Nussel <lnussel@suse.de>
- Do not recommend lang package. The lang package already has a
  supplements.
* Mon Mar 11 2019 Bernhard Voelker <mail@bernhard-voelker.de>
- Update to 8.31:
  * Noteworthy changes in release 8.31 (2019-03-10) [stable]
  * * Bug fixes
  'base64 a b' now correctly diagnoses 'b' as the extra operand, not 'a'.
  [bug introduced in coreutils-5.3.0]
  When B already exists, 'cp -il A B' no longer immediately fails
  after asking the user whether to proceed.
  [This bug was present in "the beginning".]
  df no longer corrupts displayed multibyte characters on macOS.
  [bug introduced with coreutils-8.18]
  seq no longer outputs inconsistent decimal point characters
  for the last number, when locales are misconfigured.
  [bug introduced in coreutils-7.0]
  shred, sort, and split no longer falsely report ftruncate errors
  when outputting to less-common file types.  For example, the shell
  command 'sort /dev/null -o /dev/stdout | cat' no longer fails with
  an "error truncating" diagnostic.
  [bug was introduced with coreutils-8.18 for sort and split, and
  (for shared memory objects only) with fileutils-4.1 for shred]
  sync no longer fails for write-only file arguments.
  [bug introduced with argument support to sync in coreutils-8.24]
  'tail -f file | filter' no longer exits immediately on AIX.
  [bug introduced in coreutils-8.28]
  'tail -f file | filter' no longer goes into an infinite loop
  if filter exits and SIGPIPE is ignored.
  [bug introduced in coreutils-8.28]
  * * Changes in behavior
  cksum, dd, hostid, hostname, link, logname, sleep, tsort, unlink,
  uptime, users, whoami, yes: now always process --help and --version options,
  regardless of any other arguments present before any optional '--'
  end-of-options marker.
  nohup now processes --help and --version as first options even if other
  parameters follow.
  'yes a -- b' now outputs 'a b' instead of including the end-of-options
  marker as before: 'a -- b'.
  echo now always processes backslash escapes when the POSIXLY_CORRECT
  environment variable is set.
  When possible 'ln A B' now merely links A to B and reports an error
  if this fails, instead of statting A and B before linking.  This
  uses fewer system calls and avoids some races.  The old statting
  approach is still used in situations where hard links to directories
  are allowed (e.g., NetBSD when superuser).
  ls --group-directories-first will also group symlinks to directories.
  'test -a FILE' is not supported anymore.  Long ago, there were concerns about
  the high probability of humans confusing the -a primary with the -a binary
  operator, so POSIX changed this to 'test -e FILE'.  Scripts using it were
  already broken and non-portable; the -a unary operator was never documented.
  wc now treats non breaking space characters as word delimiters
  unless the POSIXLY_CORRECT environment variable is set.
  * * New features
  id now supports specifying multiple users.
  'date' now supports the '+' conversion specification flag,
  introduced in POSIX.1-2017.
  printf, seq, sleep, tail, and timeout now accept floating point
  numbers in either the current or the C locale.  For example, if the
  current locale's decimal point is ',', 'sleep 0,1' and 'sleep 0.1'
  now mean the same thing.  Previously, these commands accepted only
  C-locale syntax with '.' as the decimal point.  The new behavior is
  more compatible with other implementations in non-C locales.
  test now supports the '-N FILE' unary operator (like e.g. bash) to check
  whether FILE exists and has been modified since it was last read.
  env now supports '--default-signal[=SIG]', '--ignore-signal[=SIG]', and
  '--block-signal[=SIG], to setup signal handling before executing a program.
  env now supports '--list-signal-handling' to indicate non-default
  signal handling before executing a program.
  * * New commands
  basenc is added to complement existing base64,base32 commands,
  and encodes and decodes printable text using various common encodings:
  base64,base64url,base32,base32hex,base16,base2,z85.
  * * Improvements
  ls -l now better aligns abbreviated months containing digits,
  which is common in Asian locales.
  stat and tail now know about the "sdcardfs" file system on Android.
  stat -f -c%%T now reports the file system type, and tail -f uses inotify.
  stat now prints file creation time when supported by the file system,
  on GNU Linux systems with glibc >= 2.28 and kernel >= 4.11.
- Refresh patches (line number changes only):
  * coreutils-disable_tests.patch
  * coreutils-i18n.patch
  * coreutils-misc.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-skip-gnulib-test-tls.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
- coreutils.spec:
  * Version: bump version.
  * URL: Use https scheme.
  * %%description: Add 'basenc' tool.
  * Change gitweb to cgit URL with https in a comment.
- coreutils.keyring:
  * Update for added section headers ('GPG keys of <MAINTAINER>').
* Tue Jul  3 2018 mail@bernhard-voelker.de
- Update to 8.30:
  * Noteworthy changes in release 8.30 (2018-07-01) [stable]
  * * Bug fixes
  'cp --symlink SRC DST' will again correctly validate DST.
  If DST is a regular file and SRC is a symlink to DST,
  then cp will no longer allow that operation to clobber DST.
  Also with -d, if DST is a symlink, then it can always be replaced,
  even if it points to SRC on a separate device.
  [bugs introduced with coreutils-8.27]
  'cp -n -u' and 'mv -n -u' now consistently ignore the -u option.
  Previously, this option combination suffered from race conditions
  that caused -u to sometimes override -n.
  [bug introduced with coreutils-7.1]
  'cp -a --no-preserve=mode' now sets appropriate default permissions
  for non regular files like fifos and character device nodes etc.,
  and leaves mode bits of existing files unchanged.
  Previously it would have set executable bits on created special files,
  and set mode bits for existing files as if they had been created.
  [bug introduced with coreutils-8.20]
  'cp --remove-destination file symlink' now removes the symlink
  even if it can't be traversed.
  [bug introduced with --remove-destination in fileutils-4.1.1]
  ls no longer truncates the abbreviated month names that have a
  display width between 6 and 12 inclusive.  Previously this would have
  output ambiguous months for Arabic or Catalan locales.
  'ls -aA' is now equivalent to 'ls -A', since -A now overrides -a.
  [bug introduced in coreutils-5.3.0]
  'mv -n A B' no longer suffers from a race condition that can
  overwrite a simultaneously-created B.  This bug fix requires
  platform support for the renameat2 or renameatx_np syscalls, found
  in recent Linux and macOS kernels.  As a side effect, ‘mv -n A A’
  now silently does nothing if A exists.
  [bug introduced with coreutils-7.1]
  * * Changes in behavior
  'cp --force file symlink' now removes the symlink even if
  it is self referential.
  ls --color now matches file extensions case insensitively.
  * * New features
  cp --reflink now supports --reflink=never to enforce a standard copy.
  env supports a new -v/--debug option to show verbose information about
  each processing step.
  env supports a new -S/--split-string=S option to split a single argument
  string into multiple arguments. Used to pass multiple arguments in scripts
  (shebang lines).
  md5sum accepts a new option: --zero (-z) to delimit the output lines with a
  NUL instead of a newline character.  This also disables file name escaping.
  This also applies to sha*sum and b2sum.
  rm --preserve-root now supports the --preserve-root=all option to
  reject any command line argument that is mounted to a separate file system.
  * * Improvements
  cut supports line lengths up to the max file size on 32 bit systems.
  Previously only offsets up to SIZE_MAX-1 were supported.
  stat and tail now know about the "exfs" file system, which is a
  version of XFS.  stat -f --format=%%T now reports the file system type,
  and tail -f uses inotify.
  wc avoids redundant processing of ASCII text in multibyte locales,
  which is especially significant on macOS.
  * * Build-related
  Adjust to glibc >= 2.28  (bsc#1182550, jsc#SLE-13520, jsc#SLE-13756)
- Refresh patches (line number changes only):
  * coreutils-build-timeout-as-pie.patch
  * coreutils-disable_tests.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-skip-gnulib-test-tls.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
- coreutils.spec:
  * (License): osc changed the value from "GPL-3.0+" to "GPL-3.0-or-later".
  * (build): Make sure that parse-datetime.{c,y} ends up in debuginfo (rh#1555079).
- coreutils-i18n.patch:
  * src/exand.c,src/unexpand.c: Avoid -Wcomment warning.
  * src/cut.c (cut_characters_or_cut_bytes_no_split): Change idx from size_t
    to uintmax_t type to avoid a regression on i586, armv7l and ppc.
    Compare upstream, non-MB commit:
    https://git.sv.gnu.org/cgit/coreutils.git/commit/?id=d1a754c8272
    (cut_fields_mb): Likewise for field_idx.
  * tests/misc/cut.pl: Remove downstream tweaks as upstream MB tests are
    working since a while.
- coreutils.keyring: Update Assaf Gordon's GPG public key.
* Thu Feb 22 2018 fvogt@suse.com
- Use %%license (boo#1082318)
* Thu Dec 28 2017 mail@bernhard-voelker.de
- Update to 8.29:
  * Noteworthy changes in release 8.29 (2017-12-27) [stable]
  * * Bug fixes
  b2sum no longer crashes when processing certain truncated check files.
  [bug introduced with b2sum coreutils-8.26]
  dd now ensures the correct cache ranges are specified for the "nocache"
  and "direct" flags.  Previously some pages in the page cache were not
  invalidated.  [bug introduced for "direct" in coreutils-7.5,
  and with the "nocache" implementation in coreutils-8.11]
  df no longer hangs when given a fifo argument.
  [bug introduced in coreutils-7.3]
  ptx -S no longer infloops for a pattern which returns zero-length matches.
  [the bug dates back to the initial implementation]
  shred --remove will again repeatedly rename files with shortening names
  to attempt to hide the original length of the file name.
  [bug introduced in coreutils-8.28]
  stty no longer crashes when processing settings with -F also specified.
  [bug introduced in fileutils-4.0]
  tail --bytes again supports non seekable inputs on all systems.
  On systems like android it always tried to process as seekable inputs.
  [bug introduced in coreutils-8.24]
  timeout will again notice its managed command exiting, even when
  invoked with blocked CHLD signal, or in a narrow window where
  this CHLD signal from the exiting child was missed.  In each case
  timeout would have then waited for the time limit to expire.
  [bug introduced in coreutils-8.27]
  * * New features
  timeout now supports the --verbose option to diagnose forced termination.
  * * Improvements
  dd now supports iflag=direct with arbitrary sized files on all file systems.
  tail --bytes=NUM will efficiently seek to the end of block devices,
  rather than reading from the start.
  Utilities which do not support long options (other than the default --help
  and --version), e.g. cksum and sleep, now use more consistent error diagnostic
  for unknown long options.
  * * Build-related
  Default man pages are now distributed which are used if perl is
  not available on the build system, or when cross compiling.
- Refresh patches (line number changes only):
  * coreutils-i18n.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
* Mon Sep  4 2017 mail@bernhard-voelker.de
- Update to 8.28
  (for details see included NEWS file)
- Refresh patches:
  * coreutils-disable_tests.patch
  * coreutils-i18n.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-skip-gnulib-test-tls.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
- coreutils.keyring: Update from upstream (Savannah).
- Remove now-upstream patches:
  * coreutils-cve-2017-7476-out-of-bounds-with-large-tz.patch
  * coreutils-tests-port-to-timezone-2017a.patch
- coreutils.spec: Add "BuildRequires: user(bin)" for the tests.
* Wed Aug 16 2017 ghe@suse.com
- Drop coreutils-ocfs2_reflinks.patch
  OCFS2 file system has supported file clone ioctls like btrfs,
  then, coreutils doesn't need this patch from the kernel v4.10-rc1
* Tue May  2 2017 mail@bernhard-voelker.de
- coreutils-cve-2017-7476-out-of-bounds-with-large-tz.patch:
  Add upstream patch to fix an heap overflow security issue
  in date(1) and touch(1) with a large TZ variable
  (CVE-2017-7476, rh#1444774, boo#1037124).
* Fri Mar 10 2017 mail@bernhard-voelker.de
- Update to 8.27
  (for details see included NEWS file)
- Refresh patches:
  * coreutils-build-timeout-as-pie.patch
  * coreutils-disable_tests.patch
  * coreutils-getaddrinfo.patch
  * coreutils-i18n.patch
  * coreutils-ocfs2_reflinks.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-skip-gnulib-test-tls.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
  * coreutils-testsuite.spec
- coreutils.keyring: Update (now ascii-armored) by
    'osc service localrun download_files'.
- coreutils-tests-port-to-timezone-2017a.patch: Add patch to
  workaround a FP test failure with newer timezone-2017a.
* Fri Dec  2 2016 mail@bernhard-voelker.de
- Update to 8.26
  (for details see included NEWS file)
- coreutils.spec (%%description): Add b2sum, a new utility.
  (BuildRequires): Add timezone to enable new 'date-debug.sh' test.
- coreutils-i18n.patch: Sync I18N patch from Fedora, as the diff
  for the old i18n implementation of expand/unexpand has become
  unmaintainable:
  git://pkgs.fedoraproject.org/coreutils.git
- Remove now-upstream patches:
  * coreutils-df-hash-in-filter.patch
  * coreutils-diagnose-fts-readdir-failure.patch
  * coreutils-m5sum-sha-sum-fix-ignore-missing-with-00-checksums.patch
  * coreutils-maint-fix-dependency-of-man-arch.1.patch
- Refresh/merge all other patches:
  * coreutils-invalid-ids.patch
  * coreutils-ocfs2_reflinks.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-skip-gnulib-test-tls.patch
  * coreutils-sysinfo.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
* Tue Nov  1 2016 mail@bernhard-voelker.de
- coreutils-m5sum-sha-sum-fix-ignore-missing-with-00-checksums.patch:
  Add upstream patch to fix "md5sum --check --ignore-missing" which
  treated files with checksums starting with "00" as missing.
* Thu Jul 28 2016 mail@bernhard-voelker.de
- coreutils-maint-fix-dependency-of-man-arch.1.patch: Add Upstream
  patch to fix the build dependency between src/arch -> man/arch.1
  which lead to spurious build failures.
- coreutils-df-hash-in-filter.patch: Refresh with -p0.
* Fri Jul 22 2016 pth@suse.de
- Add coreutils-df-hash-in-filter.patch that speeds up df.
* Wed Jul  6 2016 mail@bernhard-voelker.de
- coreutils-diagnose-fts-readdir-failure.patch: Add upstream patch
  to diagnose readdir() failures in fts-based utilities: rm, chmod,
  du, etc. (boo#984910)
* Fri Jan 29 2016 mail@bernhard-voelker.de
- Update to 8.25
  (for details see included NEWS file)
- coreutils.spec (%%description): Add base32, a new utility.
- Remove now-upstream patch:
  * coreutils-tests-avoid-FP-of-ls-stat-free-color.patch
- Refresh/merge all other patches:
  * coreutils-build-timeout-as-pie.patch
  * coreutils-disable_tests.patch
  * coreutils-i18n.patch
  * coreutils-invalid-ids.patch
  * coreutils-misc.patch
  * coreutils-ocfs2_reflinks.patch
  * coreutils-remove_hostname_documentation.patch
  * coreutils-remove_kill_documentation.patch
  * coreutils-skip-gnulib-test-tls.patch
  * coreutils-test_without_valgrind.patch
  * coreutils-tests-shorten-extreme-factor-tests.patch
* Sun Sep 20 2015 mail@bernhard-voelker.de
- coreutils-i18n.patch: Sync I18N patch from semi-official repository
  (shared among distributions, maintained by Padraig Brady):
    https://github.com/pixelb/coreutils/tree/i18n
  This fixes the following issues in multi-byte locales:
  * sort: fix large mem leak with --month-sort (boo#945361, rh#1259942):
    https://github.com/pixelb/coreutils/commit/b429f5d8c7
  * sort: fix assertion with some inputs to --month-sort
    https://github.com/pixelb/coreutils/commit/31e8211aca
* Sun Aug 30 2015 mail@bernhard-voelker.de
- coreutils-tests-avoid-FP-of-ls-stat-free-color.patch: Add upstream
  patch on top of v8.24 to avoid a FP test failure with glibc>=2.22.
* Thu Jul 16 2015 mail@bernhard-voelker.de
- Sync I18N patch from semi-official repository (shared among
  distributions, maintained by Padraig Brady):
    https://github.com/pixelb/coreutils/tree/i18n
  * coreutils-i18n.patch: Improve cut(1) performance in field-mode
    in UTF8 locales.  Squash in sort-keycompare-mb.patch.
  * sort-keycompare-mb.patch: Remove.
- coreutils-build-timeout-as-pie.patch: Refresh.
* Thu Jul  9 2015 pth@suse.de
- Update to 8.24:
  * * Bug fixes
  * dd supports more robust SIGINFO/SIGUSR1 handling for outputting statistics.
    Previously those signals may have inadvertently terminated the process.
  * df --local no longer hangs with inaccessible remote mounts.
    [bug introduced in coreutils-8.21]
  * du now silently ignores all directory cycles due to bind mounts.
    Previously it would issue a warning and exit with a failure status.
    [bug introduced in coreutils-8.1 and partially fixed in coreutils-8.23]
  * chroot again calls chroot(DIR) and chdir("/"), even if DIR is "/".
    This handles separate bind mounted "/" trees, and environments
    depending on the implicit chdir("/").
    [bugs introduced in coreutils-8.23]
  * cp no longer issues an incorrect warning about directory hardlinks when a
    source directory is specified multiple times.  Now, consistent with other
    file types, a warning is issued for source directories with duplicate names,
    or with -H the directory is copied again using the symlink name.
  * factor avoids writing partial lines, thus supporting parallel operation.
    [the bug dates back to the initial implementation]
  * head, od, split, tac, tail, and wc no longer mishandle input from files in
    /proc and /sys file systems that report somewhat-incorrect file sizes.
  * mkdir --parents -Z now correctly sets the context for the last component,
    even if the parent directory exists and has a different default context.
    [bug introduced with the -Z restorecon functionality in coreutils-8.22]
  * numfmt no longer outputs incorrect overflowed values seen with certain
    large numbers, or with numbers with increased precision.
    [bug introduced when numfmt was added in coreutils-8.21]
  * numfmt now handles leading zeros correctly, not counting them when
    settings processing limits, and making them optional with floating point.
    [bug introduced when numfmt was added in coreutils-8.21]
  * paste no longer truncates output for large input files.  This would happen
    for example with files larger than 4GiB on 32 bit systems with a '\n'
    character at the 4GiB position.
    [the bug dates back to the initial implementation]
  * rm indicates the correct number of arguments in its confirmation prompt,
    on all platforms.  [bug introduced in coreutils-8.22]
  * shuf -i with a single redundant operand, would crash instead of issuing
    a diagnostic.  [bug introduced in coreutils-8.22]
  * tail releases inotify resources when unused.  Previously it could exhaust
    resources with many files, or with -F if files were replaced many times.
    [bug introduced in coreutils-7.5]
  * tail -f again follows changes to a file after it's renamed.
    [bug introduced in coreutils-7.5]
  * tail --follow no longer misses changes to files if those files were
    replaced before inotify watches were created.
    [bug introduced in coreutils-7.5]
  * tail --follow consistently outputs all data for a truncated file.
    [bug introduced in the beginning]
  * tail --follow=name correctly outputs headers for multiple files
    when those files are being created or renamed.
    [bug introduced in coreutils-7.5]
  * * New features
  * chroot accepts the new --skip-chdir option to not change the working directory
    to "/" after changing into the chroot(2) jail, thus retaining the current wor-
    king directory.  The new option is only permitted if the new root directory is
    the old "/", and therefore is useful with the --group and --userspec options.
  * dd accepts a new status=progress level to print data transfer statistics
    on stderr approximately every second.
  * numfmt can now process multiple fields with field range specifications similar
    to cut, and supports setting the output precision with the --format option.
  * split accepts a new --separator option to select a record separator character
    other than the default newline character.
  * stty allows setting the "extproc" option where supported, which is
    a useful setting with high latency links.
  * sync no longer ignores arguments, and syncs each specified file, or with the
  - -file-system option, the file systems associated with each specified file.
  * tee accepts a new --output-error option to control operation with pipes
    and output errors in general.
  * * Changes in behavior
  * df no longer suppresses separate exports of the same remote device, as
    these are generally explicitly mounted.  The --total option does still
    suppress duplicate remote file systems.
    [suppression was introduced in coreutils-8.21]
  * mv no longer supports moving a file to a hardlink, instead issuing an error.
    The implementation was susceptible to races in the presence of multiple mv
    instances, which could result in both hardlinks being deleted.  Also on case
    insensitive file systems like HFS, mv would just remove a hardlinked 'file'
    if called like `mv file File`.  The feature was added in coreutils-5.0.1.
  * numfmt --from-unit and --to-unit options now interpret suffixes as SI units,
    and IEC (power of 2) units are now specified by appending 'i'.
  * tee will exit early if there are no more writable outputs.
  * tee does not treat the file operand '-' as meaning standard output any longer,
    for better conformance to POSIX.  This feature was added in coreutils-5.3.0.
  * timeout --foreground no longer sends SIGCONT to the monitored process,
    which was seen to cause intermittent issues with GDB for example.
  * * Improvements
  * cp,install,mv will convert smaller runs of NULs in the input to holes,
    and cp --sparse=always avoids speculative preallocation on XFS for example.
  * cp will read sparse files more efficiently when the destination is a
    non regular file.  For example when copying a disk image to a device node.
  * mv will try a reflink before falling back to a standard copy, which is
    more efficient when moving files across BTRFS subvolume boundaries.
  * stat and tail now know about IBRIX.  stat -f --format=%%T now reports the file
    system type, and tail -f uses polling for files on IBRIX file systems.
  * wc -l processes short lines much more efficiently.
  * References from --help and the man pages of utilities have been corrected
    in various cases, and more direct links to the corresponding online
    documentation are provided.
- Patches adapted because of changed sources:
  coreutils-disable_tests.patch
  coreutils-i18n.patch
  coreutils-misc.patch
  coreutils-ocfs2_reflinks.patch
  coreutils-remove_hostname_documentation.patch
  coreutils-remove_kill_documentation.patch
  coreutils-skip-gnulib-test-tls.patch
  coreutils-tests-shorten-extreme-factor-tests.patch
  sort-keycompare-mb.patch
- Patches removed because they're included in 8.24:
  coreutils-chroot-perform-chdir-unless-skip-chdir.patch
  coreutils-df-doc-df-a-includes-duplicate-file-systems.patch
  coreutils-df-improve-mount-point-selection.patch
  coreutils-df-show-all-remote-file-systems.patch
  coreutils-df-total-suppress-separate-remotes.patch
  coreutils-doc-adjust-reference-to-info-nodes-in-man-pages.patch
  coreutils-fix_false_du_failure_on_newer_xfs.patch
  coreutils-fix-man-deps.patch
  coreutils-tests-aarch64-env.patch
  coreutils-tests-make-inotify-rotate-more-robust-and-efficient.patch
  coreutils-tests-rm-ext3-perf-increase-timeout.patch
* Wed Jun  3 2015 mail@bernhard-voelker.de
- coreutils-doc-adjust-reference-to-info-nodes-in-man-pages.patch:
  add upstream patch:
  doc: adjust reference to info nodes in man pages (boo#933396)
- coreutils-i18n.patch: Use a later version of the previous patch
  to fix the sort I18N issue (boo#928749, CVE-2015-4041) to also
  avoid CVE-2015-4042.
  https://github.com/pixelb/coreutils/commit/bea5e36cc876
* Tue May 12 2015 mail@bernhard-voelker.de
- Download keyring file from Savannah; prefer HTTPS over FTP
  for remote sources.
* Tue May 12 2015 mail@bernhard-voelker.de
- Fix memory handling error with case insensitive sort using UTF-8
  (boo#928749): coreutils-i18n.patch
  src/sort.c (keycompare_mb): Ensure the buffer is big enough
  to handle anything output from wctomb().  Theoretically any
  input char could be converted to multiple output chars,
  and so we need to multiply the storage by MB_CUR_MAX.
* Tue Apr  7 2015 crrodriguez@opensuse.org
- If coreutils changes, for consistency, we must regenerate
  the initrd.
* Thu Apr  2 2015 mpluskal@suse.com
- Add gpg signature
* Thu Mar 26 2015 rguenther@suse.com
- For openSUSE > 13.2 drop coreutils-build-timeout-as-pie.patch and
  instead add a BuildRequire for gcc-PIE.
* Thu Feb  5 2015 mail@bernhard-voelker.de
- coreutils-tests-aarch64-env.patch: Add patch to avoid false
  positive failures of the coreutils-testsuite on OBS/aarch64:
  work around execve() reversing the order of "env" output.
* Mon Jan 19 2015 mail@bernhard-voelker.de
- Add upstream patches for df(1) from upstream, thus aligning with SLES12:
  * df: improve mount point selection with inaccurate mount list:
  - coreutils-df-improve-mount-point-selection.patch
  * doc: mention that df -a includes duplicate file systems (deb#737399)
  - coreutils-df-doc-df-a-includes-duplicate-file-systems.patch
  * df: ensure -a shows all remote file system entries (deb#737399)
  - coreutils-df-show-all-remote-file-systems.patch
  * df: only suppress remote mounts of separate exports with --total
    (deb#737399, rh#920806, boo#866010, boo#901905)
  - coreutils-df-total-suppress-separate-remotes.patch
- Refresh patches:
  * coreutils-chroot-perform-chdir-unless-skip-chdir.patch
  * coreutils-tests-make-inotify-rotate-more-robust-and-efficient.patch
* Sat Nov  1 2014 mail@bernhard-voelker.de
  Avoid spurious false positive failures of the testsuite on OBS due
  to high load.
- coreutils-tests-rm-ext3-perf-increase-timeout.patch:
  Add patch to increase timeout.
- coreutils-tests-make-inotify-rotate-more-robust-and-efficient.patch:
  Add upstream patch.
* Sat Sep 27 2014 schwab@linux-m68k.org
- sort-keycompare-mb.patch: make sure to NUL-terminate the sort keys.
  Fixes http://bugs.gnu.org/18540
* Thu Sep 18 2014 pth@suse.de
- Add coreutils-fix_false_du_failure_on_newer_xfs.patch that fixes a false
  negative in the testsuite.
- Add coreutils-disable_tests.patch to not run a tests that fail inside the OBS.
- Add coreutils-test_without_valgrind.patch to not use valgrind in shuf-reservoir.
* Fri Aug  1 2014 mail@bernhard-voelker.de
- Add patches for upstream glitches:
  - coreutils-fix-man-deps.patch
  - coreutils-chroot-perform-chdir-unless-skip-chdir.patch
- Refresh patches:
  - coreutils-build-timeout-as-pie.patch
  - coreutils-getaddrinfo.patch
  - coreutils-i18n.patch
  - coreutils-misc.patch
  - coreutils-ocfs2_reflinks.patch
  - coreutils-remove_hostname_documentation.patch
  - coreutils-remove_kill_documentation.patch
  - coreutils-skip-gnulib-test-tls.patch
  - coreutils-tests-shorten-extreme-factor-tests.patch
- Remove now-upstream patches:
  - coreutils-copy-fix-selinux-existing-dirs.patch
  - coreutils-gnulib-tests-ppc64le.patch
  - coreutils-tests-avoid-FP-cp-cpuinfo.patch
  - coreutils-test-avoid-FP-when-no-ACL-support.patch
  - coreutils-ln-avoid-segfault-for-empty-target.patch
  - coreutils-date-avoid-crash-in-TZ-parsing.patch
  - coreutils-shuf-repeat-avoid-crash-when-input-empty.patch
  - coreutils-improve_df_--human_and_--si,_help_and_man_page.patch
  - coreutils-avoid_sizeof_charPP__static_analysis_warning.patch
  - coreutils-also_deduplicate_virtual_file_systems.patch
  - coreutils-fix_handling_of_symlinks_in_mount_list.patch
  - coreutils-ignore_non_file_system_entries_in_proc_mounts.patch
  - coreutils-avoid_clang_-Wtautological-constant-out-of-range-compare_warning.patch
  - coreutils-use_the_last_device_name_provided_by_the_system.patch
  - coreutils-avoid_compiler_warnings_with_some_assert_implementations.patch
  - coreutils-use_all_of_the_last_device_details_provided.patch
  - coreutils-output_placeholder_values_for_inaccessible_mount_points.patch
  - coreutils-look_for_accessible_mount_points_for_specified_devices.patch
  - coreutils-report_correct_device_in_presence_of_eclipsed_mounts.patch
  - coreutils-avoid_an_inconsequential_mem_leak.patch
- Update to 8.23 (2014-07-18) [stable]
  * * Bug fixes
  chmod -Rc no longer issues erroneous warnings for files with special bits set.
  [bug introduced in coreutils-6.0]
  cp -a, mv, and install --preserve-context, once again set the correct SELinux
  context for existing directories in the destination.  Previously they set
  the context of an existing directory to that of its last copied descendent.
  [bug introduced in coreutils-8.22]
  cp -a, mv, and install --preserve-context, no longer seg fault when running
  with SELinux enabled, when copying from file systems that return an error
  when reading the SELinux context for a file.
  [bug introduced in coreutils-8.22]
  cp -a and mv now preserve xattrs of symlinks copied across file systems.
  [bug introduced with extended attribute preservation feature in coreutils-7.1]
  date could crash or go into an infinite loop when parsing a malformed TZ="".
  [bug introduced with the --date='TZ="" ..' parsing feature in coreutils-5.3.0]
  dd's ASCII and EBCDIC conversions were incompatible with common practice and
  with POSIX, and have been corrected as follows.  First, conv=ascii now
  implies conv=unblock, and conv=ebcdic and conv=ibm now imply conv=block.
  Second, the translation tables for dd conv=ascii and conv=ebcdic have been
  corrected as shown in the following table, where A is the ASCII value, W is
  the old, wrong EBCDIC value, and E is the new, corrected EBCDIC value; all
  values are in octal.
    A   W   E
    041 117 132
    133 112 255
    135 132 275
    136 137 232
    174 152 117
    176 241 137
    313 232 152
    325 255 112
    345 275 241
  [These dd bugs were present in "the beginning".]
  df has more fixes related to the newer dynamic representation of file systems:
  Duplicates are elided for virtual file systems like tmpfs.
  Details for the correct device are output for points mounted multiple times.
  Placeholder values are output for inaccessible file systems, rather than
  than error messages or values for the wrong file system.
  [These bugs were present in "the beginning".]
  df now outputs all appropriate entries in the presence of bind mounts.
  On some systems, entries would have been incorrectly elided due to
  them being considered "dummy" mounts.
  [bug introduced in coreutils-8.22]
  du now silently ignores directory cycles introduced with bind mounts.
  Previously it would issue a warning and exit with a failure status.
  [bug introduced in coreutils-8.1]
  head --bytes=-N and --lines=-N now handles devices more
  consistently, not ignoring data from virtual devices like /dev/zero,
  or on BSD systems data from tty devices.
  [bug introduced in coreutils-5.0.1]
  head --bytes=-N - no longer fails with a bogus diagnostic when stdin's
  seek pointer is not at the beginning.
  [bug introduced with the --bytes=-N feature in coreutils-5.0.1]
  head --lines=-0, when the input does not contain a trailing '\n',
  now copies all input to stdout.  Previously nothing was output in this case.
  [bug introduced with the --lines=-N feature in coreutils-5.0.1]
  id, when invoked with no user name argument, now prints the correct group ID.
  Previously, in the default output format, it would print the default group ID
  in the password database, which may be neither real nor effective.  For e.g.,
  when run set-GID, or when the database changes outside the current session.
  [bug introduced in coreutils-8.1]
  ln -sf now replaces symbolic links whose targets can't exist.  Previously
  it would display an error, requiring --no-dereference to avoid the issue.
  [bug introduced in coreutils-5.3.0]
  ln -sr '' F no longer segfaults.  Now works as expected.
  [bug introduced with the --relative feature in coreutils-8.16]
  numfmt now handles blanks correctly in all unibyte locales.  Previously
  in locales where character 0xA0 is a blank, numfmt would mishandle it.
  [bug introduced when numfmt was added in coreutils-8.21]
  ptx --format long option parsing no longer falls through into the --help case.
  [bug introduced in TEXTUTILS-1_22i]
  ptx now consistently trims whitespace when processing multiple files.
  [This bug was present in "the beginning".]
  seq again generates correct output with start or end values = -0.
  [bug introduced in coreutils-8.20.]
  shuf --repeat no longer dumps core if the input is empty.
  [bug introduced with the --repeat feature in coreutils-8.22]
  sort when using multiple threads now avoids undefined behavior with mutex
  destruction, which could cause deadlocks on some implementations.
  [bug introduced in coreutils-8.6]
  tail -f now uses polling mode for VXFS to cater for its clustered mode.
  [bug introduced with inotify support added in coreutils-7.5]
  * * New features
  od accepts a new option: --endian=TYPE to handle inputs with different byte
  orders, or to provide consistent output on systems with disparate endianness.
  configure accepts the new option --enable-single-binary to build all the
  selected programs in a single binary called "coreutils".  The selected
  programs can still be called directly using symlinks to "coreutils" or
  shebangs with the option --coreutils-prog= passed to this program.  The
  install behavior is determined by the option --enable-single-binary=symlinks
  or --enable-single-binary=shebangs (the default).  With the symlinks option,
  you can't make a second symlink to any program because that will change the
  name of the called program, which is used by coreutils to determine the
  desired program.  The shebangs option doesn't suffer from this problem, but
  the /proc/$pid/cmdline file might not be updated on all the platforms.  The
  functionality of each program is not affected but this single binary will
  depend on all the required dynamic libraries even to run simple programs.
  If you desire to build some tools outside the single binary file, you can
  pass the option --enable-single-binary-exceptions=PROG_LIST with the comma
  separated list of programs you want to build separately.  This flag
  considerably reduces the overall size of the installed binaries which makes
  it suitable for embedded system.
  * * Changes in behavior
  chroot with an argument of "/" no longer implicitly changes the current
  directory to "/", allowing changing only user credentials for a command.
  chroot --userspec will now unset supplemental groups associated with root,
  and instead use the supplemental groups of the specified user.
  cut -d$'\n' again outputs lines identified in the --fields list, having
  not done so in v8.21 and v8.22.  Note using this non portable functionality
  will result in the delayed output of lines.
  ls with none of LS_COLORS or COLORTERM environment variables set,
  will now honor an empty or unknown TERM environment variable,
  and not output colors even with --colors=always.
  * * Improvements
  chroot has better --userspec and --group look-ups, with numeric IDs never
  causing name look-up errors.  Also look-ups are first done outside the chroot,
  in case the look-up within the chroot fails due to library conflicts etc.
  install now allows the combination of the -D and -t options.
  numfmt supports zero padding of numbers using the standard printf
  syntax of a leading zero, for example --format="%%010f".
  Also throughput was improved by up to 800%% by avoiding redundant processing.
  shred now supports multiple passes on GNU/Linux tape devices by rewinding
  the tape before each pass, avoids redundant writes to empty files,
  uses direct I/O for all passes where possible, and attempts to clear
  inode storage used for small files on some file systems.
  split avoids unnecessary input buffering, immediately writing input to output
  which is significant with --filter or when writing to fifos or stdout etc.
  stat and tail work better with HFS+, HFSX, LogFS and ConfigFS.  stat -f
  - -format=%%T now reports the file system type, and tail -f now uses inotify,
  rather than the default of issuing a warning and reverting to polling.
* Fri Jul 25 2014 pth@suse.de
- Incorporate 9 bugfixes, one documentation update and two maintenance
  patches that won't harm (bnc#888215), See NEWS for specifics:
  coreutils-improve_df_--human_and_--si,_help_and_man_page.patch
  coreutils-avoid_sizeof_charPP__static_analysis_warning.patch
  coreutils-also_deduplicate_virtual_file_systems.patch
  coreutils-fix_handling_of_symlinks_in_mount_list.patch
  coreutils-ignore_non_file_system_entries_in_proc_mounts.patch
  coreutils-avoid_clang_-Wtautological-constant-out-of-range-compare_warning.patch
  coreutils-use_the_last_device_name_provided_by_the_system.patch
  coreutils-avoid_compiler_warnings_with_some_assert_implementations.patch
  coreutils-use_all_of_the_last_device_details_provided.patch
  coreutils-output_placeholder_values_for_inaccessible_mount_points.patch
  coreutils-look_for_accessible_mount_points_for_specified_devices.patch
  coreutils-report_correct_device_in_presence_of_eclipsed_mounts.patch
  coreutils-avoid_an_inconsequential_mem_leak.patch
* Sun Mar 16 2014 mail@bernhard-voelker.de
- Add upstream patch (gnu#16855):
  * coreutils-shuf-repeat-avoid-crash-when-input-empty.patch: Add
  patch for shuf: with -r, don't dump core if the input is empty.
* Sun Mar 16 2014 mail@bernhard-voelker.de
- Add upstream patch (gnu#16872):
  * coreutils-date-avoid-crash-in-TZ-parsing.patch: Add patch for
  date: fix crash or infinite loop when parsing a malformed TZ="".
* Sun Mar 16 2014 mail@bernhard-voelker.de
- Add upstream patch (gnu#17010):
  * coreutils-ln-avoid-segfault-for-empty-target.patch: Add patch
  to avoid that ln(1) segfaults for an empty, relative target.
* Mon Feb 24 2014 pth@suse.de
- Add three patches from SLE12 that aren't upstream:
  coreutils-misc.patch (fixes for tests)
  coreutils-getaddrinfo.patch (fake success as there's no network
    in the build system)
  coreutils-ocfs2_reflinks.patch (support ocfs2 reflinks in cp)
* Fri Jan 24 2014 mail@bernhard-voelker.de
- Testsuite: avoid a failure of tests/mkdir/p-acl.sh on armv7l.
  * coreutils-test-avoid-FP-when-no-ACL-support.patch: Add upstream
  patch to improve the check for a working ACL support.
- Refresh patches with QUILT_REFRESH_ARGS="-p0 --no-timestamps"
  for easier patch handling.
* Thu Jan  9 2014 mail@bernhard-voelker.de
- Add upstream patch (coreutils-copy-fix-selinux-existing-dirs.patch):
  cp -a: set the correct SELinux context on already existing
  destination directories (rh#1045122).
- Merge I18n fixes from Fedora (coreutils-i18n.patch):
  * sort: fix sorting by non-first field (rh#1003544)
  * cut: avoid using slower multi-byte code in non-UTF-8 locales
    (rh#1021403, rh#499220).
- Testsuite: skip some tests:
  * coreutils-skip-some-sort-tests-on-ppc.patch: Add patch to
    skip 2 valgrind'ed sort tests on ppc/ppc64.
  * coreutils-skip-gnulib-test-tls.patch: Add patch to skip
    the gnulib test 'test-tls' on i586, x86_64, ppc and ppc64.
  * coreutils-tests-avoid-FP-cp-cpuinfo.patch: Add patch to skip a
    test when cp fails for /proc/cpuinfo which happens on aarch64.
  * coreutils-tests-shorten-extreme-factor-tests.patch: Add patch
    to skip most of the extreme-expensive factor tests.
* Sat Jan  4 2014 mail@bernhard-voelker.de
- Refresh patches to match the new version.
  * coreutils-build-timeout-as-pie.patch: Update line number.
  * coreutils-gnulib-tests-ppc64le.patch: Likewise.
  * coreutils-invalid-ids.patch: Likewise.
  * coreutils-remove_hostname_documentation.patch: Likewise.
  * coreutils-remove_kill_documentation.patch: Likewise.
  * coreutils-sysinfo.patch: Likewise.
  * coreutils-i18n.patch: Likewise.
- Additional changes in coreutils-i18n.patch:
  * Accommodate to upstream changes in cut.c and uniq.c.
  * Fix some compiler warnings.
  * Fix 145-mb test in tests/misc/uniq.pl.
  * Skip sort's "2[01]a" test cases for now
    to avoid a test failure on i586/x86_64.
- Remove now-upstream and therefore obsolete patches.
  * coreutils-8.21.de.po.xz: Remove, upstream is latest.
  * coreutils-gnulib-tests-fix-nap-race-obs.patch:
    Remove, now upstream.
  * coreutils-gnulib-tests-fix-nap-race.patch: Likewise.
  * longlong-aarch64.patch: Likewise.
- Update to 8.22 (2013-12-13) [stable]
  * * Bug fixes
  df now processes the mount list correctly in the presence of unstatable
  mount points.  Previously it may have failed to output some mount points.
  [bug introduced in coreutils-8.21]
  df now processes symbolic links and relative paths to special files containing
  a mounted file system correctly.  Previously df displayed the statistics about
  the file system the file is stored on rather than the one inside.
  [This bug was present in "the beginning".]
  df now processes disk device nodes correctly in the presence of bind mounts.
  Now df shows the base mounted file system rather than the last one mounted.
  [This bug was present in "the beginning".]
  install now removes the target file if the strip program failed for any
  reason.  Before, that file was left behind, sometimes even with wrong
  permissions.
  [This bug was present in "the beginning".]
  ln --relative now updates existing symlinks correctly.  Previously it based
  the relative link on the dereferenced path of an existing link.
  [This bug was introduced when --relative was added in coreutils-8.16.]
  ls --recursive will no longer exit with "serious" exit code (2), if there
  is an error reading a directory not specified on the command line.
  [Bug introduced in coreutils-5.3.0]
  mkdir, mkfifo, and mknod now work better when creating a file in a directory
  with a default ACL whose umask disagrees with the process's umask, on a
  system such as GNU/Linux where directory ACL umasks override process umasks.
  [bug introduced in coreutils-6.0]
  mv will now replace empty directories in the destination with directories
  from the source, when copying across file systems.
  [This bug was present in "the beginning".]
  od -wN with N larger than 64K on a system with 32-bit size_t would
  print approximately 2*N bytes of extraneous padding.
  [Bug introduced in coreutils-7.0]
  rm -I now prompts for confirmation before removing a write protected file.
  [Bug introduced in coreutils-6.8]
  shred once again uses direct I/O on systems requiring aligned buffers.
  Also direct I/O failures for odd sized writes at end of file are now handled.
  [The "last write" bug was introduced in coreutils-5.3.0 but masked
  by the alignment bug introduced in coreutils-6.0]
  tail --retry -f now waits for the files specified to appear.  Before, tail
  would immediately exit when such a file is initially inaccessible.
  [This bug was introduced when inotify support was added in coreutils-7.5]
  tail -F has improved handling of symlinks.  Previously tail didn't respond
  to the symlink target (re)appearing after being (re)created.
  [This bug was introduced when inotify support was added in coreutils-7.5]
  * * New features
  cp, install, mkdir, mknod, mkfifo and mv now support "restorecon"
  functionality through the -Z option, to set the SELinux context
  appropriate for the new item location in the file system.
  csplit accepts a new option: --suppressed-matched, to elide the lines
  used to identify the split points.
  df --output now accepts a 'file' field, to propagate a specified
  command line argument through to the output.
  du accepts a new option: --inodes to show the number of inodes instead
  of the blocks used.
  id accepts a new option: --zero (-z) to delimit the output entries by
  a NUL instead of a white space character.
  id and ls with -Z report the SMACK security context where available.
  mkdir, mkfifo and mknod with -Z set the SMACK context where available.
  id can now lookup by user ID, in addition to the existing name lookup.
  join accepts a new option: --zero-terminated (-z). As with the sort,uniq
  option of the same name, this makes join consume and produce NUL-terminated
  lines rather than newline-terminated lines.
  uniq accepts a new option: --group to print all items, while separating
  unique groups with empty lines.
  shred accepts new parameters to the --remove option to give greater
  control over that operation, which can greatly reduce sync overhead.
  shuf accepts a new option: --repeat (-r), which can repeat items in
  the output.
  * * Changes in behavior
  cp --link now dereferences a symbolic link as source before creating the
  hard link in the destination unless the -P,--no-deref option is specified.
  Previously, it would create a hard link of the symbolic link, even when
  the dereferencing options -L or -H were specified.
  cp, install, mkdir, mknod and mkfifo no longer accept an argument to the
  short -Z option.  The --context equivalent still takes an optional argument.
  dd status=none now suppresses all non fatal diagnostic messages,
  not just the transfer counts.
  df no longer accepts the long-obsolescent --megabytes option.
  stdbuf now requires at least one buffering mode option to be specified,
  as per the documented interface.
  * * Improvements
  base64 encoding throughput for bulk data is increased by about 60%%.
  md5sum can use libcrypto hash routines where allowed to potentially
  get better performance through using more system specific logic.
  sha1sum for example has improved throughput by 40%% on an i3-2310M.
  This also affects sha1sum, sha224sum, sha256sum, sha384sum and sha512sum.
  stat and tail work better with EFIVARFS, EXOFS, F2FS, HOSTFS, SMACKFS, SNFS
  and UBIFS.  stat -f --format=%%T now reports the file system type, and tail -f
  now uses inotify for files on all those except SNFS, rather than the default
  (for unknown file system types) of issuing a warning and reverting to polling.
  shuf outputs subsets of large inputs much more efficiently.
  Reservoir sampling is used to limit memory usage based on the number of
  outputs, rather than the number of inputs.
  shred increases the default write block size from 12KiB to 64KiB
  to align with other utilities and reduce the system call overhead.
  split --line-bytes=SIZE, now only allocates memory as needed rather
  than allocating SIZE bytes at program start.
  stty now supports configuring "stick" (mark/space) parity where available.
  * * Build-related
  factor now builds on aarch64 based systems [bug introduced in coreutils-8.20]
* Thu Dec 19 2013 uweigand@de.ibm.com
- coreutils-gnulib-tests-ppc64le.patch: Fix imported gnulib long double
  math tests for little-endian PowerPC.
* Thu Dec 19 2013 mail@bernhard-voelker.de
- Fix issue with binary input in non-C locale (rh#1036289)
  (coreutils-i18n.patch): Initialize memory for some edge cases
  in the i18n patch for uniq and join.
* Wed Dec 11 2013 mail@bernhard-voelker.de
- Avoid false sort test failure (coreutils-i18n.patch):
  As for the C locale, skip the multi-byte test case
  'output-is-input-mb.p'.
* Sat Dec  7 2013 schwab@linux-m68k.org
- Require valgrind only when it exists
* Sun Dec  1 2013 mail@bernhard-voelker.de
- Update I18N patch from Fedora:
  (coreutils-i18n.patch)
  * sort: fix multibyte incompabilities (rh#821264)
  * pr -e, with a mix of backspaces and TABs, could corrupt the
    heap in multibyte locales (analyzed by J.Koncicky)
  * path in the testsuite to cover i18n regressions
  * Enable cut and sort-merge perl tests for multibyte as well
- Refresh longlong-aarch64.patch.
* Wed Aug  7 2013 mail@bernhard-voelker.de
- Remove "BuildRequires: help2man" as it is included.
* Tue Aug  6 2013 pth@suse.de
- Remove the the unnecessary povision of itself as rpmbuild takes
  care of that.
- Remove all traces of coreutils-8.9-singlethreaded-sort.patch in
  the spec file.
* Tue Jul 23 2013 mail@bernhard-voelker.de
- Undo the previous change.
  Remove configure options gl_cv_func_printf_directive_n and
  gl_cv_func_printf_infinite_long_double again because of constant
  factory build failures on x86_64 and i586.  The argument for
  adding them was that the fortify checks would be bypassed
  by the gnulib "reimplementation of printf", but that is not
  the case: instead, gnulib just adds some wrapping code to ensure
  a consistent behaviour on all supported platforms.
* Mon Jul  8 2013 schwab@suse.de
- Override broken configure checks
- coreutils-gl_printf_safe.patch: remove unused patch
* Sun Jun 16 2013 jengelh@inai.de
- Explicitly list libattr-devel as BuildRequires
- More robust make install call
* Fri Jun  7 2013 schwab@suse.de
- longlong-aarch64.patch: fix build on aarch64
* Fri Jun  7 2013 mail@bernhard-voelker.de
- Remove su(1) and kill(1) - both are provided by util-linux now.
  * su.pamd, su.default, coreutils-su.patch: Remove patch and PAM
    config files related to su(1).
  * coreutils-remove_kill_documentation.patch: Add patch to remove
    kill from the texinfo manual.
  * coreutils.spec: Remove above, su-related patch and sources.
    Remove Requires:pam and BuildRequires:pam-devel.
    Remove Provides:/bin/{su,kill}.
    Remove paragraph mentioning su(1) and kill(1) in %%description.
    Remove `moving su trickery` and other left-overs from %%install,
    %%post and %%files.
    Remove %%posttrans and %%verifyscript sections (as these contained
    su-related stuff).
    Add code to %%install to remove kill's program and man page.
* Mon May 20 2013 mail@bernhard-voelker.de
- Try to fix nap() races in gnulib-tests.
  (coreutils-gnulib-tests-fix-nap-race.patch: add upstream patch)
  (coreutils-gnulib-tests-fix-nap-race-obs.patch: add openSUSE patch for OBS)
* Wed May 15 2013 mhrusecky@suse.com
- Provides: /bin/{kill,su}
  * for compatibility with programs requiring these (like lsb) until these will
    be provided by util-linux
* Thu Apr  4 2013 mail@bernhard-voelker.de
- Fix source url for coreutils-testsuite.
* Thu Mar 21 2013 mmeister@suse.com
- Added url as source.
  Please see http://en.opensuse.org/SourceUrls
* Thu Mar 21 2013 mail@bernhard-voelker.de
- Fix multibyte issue in unexpand (rh#821262)
  (coreutils-i18n.patch: patch by Roman Kollár <rkollar@redhat.com>)
- Fix cut to terminate mbdelim string
  Otherwise, cut might do an unbounded strdup of the delimiter string
  in i18n mode (https://bugzilla.redhat.com/show_bug.cgi?id=911929)
  (coreutils-i18n.patch, from Mark Wielaard <mjw@redhat.com>)
- Add su(1) again
  Now, su(1) will be provided via a symlink trick
  to the file installed with a ".core" suffix.
  By this, we can upgrade to 8.21 without having to wait
  for a util-linux version providing it.
  * coreutils-su.patch: Add cumulative su patch from previous Base:System
    version 8.17, ported to 8.21 build structure. This supersedes the
    following partial patches:
    coreutils-8.6-compile-su-with-fpie.diff,
    coreutils-8.6-honor-settings-in-etc-default-su-resp-etc-login.defs.diff,
    coreutils-8.6-log-all-su-attempts.diff,
    coreutils-8.6-make-sure-sbin-resp-usr-sbin-are-in-PATH.diff,
    coreutils-8.6-pam-support-for-su.diff,
    coreutils-8.6-set-sane-default-path.diff,
    coreutils-8.6-update-man-page-for-pam.diff,
    coreutils-bnc#697897-setsid.patch.
  * pam, pam-devel: Add as requirements, also during build.
  * coreutils.spec (%%description): Clarify that su is included although removed
    upstreams.
    (%%install): Install su+kill files with suffix ".core".
    (%%post): Move setting permissions on su from %%posttrans to %%install.
    (%%posttrans): Create symlinks to files with ".core" suffix unless already
    existing.
- Install kill(1) with the same symlink trick.
- Remove now-obsolete patches and files:
  * coreutils-8.17.de.po.xz:
  * coreutils-8.17.tar.xz:
    Remove sources + translation of previous version
  * coreutils-acl-nofollow.patch:
  * coreutils-basename_documentation.patch:
  * coreutils-cp-corrupt-fragmented-sparse.patch:
  * coreutils-df-always-hide-rootfs.patch:
  * coreutils-skip-du-slink-test.patch:
    Fixed upstream.
  * coreutils-getaddrinfo.patch:
  * coreutils-misc.patch:
  * coreutils-no_silent-rule.patch:
    Remove test and build related patches.
  * coreutils-ptr_int_casts.patch:
    Remove because merged into coreutils-i18n.patch.
- Add files:
  * coreutils-8.21.tar.xz:
    Add tarball of the new upstream version
  * coreutils-8.21.de.po.xz:
    Add language file.
- Update patches:
  * coreutils-i18n.patch
    Merge some Fedora changes to keep the i18n patch like theirs.
    Fix and cleanup sort's multibyte test with incorporated test data.
  * coreutils-remove_hostname_documentation.patch
- Add patch to build 'timeout' as PIE (OBS requires it).
  This patch actually was included in one of the old su patches.
  * new patch name: coreutils-build-timeout-as-pie.patch
- Temporary disable some questionable patches (by commenting in the spec file):
  * coreutils-gl_printf_safe.patch
  * coreutils-8.9-singlethreaded-sort.patch
- Change build / spec file:
  * Bump version from 8.17 to 8.21.
  * Fix macro invocation in "Provides" for stat.
  * Remove ancient "Obsoletes" entries.
  * Remove/add the above removed/added sources and patches.
  * Temporarily comment the code for statically linking LIB_GMP
    (as it does not work).
  * Remove -Wall from CFLAGS as it is already included in OBS' default options.
  * Remove the --without-included-regex option to use
    coreutils' regex implementation.
  * Remove custom gl_cv_func_printf_directive_n and gl_cv_func_isnanl_works.
  * Touch "man/*.x" to force the rebuild of the man pages.
  * Make sort's multi-byte test script executable in %%check section.
  * Hardcode package name for "%%find_lang" and "%%files lang -f" lines.
  * In the %%files section, add the COPYING and THANKS files.
    Furthermore, fix the path to the LC_TIME files.
  * Change package description to accomodate to added programs
    (hostid, nproc, realpath, stdbuf, truncate)
    and mention the hacky installation of programs to move (kill, su).
- Update to 8.21 (2013-02-14) [stable]
  * * New programs
  numfmt: reformat numbers
  * * New features
  df now accepts the --output[=FIELD_LIST] option to define the list of columns
  to include in the output, or all available columns if the FIELD_LIST is
  omitted.  Note this enables df to output both block and inode fields together.
  du now accepts the --threshold=SIZE option to restrict the output to entries
  with such a minimum SIZE (or a maximum SIZE if it is negative).
  du recognizes -t SIZE as equivalent, for compatibility with FreeBSD.
  * * Bug fixes
  cp --no-preserve=mode now no longer exits non-zero.
  [bug introduced in coreutils-8.20]
  cut with a range like "N-" no longer allocates N/8 bytes.  That buffer
  would never be used, and allocation failure could cause cut to fail.
  [bug introduced in coreutils-8.10]
  cut no longer accepts the invalid range 0-, which made it print empty lines.
  Instead, cut now fails and emits an appropriate diagnostic.
  [This bug was present in "the beginning".]
  cut now handles overlapping to-EOL ranges properly.  Before, it would
  interpret "-b2-,3-" like "-b3-".  Now it's treated like "-b2-".
  [This bug was present in "the beginning".]
  cut no longer prints extraneous delimiters when a to-EOL range subsumes
  another range.  Before, "echo 123|cut --output-delim=: -b2-,3" would print
  "2:3".  Now it prints "23".  [bug introduced in 5.3.0]
  cut -f no longer inspects input line N+1 before fully outputting line N,
  which avoids delayed output for intermittent input.
  [bug introduced in TEXTUTILS-1_8b]
  factor no longer loops infinitely on 32 bit powerpc or sparc systems.
  [bug introduced in coreutils-8.20]
  install -m M SOURCE DEST no longer has a race condition where DEST's
  permissions are temporarily derived from SOURCE instead of from M.
  pr -n no longer crashes when passed values >= 32.  Also, line numbers are
  consistently padded with spaces, rather than with zeros for certain widths.
  [bug introduced in TEXTUTILS-1_22i]
  seq -w ensures that for numbers input in scientific notation,
  the output numbers are properly aligned and of the correct width.
  [This bug was present in "the beginning".]
  seq -w ensures correct alignment when the step value includes a precision
  while the start value does not, and the number sequence narrows.
  [This bug was present in "the beginning".]
  seq -s no longer prints an erroneous newline after the first number, and
  outputs a newline after the last number rather than a trailing separator.
  Also seq no longer ignores a specified step value when the end value is 1.
  [bugs introduced in coreutils-8.20]
  timeout now ensures that blocking of ALRM signals is not inherited from
  its parent, which would cause timeouts to be ignored.
  [the bug dates back to the initial implementation]
  * * Changes in behavior
  df --total now prints '-' into the target column (mount point) of the
  summary line, accommodating the --output option where the target field
  can be in any column.  If there is no source column, then df prints
  'total' in the target column.
  df now properly outputs file system information with bind mounts present on
  the system by skipping duplicate entries (identified by the device number).
  Consequently, df also elides the early-boot pseudo file system type "rootfs".
  nl no longer supports the --page-increment option, which has been
  deprecated since coreutils-7.5.  Use --line-increment instead.
  * * Improvements
  readlink now supports multiple arguments, and a complementary
  - z, --zero option to delimit output items with the NUL character.
  stat and tail now know about CEPH.  stat -f --format=%%T now reports the file
  system type, and tail -f uses polling for files on CEPH file systems.
  stty now supports configuring DTR/DSR hardware flow control where available.
  * * Build-related
  Perl is now more of a prerequisite.  It has long been required in order
  to run (not skip) a significant percentage of the tests.  Now, it is
  also required in order to generate proper man pages, via help2man.  The
  generated man/*.1 man pages are no longer distributed.  Building without
  perl, you would create stub man pages.  Thus, while perl is not an
  official prerequisite (build and "make check" will still succeed), any
  resulting man pages would be inferior.  In addition, this fixes a bug
  in distributed (not from clone) Makefile.in that could cause parallel
  build failure when building from modified sources, as is common practice
  for a patched distribution package.
  factor now builds on x86_64 with x32 ABI, 32 bit MIPS, and all HPPA systems,
  by avoiding incompatible asm.  [bug introduced in coreutils-8.20]
  A root-only test predicate would always fail.  Its job was to determine
  whether our dummy user, $NON_ROOT_USERNAME, was able to run binaries from
  the build directory.  As a result, all dependent tests were always skipped.
  Now, those tests may be run once again.  [bug introduced in coreutils-8.20]
- Update to 8.20 (2012-10-23) [stable]
  * * New features
  dd now accepts 'status=none' to suppress all informational output.
  md5sum now accepts the --tag option to print BSD-style output with GNU
  file name escaping.  This also affects sha1sum, sha224sum, sha256sum,
  sha384sum and sha512sum.
  * * Bug fixes
  cp could read from freed memory and could even make corrupt copies.
  This could happen with a very fragmented and sparse input file,
  on GNU/Linux file systems supporting fiemap extent scanning.
  This bug also affects mv when it resorts to copying, and install.
  [bug introduced in coreutils-8.11]
  cp --no-preserve=mode now no longer preserves the original file's
  permissions but correctly sets mode specified by 0666 & ~umask
  du no longer emits a "disk-corrupted"-style diagnostic when it detects
  a directory cycle that is due to a bind-mounted directory.  Instead,
  it detects this precise type of cycle, diagnoses it as such and
  eventually exits nonzero.
  factor (when using gmp) would mistakenly declare some composite numbers
  to be prime, e.g., 465658903, 2242724851, 6635692801 and many more.
  The fix makes factor somewhat slower (~25%%) for ranges of consecutive
  numbers, and up to 8 times slower for some worst-case individual numbers.
  [bug introduced in coreutils-7.0, with GNU MP support]
  ls now correctly colors dangling symlinks when listing their containing
  directories, with orphaned symlink coloring disabled in LS_COLORS.
  [bug introduced in coreutils-8.14]
  rm -i -d now prompts the user then removes an empty directory, rather
  than ignoring the -d option and failing with an 'Is a directory' error.
  [bug introduced in coreutils-8.19, with the addition of --dir (-d)]
  rm -r S/ (where S is a symlink-to-directory) no longer gives the invalid
  "Too many levels of symbolic links" diagnostic.
  [bug introduced in coreutils-8.6]
  seq now handles arbitrarily long non-negative whole numbers when the
  increment is 1 and when no format-changing option is specified.
  Before, this would infloop:
    b=100000000000000000000; seq $b $b
  [the bug dates back to the initial implementation]
  * * Changes in behavior
  nproc now diagnoses with an error, non option command line parameters.
  * * Improvements
  factor's core has been rewritten for speed and increased range.
  It can now factor numbers up to 2^128, even without GMP support.
  Its speed is from a few times better (for small numbers) to over
  10,000 times better (just below 2^64).  The new code also runs a
  deterministic primality test for each prime factor, not just a
  probabilistic test.
  seq is now up to 70 times faster than it was in coreutils-8.19 and prior,
  but only with non-negative whole numbers, an increment of 1, and no
  format-changing options.
  stat and tail know about ZFS, VZFS and VMHGFS.  stat -f --format=%%T now
  reports the file system type, and tail -f now uses inotify for files on
  ZFS and VZFS file systems, rather than the default (for unknown file
  system types) of issuing a warning and reverting to polling.  tail -f
  still uses polling for files on VMHGFS file systems.
  * * Build-related
  root-only tests now check for permissions of our dummy user,
  $NON_ROOT_USERNAME, before trying to run binaries from the build directory.
  Before, we would get hard-to-diagnose reports of failing root-only tests.
  Now, those tests are skipped with a useful diagnostic when the root tests
  are run without following the instructions in README.
  We now build most directories using non-recursive make rules.  I.e.,
  rather than running make in man/, lib/, src/, tests/, instead, the top
  level Makefile.am includes a $dir/local.mk that describes how to build
  the targets in the corresponding directory.  Two directories remain
  unconverted: po/, gnulib-tests/.  One nice side-effect is that the more
  accurate dependencies have eliminated a nagging occasional failure that
  was seen when running parallel "make syntax-check".
- Update to 8.19 (2012-08-20) [stable]
  * * Bug fixes
  df now fails when the list of mounted file systems (/etc/mtab) cannot
  be read, yet the file system type information is needed to process
  certain options like -a, -l, -t and -x.
  [This bug was present in "the beginning".]
  sort -u could fail to output one or more result lines.
  For example, this command would fail to print "1":
  (yes 7 | head -11; echo 1) | sort --p=1 -S32b -u
  [bug introduced in coreutils-8.6]
  sort -u could read freed memory.
  For example, this evokes a read from freed memory:
  perl -le 'print "a\n"."0"x900'|valgrind sort --p=1 -S32b -u>/dev/null
  [bug introduced in coreutils-8.6]
  * * New features
  rm now accepts the --dir (-d) option which makes it remove empty directories.
  Since removing empty directories is relatively safe, this option can be
  used as a part of the alias rm='rm --dir'.  This improves compatibility
  with Mac OS X and BSD systems which also honor the -d option.
- Update to 8.18 (2012-08-12) [stable]
  * * Bug fixes
  cksum now prints checksums atomically so that concurrent
  processes will not intersperse their output.
  [the bug dates back to the initial implementation]
  date -d "$(printf '\xb0')" would print 00:00:00 with today's date
  rather than diagnosing the invalid input.  Now it reports this:
  date: invalid date '\260'
  [This bug was present in "the beginning".]
  df no longer outputs control characters present in the mount point name.
  Such characters are replaced with '?', so for example, scripts consuming
  lines output by df, can work reliably.
  [This bug was present in "the beginning".]
  df --total now exits with an appropriate diagnostic and error code, when
  file system --type options do not lead to a processed file system.
  [This bug dates back to when --total was added in coreutils-7.0]
  head --lines=-N (-n-N) now resets the read pointer of a seekable input file.
  This means that "head -n-3" no longer consumes all of its input, and lines
  not output by head may be processed by other programs.  For example, this
  command now prints the final line, 2, while before it would print nothing:
    seq 2 > k; (head -n-1 > /dev/null; cat) < k
  [This bug was present in "the beginning".]
  ls --color would mis-color relative-named symlinks in /
  [bug introduced in coreutils-8.17]
  split now ensures it doesn't overwrite the input file with generated output.
  [the bug dates back to the initial implementation]
  stat and df now report the correct file system usage,
  in all situations on GNU/Linux, by correctly determining the block size.
  [df bug since coreutils-5.0.91, stat bug since the initial implementation]
  tail -f no longer tries to use inotify on AUFS or PanFS file systems
  [you might say this was introduced in coreutils-7.5, along with inotify
  support, but even now, its magic number isn't in the usual place.]
  * * New features
  stat -f recognizes the new remote file system types: aufs, panfs.
  * * Changes in behavior
  su: this program has been removed.  We stopped installing "su" by
  default with the release of coreutils-6.9.90 on 2007-12-01.  Now,
  that the util-linux package has the union of the Suse and Fedora
  patches as well as enough support to build on the Hurd, we no longer
  have any reason to include it here.
  * * Improvements
  sort avoids redundant processing in the presence of inaccessible inputs,
  or unwritable output.  Sort now diagnoses certain errors at start-up,
  rather than after potentially expensive processing.
  sort now allocates no more than 75%% of physical memory by default,
  to better share system resources, and thus operate more efficiently.
  [The default max memory usage changed from 50%% to 100%% in coreutils-8.16]
* Sun Jan 27 2013 coolo@suse.com
- do not require texinfo for building, texlive is a bit too heavy
* Sun Jan 20 2013 mail@bernhard-voelker.de
- Avoid segmentation fault in "join -i" with long line input
  (bnc#798541, VUL-1, CVE-2013-0223)
  * src/join.c: Instead of usig unreliable alloca() stack allocation,
    use heap allocation via xmalloc()+free().
    (coreutils-i18n.patch, from Philipp Thomas <pth@suse.de>)
- Avoid segmentation fault in "sort -d" and "sort -M" with long line input
  (bnc#798538, VUL-1, CVE-2013-0221)
  * src/sort.c: Instead of usig unreliable alloca() stack allocation,
    use heap allocation via xmalloc()+free().
    (coreutils-i18n.patch, from Philipp Thomas <pth@suse.de>)
- Avoid segmentation fault in "uniq" with long line input
  (bnc#796243, VUL-1, CVE-2013-0222)
  * src/cut.c: Instead of usig unreliable alloca() stack allocation,
    use heap allocation via xmalloc()+free().
    (coreutils-i18n.patch)
- Fix test-suite errors (bnc#798261).
  * tests/cp/fiemap-FMR: Fix path to src directory and declare
    require_valgrind_ function.
    (coreutils-cp-corrupt-fragmented-sparse.patch)
  * tests/misc/cut:
    Fix src/cut.c to properly pass output-delimiter tests.
    Synchronize cut.c related part of the i18n patch with Fedora's.
    Merge coreutils-i18n-infloop.patch into coreutils-i18n.patch.
    Merge coreutils-i18n-uninit.patch into coreutils-i18n.patch.
    In tests/misc/cut, do not replace the non-i18n error messages.
    (coreutils-i18n.patch)
  * tests/rm/ext3-perf:
    This test failed due to heavy parallel CPU and/or disk load because it
    is based on timeouts. Do not run the test-suite with 'make -jN.
    (coreutils.spec, coreutils-testsuite.spec)
  * tests/du/slink:
    This test fails on OBS infrastructure and will be removed upstreams
    in coreutils-8.21 anyway. Skip the test until we upgrade.
    Upstream discussion:
    http://lists.gnu.org/archive/html/coreutils/2013-01/msg00053.html
    (coreutils-skip-du-slink-test.patch)
  * Further spec changes:
    Run more tests: also run "very expensive" tests; add acl, python-pyinotify,
    strace and valgrind to the build requirements.
    Remove patch5 and patch6 as they are now merged into coreutils-i18n.patch
    (see above).
    (coreutils.spec, coreutils-testsuite.spec)
- Maintenance changes:
  (coreutils.spec, coreutils-testsuite.spec)
  * Add perl and texinfo to the build requirements as they are needed to
    re-generate the man pages and the texinfo documentation.
  * Remove already-active "-Wall" compiler option from CFLAGS variable.
  * Install the compressed test-suite.log into the documentation directory
    of the coreutils-testsuite package (section %%check and %%files).
  * Properly guard the spec sections for the coreutils and the
    coreutils-testsuite package.
  * Update patches to reflect new line numbers.
* Thu Jan 10 2013 phisama@suse.de
- Hardcode the name passed to find_lang so that it works for
  coreutils-testsuite too.
* Thu Jan 10 2013 pth@suse.de
- Don't call autoreconf on distributions older then 12.0
  because their autoconf is too old, so also patch Makefile.in
  in addition to Makefile.am where needed.
* Tue Dec  4 2012 mail@bernhard-voelker.de
- Update default posix version to 200112 (bnc#783352).
- Add coreutils-df-always-hide-rootfs.patch:
  Hide rootfs in df (df not using yet /proc/self/mountinfo).
* Mon Nov 19 2012 idonmez@suse.com
- Statically link to gmp otherwise expr depends on gmp and gmp
  configure script depends on expr which creates a build cycle.
* Thu Nov  8 2012 pth@suse.de
- Add the missing parts in coreutil.spec so that the testsuite is
  only run when coreutils-testsuite is built. Also add additional
  BuildRequires for the testsuite.
* Tue Nov  6 2012 pth@suse.de
- Add script pre_checkin.sh that creates spec and changes for
  coreutils-testsuite from their coreutils counterparts.
* Sun Oct 28 2012 mail@bernhard-voelker.de
- Add upstream patch:
  * cp could read from freed memory and could even make corrupt copies.
    This could happen with a very fragmented and sparse input file,
    on GNU/Linux file systems supporting fiemap extent scanning.
    This bug also affects mv when it resorts to copying, and install.
    [bug introduced in coreutils-8.11] (bnc#788459 gnu#12656)
* Fri Sep 21 2012 froh@suse.com
- fix coreutils-8.9-singlethreaded-sort.patch to
  respect OMP_NUM_THREADS again.
* Tue Jun 19 2012 pth@suse.de
- Update to 8.17:
  * * Bug fixes
  * stat no longer reports a negative file size as a huge positive
    number.  [bug present since 'stat' was introduced in
    fileutils-4.1.9]
  * * New features
  * split and truncate now allow any seekable files in situations
    where the file size is needed, instead of insisting on regular
    files.
  * fmt now accepts the --goal=WIDTH (-g) option.
  * stat -f recognizes new file system types: bdevfs, inodefs, qnx6
  * * Changes in behavior
  * cp,mv,install,cat,split: now read and write a minimum of 64KiB at
    a time.  This was previously 32KiB and increasing to 64KiB was
    seen to increase throughput by about 10%% when reading cached
    files on 64 bit GNU/Linux.
  * cp --attributes-only no longer truncates any existing destination
    file, allowing for more general copying of attributes from one
    file to another.
- Bring german message catalog up-to-date
* Tue May 15 2012 schwab@linux-m68k.org
- Build factor with gmp support
* Mon May  7 2012 pth@suse.de
- Two new upstream patches:
  * id and groups, when invoked with no user name argument, would
    print the default group ID listed in the password database, and
    sometimes that ID would be neither real nor effective.  For
    example, when run set-GID, or in a session for which the default
    group has just been changed, the new group ID would be listed,
    even though it is not yet effective.
  * 'cp S D' is no longer subject to a race: if an existing D were
    removed between the initial stat and subsequent
    open-without-O_CREAT, cp would fail with a confusing diagnostic
    saying that the destination, D, was not found.  Now, in this
    unusual case, it retries the open (but with O_CREAT), and hence
    usually succeeds.  With NFS attribute caching, the condition was
    particularly easy to trigger, since there, the removal of D could
    precede the initial stat.  [This bug was present in "the
    beginning".] (bnc#760926).
* Fri Apr 27 2012 pth@suse.de
- Make stdbuf binary find libstdbuf.so by looking in the right
  path (bnc#741241).
* Mon Apr 16 2012 pth@suse.de
- Update to 8.16:
  - Improvements:
  * As a GNU extension, 'chmod', 'mkdir', and 'install' now accept
    operators '-', '+', '=' followed by octal modes;
  * Also, ordinary numeric modes with five or more digits no longer
    preserve setuid and setgid bits, so that 'chmod 00755 FOO' now
    clears FOO's setuid and setgid bits.
  * dd now accepts the count_bytes, skip_bytes iflags and the
    seek_bytes oflag, to more easily allow processing portions of a
    file.
  * dd now accepts the conv=sparse flag to attempt to create sparse
    output, by seeking rather than writing to the output file.
  * ln now accepts the --relative option, to generate a relative
    symbolic link to a target, irrespective of how the target is
    specified.
  * split now accepts an optional "from" argument to
  - -numeric-suffixes, which changes the start number from the
    default of 0.
  * split now accepts the --additional-suffix option, to append an
    additional static suffix to output file names.
  * basename now supports the -a and -s options, which allow
    processing of more than one argument at a time.  Also the
    complementary -z option was added to delimit output items with
    the NUL character.
  * dirname now supports more than one argument. Also the complementary
    z option was added to delimit output items with the NUL character.
  - Bug fixes
  * du --one-file-system (-x) would ignore any non-directory
    specified on the command line. For example, "touch f; du -x f"
    would print nothing. [bug introduced in coreutils-8.15]
  * mv now lets you move a symlink onto a same-inode destination
    file that has two or more hard links.
  * "mv A B" could succeed, yet A would remain.
  * realpath no longer mishandles a root directory.
  - Improvements
  * ls can be much more efficient, especially with large directories
    on file systems for which getfilecon-, ACL-check- and XATTR-
    check-induced syscalls fail with ENOTSUP or similar.
  * 'realpath --relative-base=dir' in isolation now implies
    '--relative-to=dir' instead of causing a usage failure.
  * split now supports an unlimited number of split files as default
  behavior.
  For a detaild list se NEWS in the documentation.
- Add up-to-date german translation.
* Mon Apr 16 2012 pth@suse.de
- Add two upstream patches that speed up ls (bnc#752943):
  * Cache (l)getfilecon calls to avoid the vast majority of the failing
    underlying getxattr syscalls.
  * Avoids always-failing queries for whether a file has a nontrivial
    ACL and for whether a file has certain "capabilities".
* Fri Mar  9 2012 pth@suse.de
- Update to 8.15:
  * * New programs
    realpath: print resolved file names.
  * * Bug fixes
    du --one-file-system (-x) would ignore any non-directory specified on
    the command line.  For example, "touch f; du -x f" would print nothing.
    [bug introduced in coreutils-8.14]
    du -x no longer counts root directories of other file systems.
    [bug introduced in coreutils-5.1.0]
    ls --color many-entry-directory was uninterruptible for too long
    [bug introduced in coreutils-5.2.1]
    ls's -k option no longer affects how ls -l outputs file sizes.
    It now affects only the per-directory block counts written by -l,
    and the sizes written by -s.  This is for compatibility with BSD
    and with POSIX 2008.  Because -k is no longer equivalent to
  - -block-size=1KiB, a new long option --kibibyte stands for -k.
    [bug introduced in coreutils-4.5.4]
    ls -l would leak a little memory (security context string) for each
    nonempty directory listed on the command line, when using SELinux.
    [bug probably introduced in coreutils-6.10 with SELinux support]
    split -n 1/2 FILE no longer fails when operating on a growing file, or
    (on some systems) when operating on a non-regular file like /dev/zero.
    It would report "/dev/zero: No such file or directory" even though
    the file obviously exists.  Same for -n l/2.
    [bug introduced in coreutils-8.8, with the addition of the -n option]
    stat -f now recognizes the FhGFS and PipeFS file system types.
    tac no longer fails to handle two or more non-seekable inputs
    [bug introduced in coreutils-5.3.0]
    tail -f no longer tries to use inotify on GPFS or FhGFS file systems
    [you might say this was introduced in coreutils-7.5, along with inotify
    support, but the new magic numbers weren't in the usual places then.]
  * * Changes in behavior
    df avoids long UUID-including file system names in the default listing.
    With recent enough kernel/tools, these long names would be used, pushing
    second and subsequent columns far to the right.  Now, when a long name
    refers to a symlink, and no file systems are specified, df prints the
    usually-short referent instead.
    tail -f now uses polling (not inotify) when any of its file arguments
    resides on a file system of unknown type.  In addition, for each such
    argument, tail -f prints a warning with the FS type magic number and a
    request to report it to the bug-reporting address.
- Bring german message catalog up to date.
- Include upstream fix for du.
- Include upstream patch fixing basename documentation.
* Mon Feb  6 2012 rschweikert@suse.com
- keep binaries in /usr (UserMerge project)
* Mon Dec 19 2011 lnussel@suse.de
- Adjust license for coreutils-8.6-honor-settings-in-etc-default-su-resp-etc-login.defs.diff
  [bnc#735081].
* Fri Dec  2 2011 cfarrell@suse.com
- license update: GPL-3.0+
  Consolidate to GPL-3.0+ and use SPDX format
  (http://www.spdx.org/licenses). More or less compatible to Fedora package
  (who don^t use full SPDX implementation)
* Wed Nov 30 2011 coolo@suse.com
- add automake as buildrequire to avoid implicit dependency
* Mon Oct 17 2011 pth@suse.de
- Add upstream patch that fixes three bugs in tac:
  - remove sole use of sprintf in favor of stpcpy
  - don't misbehave with multiple non-seekable inputs
  - don't leak a file descriptor for each non-seekable input
* Fri Oct 14 2011 pth@suse.de
- Uniformly use german quotes not french ones in german messages.
* Thu Oct 13 2011 pth@suse.de
- Update to 8.14. Changes since 8.12:
  Bug fixes:
  - ls --dereference no longer outputs erroneous "argetm" strings for
    dangling symlinks when an 'ln=target' entry is in $LS_COLORS.
    [bug introduced in fileutils-4.0]
  - ls -lL symlink once again properly prints "+" when the referent has
    an ACL.  [bug introduced in coreutils-8.13]
  - sort -g no longer infloops for certain inputs containing NaNs [bug
    introduced in coreutils-8.5]
  - chown and chgrp with the -v --from= options, now output the correct
    owner.  I.E.  for skipped files, the original ownership is output,
    not the new one.  [bug introduced in sh-utils-2.0g]
  - cp -r could mistakenly change the permissions of an existing
    destination directory.  [bug introduced in coreutils-6.8]
  - cp -u -p would fail to preserve one hard link for each up-to-date
    copy of a src-hard-linked name in the destination tree.  I.e., if
    s/a and s/b are hard-linked and dst/s/a is up to date, "cp -up s
    dst" would copy s/b to dst/s/b rather than simply linking dst/s/b
    to dst/s/a.  [This bug appears to have been present in "the
    beginning".]
  - fts-using tools (rm, du, chmod, chgrp, chown, chcon) no longer use
    memory proportional to the number of entries in each directory they
    process.  Before, rm -rf 4-million-entry-directory would consume
    about 1GiB of memory.  Now, it uses less than 30MB, no matter how
    many entries there are.  [this bug was inherent in the use of fts:
    thus, for rm the bug was introduced in coreutils-8.0.  The prior
    implementation of rm did not use as much memory.  du, chmod, chgrp
    and chown started using fts in 6.0.  chcon was added in
    coreutils-6.9.91 with fts support.  ]
  - pr -T no longer ignores a specified LAST_PAGE to stop at.  [bug
    introduced in textutils-1.19q]
  - printf '%%d' '"' no longer accesses out-of-bounds memory in the
    diagnostic.  [bug introduced in sh-utils-1.16]
  - split --number l/... no longer creates extraneous files in certain
    cases.  [bug introduced in coreutils-8.8]
  - timeout now sends signals to commands that create their own process
    group.  timeout is no longer confused when starting off with a
    child process.  [bugs introduced in coreutils-7.0]
  - unexpand -a now aligns correctly when there are spaces spanning a
    tabstop, followed by a tab.  In that case a space was dropped,
    causing misalignment.  We also now ensure that a space never
    precedes a tab.  [bug introduced in coreutils-5.3.0]
  New features:
  - date now accepts ISO 8601 date-time strings with "T" as the
    separator.  It has long parsed dates like "2004-02-29 16:21:42"
    with a space between the date and time strings.  Now it also parses
    "2004-02-29T16:21:42" and fractional-second and time-zone-annotated
    variants like "2004-02-29T16:21:42.333-07:00"
  - md5sum accepts the new --strict option.  With --check, it makes the
    tool exit non-zero for any invalid input line, rather than just warning.
    This also affects sha1sum, sha224sum, sha384sum and sha512sum.
  - split accepts a new --filter=CMD option.  With it, split filters
    output through CMD.  CMD may use the $FILE environment variable,
    which is set to the nominal output file name for each invocation of
    CMD.  For example, to split a file into 3 approximately equal
    parts, which are then compressed:
    split -n3 --filter='xz > $FILE.xz' big
    Note the use of single quotes, not double quotes.  That creates
    files named xaa.xz, xab.xz and xac.xz.
  - timeout accepts a new --foreground option, to support commands not
    started directly from a shell prompt, where the command is
    interactive or needs to receive signals initiated from the
    terminal.
  Improvements:
  - md5sum --check now supports the -r format from the corresponding
    BSD tool.  This also affects sha1sum, sha224sum, sha384sum and
    sha512sum.
  - pwd now works also on systems without openat.  On such systems, pwd
    would fail when run from a directory whose absolute name contained
    more than PATH_MAX / 3 components.  The df, stat and readlink
    programs are also affected due to their use of the canonicalize_*
    functions.
  - join --check-order now prints "join: FILE:LINE_NUMBER: bad_line"
    for an unsorted input, rather than e.g., "join: file 1 is not in
    sorted order".
  - shuf outputs small subsets of large permutations much more
    efficiently.  For example `shuf -i1-$((2**32-1)) -n2` no longer
    exhausts memory.
  - stat -f now recognizes the GPFS, MQUEUE and PSTOREFS file system
    types.
  - timeout now supports sub-second timeouts.
  Changes in behavior:
  - chmod, chown and chgrp now output the original attributes in
    messages, when -v or -c specified.
  - cp -au (where --preserve=links is implicit) may now replace newer
    files in the destination, to mirror hard links from the source.
* Sat Sep 17 2011 jengelh@medozas.de
- Remove redundant tags/sections from specfile
* Tue Aug  2 2011 lchiquitto@suse.com
- file-has-acl: use acl_extended_file_nofollow if available to
  avoid triggering unwanted AutoFS mounts (bnc#701659).
* Tue May  3 2011 pth@suse.de
- Remove services.
* Tue May  3 2011 ro@suse.de
- delete coreutils-testsuite.spec
* Thu Apr 28 2011 pth@suse.de
- Update to 8.12:
  * Bug fixes
    tail's --follow=name option no longer implies --retry on systems
    with inotify support.  [bug introduced in coreutils-7.5]
  * Changes in behavior
    cp's extent-based (FIEMAP) copying code is more reliable in the face
    of varying and undocumented file system semantics:
  - it no longer treats unwritten extents specially
  - a FIEMAP-based extent copy always uses the FIEMAP_FLAG_SYNC flag.
    Before, it would incur the performance penalty of that sync only
    for 2.6.38 and older kernels.  We thought all problems would be
    resolved for 2.6.39.
  - it now attempts a FIEMAP copy only on a file that appears sparse.
    Sparse files are relatively unusual, and the copying code incurs
    the performance penalty of the now-mandatory sync only for them.
- Add complete german meesage catalogue.
* Thu Apr 14 2011 pth@suse.de
- Update to 8.11:
  * Bug fixes
    cp -a --link would not create a hardlink to a symlink, instead
    copying the symlink and then not preserving its timestamp.
    [bug introduced in coreutils-8.0]
    cp now avoids FIEMAP issues with BTRFS before Linux 2.6.38,
    which could result in corrupt copies of sparse files.
    [bug introduced in coreutils-8.10]
    cut could segfault when invoked with a user-specified output
    delimiter and an unbounded range like "-f1234567890-".
    [bug introduced in coreutils-5.3.0]
    du would infloop when given --files0-from=DIR
    [bug introduced in coreutils-7.1]
    sort no longer spawns 7 worker threads to sort 16 lines
    [bug introduced in coreutils-8.6]
    touch built on Solaris 9 would segfault when run on Solaris 10
    [bug introduced in coreutils-8.8]
    wc would dereference a NULL pointer upon an early out-of-memory error
    [bug introduced in coreutils-7.1]
  * * New features
    dd now accepts the 'nocache' flag to the iflag and oflag options,
    which will discard any cache associated with the files, or
    processed portion thereof.
    dd now warns that 'iflag=fullblock' should be used,
    in various cases where partial reads can cause issues.
  * * Changes in behavior
    cp now avoids syncing files when possible, when doing a FIEMAP copy.
    The sync is only needed on Linux kernels before 2.6.39.
    [The sync was introduced in coreutils-8.10]
    cp now copies empty extents efficiently, when doing a FIEMAP copy.
    It no longer reads the zero bytes from the input, and also can
    efficiently create a hole in the output file when --sparse=always
    is specified.
    df now aligns columns consistently, and no longer wraps entries
    with longer device identifiers, over two lines.
    install now rejects its long-deprecated --preserve_context option.
    Use --preserve-context instead.
    test now accepts "==" as a synonym for "="
* Tue Apr  5 2011 pth@suse.de
- Adapt coreutils-testsuite.spec to changes in patches.
* Tue Apr  5 2011 pth@suse.de
- Remove unneeded split_suffix patch.
* Mon Apr  4 2011 pth@suse.de
- Remove the last patch as it isn't needed. It was an old patch
  that removed the documentation for both hostname and hostid.
  I've modified that to only remove the hostname documentation.
* Fri Apr  1 2011 pth@suse.de
- Readd documentation of hostname and hostid to texinfo
  documentation.
- Remove obsolete and unused german translation.
* Thu Feb 10 2011 pth@suse.de
- Update to 8.10:
  * Bug fixes
  - du would abort with a failed assertion when two conditions are
    met: part of the hierarchy being traversed is moved to a higher
    level in the directory tree, and there is at least one more
    command line directory argument following the one containing
    the moved sub-tree.  [bug introduced in coreutils-5.1.0]
  - join --header now skips the ordering check for the first line
    even if the other file is empty.  [bug introduced in
    coreutils-8.5]
  - rm -f no longer fails for EINVAL or EILSEQ on file systems that
    reject file names invalid for that file system.
  - uniq -f NUM no longer tries to process fields after end of
    line.  [bug introduced in coreutils-7.0]
  * New features
  - cp now copies sparse files efficiently on file systems with
    FIEMAP support (ext4, btrfs, xfs, ocfs2).  Before, it had to
    read 2^20 bytes when copying a 1MiB sparse file.  Now, it
    copies bytes only for the non-sparse sections of a file.
    Similarly, to induce a hole in the output file, it had to
    detect a long sequence of zero bytes.  Now, it knows precisely
    where each hole in an input file is, and can reproduce them
    efficiently in the output file.  mv also benefits when it
    resorts to copying, e.g., between file systems.
  - join now supports -o 'auto' which will automatically infer the
    output format from the first line in each file, to ensure the
    same number of fields are output for each line.
  * Changes in behavior
  - join no longer reports disorder when one of the files is empty.
    This allows one to use join as a field extractor like:
    join -a1 -o 1.3,1.1 - /dev/null
- Add upstream patch that fixes a segfault in cut.
- Add upstream patch to fix sparse fiemap tests.
- Fix i18n patch for join.
* Fri Jan 14 2011 uli@suse.de
- sort threading still broken, it deadlocks occasionally; set
  default number of threads to 1 as a workaround
* Wed Jan  5 2011 pth@suse.de
- Update to 8.9:
  Bug fixes
  split no longer creates files with a suffix length that
  is dependent on the number of bytes or lines per file.
  [bug introduced in coreutils-8.8]
* Mon Jan  3 2011 pth@suse.de
- Update to 8.8. Changes since 8.6:
  Bug fixes:
  cp -u no longer does unnecessary copying merely because the source
  has finer-grained time stamps than the destination.
  od now prints floating-point numbers without losing information, and
  it no longer omits spaces between floating-point columns in some cases.
  sort -u with at least two threads could attempt to read through a
  corrupted pointer. [bug introduced in coreutils-8.6]
  sort with at least two threads and with blocked output would busy-loop
  (spinlock) all threads, often using 100%% of available CPU cycles to
  do no work.  I.e., "sort < big-file | less" could waste a lot of power.
  [bug introduced in coreutils-8.6]
  sort with at least two threads no longer segfaults due to use of pointers
  into the stack of an expired thread. [bug introduced in coreutils-8.6]
  sort --compress no longer mishandles subprocesses' exit statuses,
  no longer hangs indefinitely due to a bug in waiting for subprocesses,
  and no longer generates many more than NMERGE subprocesses.
  sort -m -o f f ... f no longer dumps core when file descriptors are limited.
  csplit no longer corrupts heap when writing more than 999 files,
  nor does it leak memory for every chunk of input processed
  [the bugs were present in the initial implementation]
  tail -F once again notices changes in a currently unavailable
  remote directory [bug introduced in coreutils-7.5]
  Changes in behavior:
  sort will not create more than 8 threads by default due to diminishing
  performance gains.  Also the --parallel option is no longer restricted
  to the number of available processors.
  cp --attributes-only now completely overrides --reflink.
  Previously a reflink was needlessly attempted.
  stat's %%X, %%Y, and %%Z directives once again print only the integer
  part of seconds since the epoch.  This reverts a change from
  coreutils-8.6, that was deemed unnecessarily disruptive.
  To obtain a nanosecond-precision time stamp for %%X use %%.X;
  if you want (say) just 3 fractional digits, use %%.3X.
  Likewise for %%Y and %%Z.
  stat's new %%W format directive would print floating point seconds.
  However, with the above change to %%X, %%Y and %%Z, we've made %%W work
  the same way as the others.
  New features:
  split accepts the --number option to generate a specific number of files.
- Add a complete german translation.
- Add upstreams patch for suffix calculation in split.
* Wed Dec 22 2010 pth@novell.com
- Use software services.
- Remove coreutils tarball.
- Don't use version specific patches as it breaks automatic
  updates.
* Wed Nov 17 2010 coolo@novell.com
- remove the prerequire on permissions - this will create a bad
  cycle, coreutils is just too core
* Tue Nov 16 2010 lnussel@suse.de
- split pam patch into separate independent files so the main
  feature can be shared with other distros
- don't hard require coreutils-lang
* Thu Nov 11 2010 pth@suse.de
- Update to 8.6:
  o bugfixes
  * du no longer multiply counts a file that is a directory or whose
    link count is 1.
  * du -H and -L now consistently count pointed-to files instead of
    symbolic links, and correctly diagnose dangling symlinks.
  * du --ignore=D now ignores directory D even when that directory is
    found to be part of a directory cycle.
  * split now diagnoses read errors rather than silently exiting.
  * tac would perform a double-free when given an input line longer
    than 16KiB.
  * tail -F once again notices changes in a currently unavailable
    directory, and works around a Linux kernel bug where inotify runs
    out of resources.
  * tr now consistently handles case conversion character classes.
  o New features
  * cp now accepts the --attributes-only option to not copy file data.
  * du recognizes -d N as equivalent to --max-depth=N
  * sort now accepts the --debug option, to highlight the part of the
    line significant in the sort, and warns about questionable options.
  * sort now supports -d, -f, -i, -R, and -V in any combination.
  * stat now accepts the %%m format directive to output the mount point
    for a file.  It also accepts the %%w and %%W format directives for
    outputting the birth time of a file, if one is available.
  o Changes in behavior
  * df now consistently prints the device name for a bind mounted file,
    rather than its aliased target.
  * du now uses less than half as much memory when operating on trees
    with many hard-linked files.
  * ls -l now uses the traditional three field time style rather than
    the wider two field numeric ISO style in locales where a style has
    not been specified.
  * rm's -d now evokes an error;  before, it was silently ignored.
  * sort -g now uses long doubles for greater range and precision.
  * sort -h no longer rejects numbers with leading or trailing ".", and
    no longer accepts numbers with multiple ".".  It now considers all
    zeros to be equal.
  * sort now uses the number of available processors to parallelize
    the sorting operation.
  * stat now provides translated output when no format is specified.
  * stat no longer accepts the --context (-Z) option.
  * stat no longer accepts the %%C directive when the --file-system
    option is in effect.
  * stat now outputs the full sub-second resolution for the atime,
    mtime, and ctime values since the Epoch, when using the %%X, %%Y, and
    %%Z directives of the --format option.
  * touch's --file option is no longer recognized.  Use --reference=F
    (-r) instead.
  * truncate now supports setting file sizes relative to a reference
    file. Also errors are no longer suppressed for unsupported file
    types, and relative sizes are restricted to supported file types.
  See NEWS in the package documentation for more verbose description.
- Add a man page for [ (a link to test1).
- Fix assignment of a char to a char * in join.c
- Add permissions verifying for su.
- Use RELRO for su.
* Tue Aug 31 2010 aj@suse.de
- Recommend instead of require lang package since it's not mandatory.
* Thu Jul  1 2010 jengelh@medozas.de
- Use %%_smp_mflags
* Tue Jun 29 2010 pth@suse.de
- Fix 'sort -V' not working because the i18n (mb handling) patch
  wasn't updated to handle the new option (bnc#615073).
* Mon Jun 28 2010 pth@suse.de
- Fix typo in spec file (%% missing from version).
* Fri Jun 18 2010 kukuk@suse.de
- Last part of fix for [bnc#533249]: Don't run account part of
  PAM stack for su as root. Requires pam > 1.1.1.
* Fri May  7 2010 pth@novell.com
- Update to 8.5:
  Bug fixes
  * cp and mv once again support preserving extended attributes.
  * cp now preserves "capabilities" when also preserving file ownership.7
  * ls --color once again honors the 'NORMAL' dircolors directive.
    [bug introduced in coreutils-6.11]
  * sort -M now handles abbreviated months that are aligned using
    blanks in the locale database.  Also locales with 8 bit characters
    are handled correctly, including multi byte locales with the caveat
    that multi byte characters are matched case sensitively.
  * sort again handles obsolescent key formats (+POS -POS) correctly.
    Previously if -POS was specified, 1 field too many was used in the
    sort. [bug introduced in coreutils-7.2]
  New features
  * join now accepts the --header option, to treat the first line of
    each file as a header line to be joined and printed
    unconditionally.
  * timeout now accepts the --kill-after option which sends a kill
    signal to the monitored command if it's still running the specified
    duration after the initial signal was sent.
  * who: the "+/-" --mesg (-T) indicator of whether a user/tty is
    accepting messages could be incorrectly listed as "+", when in
    fact, the user was not accepting messages (mesg no).  Before, who
    would examine only the permission bits, and not consider the group
    of the TTY device file.  Thus, if a login tty's group would change
    somehow e.g., to "root", that would make it unwritable (via
    write(1)) by normal users, in spite of whatever the permission bits
    might imply.  Now, when configured using the
  - -with-tty-group[=NAME] option, who also compares the group of the
    TTY device with NAME (or "tty" if no group name is specified).
  Changes in behavior
  * ls --color no longer emits the final 3-byte color-resetting escape
    sequence when it would be a no-op.
  * join -t '' no longer emits an error and instead operates on each
    line as a whole (even if they contain NUL characters).
  For other changes since 7.1 see NEWS.
- Split-up coreutils-%%%%{version}.diff as far as possible.
- Prefix all patches with coreutils-.
- All patches have the .patch suffix.
- Use the i18n patch from Archlinux as it fixes at least one test
  suite failure.
* Tue May  4 2010 pth@novell.com
- Fix security bug in distcheck (bnc#564373).
- refresh patches to apply cleanly.
* Tue Mar  2 2010 lnussel@suse.de
- enable hostid (bnc#584562)
* Sat Dec 12 2009 jengelh@medozas.de
- add baselibs.conf as a source
* Mon Mar 23 2009 pth@suse.de
- Add .ogv to dircolors (bnc#487561).
* Sun Feb 22 2009 schwab@suse.de
- Update to coreutils 7.1.
  * * New features
    Add extended attribute support available on certain filesystems like ext2
    and XFS.
    cp: Tries to copy xattrs when --preserve=xattr or --preserve=all specified
    mv: Always tries to copy xattrs
    install: Never copies xattrs
    cp and mv accept a new option, --no-clobber (-n): silently refrain
    from overwriting any existing destination file
    dd accepts iflag=cio and oflag=cio to open the file in CIO (concurrent I/O)
    mode where this feature is available.
    install accepts a new option, --compare (-C): compare each pair of source
    and destination files, and if the destination has identical content and
    any specified owner, group, permissions, and possibly SELinux context, then
    do not modify the destination at all.
    ls --color now highlights hard linked files, too
    stat -f recognizes the Lustre file system type
  * * Bug fixes
    chgrp, chmod, chown --silent (--quiet, -f) no longer print some diagnostics
    [bug introduced in coreutils-5.1]
    cp uses much less memory in some situations
    cp -a now correctly tries to preserve SELinux context (announced in 6.9.90),
    doesn't inform about failure, unlike with --preserve=all
    du --files0-from=FILE no longer reads all of FILE into RAM before
    processing the first file name
    seq 9223372036854775807 9223372036854775808 now prints only two numbers
    on systems with extended long double support and good library support.
    Even with this patch, on some systems, it still produces invalid output,
    from 3 to at least 1026 lines long. [bug introduced in coreutils-6.11]
    seq -w now accounts for a decimal point added to the last number
    to correctly print all numbers to the same width.
    wc --files0-from=FILE no longer reads all of FILE into RAM, before
    processing the first file name, unless the list of names is known
    to be small enough.
  * * Changes in behavior
    cp and mv: the --reply={yes,no,query} option has been removed.
    Using it has elicited a warning for the last three years.
    dd: user specified offsets that are too big are handled better.
    Previously, erroneous parameters to skip and seek could result
    in redundant reading of the file with no warnings or errors.
    du: -H (initially equivalent to --si) is now equivalent to
  - -dereference-args, and thus works as POSIX requires
    shred: now does 3 overwrite passes by default rather than 25.
    ls -l now marks SELinux-only files with the less obtrusive '.',
    rather than '+'.  A file with any other combination of MAC and ACL
    is still marked with a '+'.
* Wed Nov 19 2008 werner@suse.de
- Enable stat(1) to detect (k)AFS and CIFS network file systems
* Tue Nov 18 2008 schwab@suse.de
- Move stat to /bin.
* Tue Oct 21 2008 schwab@suse.de
- Fix pam cleanup.
* Thu Sep 18 2008 schwab@suse.de
- Move readlink and md5sum to /bin.
* Wed Aug 20 2008 schwab@suse.de
- Add libselinux-devel to BuildRequires.
* Tue Jun 24 2008 schwab@suse.de
- Fix sort field limit in multibyte case.
* Wed Jun  4 2008 schwab@suse.de
- Update to coreutils 6.12.
  * * Bug fixes
    chcon, runcon: --help output now includes the bug-reporting address
    cp -p copies permissions more portably.  For example, on MacOS X 10.5,
    "cp -p some-fifo some-file" no longer fails while trying to copy the
    permissions from the some-fifo argument.
    id with no options now prints the SELinux context only when invoked
    with no USERNAME argument.
    id and groups once again print the AFS-specific nameless group-ID (PAG).
    Printing of such large-numbered, kernel-only (not in /etc/group) group-IDs
    was suppressed in 6.11 due to ignorance that they are useful.
    uniq: avoid subtle field-skipping malfunction due to isblank misuse.
    In some locales on some systems, isblank(240) (aka &nbsp) is nonzero.
    On such systems, uniq --skip-fields=N would fail to skip the proper
    number of fields for some inputs.
    tac: avoid segfault with --regex (-r) and multiple files, e.g.,
    "echo > x; tac -r x x".  [bug present at least in textutils-1.8b, from 1992]
  * * Changes in behavior
    install once again sets SELinux context, when possible
    [it was deliberately disabled in 6.9.90]
* Sat Apr 19 2008 schwab@suse.de
- Update to coreutils 6.11.
  * * Bug fixes
    configure --enable-no-install-program=groups now works.
    "cp -fR fifo E" now succeeds with an existing E.  Before this fix, using
  - fR to copy a fifo or "special" file onto an existing file would fail
    with EEXIST.  Now, it once again unlinks the destination before trying
    to create the destination file.  [bug introduced in coreutils-5.90]
    dd once again works with unnecessary options like if=/dev/stdin and
    of=/dev/stdout.  [bug introduced in fileutils-4.0h]
    id now uses getgrouplist, when possible.  This results in
    much better performance when there are many users and/or groups.
    ls no longer segfaults on files in /proc when linked with an older version
    of libselinux.  E.g., ls -l /proc/sys would dereference a NULL pointer.
    md5sum would segfault for invalid BSD-style input, e.g.,
    echo 'MD5 (' | md5sum -c -  Now, md5sum ignores that line.
    sha1sum, sha224sum, sha384sum, and sha512sum are affected, too.
    [bug introduced in coreutils-5.1.0]
    md5sum -c would accept a NUL-containing checksum string like "abcd\0..."
    and would unnecessarily read and compute the checksum of the named file,
    and then compare that checksum to the invalid one: guaranteed to fail.
    Now, it recognizes that the line is not valid and skips it.
    sha1sum, sha224sum, sha384sum, and sha512sum are affected, too.
    [bug present in the original version, in coreutils-4.5.1, 1995]
    "mkdir -Z x dir" no longer segfaults when diagnosing invalid context "x"
    mkfifo and mknod would fail similarly.  Now they're fixed.
    mv would mistakenly unlink a destination file before calling rename,
    when the destination had two or more hard links.  It no longer does that.
    [bug introduced in coreutils-5.3.0]
    "paste -d'\' file" no longer overruns memory (heap since coreutils-5.1.2,
    stack before then) [bug present in the original version, in 1992]
    "pr -e" with a mix of backspaces and TABs no longer corrupts the heap
    [bug present in the original version, in 1992]
    "ptx -F'\' long-file-name" would overrun a malloc'd buffer and corrupt
    the heap.  That was triggered by a lone backslash (or odd number of them)
    at the end of the option argument to --flag-truncation=STRING (-F),
  - -word-regexp=REGEXP (-W), or --sentence-regexp=REGEXP (-S).
    "rm -r DIR" would mistakenly declare to be "write protected" -- and
    prompt about -- full DIR-relative names longer than MIN (PATH_MAX, 8192).
    "rmdir --ignore-fail-on-non-empty" detects and ignores the failure
    in more cases when a directory is empty.
    "seq -f %% 1" would issue the erroneous diagnostic "seq: memory exhausted"
    rather than reporting the invalid string format.
    [bug introduced in coreutils-6.0]
  * * New features
    join now verifies that the inputs are in sorted order.  This check can
    be turned off with the --nocheck-order option.
    sort accepts the new option --sort=WORD, where WORD can be one of
    general-numeric, month, numeric or random.  These are equivalent to the
    options --general-numeric-sort/-g, --month-sort/-M, --numeric-sort/-n
    and --random-sort/-R, resp.
  * * Improvements
    id and groups work around an AFS-related bug whereby those programs
    would print an invalid group number, when given no user-name argument.
    ls --color no longer outputs unnecessary escape sequences
    seq gives better diagnostics for invalid formats.
  * * Portability
    rm now works properly even on systems like BeOS and Haiku,
    which have negative errno values.
  * * Consistency
    install, mkdir, rmdir and split now write --verbose output to stdout,
    not to stderr.
* Fri Apr 11 2008 schwab@suse.de
- Work around a recent glibc/getopt.c diagnostic change.
- Fix frexpl test.
* Thu Apr 10 2008 ro@suse.de
- added baselibs.conf file to build xxbit packages
  for multilib support
* Mon Feb 18 2008 dmueller@suse.de
- split off -lang subpackage to reduce one CD media size
* Mon Feb  4 2008 kukuk@suse.de
- sux is deprecated since 3 years, let's finaly remove symlink.
* Tue Jan 22 2008 schwab@suse.de
- Update to coreutils 6.10.
  * * Bug fixes
    Fix a non-portable use of sed in configure.ac.
    [bug introduced in coreutils-6.9.92]
* Sun Jan 13 2008 rguenther@suse.de
- Reapply dropped patch:
  adjust test-getaddrinfo to not fail w/o network connection
* Sat Jan 12 2008 schwab@suse.de
- Update to coreutils 6.9.92.
  * * Bug fixes
    cp --parents no longer uses uninitialized memory when restoring the
    permissions of a just-created destination directory.
    [bug introduced in coreutils-6.9.90]
    tr's case conversion would fail in a locale with differing numbers
    of lower case and upper case characters.  E.g., this would fail:
    env LC_CTYPE=en_US.ISO-8859-1 tr '[:upper:]' '[:lower:]'
    [bug introduced in coreutils-6.9.90]
  * * Improvements
    "touch -d now writable-but-owned-by-someone-else" now succeeds
    whenever that same command would succeed without "-d now".
    Before, it would work fine with no -d option, yet it would
    fail with the ostensibly-equivalent "-d now".
* Mon Jan  7 2008 schwab@suse.de
- Update to coreutils 6.9.91.
  * * Bug fixes
    "ls -l" would not output "+" on SELinux hosts unless -Z was also given.
    "rm" would fail to unlink a non-directory when run in an environment
    in which the user running rm is capable of unlinking a directory.
    [bug introduced in coreutils-6.9]
* Mon Jan  7 2008 jblunck@suse.de
- fix a cp bug with -p --parents
* Wed Dec 12 2007 rguenther@suse.de
- adjust test-getaddrinfo to not fail w/o network connection
* Mon Dec 10 2007 ro@suse.de
- change source archive compression back to .bz2 to avoid another
  dependency in the lowest basesystem
* Mon Dec  3 2007 schwab@suse.de
- Update to coreutils-6.9.90.
  * * New programs
    arch: equivalent to uname -m, not installed by default
    But don't install this program on Solaris systems.
    chcon: change the SELinux security context of a file
    mktemp: create a temporary file or directory (or names)
    runcon: run a program in a different SELinux security context
  * * Programs no longer installed by default
    hostname, su
  * * Changes in behavior
    cp, by default, refuses to copy through a dangling destination symlink
    Set POSIXLY_CORRECT if you require the old, risk-prone behavior.
    pr -F no longer suppresses the footer or the first two blank lines in
    the header.  This is for compatibility with BSD and POSIX.
    tr now warns about an unescaped backslash at end of string.
    The tr from coreutils-5.2.1 and earlier would fail for such usage,
    and Solaris' tr ignores that final byte.
  * * New features
    Add SELinux support, based on the patch from Fedora:
  * cp accepts new --preserve=context option.
  * "cp -a" works with SELinux:
    Now, cp -a attempts to preserve context, but failure to do so does
    not change cp's exit status.  However "cp --preserve=context" is
    similar, but failure *does* cause cp to exit with nonzero status.
  * install accepts new "-Z, --context=C" option.
  * id accepts new "-Z" option.
  * stat honors the new %%C format directive: SELinux security context string
  * ls accepts a slightly modified -Z option.
  * ls: contrary to Fedora version, does not accept --lcontext and --scontext
    cp -p tries to preserve the GID of a file even if preserving the UID
    is not possible.
    uniq accepts a new option: --zero-terminated (-z).  As with the sort
    option of the same name, this makes uniq consume and produce
    NUL-terminated lines rather than newline-terminated lines.
    wc no longer warns about character decoding errors in multibyte locales.
    This means for example that "wc /bin/sh" now produces normal output
    (though the word count will have no real meaning) rather than many
    error messages.
  * * New build options
    By default, "make install" no longer attempts to install (or even build) su.
    To change that, use ./configure --enable-install-program=su.
    If you also want to install the new "arch" program, do this:
    ./configure --enable-install-program=arch,su.
    You can inhibit the compilation and installation of selected programs
    at configure time.  For example, to avoid installing "hostname" and
    "uptime", use ./configure --enable-no-install-program=hostname,uptime
    Note: currently, "make check" passes, even when arch and su are not
    built (that's the new default).  However, if you inhibit the building
    and installation of other programs, don't be surprised if some parts
    of "make check" fail.
  * * Remove deprecated options
    df no longer accepts the --kilobytes option.
    du no longer accepts the --kilobytes or --megabytes options.
    ls no longer accepts the --kilobytes option.
    ptx longer accepts the --copyright option.
    who no longer accepts -i or --idle.
  * * Improved robustness
    ln -f can no longer silently clobber a just-created hard link.
    In some cases, ln could be seen as being responsible for data loss.
    For example, given directories a, b, c, and files a/f and b/f, we
    should be able to do this safely: ln -f a/f b/f c && rm -f a/f b/f
    However, before this change, ln would succeed, and thus cause the
    loss of the contents of a/f.
    stty no longer silently accepts certain invalid hex values
    in its 35-colon commmand-line argument
  * * Bug fixes
    chmod no longer ignores a dangling symlink.  Now, chmod fails
    with a diagnostic saying that it cannot operate on such a file.
    [bug introduced in coreutils-5.1.0]
    cp attempts to read a regular file, even if stat says it is empty.
    Before, "cp /proc/cpuinfo c" would create an empty file when the kernel
    reports stat.st_size == 0, while "cat /proc/cpuinfo > c" would "work",
    and create a nonempty one. [bug introduced in coreutils-6.0]
    cp --parents no longer mishandles symlinks to directories in file
    name components in the source, e.g., "cp --parents symlink/a/b d"
    no longer fails.  Also, 'cp' no longer considers a destination
    symlink to be the same as the referenced file when copying links
    or making backups.  For example, if SYM is a symlink to FILE,
    "cp -l FILE SYM" now reports an error instead of silently doing
    nothing.  The behavior of 'cp' is now better documented when the
    destination is a symlink.
    "cp -i --update older newer" no longer prompts; same for mv
    "cp -i" now detects read errors on standard input, and no longer consumes
    too much seekable input; same for ln, install, mv, and rm.
    cut now diagnoses a range starting with zero (e.g., -f 0-2) as invalid;
    before, it would treat it as if it started with 1 (-f 1-2).
    "cut -f 2-0" now fails; before, it was equivalent to "cut -f 2-"
    cut now diagnoses the '-' in "cut -f -" as an invalid range, rather
    than interpreting it as the unlimited range, "1-".
    date -d now accepts strings of the form e.g., 'YYYYMMDD +N days',
    in addition to the usual 'YYYYMMDD N days'.
    du -s now includes the size of any stat'able-but-inaccessible directory
    in the total size.
    du (without -s) prints whatever it knows of the size of an inaccessible
    directory.  Before, du would print nothing for such a directory.
    ls -x DIR would sometimes output the wrong string in place of the
    first entry.  [introduced in coreutils-6.8]
    ls --color would mistakenly color a dangling symlink as if it were
    a regular symlink.  This would happen only when the dangling symlink
    was not a command-line argument and in a directory with d_type support.
    [introduced in coreutils-6.0]
    ls --color, (with a custom LS_COLORS envvar value including the
    ln=target attribute) would mistakenly output the string "target"
    before the name of each symlink.  [introduced in coreutils-6.0]
    od's --skip (-j) option now works even when the kernel says that a
    nonempty regular file has stat.st_size = 0.  This happens at least
    with files in /proc and linux-2.6.22.
    "od -j L FILE" had a bug: when the number of bytes to skip, L, is exactly
    the same as the length of FILE, od would skip *no* bytes.  When the number
    of bytes to skip is exactly the sum of the lengths of the first N files,
    od would skip only the first N-1 files. [introduced in textutils-2.0.9]
    ./printf %%.10000000f 1 could get an internal ENOMEM error and generate
    no output, yet erroneously exit with status 0.  Now it diagnoses the error
    and exits with nonzero status.  [present in initial implementation]
    seq no longer mishandles obvious cases like "seq 0 0.000001 0.000003",
    so workarounds like "seq 0 0.000001 0.0000031" are no longer needed.
    seq would mistakenly reject some valid format strings containing %%%%,
    and would mistakenly accept some invalid ones. e.g., %%g%%%% and %%%%g, resp.
    "seq .1 .1" would mistakenly generate no output on some systems
    Obsolete sort usage with an invalid ordering-option character, e.g.,
    "env _POSIX2_VERSION=199209 sort +1x" no longer makes sort free an
    invalid pointer [introduced in coreutils-6.5]
    sorting very long lines (relative to the amount of available memory)
    no longer provokes unaligned memory access
    split --line-bytes=N (-C N) no longer creates an empty file
    [this bug is present at least as far back as textutils-1.22 (Jan, 1997)]
    tr -c no longer aborts when translating with Set2 larger than the
    complement of Set1.  [present in the original version, in 1992]
    tr no longer rejects an unmatched [:lower:] or [:upper:] in SET1.
    [present in the original version]
* Thu Nov 29 2007 schwab@suse.de
- Update to coreutils-6.9.89.48 snapshot.
* Mon Jul 23 2007 schwab@suse.de
- Fix random sort.
- Fix invalid free.
- Fix misalignment.
* Sun May 20 2007 schwab@suse.de
- Fix compiling with glibc 2.6.
* Sun May 20 2007 schwab@suse.de
- Fix fchownat test.
* Mon Apr  2 2007 schwab@suse.de
- Fix ls -x.
* Fri Mar 23 2007 schwab@suse.de
- Update to coreutils 6.9.
  * * Bug fixes
    cp -x (--one-file-system) would fail to set mount point permissions
    The default block size and output format for df -P are now unaffected by
    the DF_BLOCK_SIZE, BLOCK_SIZE, and BLOCKSIZE environment variables.  It
    is still affected by POSIXLY_CORRECT, though.
    Using pr -m -s (i.e. merging files, with TAB as the output separator)
    no longer inserts extraneous spaces between output columns.
* Wed Mar 14 2007 lnussel@suse.de
- su: actually use /etc/pam.d/su-l when running su - (#254428)
* Mon Mar  5 2007 lnussel@suse.de
- su: don't chdir("/") before fork() (#251287)
* Fri Mar  2 2007 lnussel@suse.de
- split off and rework PAM patch for su:
  * run pam_open_session as root (#245706)
  * use separate pam configs for "su" and "su -" (RedHat #198639)
  * detect pam libs in configure script, add option to disable it
  * don't set argv[0] to "-su", use upstream behavior instead
  * don't use getlogin() for setting PAM_RUSER
* Sun Feb 25 2007 schwab@suse.de
- Update to coreutils 6.8.
  * * Bug fixes
    chgrp, chmod, and chown now honor the --preserve-root option.
    Before, they would warn, yet continuing traversing and operating on /.
    chmod no longer fails in an environment (e.g., a chroot) with openat
    support but with insufficient /proc support.
    "cp --parents F/G D" no longer creates a directory D/F when F is not
    a directory (and F/G is therefore invalid).
    "cp --preserve=mode" would create directories that briefly had
    too-generous permissions in some cases.  For example, when copying a
    directory with permissions 777 the destination directory might
    temporarily be setgid on some file systems, which would allow other
    users to create subfiles with the same group as the directory.  Fix
    similar problems with 'install' and 'mv'.
    cut no longer dumps core for usage like "cut -f2- f1 f2" with two or
    more file arguments.  This was due to a double-free bug, introduced
    in coreutils-5.3.0.
    dd bs= operands now silently override any later ibs= and obs=
    operands, as POSIX and tradition require.
    "ls -FRL" always follows symbolic links on Linux.  Introduced in
    coreutils-6.0.
    A cross-partition "mv /etc/passwd ~" (by non-root) now prints
    a reasonable diagnostic.  Before, it would print this:
    "mv: cannot remove `/etc/passwd': Not a directory".
    pwd and "readlink -e ." no longer fail unnecessarily when a parent
    directory is unreadable.
    "rm -rf /etc/passwd" (run by non-root) now prints a diagnostic.
    Before it would print nothing.
    "rm --interactive=never F" no longer prompts for an unwritable F
  * * New features
    sort's new --compress-program=PROG option specifies a compression
    program to use when writing and reading temporary files.
    This can help save both time and disk space when sorting large inputs.
  * * New features
    sort accepts the new option -C, which acts like -c except no diagnostic
    is printed.  Its --check option now accepts an optional argument, and
  - -check=quiet and --check=silent are now aliases for -C, while
  - -check=diagnose-first is an alias for -c or plain --check.
* Tue Jan  9 2007 schwab@suse.de
- Fix localized month sorting [#231790].
* Wed Dec 13 2006 schwab@suse.de
- Fix acl tests.
* Sat Dec  9 2006 schwab@suse.de
- Update to coreutils 6.7.
  * * Bug fixes
    When cp -p copied a file with special mode bits set, the same bits
    were set on the copy even when ownership could not be preserved.
    This could result in files that were setuid to the wrong user.
    To fix this, special mode bits are now set in the copy only if its
    ownership is successfully preserved.  Similar problems were fixed
    with mv when copying across file system boundaries.  This problem
    affects all versions of coreutils through 6.6.
    cp --preserve=ownership would create output files that temporarily
    had too-generous permissions in some cases.  For example, when
    copying a file with group A and mode 644 into a group-B sticky
    directory, the output file was briefly readable by group B.
    Fix similar problems with cp options like -p that imply
  - -preserve=ownership, with install -d when combined with either -o
    or -g, and with mv when copying across file system boundaries.
    This bug affects coreutils 6.0 through 6.6.
    du --one-file-system (-x) would skip subdirectories of any directory
    listed as second or subsequent command line argument.  This bug affects
    coreutils-6.4, 6.5 and 6.6.
* Wed Nov 22 2006 schwab@suse.de
- Update to coreutils 6.6.
  * * Bug fixes
    ls would segfault (dereference a NULL pointer) for a file with a
    nameless group or owner.  This bug was introduced in coreutils-6.5.
    A bug in the latest official m4/gettext.m4 (from gettext-0.15)
    made configure fail to detect gettext support, due to the unusual
    way in which coreutils uses AM_GNU_GETTEXT.
  * * Improved robustness
    Now, du (and the other fts clients: chmod, chgrp, chown) honor a
    trailing slash in the name of a symlink-to-directory even on
    Solaris 9, by working around its buggy fstatat implementation.
* Mon Nov 20 2006 schwab@suse.de
- Update to coreutils 6.5.
  * * Bug fixes
    du (and the other fts clients: chmod, chgrp, chown) would exit early
    when encountering an inaccessible directory on a system with native
    openat support (i.e., linux-2.6.16 or newer along with glibc-2.4
    or newer).  This bug was introduced with the switch to gnulib's
    openat-based variant of fts, for coreutils-6.0.
    "ln --backup f f" now produces a sensible diagnostic
  * * New features
    rm accepts a new option: --one-file-system
* Mon Oct 23 2006 schwab@suse.de
- Update to coreutils 6.4.
  * * Bug fixes
    chgrp and chown would malfunction when invoked with both -R and -H and
    with one or more of the following: --preserve-root, --verbose, --changes,
  - -from=o:g (chown only).  This bug was introduced with the switch to
    gnulib's openat-based variant of fts, for coreutils-6.0.
    cp --backup dir1 dir2, would rename an existing dir2/dir1 to dir2/dir1~.
    This bug was introduced in coreutils-6.0.
    With --force (-f), rm no longer fails for ENOTDIR.
    For example, "rm -f existing-non-directory/anything" now exits
    successfully, ignoring the error about a nonexistent file.
* Mon Oct  9 2006 schwab@suse.de
- Update to coreutils 6.3.
  * * Improved robustness
    pinky no longer segfaults on Darwin 7.9.0 (MacOS X 10.3.9) due to a
    buggy native getaddrinfo function.
    rm works around a bug in Darwin 7.9.0 (MacOS X 10.3.9) that would
    sometimes keep it from removing all entries in a directory on an HFS+
    or NFS-mounted partition.
    sort would fail to handle very large input (around 40GB) on systems with a
    mkstemp function that returns a file descriptor limited to 32-bit offsets.
  * * Bug fixes
    chmod would fail unnecessarily in an unusual case: when an initially-
    inaccessible argument is rendered accessible by chmod's action on a
    preceding command line argument.  This bug also affects chgrp, but
    it is harder to demonstrate.  It does not affect chown.  The bug was
    introduced with the switch from explicit recursion to the use of fts
    in coreutils-5.1.0 (2003-10-15).
    cp -i and mv -i occasionally neglected to prompt when the copy or move
    action was bound to fail.  This bug dates back to before fileutils-4.0.
    With --verbose (-v), cp and mv would sometimes generate no output,
    or neglect to report file removal.
    For the "groups" command:
    "groups" no longer prefixes the output with "user :" unless more
    than one user is specified; this is for compatibility with BSD.
    "groups user" now exits nonzero when it gets a write error.
    "groups" now processes options like --help more compatibly.
    shuf would infloop, given 8KB or more of piped input
  * * Portability
    Versions of chmod, chown, chgrp, du, and rm (tools that use openat etc.)
    compiled for Solaris 8 now also work when run on Solaris 10.
* Wed Oct  4 2006 agruen@suse.de
- cp: Replace the old --attributes=regex option with
  - -preserve=xattrs.  Only copy extended attributes if this
  option is given. Use libattr's new copy_attr_action() function
  to check which attributes to copy in /etc/xattr.conf.
* Tue Sep 19 2006 schwab@suse.de
- Disable broken autopoint.
* Mon Sep 18 2006 schwab@suse.de
- Update to coreutils 6.2.
  * * Changes in behavior
    mkdir -p and install -d (or -D) now use a method that forks a child
    process if the working directory is unreadable and a later argument
    uses a relative file name.  This avoids some race conditions, but it
    means you may need to kill two processes to stop these programs.
    rm now rejects attempts to remove the root directory, e.g., `rm -fr /'
    now fails without removing anything.  Likewise for any file name with
    a final `./' or `../' component.
    tail now ignores the -f option if POSIXLY_CORRECT is set, no file
    operand is given, and standard input is any FIFO; formerly it did
    this only for pipes.
  * * Infrastructure changes
    Coreutils now uses gnulib via the gnulib-tool script.
    If you check the source out from CVS, then follow the instructions
    in README-cvs.  Although this represents a large change to the
    infrastructure, it should cause no change in how the tools work.
  * * Bug fixes
    cp --backup no longer fails when the last component of a source file
    name is "." or "..".
    "ls --color" would highlight other-writable and sticky directories
    no differently than regular directories on a file system with
    dirent.d_type support.
    "mv -T --verbose --backup=t A B" now prints the " (backup: B.~1~)"
    suffix when A and B are directories as well as when they are not.
    mv and "cp -r" no longer fail when invoked with two arguments
    where the first one names a directory and the second name ends in
    a slash and doesn't exist.  E.g., "mv dir B/", for nonexistent B,
    now succeeds, once more.  This bug was introduced in coreutils-5.3.0.
* Fri Sep  1 2006 schwab@suse.de
- Fix sbin patch [#202632].
* Mon Aug 21 2006 schwab@suse.de
- Update to coreutils 6.1.
  * * Changes in behavior
    df now considers BSD "kernfs" file systems to be dummies
  * * Bug fixes
    cp --sparse preserves sparseness at the end of a file, even when
    the file's apparent size is not a multiple of its block size.
    [introduced with the original design, in fileutils-4.0r, 2000-04-29]
    df (with a command line argument) once again prints its header
    [introduced in coreutils-6.0]
    ls -CF would misalign columns in some cases involving non-stat'able files
    [introduced in coreutils-6.0]
* Tue Aug 15 2006 schwab@suse.de
- Update to coreutils 6.0.
  * * Improved robustness
    df: if the file system claims to have more available than total blocks,
    report the number of used blocks as being "total - available"
    (a negative number) rather than as garbage.
    dircolors: a new autoconf run-test for AIX's buggy strndup function
    prevents malfunction on that system;  may also affect cut, expand,
    and unexpand.
    fts no longer changes the current working directory, so its clients
    (chmod, chown, chgrp, du) no longer malfunction under extreme conditions.
    pwd and other programs using lib/getcwd.c work even on file systems
    where dirent.d_ino values are inconsistent with those from stat.st_ino.
    rm's core is now reentrant: rm --recursive (-r) now processes
    hierarchies without changing the working directory at all.
  * * Changes in behavior
    basename and dirname now treat // as different from / on platforms
    where the two are distinct.
    chmod, install, and mkdir now preserve a directory's set-user-ID and
    set-group-ID bits unless you explicitly request otherwise.  E.g.,
    `chmod 755 DIR' and `chmod u=rwx,go=rx DIR' now preserve DIR's
    set-user-ID and set-group-ID bits instead of clearing them, and
    similarly for `mkdir -m 755 DIR' and `mkdir -m u=rwx,go=rx DIR'.  To
    clear the bits, mention them explicitly in a symbolic mode, e.g.,
    `mkdir -m u=rwx,go=rx,-s DIR'.  To set them, mention them explicitly
    in either a symbolic or a numeric mode, e.g., `mkdir -m 2755 DIR',
    `mkdir -m u=rwx,go=rx,g+s' DIR.  This change is for convenience on
    systems where these bits inherit from parents.  Unfortunately other
    operating systems are not consistent here, and portable scripts
    cannot assume the bits are set, cleared, or preserved, even when the
    bits are explicitly mentioned.  For example, OpenBSD 3.9 `mkdir -m
    777 D' preserves D's setgid bit but `chmod 777 D' clears it.
    Conversely, Solaris 10 `mkdir -m 777 D', `mkdir -m g-s D', and
    `chmod 0777 D' all preserve D's setgid bit, and you must use
    something like `chmod g-s D' to clear it.
    `cp --link --no-dereference' now works also on systems where the
    link system call cannot create a hard link to a symbolic link.
    This change has no effect on systems with a Linux-based kernel.
    csplit and nl now use POSIX syntax for regular expressions, not
    Emacs syntax.  As a result, character classes like [[:print:]] and
    interval expressions like A\{1,9\} now have their usual meaning,
    . no longer matches the null character, and \ must precede the + and
    ? operators.
    date: a command like date -d '2006-04-23 21 days ago' would print
    the wrong date in some time zones.  (see the test for an example)
    df now considers "none" and "proc" file systems to be dummies and
    therefore does not normally display them.  Also, inaccessible file
    systems (which can be caused by shadowed mount points or by chrooted
    bind mounts) are now dummies, too.
    expr no longer complains about leading ^ in a regular expression
    (the anchor is ignored), or about regular expressions like A** (the
    second "*" is ignored).  expr now exits with status 2 (not 3) for
    errors it detects in the expression's values; exit status 3 is now
    used only for internal errors (such as integer overflow, which expr
    now checks for).
    install and mkdir now implement the X permission symbol correctly,
    e.g., `mkdir -m a+X dir'; previously the X was ignored.
    install now creates parent directories with mode u=rwx,go=rx (755)
    instead of using the mode specified by the -m option; and it does
    not change the owner or group of parent directories.  This is for
    compatibility with BSD and closes some race conditions.
    ln now uses different (and we hope clearer) diagnostics when it fails.
    ln -v now acts more like FreeBSD, so it generates output only when
    successful and the output is easier to parse.
    ls now defaults to --time-style='locale', not --time-style='posix-long-iso'.
    However, the 'locale' time style now behaves like 'posix-long-iso'
    if your locale settings appear to be messed up.  This change
    attempts to have the default be the best of both worlds.
    mkfifo and mknod no longer set special mode bits (setuid, setgid,
    and sticky) with the -m option.
    nohup's usual diagnostic now more precisely specifies the I/O
    redirections, e.g., "ignoring input and appending output to
    nohup.out".  Also, nohup now redirects stderr to nohup.out (or
    $HOME/nohup.out) if stdout is closed and stderr is a tty; this is in
    response to Open Group XCU ERN 71.
    rm --interactive now takes an optional argument, although the
    default of using no argument still acts like -i.
    rm no longer fails to remove an empty, unreadable directory
    seq changes:
    seq defaults to a minimal fixed point format that does not lose
    information if seq's operands are all fixed point decimal numbers.
    You no longer need the `-f%%.f' in `seq -f%%.f 1048575 1024 1050623',
    for example, since the default format now has the same effect.
    seq now lets you use %%a, %%A, %%E, %%F, and %%G formats.
    seq now uses long double internally rather than double.
    sort now reports incompatible options (e.g., -i and -n) rather than
    silently ignoring one of them.
    stat's --format=FMT option now works the way it did before 5.3.0:
    FMT is automatically newline terminated.  The first stable release
    containing this change was 5.92.
    stat accepts the new option --printf=FMT, where FMT is *not*
    automatically newline terminated.
    stat: backslash escapes are interpreted in a format string specified
    via --printf=FMT, but not one specified via --format=FMT.  That includes
    octal (\ooo, at most three octal digits), hexadecimal (\xhh, one or
    two hex digits), and the standard sequences (\a, \b, \f, \n, \r, \t,
    \v, \", \\).
    With no operand, 'tail -f' now silently ignores the '-f' only if
    standard input is a FIFO or pipe and POSIXLY_CORRECT is set.
    Formerly, it ignored the '-f' when standard input was a FIFO, pipe,
    or socket.
  * * Scheduled for removal
    ptx's --copyright (-C) option is scheduled for removal in 2007, and
    now evokes a warning.  Use --version instead.
    rm's --directory (-d) option is scheduled for removal in 2006.  This
    option has been silently ignored since coreutils 5.0.  On systems
    that support unlinking of directories, you can use the "unlink"
    command to unlink a directory.
    Similarly, we are considering the removal of ln's --directory (-d,
  - F) option in 2006.  Please write to <bug-coreutils@gnu.org> if this
    would cause a problem for you.  On systems that support hard links
    to directories, you can use the "link" command to create one.
  * * New programs
    base64: base64 encoding and decoding (RFC 3548) functionality.
    sha224sum: print or check a SHA224 (224-bit) checksum
    sha256sum: print or check a SHA256 (256-bit) checksum
    sha384sum: print or check a SHA384 (384-bit) checksum
    sha512sum: print or check a SHA512 (512-bit) checksum
    shuf: Shuffle lines of text.
  * * New features
    chgrp now supports --preserve-root, --no-preserve-root (default),
    as it was documented to do, and just as chmod, chown, and rm do.
    New dd iflag= and oflag= flags:
    'directory' causes dd to fail unless the file is a directory, on
    hosts that support this (e.g., Linux kernels, version 2.1.126 and
    later).  This has limited utility but is present for completeness.
    'noatime' causes dd to read a file without updating its access
    time, on hosts that support this (e.g., Linux kernels, version
    2.6.8 and later).
    'nolinks' causes dd to fail if the file has multiple hard links,
    on hosts that support this (e.g., Solaris 10 and later).
    ls accepts the new option --group-directories-first, to make it
    list directories before files.
    rm now accepts the -I (--interactive=once) option.  This new option
    prompts once if rm is invoked recursively or if more than three
    files are being deleted, which is less intrusive than -i prompting
    for every file, but provides almost the same level of protection
    against mistakes.
    shred and sort now accept the --random-source option.
    sort now accepts the --random-sort (-R) option and `R' ordering option.
    sort now supports obsolete usages like "sort +1 -2" unless
    POSIXLY_CORRECT is set.  However, when conforming to POSIX
    1003.1-2001 "sort +1" still sorts the file named "+1".
    wc accepts a new option --files0-from=FILE, where FILE contains a
    list of NUL-terminated file names.
  * * Bug fixes
    cat with any of the options, -A -v -e -E -T, when applied to a
    file in /proc or /sys (linux-specific), would truncate its output,
    usually printing nothing.
    cp -p would fail in a /proc-less chroot, on some systems
    When `cp -RL' encounters the same directory more than once in the
    hierarchy beneath a single command-line argument, it no longer confuses
    them with hard-linked directories.
    fts-using tools (chmod, chown, chgrp, du) no longer fail due to
    a double-free bug -- it could be triggered by making a directory
    inaccessible while e.g., du is traversing the hierarchy under it.
    fts-using tools (chmod, chown, chgrp, du) no longer misinterpret
    a very long symlink chain as a dangling symlink.  Before, such a
    misinterpretation would cause these tools not to diagnose an ELOOP error.
    ls --indicator-style=file-type would sometimes stat a symlink
    unnecessarily.
    ls --file-type worked like --indicator-style=slash (-p),
    rather than like --indicator-style=file-type.
    mv: moving a symlink into the place of an existing non-directory is
    now done atomically;  before, mv would first unlink the destination.
    mv -T DIR EMPTY_DIR no longer fails unconditionally.  Also, mv can
    now remove an empty destination directory: mkdir -p a b/a; mv a b
    rm (on systems with openat) can no longer exit before processing
    all command-line arguments.
    rm is no longer susceptible to a few low-probability memory leaks.
    rm -r no longer fails to remove an inaccessible and empty directory
    rm -r's cycle detection code can no longer be tricked into reporting
    a false positive (introduced in fileutils-4.1.9).
    shred --remove FILE no longer segfaults on Gentoo systems
    sort would fail for large inputs (~50MB) on systems with a buggy
    mkstemp function.  sort and tac now use the replacement mkstemp
    function, and hence are no longer subject to limitations (of 26 or 32,
    on the maximum number of files from a given template) on HP-UX 10.20,
    SunOS 4.1.4, Solaris 2.5.1 and OSF1/Tru64 V4.0F&V5.1.
    tail -f once again works on a file with the append-only
    attribute (affects at least Linux ext2, ext3, xfs file systems)
* Tue Aug  8 2006 schwab@suse.de
- Move sux to %%{_bindir}.
* Mon Jun 26 2006 schwab@suse.de
- Update to coreutils 5.97.
  * * Bug fixes
    rebuild with better autoconf test for when the lstat replacement
    function is needed -- required for Solaris 9
    cat with any of the options, -A -v -e -E -T, when applied to a
    file in /proc or /sys (linux-specific), would truncate its output,
    usually printing nothing.
  * * Improved robustness
    dircolors: a new autoconf run-test for AIX's buggy strndup function
    prevents malfunction on that system;  may also affect cut, expand,
    and unexpand.
  * * New features
    chgrp now supports --preserve-root, --no-preserve-root (default),
    as it was documented to do, and just as chmod, chown, and rm do.
* Thu Jun 22 2006 schwab@suse.de
- Fix conflict with <fcntl.h>.
* Mon May 22 2006 schwab@suse.de
- Update to coreutils 5.96.
* Sat May 13 2006 schwab@suse.de
- Update to coreutils 5.95.
* Fri Apr  7 2006 cthiel@suse.de
- added Obsoletes: libselinux (hack for bug #156519)
* Mon Feb 13 2006 schwab@suse.de
- Fix spurious failure with cp -LR.
- Move check for /proc.
* Mon Jan 30 2006 schwab@suse.de
- Always print newline after format in stat [#145905].
- Barf if /proc is not mounted.
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Thu Jan 19 2006 meissner@suse.de
- Do not strip /bin/su.
* Wed Jan 11 2006 schwab@suse.de
- Fix infloop when ignoring characters [#141756].
* Mon Dec 19 2005 kukuk@suse.de
- Add fallback if futimesat does not work
* Mon Dec  5 2005 ke@suse.de
- Fix typo in German translation file; reported by Olaf Hering
  [#105863].
* Mon Dec  5 2005 schwab@suse.de
- Drop SELinux support.
* Tue Nov 15 2005 uli@suse.de
- some tests fail on ARM (QEMU problem?); ignore for now
* Sun Nov  6 2005 schwab@suse.de
- Update to coreutils 5.93.
* Wed Nov  2 2005 schwab@suse.de
- Update to coreutils 5.92.
- Fix invalid use of va_list.
- Add some fixes from cvs.
* Thu Oct 20 2005 schwab@suse.de
- Reenable DEFAULT_POSIX2_VERSION.
* Wed Oct 19 2005 agruen@suse.de
- Add acl and xattr patches.
* Mon Oct 17 2005 schwab@suse.de
- Update to coreutils 5.91.
* Sat Oct  1 2005 schwab@suse.de
- Update to coreutils 5.90.
- Disable acl patches for now.
* Sun Sep 25 2005 schwab@suse.de
- Fix warning.
* Wed Aug 24 2005 werner@suse.de
- Let `su' handle /sbin and /usr/sbin in path
* Mon Aug  1 2005 kukuk@suse.de
- And yet another uninitialized variable fix.
* Fri Jul 29 2005 schwab@suse.de
- Fix another uninitialized variable.
* Wed Jul  6 2005 schwab@suse.de
- Fix uninitialized variable.
* Mon Jul  4 2005 schwab@suse.de
- Update i18n patch.
* Mon Jun 20 2005 schwab@suse.de
- Fix last change.
* Wed Jun 15 2005 kukuk@suse.de
- Compile/link su with -fpie/-pie
* Sat May 21 2005 kukuk@suse.de
- Add support for /etc/default/su
* Mon May  2 2005 kukuk@suse.de
- Don't overwrite PATH if su is called with "-" option.
* Wed Mar  2 2005 schwab@suse.de
- Fix merge error [#67103].
* Mon Feb 28 2005 schwab@suse.de
- Call pam_getenvlist before pam_end.
* Mon Feb 28 2005 schwab@suse.de
- Link su to sux [#66830].
* Wed Feb  2 2005 schwab@suse.de
- Handle xfs and jfs in stat [#50415].
* Wed Feb  2 2005 schwab@suse.de
- Handle subfs like autofs.
* Tue Jan 25 2005 schwab@suse.de
- Fix path_concat.
* Thu Jan 20 2005 schwab@suse.de
- Use pam_xauth [#42238].
* Fri Jan 14 2005 schwab@suse.de
- Fix merge error [#49853].
* Tue Jan 11 2005 schwab@suse.de
- Update to coreutils 5.3.0.
* Mon Nov  8 2004 kukuk@suse.de
- Use common-* PAM config files for su PAM configuration
* Mon Oct 25 2004 schwab@suse.de
- Fix last change.
- Fix selinux patch.
* Tue Oct 19 2004 ro@suse.de
- remove no language support (nb is already there)
* Sat Oct  2 2004 agruen@suse.de
- #46609: Fix chown and chgrp utilities for uid == (uid_t) -1 and
  gid == (gid_t) -1 case.
- Add missing #include to have NULL defined in lib/acl.c
* Thu Sep  9 2004 schwab@suse.de
- Fix uninitialized variable [#44929].
- Fix selinux patch.
* Wed Aug 25 2004 schwab@suse.de
- Fix hardlink accounting patch.
* Mon May 24 2004 schwab@suse.de
- Update testsuite for change in chown.
* Mon May 24 2004 schwab@suse.de
- Precompute length in caller of ismbblank to avoid quadratic behaviour
  [#40741].
* Mon May 17 2004 schwab@suse.de
- Fix handling of symlinks in chown [#40691].
* Sat Apr 17 2004 schwab@suse.de
- Pacify autobuild.
* Fri Apr  2 2004 schwab@suse.de
- Add support for IUTF8 in stty.
* Tue Mar 30 2004 schwab@suse.de
- Fix merge error in selinux patch [#37431].
* Mon Mar 29 2004 schwab@suse.de
- Fix hardlink accounting in du.
* Mon Mar 22 2004 schwab@suse.de
- Fix race in the testsuite.
* Mon Mar 15 2004 kukuk@suse.de
- Update SELinux patch to new libselinux interface
* Mon Mar 15 2004 schwab@suse.de
- Fix date parsing.
* Sat Mar 13 2004 schwab@suse.de
- Update to coreutils 5.2.1.
  * Includes mv fix.
  * Fix sparse handling in cp.
  * Fix descriptor leak in nohup.
  * Fix POSIX issues in expr.
  * Always allow user.group in chown.
* Fri Mar 12 2004 schwab@suse.de
- Fix sysinfo patch [#35337].
* Fri Mar 12 2004 schwab@suse.de
- Fix preserving links in mv.
* Wed Mar  3 2004 schwab@suse.de
- Fix help output from mkdir.
* Fri Feb 20 2004 schwab@suse.de
- Update to coreutils 5.2.0.
* Mon Feb  9 2004 schwab@suse.de
- Update to coreutils 5.1.3.
* Mon Feb  2 2004 agruen@suse.de
- Update acl and xattr patches, and add some Changelog text.
* Mon Jan 26 2004 schwab@suse.de
- Update to coreutils 5.1.2.
* Fri Jan 23 2004 schwab@suse.de
- Don't link [ to test.
* Mon Jan 19 2004 schwab@suse.de
- Update to coreutils 5.1.1.
- Default to POSIX.2-1992.
* Fri Jan 16 2004 kukuk@suse.de
- Add pam-devel to neededforbuild
* Fri Jan  9 2004 schwab@suse.de
- Fix spurious test failure.
* Thu Jan  8 2004 schwab@suse.de
- Update to coreutils 5.1.0.
* Fri Dec 12 2003 schwab@suse.de
- Fix use of AC_SEARCH_LIBS.
* Tue Dec  9 2003 schwab@suse.de
- Cleanup SELinux patch.
* Tue Dec  9 2003 kukuk@suse.de
- Add SELinux patch.
* Wed Nov 26 2003 schwab@suse.de
- Fix sorting of months in multibyte case [#33299].
* Wed Oct 22 2003 schwab@suse.de
- Fix building without extended attributes.
* Wed Oct 15 2003 schwab@suse.de
- Cleanup sysinfo patch.
* Fri Sep 19 2003 kukuk@suse.de
- Add missing textutil to Provides
* Mon Aug 25 2003 agruen@suse.de
- Fix uname command to report reasonable processor and platform
  information (coreutils-sysinfo.diff: based on similar RedHat
  patch).
* Mon Jul 21 2003 schwab@suse.de
- Fix typo in i18n patch for join.
* Fri Jul 18 2003 schwab@suse.de
- Avoid abort in sort on inconsistent locales [#26506].
* Tue Jul 15 2003 okir@suse.de
- make su export variables declared via pam_putenv
* Wed May 28 2003 kukuk@suse.de
- PAM fixes for su:
  - Move pam_open_session call before dropping privilegs, session
    management needs max. possible credentials and needs to be done
    before we change into the home directory of the user.
  - Don't set PAM_TTY and PAM_RUSER to fake names.
  - Use conversion function from libpam_misc.
* Fri May 16 2003 schwab@suse.de
- Fix exit status from su.
* Thu Apr 24 2003 ro@suse.de
- fix head calling syntax
* Mon Apr  7 2003 schwab@suse.de
- Only delete info entries when removing last version.
* Fri Apr  4 2003 schwab@suse.de
- Update to coreutils 5.0.
* Mon Mar 31 2003 schwab@suse.de
- Update to coreutils 4.5.12.
* Thu Mar 20 2003 schwab@suse.de
- Update to coreutils 4.5.11.
* Mon Mar 10 2003 schwab@suse.de
- Fix LFS bug in du [#24960].
* Thu Feb 27 2003 schwab@suse.de
- Readd textutils i18n patches.
* Thu Feb 27 2003 agruen@suse.de
- Per hint from Andreas Schwab, don't use awk in autoconf. (The
  improved test is simpler, too.)
* Thu Feb 27 2003 agruen@suse.de
- Fix autoconf test for attr_copy_file that caused all binaries
  to be linked needlessly against libattr.so.
* Tue Feb 25 2003 agruen@suse.de
- Extended attribute copying: Use the newly exported
  attr_copy_check_permissions() callback exported by libattr.so,
  so that the EA copying done by coreutils is consistent with
  other apps [#24244].
* Mon Feb 24 2003 schwab@suse.de
- Update to coreutils 4.5.8.
  * Fixes bugs in du.
* Mon Feb 17 2003 agruen@suse.de
- Add extended attribute copying patch: Affects cp, mv, install.
  See the cp manual page for details on the changes in cp. The
  mv utility always tries to copy extended attributes; install
  never does.
* Mon Feb 10 2003 schwab@suse.de
- Update to coreutils 4.5.7.
* Fri Feb  7 2003 kukuk@suse.de
- Use pam_unix2.so instead of pam_unix.so, use same rules for
  password changing as passwd.
* Thu Feb  6 2003 schwab@suse.de
- Use %%install_info.
* Thu Feb  6 2003 schwab@suse.de
- Update to coreutils 4.5.6.
* Mon Feb  3 2003 schwab@suse.de
- Package created, combining textutils, sh-utils and fileutils.
