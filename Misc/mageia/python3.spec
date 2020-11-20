# NOTES ON BOOTSTRAPING PYTHON 3.x:
#
# Due to a dependency cycle between Python, rpm, pip, setuptools, wheel,
# and other packages, in order to rebase Python 3 one has to build in the
# following order:
#
# 1.  gdb %%bcond_with python
# 2.  rpm-mageia-setup %%bcond_without bootstrap
# 3.  python-rpm-generators %%bcond_without bootstrap
# 4   python3 (if python3 is build to core/udpates_testing there's no need to use %bcond_with rpmwheels)
# 5.  python-setuptools %%bcond_without bootstrap
# 6.  python-rpm-generators %%bcond_with bootstrap
# 7.  python-pip %%bcond_without bootstrap
# 8.  python-wheel %%bcond_without bootstrap
# 9.  python-setuptools %%bcond_with bootstrap
# 10. python-pip %%bcond_with bootstrap
# 11. python-wheel %%bcond_with bootstrap
# 12. rpm
# 13. python-cython
# 14. python-numpy
# 15. boost
# 16. gdb %%bcond_without python
# 17. meson
# 18. python-coverage
# 19. python-nose
# 20. python-yaml
# 21. python-markdown
# 22. python-markupsafe
# 23. python-beaker
# 24. python-setuptools_scm
# 25. python-dateutil
# 26. python-six
# 27. python-pbr
# 28. python-argparse
# 29. python-traceback2
# 30. python-linecache2
# 31. python-unittest2
# 32. python-funcsigs
# 33. python-mock
# 34. python-mako
# 35  python-pygments
# 36. gobject-introspection
# 37. python-enchant
# 38. file
# 39. rpmlint
# 40. rpm-mageia-setup %%bcond_with bootstrap

# Then the most important packages have to be built, starting from their
# various leaf dependencies recursively. After these have been built, a
# targeted rebuild should be requested for the rest.
#
# Currently these packages are recommended to have been built before a targeted
# rebuild after a python abi change:
#   python-sphinx, python-pytest, python-requests

%global pybasever 3.8
%global familyver 3

# pybasever without the dot:
%global pyshortver 38

# version
%global version 3.8.5
%global docver %{version}

# comment out if not prerel
#global prerel rc1

# rel for bumping
%global rel 1

# filter out bogus requires on python(abi) = 3.6 for testsuite
%global __requires_exclude_from %{?__requires_exclude_from:%__requires_exclude_from|}^%{_libdir}/python%{pybasever}/test/test_importlib/data

# For bootstrapping python3.x to python3.y
%bcond_with bootstrap

# Whether to use RPM build wheels from the python-{pip,setuptools}-wheel package
# Uses upstream bundled prebuilt wheels otherwise
%bcond_without rpmwheels
# The following versions of setuptools/pip are bundled when this patch is not applied.
# The versions are written in Lib/ensurepip/__init__.py, this patch removes them.
# When the bundled setuptools/pip wheel is updated, the patch no longer applies cleanly.
# In such cases, the patch needs to be amended and the versions updated here:
%global pip_version 20.1.1
%global setuptools_version 47.1.0

# Expensive optimizations (mainly, profile-guided optimizations)
%bcond_without optimizations

# Run the test suite in %%check
%bcond_without tests

# Support for the GDB debugger
%bcond_with gdb_hooks

# The dbm.gnu module (key-value database)
%bcond_without gdbm

# Main interpreter loop optimization
%bcond_without computed_gotos

# Support for the Valgrind debugger/profiler
%ifarch %{valgrind_arches}
%bcond_without valgrind
%else
%bcond_with valgrind
%endif


# =====================
# General global macros
# =====================

%global pylibdir %{_libdir}/python%{pybasever}
%global dynload_dir %{pylibdir}/lib-dynload
%global site_packages %{pylibdir}/site-packages

# ABIFLAGS, LDVERSION and SOABI are in the upstream configure.ac
# See PEP 3149 for some background: http://www.python.org/dev/peps/pep-3149/
%global ABIFLAGS_optimized %{nil}

%global LDVERSION_optimized %{pybasever}%{ABIFLAGS_optimized}

%global SOABI_optimized cpython-%{pyshortver}%{ABIFLAGS_optimized}-%{_arch}-linux%{_gnu}

# All bytecode files are in a __pycache__ subdirectory, with a name
# reflecting the version of the bytecode.
# See PEP 3147: http://www.python.org/dev/peps/pep-3147/
# For example,
#   foo/bar.py
# has bytecode at:
#   foo/__pycache__/bar.cpython-%%{pyshortver}.pyc
#   foo/__pycache__/bar.cpython-%%{pyshortver}.opt-1.pyc
#   foo/__pycache__/bar.cpython-%%{pyshortver}.opt-2.pyc
%global bytecode_suffixes .cpython-%{pyshortver}*.pyc

# Disable automatic bytecompilation. The python3 binary is not yet be
# available in /usr/bin when Python is built. Also, the bytecompilation fails
# on files that test invalid syntax.
%global __brp_python_bytecompile %nil

