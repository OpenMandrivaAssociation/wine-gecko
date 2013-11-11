%define	debug_package	%nil
%define name	wine-gecko
%define oname	wine-mozilla
%define version	2.24
%define rel	1

%define mingw64_snap	5421
%define binutils_version 2.23.2
%define gcc_version linaro-4.7-2012.10

# See:
# http://wiki.winehq.org/Gecko
# http://wiki.winehq.org/BuildingWineGecko

# Building instructions and upstream-used toolchain versions are detailed in
# wine/README file inside the source tarball.

%ifarch x86_64
%define mingw_host x86_64-w64-mingw32
%else
%define mingw_host i686-w64-mingw32
%endif

# We bundle custom versions of mingw64 headers and crt here because
# wine-gecko does not currently build with those from our system mingw32.
# Addendum: We also bundle the recommended versions of gcc and binutils as it
# doesn't build with our system ones, plus this allows 64-bit build as well.
# Build instructions from upstream README are followed.
# TODO: Investigate if the system mingw toolchain could be switched to
# ming64 to accommodate wine-gecko.

Summary:	HTML engine for Wine based on Gecko
Name:		%{name}
Version:	%{version}
Release:	%{rel}
Group:		Emulators
License:	MPLv1.1
URL:		http://wiki.winehq.org/Gecko
Source0:	http://downloads.sourceforge.net/wine/%{oname}-%{version}-src.tar.bz2
# URL=http://mingw-w64.svn.sourceforge.net/svnroot/mingw-w64/trunk
# REV=$(svn info $URL | sed -n 's,^Last Changed Rev: ,,p')
# rm -rf mingw-w64-crt mingw-w64-headers
# svn export -r $REV $URL/mingw-w64-crt
# svn export -r $REV $URL/mingw-w64-headers
# tar -cjf mingw-w64-crt-svn$REV.tar.bz2 mingw-w64-crt
# tar -cjf mingw-w64-headers-svn$REV.tar.bz2 mingw-w64-headers
Source1:	mingw-w64-headers-svn%mingw64_snap.tar.bz2
Source2:	mingw-w64-crt-svn%mingw64_snap.tar.bz2
# This is officially overkill:
Source3:	http://ftp.gnu.org/gnu/binutils/binutils-%{binutils_version}.tar.bz2
Source4:	http://gcc.fyxm.net/releases/gcc-%{gcc_version}/gcc-%{gcc_version}.tar.bz2
# Fix mozilla build with mga multiarch (patch by cjw)
Patch0:		iceape-2.12-system-virtualenv.patch
ExclusiveArch:	%ix86 x86_64
Requires:	wine32
BuildRequires:	autoconf2.1
BuildRequires:	zip
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	libIDL-devel
BuildRequires:	x11-proto-devel
BuildRequires:	yasm
BuildRequires:	texinfo
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	python-setuptools
BuildRequires:	python-virtualenv

# for msi package generation
BuildRequires:	wine-bin
# for gcc
BuildRequires:	gmp-devel
BuildRequires:	mpfr-devel
BuildRequires:	libmpc-devel

%description
A custom version of Mozilla's Gecko Layout Engine for Wine. This package
is needed when running such Windows applications in Wine that display web
pages using embedded IE.

%ifarch x86_64
%package -n wine64-gecko
Summary:	HTML engine for 64-bit Wine based on Gecko
Group:		Emulators
Requires:	wine64

%description -n wine64-gecko
A custom version of Mozilla's Gecko Layout Engine for Wine. This package
is needed when running such Windows applications in Wine that display web
pages using embedded IE.

This package is for use with 64-bit wine64.
%endif

%prep
%setup -q -c -a1 -a2 -a3 -a4
ln -s wine-mozilla-%version wine-mozilla

cd wine-mozilla
#patch0 -p2
cd ..

# NOTE: any deviations from wine/README below are only there to make the
# package build successfully. If something seems to be unnecessary, it is ok
# to drop it.

%ifarch %ix86
# Fixes build - for some strange reason the detection fails here:
sed -i 's,cross_compiling=.*$,cross_compiling=yes,' wine-mozilla/nsprpub/configure
%endif

%build
builddir=$PWD

cd wine-mozilla
# for virtualenv patch
autoconf-2.13
cd ..

mkdir -p binutils-build gcc-build
mkdir -p mingw-headers-build mingw-crt-build

# Per Fedora mingw
export CFLAGS="-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions --param=ssp-buffer-size=4"
export CXXFLAGS="$CFLAGS"

# Make sure nothing leaks outside build dir:
export WINEPREFIX="$builddir/wine-prefix"

sed -i -e 's/@colophon/@@colophon/' \
       -e 's/doc@cygnus.com/doc@@cygnus.com/' binutils-%{binutils_version}/bfd/doc/bfd.texinfo

cd binutils-build
../binutils-%{binutils_version}/configure --prefix=$builddir/mingw-sysroot --target=%mingw_host --disable-multilib
%make
%make install
cd ..

cd mingw-headers-build
../mingw-w64-headers/configure --host=%mingw_host --prefix=$builddir/mingw-sysroot/%mingw_host --enable-sdk=all --enable-secure-api
%make install
ln -s %mingw_host $builddir/mingw-sysroot/mingw
cd ..

cd gcc-build
../gcc-%{gcc_version}/configure --prefix=$builddir/mingw-sysroot --target=%mingw_host --with-gnu-ld --with-gnu-as --enable-__cxa_atexit --enable-languages=c,c++ --disable-multilib
%make all-gcc
%make install-gcc
cd ..

export PATH=$builddir/mingw-sysroot/bin:$PATH

cd mingw-crt-build
../mingw-w64-crt/configure --host=%mingw_host --prefix=$builddir/mingw-sysroot/%mingw_host
%make
%make install
cd ..

cd gcc-build
%make
%make install
cd ..

%ifarch x86_64
ln -s %{_bindir}/wine64 $builddir/mingw-sysroot/bin/wine
%endif

cd wine-mozilla
MAKEOPTS="%_smp_mflags" wine/make_package \
%ifarch x86_64
	-win64
%else
	-win32
%endif

%install
install -d -m755 %{buildroot}%{_datadir}/wine/gecko
install -m644 wine_gecko-*/dist/wine_gecko-%{version}-*.msi %{buildroot}%{_datadir}/wine/gecko

%ifarch x86_64
%files -n wine64-gecko
%else
%files
%endif
%doc wine-mozilla/LEGAL
%doc wine-mozilla/LICENSE
%doc wine-mozilla/toolkit/content/license.html
%dir %{_datadir}/wine/gecko
%{_datadir}/wine/gecko/*.msi
