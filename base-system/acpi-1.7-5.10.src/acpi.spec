#
# spec file for package acpi
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


Name:           acpi
Version:        1.7
Release:        5.10
Summary:        Command-line ACPI client
License:        GPL-2.0-or-later
Group:          System/Daemons
URL:            https://sourceforge.net/projects/acpiclient/
Source:         https://sourceforge.net/projects/acpiclient/files/acpiclient/%{version}/%{name}-%{version}.tar.gz
# Package was split from acpid package
Provides:       acpid:%{_bindir}/acpi
ExclusiveArch:  %{ix86} x86_64 ia64 aarch64 loongarch64

%description
Linux ACPI client is a small command-line program that attempts to
replicate the functionality of the 'old' apm command on ACPI systems.
It includes battery and thermal information.

%prep
%setup -q

%build
%configure
%make_build

%install
%make_install

%files
%license COPYING
%doc AUTHORS ChangeLog README
%{_bindir}/acpi
%{_mandir}/man1/acpi.1%{?ext_man}

%changelog
* Mon Jan  4 2021 Dirk Müller <dmueller@suse.com>
- spec-cleaner
* Mon Mar  9 2015 mpluskal@suse.com
- Use url for source
- Cleanup spec file with spec-cleaner
- Enable build for aarch64
* Thu Dec 12 2013 p.drouand@gmail.com
- Update to version 1.7
  + ChangeLog has not been updated
- Remove acpi-memset-with-zero-length.patch; merged on upstream release
* Sat Oct 19 2013 p.drouand@gmail.com
- Package doesn't contain sysconfig file or sysvinit script; remove
  useless %%insserv_prereq and %%fillup_prereq macros
* Sat Sep 17 2011 jengelh@medozas.de
- Remove redundant tags/sections from specfile
* Tue Apr  5 2011 crrodriguez@opensuse.org
- Fix memset-with-zero-length bug.
* Sat Oct  2 2010 aj@suse.de
- Update to new upstream version 1.5:
  * Print error message if no information can be retrieved e.g. because acpi
    is not activated
  * Read power_now and use it to replace current_now if the battery is
    reporting energy values, closes: 532000
* Sat Oct  2 2010 aj@suse.de
- Split up from acpid package.