%define lib_major       %{pybasever}
%define lib_name_orig   libpython%{familyver}
%define lib_name        %mklibname python %{lib_major}
%define develname       %mklibname python3 -d

Summary:        An interpreted, interactive object-oriented programming language
Name:           python3
Version:        %{version}
Release:        %mkrel %{?prerel:0.%prerel.}%{rel}
License:        Modified CNRI Open Source License
Group:          Development/Python

BuildRequires:  automake
BuildRequires:  gcc-c++
BuildRequires:  blt
BuildRequires:  pkgconfig(bluez)
BuildRequires:  db-devel
BuildRequires:  pkgconfig(expat)
BuildRequires:  gdbm-devel
BuildRequires:  gmp-devel
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(ncursesw)
BuildRequires:  pkgconfig(openssl) >= 1.1
BuildRequires:  readline-devel
BuildRequires:  termcap-devel
BuildRequires:  tcl
BuildRequires:  pkgconfig(tcl)
BuildRequires:  tk
BuildRequires:  pkgconfig(tk)
BuildRequires:  autoconf
BuildRequires:  pkgconfig(bzip2)
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(liblzma)
# uncomment once the emacs part no longer conflict with python 2.X
#BuildRequires: emacs
#BuildRequires: emacs-bin
%if %{with valgrind}
BuildRequires:  pkgconfig(valgrind)
%endif

BuildRequires:  systemtap-sdt-devel

%if %{with rpmwheels}
BuildRequires:  python-setuptools-wheel >= %{setuptools_version}
BuildRequires:  python-pip-wheel >= %{pip_version}
%endif

%if %{without bootstrap}
# for make regen-all and distutils.tests.test_bdist_rpm
BuildRequires: python3
%endif

Source0:        https://www.python.org/ftp/python/%{version}/Python-%{version}%{?prerel}.tar.xz
Source1:        https://docs.python.org/%{pybasever}/archives/python-%{docver}%{?prerel}-docs-html.tar.bz2

# A simple script to check timestamps of bytecode files
# Run in check section with Python that is currently being built
# Originally written by bkabrda
Source8: check-pyc-timestamps.py

#
# Upstream patches
#

#
# Fedora patches
#

# 00001 #
# Fixup distutils/unixccompiler.py to remove standard library path from rpath:
# Was Patch0 in ivazquez' python3000 specfile:
Patch101: 00001-rpath.patch

# 00102 #
# Change the various install paths to use /usr/lib64/ instead or /usr/lib
# Only used when "%%{_lib}" == "lib64"
# Not yet sent upstream.
Patch102: 00102-lib64.patch

# 00111 #
# Patch the Makefile.pre.in so that the generated Makefile doesn't try to build
# a libpythonMAJOR.MINOR.a
# See https://bugzilla.redhat.com/show_bug.cgi?id=556092
# Downstream only: not appropriate for upstream
Patch111: 00111-no-static-lib.patch

# 00189 #
# Instead of bundled wheels, use our RPM packaged wheels from
# /usr/share/python-wheels
# Downstream only: upstream bundles
# We might eventually pursuit upstream support, but it's low prio
Patch189: 00189-use-rpm-wheels.patch

# 00251
# Set values of prefix and exec_prefix in distutils install command
# to /usr/local if executable is /usr/bin/python* and RPM build
# is not detected to make pip and distutils install into separate location
# Fedora Change: https://fedoraproject.org/wiki/Changes/Making_sudo_pip_safe
# Downstream only: Awaiting resources to work on upstream PEP
Patch251: 00251-change-user-install-location.patch

# 00274 #
# Upstream uses Debian-style architecture naming. Change to match Fedora.
Patch274: 00274-fix-arch-names.patch

# 00328 #
# Restore pyc to TIMESTAMP invalidation mode as default in rpmbubild
# See https://src.fedoraproject.org/rpms/redhat-rpm-config/pull-request/57#comment-27426
# Downstream only: only used when building RPM packages
# Ideally, we should talk to upstream and explain why we don't want this
Patch328: 00328-pyc-timestamp-invalidation-mode.patch

# (New patches go here ^^^)
#
# Mageia patches
#
Patch500:        python3-3.7.1-module-linkage.patch
Patch501:        python3-3.5.2-skip-distutils-tests-that-fail-in-rpmbuild.patch
Patch502:        python3-3.7.1-uid-gid-overflows.patch
Patch503:        python3-3.5.2-dont-raise-from-py_compile.patch
Patch506:        python3-3.6.2-python3-config-LIBPLUSED-cmp0004-error.patch
Patch507:        link-C-modules-with-libpython.patch

Provides:       python(abi) = %{pybasever}
Provides:       /usr/bin/python%{LDVERSION_optimized}
Provides:       /usr/bin/python%{pybasever}
Requires:       python-rpm-macros >= 3-8
Requires:       python3-rpm-macros >= 3-8

