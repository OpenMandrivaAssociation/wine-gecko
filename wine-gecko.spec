%define name	wine-gecko
%define oname	wine-mozilla
%define version	1.4

%define mingw64_snap	4705
%define binutils_version 2.22
%define gcc_version 4.6.3

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
Release:	%mkrel 1
Group:		Emulators
License:	MPLv1.1
URL:		http://wiki.winehq.org/Gecko
Source:		http://downloads.sourceforge.net/wine/%{oname}-%{version}-src.tar.bz2
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
ExclusiveArch:	%ix86 x86_64
Requires:	wine32
BuildRequires:	autoconf2.1
BuildRequires:	zip
BuildRequires:	glib2-devel
BuildRequires:	libIDL-devel
BuildRequires:	x11-proto-devel
BuildRequires:	yasm
# for msi package generation
BuildRequires:	wine-bin
# for gcc
BuildRequires:	gmp-devel
BuildRequires:	mpfr-devel
BuildRequires:	libmpc-devel
# for propvarutil.h hack below
BuildRequires:	libwine-devel

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
%make all-gcc
%make install-gcc
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
# as per wine/README, fixes build
echo "#include_next <float.h>" >> $(echo $builddir/mingw-sysroot/lib/gcc/*/*/include/float.h)
cd ..

%ifarch x86_64
ln -s %{_bindir}/wine64 $builddir/mingw-sysroot/bin/wine
%endif

# (anssi) another hack, this seems to be missing from mingw so we grab it from
# wine - fixes build
[ "$(find -name propvarutil.h)" ] && echo "remove this hack" && exit 1
ln -s %{_includedir}/wine/windows/propvarutil.h $builddir/mingw-sysroot/mingw/include

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


%changelog

* Thu Aug 16 2012 dams <dams> 1.4-1.mga2
+ Revision: 281675
- update to 1.4 to fix compatibility with wine 1.4.1

  + anssi <anssi>
    - new version (resolves mga bug #3783)
    - update toolchain to match upstream (also fixes build)
    - use parallel make for gcc core
    - use float.h hack from wine/README to fix build
    - use propvarutil.h from wine-devel to fix build
    - update .spec comments

* Fri Sep 09 2011 anssi <anssi> 1.3-1.mga2
+ Revision: 141685
- new version 1.3
- add buildrequire on now required yasm

* Mon May 09 2011 anssi <anssi> 1.2.0-1.mga1
+ Revision: 96591
- update mingw-w64 headers and crt to recent snapshots (needed to fix build)
- bundle upstream recommended versions of gcc and binutils and build them
  against mingw-w64 headers for now (needed to fix build)
- enable x86_64 build (wine64-gecko) now, it works with the bundled
  toolchain
- drop now unneeded buildrequires on lcab, instead buildrequire wine-bin
- remove now unneeded mozilla build workaround
- workaround cross compilation misdetection in mozilla/nsprpub configure

  + ahmad <ahmad>
    - Update to 1.2.0

* Thu Mar 10 2011 ahmad <ahmad> 1.1.0-2.mga1
+ Revision: 67279
- imported package wine-gecko


* Sun Oct 10 2010 Anssi Hannula <anssi@mandriva.org> 1.1.0-1mdv2011.0
+ Revision: 584505
- new version
- build from sources (with bundled mingw-w64 crt+headers)

* Mon Dec 14 2009 Anssi Hannula <anssi@mandriva.org> 1.0.0-1mdv2011.0
+ Revision: 478585
- initial Mandriva release

