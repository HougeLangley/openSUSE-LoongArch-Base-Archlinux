#
# spec file for package bpftool
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


%define version %(rpm -q --qf '%%{VERSION}' kernel-source)
Name:           bpftool
Version:        5.19.0
Release:        4.19
Summary:        Tool for inspection and manipulation of BPF programs and maps
License:        GPL-2.0-only
Group:          Development/Tools/Other
URL:            https://www.kernel.org/
#BuildRequires:  binutils-devel
#BuildRequires:  docutils
#BuildRequires:  kernel-source
#BuildRequires:  libelf-devel

%description
bpftool allows for inspection and simple modification of BPF objects (programs
and maps) on the system.

%package rebuild
Summary:        Empty package to ensure rebuilding bpftool in OBS
Group:          System/Monitoring
#%requires_eq    kernel-source

%description rebuild
This is empty package that ensures bpftool is rebuilt every time
kernel-default is rebuilt in OBS.

There is no reason to install this package.

%prep
(cd %{_prefix}/src/linux ; tar -cf - COPYING CREDITS README tools include scripts Kbuild Makefile arch/*/{include,lib,Makefile} kernel/bpf lib) | tar -xf -
cp %{_prefix}/src/linux/LICENSES/preferred/GPL-2.0 .
sed -i -e 's/CFLAGS += -O2/CFLAGS = $(RPM_OPT_FLAGS)/' Makefile

%build
cd tools/bpf/bpftool
%make_build \
    feature-reallocarray=1 \
    feature-libbfd-liberty=1 \
    feature-disassembler-four-args=1 \
    all \
    doc

%install
cd tools/bpf/bpftool
make install doc-install DESTDIR=%{buildroot} prefix=%{_prefix} mandir=%{_mandir}

%files
%license GPL-2.0
%{_sbindir}/bpftool
%{_datadir}/bash-completion/completions/bpftool
%{_mandir}/man8/.

%files rebuild
%license GPL-2.0

%changelog
* Fri Apr  8 2022 Dirk Müller <dmueller@suse.com>
- add rebuild subpackage to ensure rebuild in TW
* Thu Oct 14 2021 Shung-Hsi Yu <shung-hsi.yu@suse.com>
- Enable libbfd feature to support dumping jited form of BPF programs
* Wed Jan  8 2020 Ludwig Nussel <lnussel@suse.de>
- use optflags for building
- build and install man pages
* Thu May  9 2019 Michal Rostecki <mrostecki@opensuse.org>
- Initial release
