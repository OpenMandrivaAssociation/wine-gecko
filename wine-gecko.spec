
%define name	wine-gecko
%define oname	wine-mozilla
%define version	1.2.0
%define rel	1

# random working revision from mingw-w64 trunk:
%define mingw64_snap	4156
# not working due to various errors:
# - 2847 ('swprintf_s' was not declared in this scope" while building mozilla)
# - 3272 (crt build failure)
# - 3500 (redefinition of UINT8 while building mozilla)
# - 3713 (crt build failure)

%define binutils_version 2.21
%define gcc_version 4.5.2

# See:
# http://wiki.winehq.org/Gecko
# http://wiki.winehq.org/BuildingWineGecko

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
Release:	%mkrel %{rel}
Group:		Emulators
License:	MPLv1.1
URL:		http://wiki.winehq.org/Gecko
Source:		http://downloads.sourceforge.net/wine/%{oname}-%{version}-src.tar.bz2
# https://mingw-w64.svn.sourceforge.net/svnroot/mingw-w64/trunk
Source1:	mingw-w64-headers-svn%mingw64_snap.tar.bz2
Source2:	mingw-w64-crt-svn%mingw64_snap.tar.bz2
# This is officially overkill:
Source3:	http://ftp.gnu.org/gnu/binutils/binutils-%{binutils_version}.tar.bz2
Source4:	http://gcc.fyxm.net/releases/gcc-%{gcc_version}/gcc-%{gcc_version}.tar.bz2
ExclusiveArch:	%ix86 x86_64
Requires:	wine32
BuildRequires:	autoconf2.1
BuildRequires:	zip
BuildRequires:	glib2-devel
BuildRequires:	libIDL-devel
BuildRequires:	x11-proto-devel
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

%ifarch %ix86
# Fixes build - for some strange reason the detection fails here:
sed -i 's,cross_compiling=.*$,cross_compiling=yes,' wine-mozilla/nsprpub/configure
%endif

%build
builddir=$PWD
mkdir -p binutils-build gcc-build
mkdir -p mingw-headers-build mingw-crt-build

cd binutils-build
../binutils-%{binutils_version}/configure --prefix=$builddir/mingw-sysroot --target=%mingw_host
%make
%make install
cd ..

cd mingw-headers-build
../mingw-w64-headers/configure --host=%mingw_host --prefix=$builddir/mingw-sysroot --enable-sdk=all --enable-secure-api
%make install
ln -s %mingw_host $builddir/mingw-sysroot/mingw
cd ..

cd gcc-build
../gcc-%{gcc_version}/configure --prefix=$builddir/mingw-sysroot --target=%mingw_host --with-gnu-ld --with-gnu-as --enable-__cxa_atexit --enable-languages=c,c++ --disable-multilib
make all-gcc
make install-gcc
cd ..

export PATH=$builddir/mingw-sysroot/bin:$PATH

cd mingw-crt-build
../mingw-w64-crt/configure --host=%mingw_host --prefix=$builddir/mingw-sysroot
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
wine/make_package \
%ifarch x86_64
	-win64
%else
	-win32
%endif

%install
rm -rf %{buildroot}
install -d -m755 %{buildroot}%{_datadir}/wine/gecko
install -m644 wine_gecko-*/dist/wine_gecko-%{version}-*.msi %{buildroot}%{_datadir}/wine/gecko

%clean
rm -rf %{buildroot}

%ifarch x86_64
%files -n wine64-gecko
%else
%files
%endif
%defattr(-,root,root)
%doc wine-mozilla/LEGAL
%doc wine-mozilla/LICENSE
%doc wine-mozilla/toolkit/content/license.html
%dir %{_datadir}/wine/gecko
%{_datadir}/wine/gecko/*.msi
