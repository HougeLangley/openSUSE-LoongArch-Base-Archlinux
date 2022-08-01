#
# spec file for package bcc
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


%if 0%{?suse_version} > 1500
%ifarch %ix86 x86_64
%{!?with_lua: %global with_lua 1}
%else
%{!?with_lua: %global with_lua 0}
%endif
%else
%{!?with_lua: %global with_lua 0}
%endif

Name:           bcc
Version:        0.24.0
Release:        1.6
Summary:        BPF Compiler Collection (BCC)
License:        Apache-2.0
Group:          Development/Tools/Other
URL:            https://github.com/iovisor/bcc
Source:         https://github.com/iovisor/bcc/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
#ExcludeArch:    ppc s390
#BuildRequires:  bison
#BuildRequires:  cmake >= 2.8.7
#BuildRequires:  flex
#BuildRequires:  gcc-c++
#BuildRequires:  libbpf-devel
#BuildRequires:  libelf-devel
#BuildRequires:  llvm-clang-devel >= 3.7.0
#BuildRequires:  llvm-devel >= 3.7.0
#%if 0%{?suse_version} > 1320
#BuildRequires:  clang-devel
#BuildRequires:  llvm-gold
#%else
#BuildRequires:  libstdc++-devel
#%endif
#%if %{with_lua}
#BuildRequires:  luajit-devel
#%endif
#BuildRequires:  pkgconf-pkg-config
#BuildRequires:  python3-base

%description
BCC is a toolkit for creating efficient kernel tracing and manipulation
programs, and includes several useful tools and examples. It makes use
of eBPF (Extended Berkeley Packet Filters), a feature that was first
added to Linux 3.15. Much of what BCC uses requires Linux 4.1 and above.

%package -n libbcc0
Summary:        Shared library from the BPF Compiler Collection
Group:          System/Libraries
Requires:       kernel >= 4.1.0
Requires:       kernel-devel >= 4.1.0
Requires:       (kernel-debug-devel if kernel-debug)
Requires:       (kernel-default-devel if (kernel-default or kernel-default-base))
Requires:       (kernel-kvmsmall-devel if kernel-kvmsmall)
Requires:       (kernel-pae-devel if kernel-pae)
Requires:       (kernel-vanilla-devel if kernel-vanilla)

%description -n libbcc0
Shared Library from the BPF Compiler Collection.

%package devel
Summary:        Header files for the BPF Compiler Collection
Group:          Development/Languages/C and C++
Requires:       libbcc0 = %{version}

%description devel
Headers and pkg-config build descriptions for developing BCC programs.

%package -n python3-bcc
Summary:        Python3 bindings for the BPF Compiler Collection
Group:          Development/Languages/Python
Requires:       libbcc0 = %{version}
BuildArch:      noarch

%description -n python3-bcc
Python 3.x bindings for the BPF Compiler Collection.

%package lua
Summary:        Lua interpreter for the BPF Compiler Collection
Group:          Development/Languages/Other
Requires:       libbcc0 = %{version}

%description lua
Lua interpreter for the BPF Compiler Collection.

%package examples
Summary:        Examples from the BPF Compiler Collection
Group:          Documentation/Other
Requires:       python3-bcc = %{version}
Requires:       python3-future
Recommends:     netperf
Recommends:     python3-netaddr
Recommends:     python3-pyroute2
BuildArch:      noarch

%description examples
Python and C examples from the BPF Compiler Collection.

%package tools
Summary:        Tracing tools from the BPF Compiler Collection
# ausyscall from audit is required by syscount.py
Group:          System/Monitoring
Requires:       audit
Requires:       python3-bcc = %{version}
Requires:       python3-future

%description tools
Python tracing scripts from the BPF Compiler Collection.

%package docs
Summary:        BPF Compiler Collection documentation
Group:          Documentation/Other
BuildArch:      noarch

%description docs
Documentation on how to write programs with the BPF Compiler Collection.

%prep
%setup -q

%build
# Prevent the cpp examples from compilation and installation
# Those programs are statically linked and huge in binary size.
sed -i "/add_subdirectory(cpp)/d" examples/CMakeLists.txt

# Remove the lua scripts if bcc-lua is disabled
%if %{with_lua} == 0
sed -i "/add_subdirectory(lua)/d" examples/CMakeLists.txt
%endif

# Install bps to /usr/bin
sed -i "s,share/bcc/introspection,bin," introspection/CMakeLists.txt

export LD_LIBRARY_PATH="%{_builddir}/usr/lib64"
export PATH="%{_builddir}/usr/bin":$PATH

mkdir build
pushd build
CFLAGS="%{optflags}" CXXFLAGS="%{optflags}" cmake \
	-DCMAKE_USE_LIBBPF_PACKAGE=yes \
	-DPYTHON_CMD=python3 \
	-DREVISION_LAST=%{version} \
	-DREVISION=%{version} \
	-DCMAKE_INSTALL_PREFIX=/usr \
%if 0%{?suse_version} > 1320
	-DENABLE_LLVM_SHARED=1 \
%endif
%if %{with_lua}
	-DLUAJIT_INCLUDE_DIR=`pkg-config --variable=includedir luajit` \
	-DLUAJIT_LIBRARY=%{_libdir}/lib`pkg-config --variable=libname luajit`.so \
	-DENABLE_NO_PIE=OFF \
%endif
%ifarch %arm || %ix86
	-DENABLE_USDT=OFF \
%endif
	..
make -j32 VERBOSE=1
popd

# Fix up #!-lines.
find tools/ examples/ -type f -exec \
	sed -Ei '1s|^#!/usr/bin/env python3?|#!/usr/bin/python3|' {} +
find tools/ examples/ -type f -exec \
	sed -Ei '1s|^#!/usr/bin/env bcc-lua|#!/usr/bin/bcc-lua|' {} +
find tools/ examples/ -type f -exec \
	sed -i '1s|/bin/python$|/bin/python3|g' {} +

%install
pushd build
%make_install

%if 0%{?suse_version} <= 1500
# Remove bps due to the incomplete support in kernel (bsc#1085403)
rm -f %{buildroot}/%{_bindir}/bps
%endif

popd

# Remove the static libraries
rm -f %{buildroot}/%{_libdir}/libbcc*.a

%post -n libbcc0 -p /sbin/ldconfig

%postun -n libbcc0 -p /sbin/ldconfig

%files -n bcc-devel
%{_libdir}/libbcc.so
%{_libdir}/libbcc_bpf.so
%dir %{_includedir}/bcc/
%{_includedir}/bcc/bcc_common.h
%{_includedir}/bcc/bcc_elf.h
%{_includedir}/bcc/bcc_exception.h
%{_includedir}/bcc/bcc_proc.h
%{_includedir}/bcc/bcc_syms.h
%{_includedir}/bcc/bcc_usdt.h
%{_includedir}/bcc/bcc_version.h
%{_includedir}/bcc/BPF.h
%{_includedir}/bcc/bpf_module.h
%{_includedir}/bcc/BPFTable.h
%{_includedir}/bcc/compat/linux
%{_includedir}/bcc/file_desc.h
%{_includedir}/bcc/libbpf.h
%{_includedir}/bcc/perf_reader.h
%{_includedir}/bcc/table_desc.h
%{_includedir}/bcc/table_storage.h
%{_libdir}/pkgconfig/libbcc.pc