Conflicts:      python < 2.7.17-2
Conflicts:	%{_lib}python3-devel < 3.8.1
Requires:       %{lib_name} = %{version}-%{release}

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that
need a programmable interface. This package contains most of the
standard Python modules, as well as modules for interfacing to the
Tix widget set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.

%package -n     %{lib_name}
Summary:        Shared libraries for Python %{version}
Group:          System/Libraries
Requires:       %{lib_name}-stdlib = %{version}-%{release}

%description -n %{lib_name}
This packages contains Python shared object library.  Python is an
interpreted, interactive, object-oriented programming language often
compared to Tcl, Perl, Scheme or Java.

%package -n     %{lib_name}-stdlib
Summary:        Python %{version} standard library
Group:          Development/Python
%if %{with rpmwheels}
Requires:	python-setuptools-wheel
Requires:	python-pip-wheel
%else
Provides:	bundled(python3-pip) = %{pip_version}
Provides:	bundled(python3-setuptools) = %{setuptools_version}
%endif

%description -n %{lib_name}-stdlib
This package contains Python 3's standard library.
It is normally not used on its own, but as a dependency of Python %{version}.

%package -n     %{lib_name}-testsuite
Summary:        Testsuite for the Python %{version} standard library
Group:          Development/Python
Provides:       python3-testsuite = %{version}-%{release}
Requires:       %{lib_name}-stdlib = %{version}-%{release}
Requires:       %{lib_name} = %{version}-%{release}
Recommends:     tkinter3

%description -n %{lib_name}-testsuite
The complete testsuite for the Python standard library.
It is normally not used on its own, but as a dependency of Python %{version}.

%package -n     %{develname}
Summary:        The libraries and header files needed for Python development
Group:          Development/Python
Requires:       %{name} = %{version}-%{release}
Requires:       %{lib_name} = %{version}-%{release}
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{lib_name_orig}-devel = %{version}-%{release}
Conflicts:	%{_lib}python-devel < 2.7.17-2
Recommends:     %{lib_name}-testsuite
Recommends:     %{name}-docs

%description -n %{develname}
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install %{develname} if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package        docs
Summary:        Documentation for the Python programming language
Requires:       %{name} >= %{version}
Requires:       xdg-utils
Group:          Development/Python
BuildArch:      noarch

%description    docs
The python-docs package contains documentation on the Python
programming language and interpreter.  The documentation is provided
in ASCII text files and in LaTeX source files.

Install the python-docs package if you'd like to use the documentation
for the Python language.

%package -n     tkinter3
Summary:        A graphical user interface for the Python scripting language
Group:          Development/Python
Requires:       %{name} = %{version}-%{release}
Requires:       tcl tk
Provides:       python3-tkinter

%description -n tkinter3
The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%package -n     tkinter3-apps
Summary:        Various applications written using tkinter
Group:          Development/Python
Requires:       tkinter3

%description -n tkinter3-apps
Various applications written using tkinter

%prep
%setup -qn Python-%{version}%{?prerel}
# Remove all exe files to ensure we are not shipping prebuilt binaries
# note that those are only used to create Microsoft Windows installers
# and that functionality is broken on Linux anyway
find -name '*.exe' -print -delete

# Remove bundled libraries to ensure that we're using the system copy.
rm -r Modules/expat

# Upstream patches

# Fedora patches
%patch101 -p1

%if "%{_lib}" == "lib64"
%patch102 -p1
%endif
%patch111 -p1

