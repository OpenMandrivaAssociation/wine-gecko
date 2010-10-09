
%define name	wine-gecko
%define oname	wine-mozilla
%define version	1.1.0
%define rel	1

# random working revision from mingw-w64 trunk:
%define mingw64_snap	2847
# not working due to various errors:
# - 3272 (crt build failure)
# - 3500 (redefinition of UINT8 while building mozilla)
# - 3713 (crt build failure)

# See:
# http://wiki.winehq.org/Gecko
# http://wiki.winehq.org/BuildingWineGecko

# We bundle custom versions of mingw64 headers and crt here because
# wine-gecko does not currently build with those from our system mingw32.

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
BuildRoot:	%{_tmppath}/%{name}-root
# We would need a mingw64 crosscompiler for a 64-bit binary.
# NOTE: building this package as-is on x86_64 will build a 32-bit binary instead.
ExclusiveArch:	%ix86
Requires:	wine32
BuildRequires:	mingw32-gcc
BuildRequires:	mingw32-gcc-c++
BuildRequires:	autoconf2.1
BuildRequires:	zip
BuildRequires:	glib2-devel
BuildRequires:	libIDL-devel
BuildRequires:	x11-proto-devel
# lcab creates cabs without compression, but it is better than nothing
BuildRequires:	lcab

%description
A custom version of Mozilla's Gecko Layout Engine for Wine. This package
is needed when running such Windows applications in Wine that display web
pages using embedded IE.

%prep
%setup -q -c -a1 -a2

%build
# disabled as build fails due to various issues if set:
# %%_mingw32_env

builddir=$PWD
mkdir -p mingw-headers-build mingw-crt-build
cd mingw-headers-build
../mingw-w64-headers/configure --host=%_mingw32_host --prefix=$builddir/mingw-sysroot --enable-sdk=all
%make install
ln -s %_mingw32_host $builddir/mingw-sysroot/mingw
cd ..

OVERRIDE_FLAGS="--sysroot=$builddir/mingw-sysroot"
export CC="%_mingw32_cc $OVERRIDE_FLAGS"
export CXX="%_mingw32_cxx $OVERRIDE_FLAGS"

cd mingw-crt-build
../mingw-w64-crt/configure --host=%_mingw32_host --prefix=$builddir/mingw-sysroot
%make
%make install
cd ..

# Something strange happens here. Mozilla configure will detect this as true,
# but the relevant code using __stdcall will fail to compile anyway (even if
# the test in configure compiled fine). - Anssi 10/2010
export ac_cv___stdcall=false

cd wine-mozilla
cp -af wine/mozconfig wine/mozconfig-mdv
echo "ac_add_options --target=%_mingw32_host" >> wine/mozconfig-mdv
export MOZCONFIG=$PWD/wine/mozconfig-mdv

%make -f client.mk build
wine/make_package ../wine_gecko
cd ../wine_gecko/dist

lcab -r wine_gecko ../../wine_gecko-%{version}-x86.cab

%install
rm -rf %{buildroot}
install -d -m755 %{buildroot}%{_datadir}/wine/gecko
install -m644 wine_gecko-%{version}-x86.cab %{buildroot}%{_datadir}/wine/gecko

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc wine-mozilla/LEGAL
%doc wine-mozilla/LICENSE
%doc wine-mozilla/toolkit/content/license.html
%dir %{_datadir}/wine/gecko
%{_datadir}/wine/gecko/*.cab