%files -n libbcc0
%license LICENSE.txt
%{_libdir}/libbcc.so.0
%{_libdir}/libbcc.so.0.24.0
%{_libdir}/libbcc_bpf.so.0
%{_libdir}/libbcc_bpf.so.0.24.0

%files -n python3-bcc
%{_libdir}/python3.10/site-packages/bcc/containers.py
%{_libdir}/python3.10/site-packages/bcc/disassembler.py
%{_libdir}/python3.10/site-packages/bcc/__init__.py
%{_libdir}/python3.10/site-packages/bcc/libbcc.py
%{_libdir}/python3.10/site-packages/bcc/perf.py
%{_libdir}/python3.10/site-packages/bcc/__pycache__/containers.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/disassembler.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/__init__.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/libbcc.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/perf.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/syscall.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/table.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/tcp.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/usdt.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/utils.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/__pycache__/version.cpython-310.pyc
%{_libdir}/python3.10/site-packages/bcc/syscall.py
%{_libdir}/python3.10/site-packages/bcc/table.py
%{_libdir}/python3.10/site-packages/bcc/tcp.py
%{_libdir}/python3.10/site-packages/bcc/usdt.py
%{_libdir}/python3.10/site-packages/bcc/utils.py
%{_libdir}/python3.10/site-packages/bcc/version.py
%{_libdir}/python3.10/site-packages/bcc-0.24.0-py3.10.egg-info

%if %{with_lua}
%files lua
%{_bindir}/bcc-lua
%endif

%files examples
%dir %{_datadir}/bcc/
%dir %{_datadir}/bcc/examples/
%{_datadir}/bcc/examples/.

%files tools
%dir %{_datadir}/bcc/
%dir %{_datadir}/bcc/tools/
%{_datadir}/bcc/tools/.
%dir %{_datadir}/bcc/man/
%{_datadir}/bcc/man/.
%if 0%{?suse_version} > 1500
%{_bindir}/bps
%endif

%files docs
%doc README.md FAQ.txt
%doc docs/kernel-versions.md docs/reference_guide.md
%doc docs/tutorial_bcc_python_developer.md docs/tutorial.md

%changelog
* Fri Apr 22 2022 Dominique Leuenberger <dimstar@opensuse.org>
- Update to version 0.24.0:
  + Support for kernel up to 5.16
  + bcc tools: update for trace.py, sslsniff.py, tcptop.py, hardirqs.py, etc.
  + new libbpf tools: bashreadline
  + allow specify wakeup_events for perf buffer
  + support BPF_MAP_TYPE_{INODE, TASK}_STORAGE maps
  + remove all deprecated libbpf function usage
  + remove P4/B language support
  + major test infra change, using github actions now
  + doc update, bug fixes and other tools improvement
- Changes from version 0.23.0:
  + Support for kernel up to 5.15
  + bcc tools: update for kvmexit.py, tcpv4connect.py, cachetop.py, cachestat.py, etc.
  + libbpf tools: update for update for mountsnoop, ksnoop, gethostlatency, etc.
  + fix renaming of task_struct->state
  + get pid namespace properly for a number of tools
  + initial work for more libbpf utilization (less section names)
  + doc update, bug fixes and other tools improvement
- Drop Do-not-export-USDT-function-when-ENABLE_USDT-is-OFF.patch:
  fixed upstream.
* Wed Feb 16 2022 Aaron Puchert <aaronpuchert@alice-dsl.net>
- Move kernel{,-devel} requirements to libbcc0 for deduplication.
- Require additionally kernel-$variant-devel for libbcc0.
- Declare python3-bcc, bcc-examples and bcc-docs as noarch.
* Fri Oct  1 2021 Shung-Hsi Yu <shung-hsi.yu@suse.com>
- Use shared libbpf library instead of building it along with bcc
    + Delete libbpf-0.5.tar.gz
- Fix build on i586 due to use of shared libbpf library
    + Do-not-export-USDT-function-when-ENABLE_USDT-is-OFF.patch
* Fri Sep 17 2021 Shung-Hsi Yu <shung-hsi.yu@suse.com>
- Update to 0.22.0
  + Support for kernel up to 5.14
  + add ipv4/ipv6 filter support for tcp trace tools
  + add python interface to attach raw perf events
  + fix tcpstates for incorrect display of dport
  + new options for bcc tools runqslower, argdist
  + new libbpf-tools: filetop, exitsnoop, tcprtt
  + doc update, bug fixes and other tools improvement
* Fri Sep 17 2021 Shung-Hsi Yu <shung-hsi.yu@suse.com>
- Update to 0.21.0
  + Support for kernel up to 5.13
  + support for debug information from libdebuginfod
  + finished support for map elements items_*_batch() APIs
  + add atomic_increment() API
  + support attach_func() and detach_func() in python
  + fix displaying PID instead of TID for many tools
  + new tools: kvmexit.py
  + new libbpf-tools: gethostlatency, statsnoop, fsdist and solisten
  + fix tools ttysnoop/readahead for newer kernels
  + doc update and bug fixes
- Update libbpf to 0.5
  + libbpf_set_strict_mode() allowing to opt-in into backwards incompatible libbpf-1.0 changes. See "Libbpf: the road to 1.0" and "Libbpf 1.0 migration guide" for more details.
  + streamlined error reporting for low-level APIs, high-level error-returning APIs, and pointer-returning APIs (as a libbpf-1.0 opt-in);
  + "Light" BPF skeleton support;
  + BPF_PROG_TYPE_SYSCALL support;
  + BPF perf link support for kprobe, uprobe, tracepoint, and perf_event BPF programs;
  + BPF cookie support for kprobe, uprobe, tracepoint, and perf_event BPF programs through bpf_program__attach_[ku]probe_opts() APIs;
  + allow to specify ref_ctr_off for USDT semaphores through bpf_program__attach_uprobe_opts() API;
  + btf_custom_path support in bpf_object_open_opts, allowing to specify custom BTF for CO-RE relocations;
  + sk_reuseport/migrate program type support;
  + btf_dump__dump_type_data() API, allowing to dump binary data according to BTF type description;
  + btf__load_into_kernel() and btf__load_from_kernel_by_id(), and split BTF variants of them;
  + btf__load_vmlinux_btf() and btf__load_module_btf() APIs;
  + bpf_map__initial_value() API to get initial value of mmap-ed BPF maps;
  + bpf_map_lookup_and_delete_elem_flags() API.
  + support for weak typed __ksym externs;
  + BPF timer helpers: bpf_timer_init(), bpf_timer_set_callback(), bpf_timer_start(), bpf_timer_cancel();
  + bpf_get_attach_cookie() helper to get BPF cookie from BPF program side;
  + bpf_get_func_ip() helper;
  + bpf_sys_bpf() helper;
  + bpf_task_pt_regs() helper;
  + bpf_btf_find_by_name_kind() helper;
  + usability improvements for bpf_tracing.h when target architecture is missing.
  + improve BPF support detection on old Red Hat kernels with backported BPF patches;
  + improvements for LTO builds with GCC 10+;
  + pass NLM_F_EXCL when creating TC qdisc;
  + better support of BPF map reuse on old kernels;
  + fix the bug resulting in sometimes closing FD 0, which wasn't created and owned by libbpf itself.