%if %{with rpmwheels}
%patch189 -p1
rm Lib/ensurepip/_bundled/*.whl
%endif

%patch251 -p1
%patch274 -p1
%patch328 -p1

# Mageia patches
#patch500 -p1
%patch501 -p1
%patch502 -p1
%patch503 -p1
%patch506 -p1
%patch507 -p1

# Remove files that should be generated by the build
# (This is after patching, so that we can use patches directly from upstream)
rm configure pyconfig.h.in

# drop Autoconf version requirement
sed -i 's/^AC_PREREQ/dnl AC_PREREQ/' configure.ac

# docs
mkdir html
bzcat %{SOURCE1} | tar x  -C html

find . -type f -print0 | xargs -0 perl -p -i -e 's@/usr/local/bin/python@/usr/bin/python3@'

%build
autoreconf -vfi

# Remove -Wl,--no-undefined in accordance with MGA #9395 :
# https://bugs.mageia.org/show_bug.cgi?id=9395
%define _disable_ld_no_undefined 1

# Get proper option names from bconds
%if %{with computed_gotos}
%global computed_gotos_flag yes
%else
%global computed_gotos_flag no
%endif

%if %{with optimizations}
%global optimizations_flag "--enable-optimizations"
%else
%global optimizations_flag "--disable-optimizations"
%endif

export CFLAGS="%{optflags} -D_GNU_SOURCE -fPIC -fwrapv"
export CFLAGS_NODIST="%{optflags} -D_GNU_SOURCE -fPIC -fwrapv -fno-semantic-interposition"
export CXXFLAGS="%{optflags} -D_GNU_SOURCE -fPIC -fwrapv"
export OPT="%{optflags} -D_GNU_SOURCE -fPIC -fwrapv"
export LINKCC="gcc"
export LDFLAGS="%{ldflags}"
export LDFLAGS_NODIST="%{ldflags} -fno-semantic-interposition"

%configure --host='' \
  --enable-ipv6 \
  --enable-shared \
  --with-computed-gotos=%{computed_gotos_flag} \
  --with-dbmliborder=gdbm:ndbm:bdb \
  --with-system-expat \
  --with-system-ffi \
  --enable-loadable-sqlite-extensions \
  --with-dtrace \
  --with-lto \
  --with-ssl-default-suites=openssl \
%if %{with valgrind}
  --with-valgrind \
%endif
  --with-threads \
  --without-ensurepip \
  %{optimizations_flag}

# (misc) if the home is nfs mounted, rmdir fails due to delay
export TMP="/tmp" TMPDIR="/tmp"

%if %{without bootstrap}
  # Regenerate generated files (needs python3)
  %make_build regen-all PYTHON_FOR_REGEN="python%{pybasever}"
%endif

%make_build EXTRA_CFLAGS="$CFLAGS" LN="ln -sf"

%install

%if %{with gdb_hooks}
DirHoldingGdbPy=%{_prefix}/lib/debug/%{_libdir}
mkdir -p %{buildroot}$DirHoldingGdbPy
%endif # with gdb_hooks

# fix Makefile to get rid of reference to distcc
perl -pi -e "/^CC=/ and s/distcc/gcc/" Makefile

# set the install path
echo '[install_scripts]' >setup.cfg
echo 'install_dir='"${RPM_BUILD_ROOT}/usr/bin" >>setup.cfg

%make_install LN="ln -sf"

%if %{with gdb_hooks}
  # See comment on $DirHoldingGdbPy above
  PathOfGdbPy=$DirHoldingGdbPy/libpython%{pybasever}%{ABIFLAGS_optimized}-%{version}-%{release}.%{_arch}.debug-gdb.py
  cp Tools/gdb/libpython.py %{buildroot}$PathOfGdbPy
%endif # with gdb_hooks

# Install directories for additional packages
install -d -m 0755 %{buildroot}%{pylibdir}/site-packages/__pycache__
%if "%{_lib}" == "lib64"
# The 64-bit version needs to create "site-packages" in /usr/lib/ (for
# pure-Python modules) as well as in /usr/lib64/ (for packages with extension
# modules).
# Note that rpmlint will complain about hardcoded library path;
# this is intentional.
install -d -m 0755 %{buildroot}%{_prefix}/lib/python%{pybasever}/site-packages/__pycache__
%endif

# overwrite the copied binary with a link
pushd %{buildroot}%{_bindir}
#ln -sf python%{LDVERSION_optimized} python%{pybasever}
ln -sf python%{pybasever} python%{familyver}
popd

pushd %{buildroot}%{_libdir}
ln -sf $(ls libpython%{lib_major}*.so.*) libpython%{lib_major}.so
popd

# make python3 as default one
ln -s ./python3 %{buildroot}%{_bindir}/python
ln -s ./pydoc3 %{buildroot}%{_bindir}/pydoc
ln -s ./pygettext3.py %{buildroot}%{_bindir}/pygettext.py
ln -s ./msgfmt3.py %{buildroot}%{_bindir}/msgfmt.py
ln -s ./python3-config %{buildroot}%{_bindir}/python-config
ln -s ./python3.1 %{buildroot}%{_mandir}/man1/python.1
ln -s ./python3.pc %{buildroot}%{_libdir}/pkgconfig/python.pc

# install pynche as pynche3
cat << EOF > %{buildroot}%{_bindir}/pynche3
#!/usr/bin/bash
exec %{_libdir}/python%{pybasever}/site-packages/pynche/pynche
EOF
rm -f Tools/pynche/*.pyw
cp -r Tools/pynche %{buildroot}%{_libdir}/python%{pybasever}/site-packages/

chmod 755 %{buildroot}%{_bindir}/{idle3,pynche3}

ln -f Tools/pynche/README Tools/pynche/README.pynche

%if %{with valgrind}
install Misc/valgrind-python.supp -D %{buildroot}%{_libdir}/valgrind/valgrind-python3.supp
%endif

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{_real_vendor}-tkinter3.desktop << EOF
[Desktop Entry]
Name=IDLE
Comment=IDE for Python3
Exec=%{_bindir}/idle3
Icon=development_environment_section
Terminal=false
Type=Application
Categories=Development;IDE;
EOF

cat > %{buildroot}%{_datadir}/applications/%{_real_vendor}-%{name}-docs.desktop << EOF
[Desktop Entry]
Name=Python documentation
Comment=Python complete reference
Exec=%{_bindir}/xdg-open %_defaultdocdir/%{name}-docs/index.html
Icon=documentation_section
Terminal=false
Type=Application
Categories=Documentation;
EOF

# fix non real scripts
#chmod 644 %{buildroot}%{_libdir}/python*/test/test_{binascii,grp,htmlparser}.py*
find %{buildroot} -type f \( -name "test_binascii.py*" -o -name "test_grp.py*" -o -name "test_htmlparser.py*" \) -exec chmod 644 {} \;

# fix python library not stripped
chmod u+w %{buildroot}%{_libdir}/libpython%{lib_major}*.so.1.0 $RPM_BUILD_ROOT%{_libdir}/libpython3.so

# Make python3-devel multilib-ready
mv %{buildroot}%{_includedir}/python%{LDVERSION_optimized}/pyconfig.h \
   %{buildroot}%{_includedir}/python%{LDVERSION_optimized}/pyconfig-%{__isa_bits}.h
cat > %{buildroot}%{_includedir}/python%{LDVERSION_optimized}/pyconfig.h << EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "pyconfig-32.h"
#elif __WORDSIZE == 64
#include "pyconfig-64.h"
#else
#error "Unknown word size"
#endif
EOF

# Make sure distutils looks at the right pyconfig.h file
# See https://bugzilla.redhat.com/show_bug.cgi?id=201434
# Similar for sysconfig: sysconfig.get_config_h_filename tries to locate
# pyconfig.h so it can be parsed, and needs to do this at runtime in site.py
# when python starts up (see https://bugzilla.redhat.com/show_bug.cgi?id=653058)
#
# Split this out so it goes directly to the pyconfig-32.h/pyconfig-64.h
# variants:
sed -i -e "s/'pyconfig.h'/'pyconfig-%{__isa_bits}.h'/" \
  %{buildroot}%{pylibdir}/distutils/sysconfig.py \
  %{buildroot}%{pylibdir}/sysconfig.py

# Install pathfix.py to bindir
# See https://github.com/fedora-python/python-rpm-porting/issues/24
cp -p Tools/scripts/pathfix.py %{buildroot}%{_bindir}/

# Install i18n tools to bindir
# They are also in python2, so we version them
# https://bugzilla.redhat.com/show_bug.cgi?id=1571474
for tool in pygettext msgfmt; do
  cp -p Tools/i18n/${tool}.py %{buildroot}%{_bindir}/${tool}%{pybasever}.py
  ln -s ${tool}%{pybasever}.py %{buildroot}%{_bindir}/${tool}3.py
done

# Switch all shebangs to refer to the specific Python version.
# This currently only covers files matching ^[a-zA-Z0-9_]+\.py$,
# so handle files named using other naming scheme separately.
LD_LIBRARY_PATH=./ ./python \
  Tools/scripts/pathfix.py \
  -i "%{_bindir}/python%{pybasever}" -pn \
  %{buildroot} \
  %{buildroot}%{_bindir}/*%{pybasever}.py \
  %{buildroot}%{_libdir}/python%{pybasever}/site-packages/pynche/pynche \
  %{?with_gdb_hooks:%{buildroot}$DirHoldingGdbPy/*.py}

# Remove shebang lines from .py files that aren't executable, and
# remove executability from .py files that don't have a shebang line:
find %{buildroot} -name \*.py \
  \( \( \! -perm /u+x,g+x,o+x -exec sed -e '/^#!/Q 0' -e 'Q 1' {} \; \
  -print -exec sed -i '1d' {} \; \) -o \( \
  -perm /u+x,g+x,o+x ! -exec grep -m 1 -q '^#!' {} \; \
  -exec chmod a-x {} \; \) \)

# Get rid of DOS batch files:
find %{buildroot} -name \*.bat -exec rm {} \;

# Get rid of backup files:
find %{buildroot}/ -name "*~" -exec rm -f {} \;
find . -name "*~" -exec rm -f {} \;

# Get rid of a stray copy of the license:
rm -f %{buildroot}%{pylibdir}/LICENSE.txt

# Do bytecompilation with the newly installed interpreter.
# This is similar to the script in macros.pybytecompile
# compile *.pyc
find %{buildroot}%{_libdir}/python%{pybasever} -type f -a -name "*.py" -print0 | \
    LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{_libdir}" \
    PYTHONPATH="%{buildroot}%{_libdir}/python%{pybasever} %{buildroot}%{_libdir}/python%{pybasever}/site-packages" \
    xargs -0 %{buildroot}%{_bindir}/python%{pybasever} -O -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("%{buildroot}")[2], optimize=opt) for opt in range(3) for f in sys.argv[1:]]' || :

# Since we have pathfix.py in bindir, this is created, but we don't want it
rm -rf %{buildroot}%{_bindir}/__pycache__

# Fixup permissions for shared libraries from non-standard 555 to standard 755:
find %{buildroot} -perm 555 -exec chmod 755 {} \;

# make man python3.Xm work https://bugzilla.redhat.com/show_bug.cgi?id=1612241
ln -s ./python%{pybasever}.1 %{buildroot}%{_mandir}/man1/python%{pybasever}m.1 

%if %{with tests}
%check
# (misc) if the home is nfs mounted, rmdir fails
export TMP="/tmp" TMPDIR="/tmp"

# Exclude some tests that hangs on the BS
EXCLUDE="test_ssl test_socket test_epoll"
%ifarch x86_64
EXCLUDE="$EXCLUDE test_faulthandler"
%endif
%ifarch %arm
EXCLUDE="$EXCLUDE test_float test_asyncio test_cmath"
%endif
# Local aarch64 tests succeeds, but fails on BS
%ifarch aarch64
EXCLUDE="$EXCLUDE test_posix test_asyncio test_openpty test_os test_pty test_readline"
%endif
# json test pass on local build but fail on BS
EXCLUDE="$EXCLUDE test_json"
# to investigate why it fails on local build
EXCLUDE="$EXCLUDE test_site"
# why this fails?
EXCLUDE="$EXCLUDE test_distutils"
# failing with 3.8RC1:
EXCLUDE="$EXCLUDE test___all__ test_embed test_mmap test_os"
# all tests must pass
# but we disable network on BS
WITHIN_PYTHON_RPM_BUILD= \
make test TESTOPTS="-wW --slowest -j0 -u none -x $EXCLUDE"
# consider use network on local build
#EXCLUDE=""
#WITHIN_PYTHON_RPM_BUILD= make test TESTOPTS="-u network -x $EXCLUDE"
%endif

%files
%{_bindir}/pathfix.py
%{_bindir}/pydoc
%{_bindir}/pydoc%{familyver}
%{_bindir}/pydoc%{pybasever}
%{_bindir}/python
%{_bindir}/python%{familyver}
%{_bindir}/python%{pybasever}
%{_bindir}/python%{LDVERSION_optimized}
%{_bindir}/2to3
%{_bindir}/2to3-%{pybasever}
%{_mandir}/man*/*