* Tue Jul 27 2021 Shung-Hsi Yu <shung-hsi.yu@suse.com>
- Update source URL for bcc and libbpf
* Tue Jul 27 2021 Shung-Hsi Yu <shung-hsi.yu@suse.com>
- Update to 0.20.0
  + Support for kernel up to 5.12
  + Some basic support for MIPS
  + added bpf_map_lookup_batch and bpf_map_delete_batch support
  + tools/funclatency.py support nested or recursive functions
  + tools/biolatency.py can optionally print out average/total value
  + fix possible marco HAVE_BUILTIN_BSWAP redefine warning for kernel >= 5.10.
  + new tools: virtiostat
  + new libbpf-tools: ext4dist
  + doc update and bug fixes
- Update libbpf to 0.4
  + BPF static linker APIs;
  + subprogram address relocation support (e.e., for use with bpf_for_each_map_elem());
  + support for extern kernel functions (a.k.a. BPF unstable helpers);
  + TC-BPF APIs;
  + ksym externs support for kernel modules;
  + BTF_KIND_FLOAT support;
  + various AF_XDP (xsk.{c, h}) improvements and fixes;
  + btf__add_type() API to copy/append BTF types generically;
  + bpf_object__set_kernel_version() setter;
  + bpf_map__inner_map() getter;
  + __hidden attribute for global sub-program forces static BPF verifier verification;
  + static BPF maps and entry-point BPF programs are explicitly rejected.
  + libbpf will ignore non-function pointer members in struct_ops;
  + Makefile fixes for install target;
  + use SOCK_CLOEXEC for netlink sockets;
  + btf_dump fixes for pointer to array of struct;
  + fixes for some of xxx_opts structs to work better with debug compilation modes;
  + ringbuf APIs fixes and improvements for extreme cases of never ending consumption of records;
  + BPF_CORE_READ_BITFIELD() macro fixes.
* Mon Mar 29 2021 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.19.0
  + Support for kernel up to 5.11
  + allow BCC as a cmake subproject
  + add LPORT support in tcpconnlat and tcpconnect
  + added bpf_map_lookup_and_delete_batch support
  + new tools: virtiostat
  + new libbpf-tools: cpufreq, funclatency, cachestat
  + add install target to libbpf-tools
  + a few lua fixes
  + doc update and bug fixes