%files -n %{lib_name}-stdlib
%license LICENSE
%doc README.rst
%{_includedir}/python%{LDVERSION_optimized}/pyconfig-%{__isa_bits}.h
%{pylibdir}/config-%{LDVERSION_optimized}-%{_arch}-linux%{_gnu}/Makefile
%if "%{_lib}" == "lib64"
%dir %{_prefix}/lib/python%{pybasever}
%dir %{_prefix}/lib/python%{pybasever}/site-packages
%dir %{_prefix}/lib/python%{pybasever}/site-packages/__pycache__/
%endif
%dir %{pylibdir}
%dir %{dynload_dir}
%dir %{site_packages}
%dir %{site_packages}/__pycache__/
%{site_packages}/README.txt
%{pylibdir}/*.py
%dir %{pylibdir}/__pycache__/
%{pylibdir}/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/unittest/
%dir %{pylibdir}/unittest/__pycache__/
%{pylibdir}/unittest/*.py
%{pylibdir}/unittest/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/asyncio/
%dir %{pylibdir}/asyncio/__pycache__/
%{pylibdir}/asyncio/*.py
%{pylibdir}/asyncio/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/venv/
%dir %{pylibdir}/venv/__pycache__/
%{pylibdir}/venv/*.py
%{pylibdir}/venv/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/venv/scripts

%{pylibdir}/wsgiref
%{pylibdir}/xml
%{pylibdir}/xmlrpc

%dir %{pylibdir}/ensurepip/
%dir %{pylibdir}/ensurepip/__pycache__/
%{pylibdir}/ensurepip/*.py
%{pylibdir}/ensurepip/__pycache__/*%{bytecode_suffixes}

%if %{with rpmwheels}
%exclude %{pylibdir}/ensurepip/_bundled
%else
%dir %{pylibdir}/ensurepip/_bundled
%{pylibdir}/ensurepip/_bundled/*.whl
%endif

%dir %{pylibdir}/concurrent/
%dir %{pylibdir}/concurrent/__pycache__/
%{pylibdir}/concurrent/*.py
%{pylibdir}/concurrent/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/concurrent/futures/
%dir %{pylibdir}/concurrent/futures/__pycache__/
%{pylibdir}/concurrent/futures/*.py
%{pylibdir}/concurrent/futures/__pycache__/*%{bytecode_suffixes}

%{pylibdir}/pydoc_data

%dir %{pylibdir}/collections/
%dir %{pylibdir}/collections/__pycache__/
%{pylibdir}/collections/*.py
%{pylibdir}/collections/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/ctypes/
%dir %{pylibdir}/ctypes/__pycache__/
%{pylibdir}/ctypes/*.py
%{pylibdir}/ctypes/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/ctypes/macholib

%{pylibdir}/curses

%dir %{pylibdir}/dbm/
%dir %{pylibdir}/dbm/__pycache__/
%{pylibdir}/dbm/*.py
%{pylibdir}/dbm/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/distutils/
%dir %{pylibdir}/distutils/__pycache__/
%{pylibdir}/distutils/*.py
%{pylibdir}/distutils/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/distutils/README
%{pylibdir}/distutils/command

%dir %{pylibdir}/email/
%dir %{pylibdir}/email/__pycache__/
%{pylibdir}/email/*.py
%{pylibdir}/email/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/email/mime
%doc %{pylibdir}/email/architecture.rst

%{pylibdir}/encodings

%{pylibdir}/html
%{pylibdir}/http

%dir %{pylibdir}/importlib/
%dir %{pylibdir}/importlib/__pycache__/
%{pylibdir}/importlib/*.py
%{pylibdir}/importlib/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/json/
%dir %{pylibdir}/json/__pycache__/
%{pylibdir}/json/*.py
%{pylibdir}/json/__pycache__/*%{bytecode_suffixes}

%{pylibdir}/lib2to3
%exclude %{pylibdir}/lib2to3/tests

%{pylibdir}/logging
%{pylibdir}/multiprocessing

%dir %{pylibdir}/sqlite3/
%dir %{pylibdir}/sqlite3/__pycache__/
%{pylibdir}/sqlite3/*.py
%{pylibdir}/sqlite3/__pycache__/*%{bytecode_suffixes}

%exclude %{pylibdir}/turtle.py
%exclude %{pylibdir}/__pycache__/turtle*%{bytecode_suffixes}

%{pylibdir}/urllib

%{dynload_dir}/_bisect.%{SOABI_optimized}.so
%{dynload_dir}/_bz2.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_cn.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_hk.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_iso2022.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_jp.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_kr.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_tw.%{SOABI_optimized}.so
%{dynload_dir}/_contextvars.%{SOABI_optimized}.so
%{dynload_dir}/_crypt.%{SOABI_optimized}.so
%{dynload_dir}/_csv.%{SOABI_optimized}.so
%{dynload_dir}/_ctypes.%{SOABI_optimized}.so
%{dynload_dir}/_curses.%{SOABI_optimized}.so
%{dynload_dir}/_curses_panel.%{SOABI_optimized}.so
%{dynload_dir}/_dbm.%{SOABI_optimized}.so
%{dynload_dir}/_decimal.%{SOABI_optimized}.so
%{dynload_dir}/_elementtree.%{SOABI_optimized}.so
%{dynload_dir}/_gdbm.%{SOABI_optimized}.so
%{dynload_dir}/_hashlib.%{SOABI_optimized}.so
%{dynload_dir}/_heapq.%{SOABI_optimized}.so
%{dynload_dir}/_json.%{SOABI_optimized}.so
%{dynload_dir}/_lsprof.%{SOABI_optimized}.so
%{dynload_dir}/_lzma.%{SOABI_optimized}.so
%{dynload_dir}/_multibytecodec.%{SOABI_optimized}.so
%{dynload_dir}/_multiprocessing.%{SOABI_optimized}.so
%{dynload_dir}/_opcode.%{SOABI_optimized}.so
%{dynload_dir}/_pickle.%{SOABI_optimized}.so
%{dynload_dir}/_posixshmem.%{SOABI_optimized}.so
%{dynload_dir}/_posixsubprocess.%{SOABI_optimized}.so
%{dynload_dir}/_queue.%{SOABI_optimized}.so
%{dynload_dir}/_random.%{SOABI_optimized}.so
%{dynload_dir}/_socket.%{SOABI_optimized}.so
%{dynload_dir}/_sqlite3.%{SOABI_optimized}.so
%{dynload_dir}/_statistics.%{SOABI_optimized}.so
%{dynload_dir}/_ssl.%{SOABI_optimized}.so
%{dynload_dir}/_struct.%{SOABI_optimized}.so
%{dynload_dir}/_md5.%{SOABI_optimized}.so
%{dynload_dir}/_sha1.%{SOABI_optimized}.so
%{dynload_dir}/_sha256.%{SOABI_optimized}.so
%{dynload_dir}/_sha512.%{SOABI_optimized}.so
%{dynload_dir}/_xxsubinterpreters.%{SOABI_optimized}.so
%{dynload_dir}/array.%{SOABI_optimized}.so
%{dynload_dir}/audioop.%{SOABI_optimized}.so
%{dynload_dir}/binascii.%{SOABI_optimized}.so
%{dynload_dir}/cmath.%{SOABI_optimized}.so
%{dynload_dir}/_datetime.%{SOABI_optimized}.so
%{dynload_dir}/fcntl.%{SOABI_optimized}.so
%{dynload_dir}/grp.%{SOABI_optimized}.so
%{dynload_dir}/math.%{SOABI_optimized}.so
%{dynload_dir}/mmap.%{SOABI_optimized}.so
%{dynload_dir}/nis.%{SOABI_optimized}.so
%{dynload_dir}/ossaudiodev.%{SOABI_optimized}.so
%{dynload_dir}/parser.%{SOABI_optimized}.so
%{dynload_dir}/pyexpat.%{SOABI_optimized}.so
%{dynload_dir}/readline.%{SOABI_optimized}.so
%{dynload_dir}/resource.%{SOABI_optimized}.so
%{dynload_dir}/select.%{SOABI_optimized}.so
%{dynload_dir}/spwd.%{SOABI_optimized}.so
%{dynload_dir}/syslog.%{SOABI_optimized}.so
%{dynload_dir}/termios.%{SOABI_optimized}.so
%{dynload_dir}/unicodedata.%{SOABI_optimized}.so
%{dynload_dir}/_uuid.%{SOABI_optimized}.so
%{dynload_dir}/xxlimited.%{SOABI_optimized}.so
%{dynload_dir}/zlib.%{SOABI_optimized}.so
%{dynload_dir}/_asyncio.%{SOABI_optimized}.so
%{dynload_dir}/_blake2.%{SOABI_optimized}.so
%{dynload_dir}/_sha3.%{SOABI_optimized}.so

%files -n %{lib_name}-testsuite
%{pylibdir}/ctypes/test
%{pylibdir}/distutils/tests
%{pylibdir}/lib2to3/tests
%{pylibdir}/sqlite3/test
%{pylibdir}/test/
%{pylibdir}/unittest/test
# These two are shipped in the main subpackage:
%exclude %{pylibdir}/test/test_support.py*
%exclude %{pylibdir}/test/__init__.py*
%{dynload_dir}/_ctypes_test.%{SOABI_optimized}.so
%{dynload_dir}/_testcapi.%{SOABI_optimized}.so
%{dynload_dir}/_testbuffer.%{SOABI_optimized}.so
%{dynload_dir}/_testimportmultiple.%{SOABI_optimized}.so
%{dynload_dir}/_testinternalcapi.%{SOABI_optimized}.so
%{dynload_dir}/_testmultiphase.%{SOABI_optimized}.so
%{dynload_dir}/_xxtestfuzz.%{SOABI_optimized}.so

%files -n %{lib_name}
%{_libdir}/libpython%{LDVERSION_optimized}.so.1*

%files -n %{develname}
%{_bindir}/pygettext.py
%{_bindir}/pygettext%{familyver}*.py

%{_bindir}/msgfmt.py
%{_bindir}/msgfmt%{familyver}*.py

%{_bindir}/python-config
%{_bindir}/python%{pybasever}-config
%{_bindir}/python%{LDVERSION_optimized}-config
%{_bindir}/python%{familyver}-config

%{_libdir}/libpython%{LDVERSION_optimized}.so
%{_libdir}/libpython%{pybasever}.so
%{_libdir}/libpython%{familyver}.so
%{_includedir}/python%{LDVERSION_optimized}
%exclude %{_includedir}/python%{LDVERSION_optimized}/pyconfig-%{__isa_bits}.h
%{pylibdir}/config-%{LDVERSION_optimized}-%{_arch}-linux%{_gnu}
%{_libdir}/pkgconfig/python.pc
%{_libdir}/pkgconfig/python-%{LDVERSION_optimized}.pc
%{_libdir}/pkgconfig/python-%{pybasever}{,-embed}.pc
%{_libdir}/pkgconfig/python%{familyver}{,-embed}.pc

%exclude %{pylibdir}/config-%{LDVERSION_optimized}-%{_arch}-linux%{_gnu}/Makefile
%if %{with valgrind}
%{_libdir}/valgrind/valgrind-python3.supp
%endif

%files docs
%doc html/*/*
%{_datadir}/applications/%{_real_vendor}-%{name}-docs.desktop