- Set ENABLE_NO_PIE to "OFF" to enable PIE for bcc-lua (bsc#1183399)
* Wed Jan  6 2021 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.18.0
  + Support for kernel up to 5.10
  + add bpf kfunc/kretfunc C++ example
  + add PT_REGS_PARMx_SYSCALL helper macro
  + biolatency: allow json output
  + biolatpcts: support measuring overall latencies between two events
  + fix build when ENABLE_CLANG_JIT is disabled
  + doc update and bug fixes
- Update libbpf to 0.3
  + kernel modules BTF support on all levels
  + ring_buffer__epoll_fd() API
  + xsk_socket__update_xskmap() and xsk_setup_xdp_prog() APIs
  + New BPF helpers:
  - bpf_task_storage_get() and bpf_task_storage_delete();
  - get_current_task_btf();
  - bpf_bprm_opts_set();
  - bpf_ktime_get_coarse_ns();
  - bpf_ima_inode_hash();
  - bpf_sock_from_file().
  + ring_buffer__poll() returns number of consumed records
    correctly
  + handle corner-case case with unused sub-programs
  + xsk_socket__delete() bug fixes
* Wed Nov  4 2020 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.17.0
  + Support for kernel up to 5.9
  + usdt: add uprobe refcnt support
  + add bpf iterator C++ support
  + new bcc tools: tcprtt, netqtop, swapin, tcpsynbl, threadsnoop
  + tcpconnect: add DNS correlation to connect tracking
  + new libbpf-tools: llcstat, numamove, runqlen, runqlat,
    softirgs, hardirqs
  + doc update, bug fixes and some additional arguments for tools
- Update libbpf to 0.2
  + full support for BPF-to-BPF function calls, no more need for
    __always_inline;
  + support for multiple BPF programs with the same section name;
  + support for accessing in-kernel per-CPU variables;
  + support for type and enum value CO-RE relocations;
  + libbpf will auto-adjust CO-RE direct memory loads to adjust
    to 32-bit host architecture;
  + BPF_PROG_BIND_MAP support, .rodata will be bound automatically
    if kernel supports it;
  + new APIs for programmatic generation of BTF;
  + support for big-endian and little-endian endianness in BTF;
  + sleepable fentry/fexit/fmod_ret/lsm BPF program.
- Enable lua support only for Tumbleweed to close the gap between
  SLE and openSUSE Leap
* Fri Sep 25 2020 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.16.0
  + Support for kernel up to 5.8
  + trace.py: support kprobe/uprobe func offset
  + support raw perf config for perf_event_open in python
  + add BPFQueueStackTable support
  + added Ringbuf support support
  + libbpf-tools: readahead, biosnoop, bitesize, tcpconnlat,
    biopattern, biostacks
  + bug fixes and some additional arguments for tools
- Update libbpf to 0.1.1
  + __ksym extern variables support for getting kernel symbol
    addresses;
  + BPF XDP link support;
  + bpf_program__set_autoload() to disable loading and verifying
    specific BPF programs;
  + support for attaching map elements BPF iterator programs;
  + new getters/setters for more control over BPF map definitions;
  + all destructor-like APIs (e.g., perf_buffer__free() and
    bpf_object__close()) now accept pointers returned on error
    (in addition to NULL and valid pointers) and ignore them, no
    need to guard destructors with extra checks now;
  + bpf_link__detach() for force-detaching link, while it's still
    alive;
  + btf__parse_raw() and btf__parse() APIs for more convenient and
    flexible BTF parsing.
  + fix an issue with loading XDP programs on older kernels.
  + CO-RE relocations in .text section (in sub-programs) are now
    performed properly;
  + vmlinux BTF is not loaded unnecessarily twice;
  + perf_buffer__new() can be used on old kernels down to at least
    4.9 version;
  + libbpf's internal hashmap fixes for 32-bit architectures;
  + few BTF sanitization bugs and memory leaks fixed;
  + btf_dump handling of GCC built-in types for Arm NEON fixed;
  + BTF-defined map-in-map initialization fixed for 32-bit
    architectures;
  + various BTF fixes for 32-bit architectures.
* Fri Aug  7 2020 Gary Ching-Pang Lin <glin@suse.com>
- Modify URLs to get the tarballs with names not just versions
- Drop _constraints
  + We don't link the static clang libraries anymore and this
    reduces the requirements of hardware.
- Drop the unused _service file
* Thu Jul  2 2020 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.15.0
  + Support for kernel up to 5.7
  + new tools: funcinterval.py, dirtop.py
  + support lsm bpf programs
  + support multiple pid/tids for offwaketime
  + usdt: add helpers to set semaphore values
  + turn off x86 jump table optimization during jit compilation
  + add support to use bpf_probe_read[str}{_user,kernel} in all bpf
  + programs, fail back to old bpf_probe_read[_str] for old kernels
  + tools: add filtering by mount namespace
  + libbpf-tools: cpudist, syscount, execsnoop, vfsstat
  + lots of bug fixes and a few additional arguments for tools
- Update libbpf to 0.0.9
  + BTF-defined map-in-map support;
  + bpf_link support expanded to support new kernel BPF link objects;
  + BPF_ENABLE_STATS API;
  + new BPF ringbuf map support, added ring_buffer API for consuming;
  + bpf_link-backed netns attachment (flow_dissector).
  + bpf_object__load() better error code propagation;
  + few memory leaks and corruptions fixed;
  + register naming in PT_REGS s390 macros;
  + .bss pre-setting through skeleton is now supported as well.
- Drop upstreamed patch
  + bcc-bsc1172493-Make-reading-blacklist-optional.patch
* Thu Jun  4 2020 Gary Ching-Pang Lin <glin@suse.com>
- Add bcc-bsc1172493-Make-reading-blacklist-optional.patch to make
  reading kprobe blacklist optional so that the bcc scripts can
  work with the locked down kernel (bsc#1172493)
* Thu Apr 23 2020 Gary Ching-Pang Lin <glin@suse.com>
- Amend the sed rule for python3 shebang
* Wed Apr 22 2020 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.14.0
  + Support for kernel up to 5.6
  + new tools: biolatpcts.py
  + libbpf-tools: tools based on CORE and libbpf library directly
  + add --cgroupmap to various tools, filtering based cgroup
  + support kfunc (faster kprobe) for vfsstat, klockstat and
    opensnoop
  + lots of bug fixes and a few additional arguments for tools
- Update libbpf to 0.0.8
  + Add support for BPF-LSM
  + CO-RE relocation edge cases
  + expected_attach_type handling fixes at load time
  + fixes in hanling kernels without BTF support
  + internal map sanitization improvements
- Drop support-clang9.patch
  + Upstream fixed it in another way.
* Tue Mar  3 2020 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.13.0
  + Support for kernel up to 5.5
  + bindsnoop tool to track tcp/udp bind information
  + added compile-once run-everywhere based libbpf-tools, currently
    only runqslower is implemented.
  + new map support: sockhash, sockmap, sk_storage, cgroup_storage
  + enable to run github actions on the diff
  + cgroupmap based cgroup filtering for opensnoop, execsnoop and
    bindsnoop.
  + lots of bug fixes.
- Update libbpf to 0.0.7
  + Major new features:
  - BPF skeleton support;
  - Kconfig extern variables support;
  - STRUCT_OPS support;
  - support for BPF program extensions;
  - cgroup MULTI-mode support (bpf_prog_attach_xattr() API).
  - bpf_send_signal_thread() BPF helper;
  + Usability improvements:
  - BPF CO-RE improvements (flexible array, LDX/ST/STX instructions,
    improved conditional relocations);
  - generic bpf_program__attach() API;
  - SK_REUSEPORT program type support;
  - bpf_link_disconnect();
  - bpf_find_kernel_btf() API exposed;
  - large instruction limit probing added;
  - improved error message for RLIMIT_MEMLOCK.
  + Fixes:
  - fix perf_buffer handling of offline/missing CPUs;
  - various other fixes and usability improvements.
- Drop upstreamed fix: bcc-fix-test_map_in_map.patch
* Mon Jan 20 2020 Ondřej Súkup <mimi.vx@gmail.com>
- drop python2 bindings
- don't require python3-devel package
* Mon Dec 23 2019 Ismail Dönmez <idonmez@suse.com>
- Fix build when pkg_vcmp is not defined
* Mon Dec 16 2019 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.12.0
  + Support for kernel up to 5.4
  + klockstat tool to track kernel mutex lock statistics
  + cmake option CMAKE_USE_LIBBPF_PACKAGE to build a bcc shared
    library
  + linking with distro libbpf_static.a
  + new map.lookup_or_try_init() API to remove hidden return in
    map.lookup_or_init()
  + BPF_ARRAY_OF_MAPS and BPF_HASH_OF_MAPS support
  + support symbol offset for uprobe in both C++ and python API,
    kprobe already has the support
  + bug fixes for trace.py, tcpretrans.py, runqslower.py, etc.
- Update libbpf to 0.0.6
  + New features
  - new extensible bpf_object__open_{file,mem} APIs and
    DECLARE_LIBBPF_OPTS() macro to go with them
  - bpf_helpers.h, bpf_endian.h, and bpf_tracing.h are now
    distributed with libbpf
  - BPF CO-RE: added field size, field existence, and bitfield
    relocation support
  - BPF CO-RE: BPF_CORE_READ(), bpf_core_field_exists(),
    bpf_core_field_size() and other BPF CO-RE related helpers
    available through bpf_core_read.h header
  - bpf_object__open() API now auto-detects program type from
    its section name
  - BPF_PROG_TRACING programs support (incuding BTF-typed raw
    tracepoints, fentry/fexit programs)
  - mmap() support for BPF global variables
  - declarative map pinning support added
  - probe_read_{user,kernel}[_str]() BPF helpers added
  - bpf_get_link_xdp_info() function to get more XDP information
    added
  - a bunch of other AF_XDP changes
  + Usability improvements
  - no need for int version SEC('version') = 1; anymore
  - raw_tp/tp and uprobe/uretprobe section prefixes added
  - new bpf_program__get_{type,expected_attach_type} getters
  - preserve error code on program load failure
  + Fixes
  - btf_dump padding handling
  - bpf_object__name() returning name, not path
  - ELF section handling off-by-one bug fix
  - mem leak/double free fix in BPF program relocation code
- Replace lua51-luajit-devel with luajit-devel to reflect the
  recent change in Factory (bsc#1159191)
- Add bcc-fix-test_map_in_map.patch to fix the build error in the
  test case
* Tue Nov 19 2019 Gary Ching-Pang Lin <glin@suse.com>
- Enable USDT for s390x since 0.10.0 already supports it
* Thu Oct 31 2019 Ismail Dönmez <idonmez@suse.com>
- Add support-clang9.patch and apply it for llvm >= 9
- Fix sed call for python
* Mon Oct 14 2019 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.11.0
  + Support for kernel up to 5.3
  + Corresponding libbpf submodule release is v0.0.5
  + Fix USDT issue with multi-threaded applications
  + Fixed the early return behavior of lookup_or_init
  + Support for nic hardware offload
  + Fixed and Enabled Travis CI
  + A lot of tools change with added new options, etc.
- Update libbpf to 0.0.5
  + bpf_btf_get_next_id() API to iterate over system's BTF objects
  + libbpf_set_print() now returns previously set print callback
  + libbpf versioning, build, and packaging improvements
  + convenience helpers for working with BTF types
  + experimental BPF CO-RE relocation support
  + various AF_XDP fixes and enhancements
  + BTF-defined maps
  + tracing attachment APIs and bpf_link abstraction
  + perf buffer API
  + BTF-to-C conversion API
  + btf__parse_elf API for loading .BTF from ELF files
  + libbpf_num_possible_cpus() added
  + passing through prog_flags through bpf_object__open
  + new attach types detection added
- Use version for REVISION instead of libversion
* Tue Jun  4 2019 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.10.0
  + Support for kernel up to 5.1
  + corresponding libbpf submodule release is v0.0.3
  + support for reading kernel headers from /proc
  + libbpf.{a,so} renamed to libcc_bpf.{a,so}
  + new common options for some tools
  + new tool: drsnoop
  + s390 USDT support
- Update libbpf to 0.0.3
  + Also add the source url of libbpf
- Drop upstreamed patches
  + 0001-fix-string-re-being-used-on-bytes-for-Python-3.patch
  + 0001-Convert-bytes-to-string-for-re-in-get_tracepoints.patch
  + 0001-tools-don-t-mix-print-end-with-printb.patch
- Drop bcc-libbpf0 since upstream dropped the so file
- Enable SMP build flags since we don't need static clang anymore
* Tue Apr 23 2019 Gary Ching-Pang Lin <glin@suse.com>
- Add upstream patches to improve python3 compatibility
  + 0001-fix-string-re-being-used-on-bytes-for-Python-3.patch
  + 0001-Convert-bytes-to-string-for-re-in-get_tracepoints.patch
  + 0001-tools-don-t-mix-print-end-with-printb.patch
* Mon Mar 11 2019 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.9.0
- Add libbpf-5beb8a2ebffd.tar.gz since libbpf became a submodule
  of bcc
- Drop bcc-bsc1080085-import-readline-from-lib.patch
  + Upstream provide an additional argutment for the shared
    readline
* Thu Mar  7 2019 Gary Ching-Pang Lin <glin@suse.com>
- Correct the library version
* Thu Jan 17 2019 Jan Engelhardt <jengelh@inai.de>
- Remove unnecessary use of xargs.
- Remove idempotent %%if..%%endif guards.
- Update descriptions for grammar.
* Tue Jan 15 2019 Aleksa Sarai <asarai@suse.com>
- Update to 0.8.0.
- Remove upstreamed patches, and un-needed ones.
  - bcc-check_int128.patch
  - bcc-python3.patch (replaced with sed pipeline)
  - bcc-install-additional-headers.patch (bpftrace has fixes now)
* Sun Nov 25 2018 Aleksa Sarai <asarai@suse.com>
- Switch to %%license over %%doc for licenses.
- Add upstream patch for bpftrace builds. boo#1117223
  + bsc-install-additional-headers.patch
* Thu Oct 11 2018 Gary Ching-Pang Lin <glin@suse.com>
- Update to 0.7.0
- Refresh bcc-python3.patch
- Drop upstreamed patches
  + bcc-bpf_probe_read-fixes.patch
  + bcc-fix-ext4slower.patch
  + bcc-fix-tcpaccept.patch
  + bcc-prevent-bpf_probe_read-MemberExpre-rewrite.patch
- Remove bcc-bsc1065593-llvm4-hack.patch and set ENABLE_LLVM_SHARED
- Remove COPYRIGHT.txt which was dropped by upstream
* Tue Jun 19 2018 glin@suse.com
- Update to 0.6.0
- Add upstream patches
  + bcc-bpf_probe_read-fixes.patch
  + bcc-fix-ext4slower.patch
  + bcc-fix-tcpaccept.patch
  + bcc-prevent-bpf_probe_read-MemberExpre-rewrite.patch
- Drop upstreamed patches
  + bcc-fix-build-for-llvm-5.0.1.patch
  + bcc-fix-a-compilation-error-with-latest-llvm-clang-trunk.patch
  + bcc-bsc1080085-backport-bytes-strings.patch
  + bcc-bsc1080085-detect-slab-for-slabratetop.patch
  + bcc-bsc1080085-fix-cachetop-py3-str.patch
  + bcc-bsc1080085-fix-syscount-str.patch
- Refresh bcc-python3.patch
* Fri Apr  6 2018 msrb@suse.com
- Add bcc-fix-a-compilation-error-with-latest-llvm-clang-trunk.patch
  to fix build with LLVM6.
* Tue Mar 27 2018 glin@suse.com
- Add bcc-bsc1080085-fix-syscount-str.patch to convert ausyscall
  output to string (bsc#1080085)
* Tue Mar 20 2018 glin@suse.com
- Only enable bcc-lua for openSUSE (bsc#1085810)
- Amend the spec file to enable bps only for Tumbleweed
  (bsc#1085403)
* Thu Mar 15 2018 glin@suse.com
- Add bcc-bsc1080085-import-readline-from-lib.patch to read the
  symbol "readline" from libreadline. (bsc#1080085)
- Add bcc-bsc1080085-detect-slab-for-slabratetop.patch to detect
  the current memory allocator and include the correct header.
  (bsc#1080085)
- Make bcc-tools require audit since syscount.py needs ausyscall
  to get the syscall list. (bsc#1080085)
* Wed Feb 21 2018 glin@suse.com
- Add bcc-bsc1080085-backport-bytes-strings.patch and
  bcc-bsc1080085-fix-cachetop-py3-str.patch to fix the python3
  compatibility issue (bsc#1080085)
* Thu Feb  8 2018 glin@suse.com
- Update bcc-python3.patch to make python3 default for all the
  python scripts (bsc#1079961)
* Fri Jan 19 2018 glin@suse.com
- Add bcc-fix-build-for-llvm-5.0.1.patch to fix the compilation
  error against llvm-5.0.1
* Tue Dec 19 2017 dimstar@opensuse.org
- Replace clang4-devel-static BuildRequires with
  clang-devel-static: use the unversioned one, folling the llvm
  meta package version (like all the other llvm/clang packages in
  the build chain).
* Fri Dec 15 2017 glin@suse.com
- Request at least 10GB disk since the clang4-devel-static needs
  more than 3GB and sometimes caused build fail (FATE#322227)
* Thu Dec  7 2017 glin@suse.com
- Request at least 4G RAM for the s390x build
  (FATE#322227, bsc#1070362)
* Mon Dec  4 2017 glin@suse.com
- Tweak the installation path of bps directly instead of installing
  it manually. For those architectures without luajit, %%{_bindir}
  wasn't created and it failed the previous install command.
  (FATE#322227, bsc#1070362)
* Fri Dec  1 2017 glin@suse.com
- Update to 0.5.0 (bsc#1070563)
  + Explain possible reason of an error in scripts that rely on
    /proc/kallsyms
  + bpf: fix a couple of issues related to arm64
  + bpf: Add support for prog_name and map_name
  + Add a few introspection helpers
  + Introduce BPF Program Snapshot helper (bps)
  + Trace external pointers through maps
  + Merge BType, Map, and Probe Consumers
  + Fix exception handling in python3
  + Add usdt support for ARM64
  + bpf: make test py_test_tools_smoke pass on arm64
  + Add soname to libbpf.so
  + Fix Module display for unreadable Modules
  + Use bpf_prog_load_flag in APIs
  + Add flag to enable verifier log_level 2
  + bpf: use MCJIT explicitly for ExecutionEngine
  + change frontend rewriter to better handle anonymous struct/union
  + Move BCC debug options to an installed header file
  + use user-provided log_level in bpf_prog_load
  + Add utility for cc tests to read command outputs
  + Fix 'test_libbcc' from failing due to symbol name mismatch
  + Update perf event type and config checks
  + libbpf: Support unbound raw socket creation
  + force linking the whole api-static library into shared library
  + man/bps: Add a man page for introspection/bps.c
  + Do not keep Loader instances around
  + python: make _decode_table_types aware of __int128
  + python: Avoid unnecessary pointer object creations
- Only exclude ppc and s390 build (FATE#322227, bsc#1070362)
- Add _constraints to reserve 2GB memory for linking with
  clang4-devel-static
- Rename armv7.patch as bcc-check_int128.patch to check if the
  compiler support int128 or not
- Drop upstreamed patches:
  + bcc-bsc1065593-switch-to-mcjit.patch
  + bcc-add-soname-to-libbpf.patch
* Fri Nov 24 2017 manfred.h@gmx.net
- Add patch (bcc-python3.patch) to explicitly use "/usr/bin/python3"
* Fri Nov 17 2017 glin@suse.com
- Use the python3 package by default
- Provide and obsolete python-bcc (it's python2-bcc now)
* Thu Nov  9 2017 glin@suse.com
- Update to 0.4.0
  + Fix helper to access stack pointer for powerpc
  + bpf: rename helper function bpf_get_stackid
  + bpf: print out the src debug info to a temporary file
  + attempt to compile with system bpf.h if default compile failed
  + sync src/cc/compat/linux headers with latest net-next
  + Fix segfault with enumerations
  + Allow BCC to parse vDSO symbols
  + libbpf: print error to error stream
  + Avoid potential SEGFAULT when resolving Kernel symbols
  + Fix 'tools/statsnoop' from failing to attach kprobes
  + Update USDT argument constraint for powerpc and powerpc64
  + examples:dns_matching: make it work as DNS sniffer
  + add debug option to dump asm insns embedded with source
  + examples:dns_matching: helper function for adding cache entry
  + Traces external pointers in parenthesized expressions
  + examples:dns_matching: fixed loop break condition
  + Fix bcc_resolve_global_addr on shared libraries
  + BCC macro for the creation of LPM trie maps (#1359)
  + bpf_probe_read*: src argument should be const void *.
  + hardirqs, softirqs: Fix distribution mode units handling
  + Add a generic utility to check any binary availability
  + Fix 'test_debuginfo' from failing if a symbol has multiple
    aliases
  + nfsdist tool (#1347)
  + annotate program tag
  + add helpers to access program tag
  + examples: fixed http_filter example
  + nfsslower: trace slow NFS operations
  + Update after lookup in map.increment for HASH types
  + fix a bug introduced by previous lua-bcc build fix commit
  + Better check for compiler standard support
  + fix lua-bcc build issue with cmake try_compile
  + Fix segfault on incomplete types
  + Trace external pointers from helpers
  + Allow the flags to be specified in remove_xdp()
  + bcc-lua: --no-pie, not -no-pie
  + solisten, tcpconnlat, tcpretrans: Remove unnecessary
    bpf_probe_reads
- Add the new subpackage libbpf0
- Add bcc-bsc1065593-llvm4-hack.patch to work around the llvm
  libraries searching issue (bsc#1065593)
  (Also add clang4-devel-static to BuildRequires)
- Add bcc-bsc1065593-switch-to-mcjit.patch to switch from OrcJIT
  to MCJIT. OrcJIT actually doesn't work for bcc, and the bug was
  covered until we start to use the unified LLVM shared library.
  (bsc#1065593)
- Add bcc-add-soname-to-libbpf.patch to install the shared library
  properly
- Update the group of packages
- Disable USDT for ARM and AArch64 since it's not ready.
* Fri Aug 18 2017 glin@suse.com
- Update to 0.3.0+git1502955391.9de830a
  + avoid large map memory allocation in userspace
  + python - set attach_xdp's default flag value to 0
  + have uniform uprobe event names for python and C++
  + Remove extra S_MAXSTAT array allocation in some tools
  + Omit include of ptrace.h for empty usdt contexts
  + Add clang check for -nopie option
  + Correct commit id for BPF_FUNC_get_socket_cookie
  + tools/tcptracer: add timestamp option
  + Since LUA_GLOBALSINDEX is obsolete from Lua 5.2, use
    lua_getglobal function instead.
  + better state default value handling
  + add --state to offcputime
  + tcptop: Filter out negative values in receive probe
  + tcptop: Cleanup argument parsing
  + Use unsigned conversion specifier for nlmsg_pid
  + Fix wrong netlink port id check
  + 1. Use more safe snprintf instead of sprintf;
    2. Modify procfilename buffer length in bcc_procutils_language
    function.
  + permit multiple pids attaching to the same probe
  + generate proper usdt code to prevent llvm meddling with
    ctx->#fields
  + MySQL tracing without USDT (#1239)
  + Fix a clang memory leak
  + Update bpf.h and virtual_bpf.h to 4.13-rc1
  + Fix trace.py for library filenames containing colons (#1252)
  + cc: Add open_perf_event to the C/C++ API (#1232)
  + memleak: expand allocator coverage (#1214)
  + libbpf: fix build warning on setns (#1246)
  + usdt: Use ProcMountNS
  + proc: Enhance bcc_mapping_is_file_backed
  + Fix bcc.lua build issue in Ubuntu 17.04
  + Added helpers for BPF_PERCPU_ARRAY (#1230)
  + Add an option to strip leading zeros from histograms (#1226)
  + gethostlatency was rounding to full ms
  + Change clang frontend optimization level from 0 to 2
  + fix cc: error: unrecognized command line option -no-pie
  + fix incorrect code generation in usdt
* Mon Jun  5 2017 glin@suse.com
- Update to 0.3.0+git1496334311.6fa3681
  + Improve PerfEventArray clean up
  + make libbpf standalone-ready
  + Add support for generic XDP mode
  + Add option to control bcc_elf_foreach_sym behavior
  + Add bpf_get_first_key helper
  + Enable recursive scanf support for char[] as string
  + Fix computation of LUAJIT_INCLUDE_DIR
  + cc: Work around verifier error when reading USDT probe arguments
  + Disable non-static function calls
  + Added the option(USINGISYSTEM) of Cmake for controling whether
    using -isystem. (#1064)
  + softirqs: Migrate to kernel tracepoints instead of kprobes
    (#1091)
  + lua/bpf: implemented packet direct access
  + lua/bpf: support for NET_OFF for dissector
  + KVM hypercall analysis example (#1082)
  + cc: add support for prog table
  + cc: add support for array table
  + Add TableStorage class for wrapping bpf map tracking
  + funcslower: Trace slow kernel or user function calls
  + map.insert bcc helper to expose the BPF_NOEXIST flag (#1085)
  + bcc container improvements (#1051)
  + cc: define load_func and unload_func public
  + Python 3 compatibility fixes around string handling (#986)
  + Verify format specifiers in bpf_trace_printk in rewriter
  + Add build option for installing C++ examples
  + bpflist: Display processes with running BPF programs and maps
  + python: Allow module=None when resolving kernel symbols
  + mdflush: Add missing #include <linux/bio.h>
- Enable AArch64 build (FATE#322227)
- Remove remove-isystem.patch since it can be controlled by the
  cmake option now.
- Add gcc-c++ to the BuildRequires and switch to gcc/g++
* Fri Mar 10 2017 glin@suse.com
- Update to 0.3.0
  + Added s390x support. Needs 4.10 Kernel
  + Restrict rewrite of unary operators to dereference operator
  + cmake: Explicitly mark static libraries as such
  + Fix bpf_dins_pkt rewrite in BinaryOperator
  + cc: Symbol resolution with multiple executable regions per
    module
  + cc: Fix assertion for debug builds
  + cc: Don't parse the same module multiple times for USDT probes
  + add XDP return values to python interface
  + python: handle null module in BPF.sym
  + filetop: support specifying sort column via cmdline argument
  + cc: Retry symbol resolution using perfmap
  + cc: Handle nested functions correctly when resolving symbols
* Thu Mar  2 2017 idonmez@suse.com
- Add remove-isystem.patch to unconditionally removing -isystem,
  looks like the gcc check is broken.
- Add armv7.patch to disable __uint128_t usage which does not
  exist on ARMv7.
- Always use clang as C compiler, note that the build system will
  always use clang++ ad CXX compiler if it finds it.
* Thu Mar  2 2017 glin@suse.com
- Update to 0.2.0+git1488325605.4d0d430
  + Fix long running test_debuginfo and python3 fix
  + Make perf ring buffer size configurable
  + docs: Update eBPF features list
  + Improve matching of file-backed memory mappings
  + Fix symbol resolution by name (SymbolCache.resolve_name)
  + cc: Resolve symbols from external debuginfo
  + cc: Correctly treat PIE files as shared objects for symbols
  + Migrate to new symbols resolution API
  + Simplify BCC symbol resolution API
  + trace, argdist: Treat small USDT arguments correctly
  + Support base + index * scale addressing for USDT arguments
  + cc: Fix SEGV when there is no build-id section
  + syscount: Summarize syscall counts and latencies
  + u* tools: PHP support
  + bcc: add support for lpm trie map type
  + cc: Support for __data_loc tracepoint fields
  + Fix python2/3 incompatible percpu helpers
  + fix iteration over CPUs
  + Fixes for LLVM 4.0 and python3
  + Update [virtual_]bpf.h to 4.10
  + add bpf_obj_pin/bpf_obj_get to pin/get bpf objects
  + uobjnew: Attach uprobe only to the requested process
  + uflow: Trace method execution flow
  + ustat: Activity stats from high-level languages
  + ugc: Monitor GC events in high-level languages
  + ucalls: Summarize method calls with USDT
  + Example of using USDT
  + Add USDT support to C++ API
  + Improve linear histogram limit, and improve error message
  + add runqlen tool
  + docs: Update eBPF features list
  + Improve C++ API perf buffer polling
  + add support for bpf map flags
  + Fix bug of missing to install simple_tc.py
  + Add support for aarch64
  + Avoid unexpected log message on BPF program load error
  + Add lru_hash/lru_percpu_hash to python/lua
  + bcc: add lru_hash and lru_percpu_hash map types
- Remove the clang workaround since llvm 3.9.1 supports gcc c++11
  abi tag. (bsc#935533)
- Enable PowerPC64 and PowerPC64le build
* Tue Dec  6 2016 glin@suse.com
- Move manpages back to /usr/share/bcc/man since trace.8 is
  conflicted with the one from postfix.
* Thu Dec  1 2016 glin@suse.com
- Update to 0.2.0+git1480569532.5647de0
  + profile: -p should match user PID
  + tcplife: reorder logic to catch missed timestamps
  + hello_perf_output: match the data type of pid
  + Remove debug flag override in bcc_exception.h
  + Use StatusTuple constructor in mkstatus_
  + Implement StatusTuple class instead of using std::tuple
  + biotop.py: fix compiler error on newer kernels
  + Determine kernel dirs at runtime (fix #743)
  + Rename exception.h to bcc_exception.h
  + tcplife.py: Catch passive closed by server, #788
  + Install exception.h and common.h
  + Fixup test errors in clang, c api
  + trace: Avoid passing -1 as the pid to USDT
  + Fix Tracepoint example (#809)
  + cc, python: Clean up BPF module and tables
  + Fix warnings covered by -Wdelete-non-virtual-dtor
  + Fix argument type for increment() in documentation (#794)
  + trace: add pid/tid filtering, fix symbolizing, misc nits (#798)
  + Expose destruction of SymbolCache in libbcc
  + perf_reader: install perf_reader.h
  + Use headers from BCC in installed files (#793)
  + funccount: Bail early if there are no matching functions (#792)
  + python: Grab all keys before zeroing
  + funccount: Switch to BPF array instead of hash
  + Update profile.py to use new perf support (#776)
  + Example for using BPF perf event
  + funccount: Do not prepopulate location cache
  + python: Filter duplicate in get_kprobe_functions
  + Python API for BPF perf event
  + Add bpf_attach_perf_event in libbpf
  + Add BPF_PROG_TYPE_PERF_EVENT to bpf_prog_type enum
  + add tcplife (#773)
  + add reset-trace (#766)
  + funccount: Verify probe max limit (#771)
  + python: Fix kprobe quota test breakage, add uprobes
  + funccount: Generalize for uprobes, tracepoints, and USDT
  + bcc: Make regex helpers publicly accessible
  + stackcount: Style fixes for linter (pep8)
  + fix profile.py page_offset_base breakage (#768)
  + trace, argdist: -I switch for trace and miscellaneous fixes
    (#761)
  + cc: Support glob+offset format in USDT arguments (#753)
  + Support filtering by process ID in the filesystem slower tools
    (#756)
  + trace: STRCMP helper function
  + mysqld_slower: Fix breakage after USDT API change
  + trace: Add %%K and %%U format specifiers (#742)
  + Update opensnoop to filter by PID and TID (#739)
  + funclatency: user functions support (#733)
  + tplist: Print USDT locations and arguments (#734)
  + src/lua: LuaJIT BPF compiler, examples, tests (#652)
  + stackcount: Support uprobes, tracepoints, and USDT (#730)
  + trace: Initialize USDT arguments to 0 before reading (#725)
  + argdist, trace: Native tracepoint support (#724)
  + argdist: Cumulative mode (-c) (#719)
  + trace: Print USDT arg helpers in verbose mode (#723)
  + argdist, trace: Support naked executable names in probes (#720)
  + docs: Update eBPF features list by kernel version (#717)
  + fixup the issue in which distributed_bridge example (#716)
  + Fix bpf_common.cc include style (#715)
  + Fix argdist, trace, tplist to use the libbcc USDT support (#698)
  + [tcpconnect] filter traced connection based on destination ports
  + Fix bpf log buffer for large bpf program: (#680)
  + opensnoop: Introduce process name filtering
- Exclude the cpp examples from installation
- Remove the isystem path since we are using clang++
- Install the manpages correctly
- Improve the spec file to search the luajit pathes and fix some
  dependency issue in Leap 42.2
- Remove "-DBCC_KERNEL_HAS_SOURCE_DIR=1" since bcc can detect the
  kernel dir dynamically now.
* Mon Sep 26 2016 glin@suse.com
- Add llvm-gold to the BuildRequires since the package was split
  from llvm since 3.8.1
* Fri Sep  9 2016 glin@suse.com
- Update to 0.2.0
  + examples: fix indentation in tracing/tcpv4connect
  + fileslower/filetop: use de->d_name.name, add filtering
* Fri Aug 26 2016 glin@suse.com
- Update to snapshot v0.1.8+git1472097662.4ebb7cf
  + fix biosnoop after kernel change
  + offcputime improvements: use less RAM, add PID/TID support
  + Add perf_submit_skb
  + Adjustments to the documentation
  + fix build with 4.0 llvm trunk
  + frontends/clang: Safety check for invalid opLoc in ProbeVisitor
  + Tool to sniff data contents before encrypted with OpenSSL or
    GnuTLS
  + Add bpf_get_current_task() helper definition
  + USDT Python API and example
  + Lua Tools for BCC
  + BPF: better format for `ksymaddr`
  + table: Implement a StackWalker for StackTrace tables
  + added percpu support in bcc
  + Fix error handling when attaching {u,k}{,ret}probes
  + Fix python3 incompatibilities
  + Update headers with 4.5+ features
  + Add v6 headers to proto.h
  + Use pre-calculated function addresses in funccount
  + Add name to address ksym helper
  + Add a table.zero() function to bcc.TableBase
  + Enforce limit of 1000 open [uk]probes
- Drop upstreamed bcc-kernel-header-search.patch
- Add bcc-docs to collect the documentation
- Add bcc-lua to process the lua scripts
- Add the license files to libbcc0
* Fri Jul 22 2016 glin@suse.com
- Use the upstream tarball and add the URL
- Amend the description of the pacakge
- Use the right group for libbcc0
* Wed Apr 20 2016 glin@suse.com
- Remove "strip" from "make install" to enable debuginfo
* Tue Mar 15 2016 glin@suse.com
- Switch to clang to avoid the c++11 tag issue (bsc#935533)
- Update bcc-kernel-header-search.patch to include headers in
  /lib/modules/$(uname -r)/build/
* Tue Mar  8 2016 glin@suse.com
- Replace bcc-suse-kernel-headers.patch with the upstream fix,
  bcc-kernel-header-search.patch, and add
  "-DBCC_KERNEL_HAS_SOURCE_DIR=1" to cmake.
- Fix the formation in the spec file
* Thu Feb 25 2016 glin@suse.com
- Update to version 0.1.8
  + http_filter renamed, README fixed
  + Migrated filelife to bpf_perf_event
  + migrated to use bpf_perf_events
  + Migrated killsnoop to bpf_perf_event
  + Print traceback only if verbose mode was requested
  + trace: trace function execution with custom format strings and
    filters
- Add back python3-bcc
- Make python-bcc require libbcc0
* Thu Feb 18 2016 glin@suse.com
- Update to version 0.1.7+git1455766673.13e74d3
  + use __builtin_memcpy() instead of unrolled loop
  + http filter example
  + Add bpf_module.h to CMakeLists.txt
  + different man formats
  + Fix segfault in ~BPFModule on syntax error
  + Add bitesize tool
  + Support array and pointer types in scanf generated function
  + Add biotop tool
  + Added memory leak tracer
  + Fix python map.items() racing with bpf delete
  + Don't show allocations newer than a configurable age
  + Add bpf_get_prandom_u32 to helpers
  + Added --stack-depth switch to control the number of stack
    frames captured for each allocation
  + Fixed long arg name from stack_depth to stack-depth
  + Added option to display only top N stacks by size
  + use bpf_perf_event_output() instead
  + save one bpf_probe_read()
  + 3 tools: oomkill, dcstat, dcsnoop
  + Implemented histogram functionality, including strings; added
    examples
  + Added ret probes
  + Renamed to argdist.py, updated command-line switches, added
    kernel probe pid filtering, added verbose mode that prints the
    BPF program
  + ext4 and xfs tools
  + tcp to bpf_perf_output
  + 3 tools: tcpretrans, zfsslower, zfsdist
  + inline C in /tools
  + 2 tools: btrfsdist, btrfsslower
  + Split bcc/__init__.py into multiple files
  + Split bcc.table.BPFTable into multiple type-specific classes
  + Support native integer indexing in table.Array type
  + Fix breakage in open_perf_buffer
  + Embed runtime header files in libbcc.so
- Add bcc-suse-kernel-headers.patch to fix the kernel header path
- Drop bcc-workaround-gcc5-abi.patch since it never works...
- Drop the dependency of bcc-devel from python-bcc
* Tue Feb  2 2016 glin@suse.com
- Update to version v0.1.7+git20160131.143df80
  + Updates to use cmake GLOB and libbcc.so.0 in python init
  + Add decode() to ascii string in offcputime.py
  + Add libbpf.c support for uprobes
  + Add python support for attaching bpf programs to uprobes
  + Fixes for address calculation
  + Fixup objdump calling syntax and add docstrings
  + Add uprobe strlen histogram example
  + Update test_dump_func to be python3 compatible
* Tue Jan 26 2016 glin@suse.com
- Update to version v0.1.7+git20160119.f50ca1f
  + fix pep8 lint errors in the rest of the tools
  + Close fd and unshare when public map is destructed
  + stack walker typo and improvement
  + optimize code, remove unnecessary filter check
  + add -u, and change from 2 to 1 traced funcitons
* Mon Jan 11 2016 glin@suse.com
- Update to version v0.1.7+git20160110.a0aa7f2
  + Remove runtime dependency on gcc stdarg headers and make
  + Add ability to set custom cflags when loading programs
  + Add ability to export maps, enables cross-program sharing
  + Rename BPF_EXPORT to BPF_TABLE_PUBLIC
  + fix pep8 lint errors in biolatency and biosnoop
- Remove make from Requires of python-bcc
* Wed Dec 16 2015 glin@suse.com
- Update to version v0.1.7+git20151210.23b87e5:
  + Fixup dependencies of bcc-tools package
  + Automatically bump memlock ulimit
  + fixed bugs in control-flow generation
  + Fix breakage from LLVM 3.8 API change
  + make sure LDFLAGS are propagated as well
  + Improve json type support for misc struct/union types
  + Drop broken p4/docs symlink and create README.md+URL
- Drop upstreamed bcc-honor-external-cflags.patch
* Mon Nov 30 2015 glin@suse.com
- Udpate to bcc-0.1.7+git48.g1c7debd
- Add python-future as the Recommends for bcc-examples so that
  the scripts can be compatible with python 2 and python 3.
- Remove python3-bcc
* Mon Nov 16 2015 glin@suse.com
- Update to bcc-0.1.7+git34.gfa9684d
- Add bcc-workaround-gcc5-abi.patch to work around the old c++11
  abi in clang
- Add bcc-honor-external-cflags.patch to adopt the external cflags
- Drop bcc-fix-packaging.patch which is already in the tarball
- Amend the requirements of python-bcc
  + make and kernel-devel are necessary
- Add python3-bcc since the python binding is compatiable with both
  2 and 3
* Fri Oct 23 2015 glin@suse.com
- initial import: v0.1.7
- Add bcc-fix-packaging.patch to fix versioning issue of the shared
  library