%files -n tkinter3
%{pylibdir}/tkinter/
%{dynload_dir}/_tkinter.%{SOABI_optimized}.so
%{pylibdir}/idlelib
%{site_packages}/pynche
%{pylibdir}/turtle.py
%{pylibdir}/__pycache__/turtle*%{bytecode_suffixes}
%dir %{pylibdir}/turtledemo
%{pylibdir}/turtledemo/*.py
%{pylibdir}/turtledemo/*.cfg
%dir %{pylibdir}/turtledemo/__pycache__/
%{pylibdir}/turtledemo/__pycache__/*%{bytecode_suffixes}

%files -n tkinter3-apps
%{_bindir}/idle%{familyver}
%{_bindir}/idle%{pybasever}
%{_bindir}/pynche%{familyver}
%{_datadir}/applications/%{_real_vendor}-tkinter3.desktop

# We put the debug-gdb.py file inside /usr/lib/debug to avoid noise from ldconfig
# See https://bugzilla.redhat.com/show_bug.cgi?id=562980
#
# The /usr/lib/rpm/redhat/macros defines %%__debug_package to use
# debugfiles.list, and it appears that everything below /usr/lib/debug and
# (/usr/src/debug) gets added to this file (via LISTFILES) in
# /usr/lib/rpm/find-debuginfo.sh
#
# Hence by installing it below /usr/lib/debug we ensure it is added to the
# -debuginfo subpackage
# (if it doesn't, then the rpmbuild ought to fail since the debug-gdb.py
# payload file would be unpackaged)

# Workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1476593
%undefine _debuginfo_subpackages
