
%define name	wine-gecko
%define oname	wine_gecko
%define version	1.0.0
%define rel	1

# See:
# http://wiki.winehq.org/Gecko
# http://wiki.winehq.org/BuildingWineGecko
#
# It is not yet possible (or at least no one has succeeded) to rebuild
# this package cleanly from source on a linux system. As per advise from
# CodeWeavers, we use the prebuilt binary for now.

Summary:	HTML engine for Wine based on Gecko
Name:		%{name}
Version:	%{version}
Release:	%mkrel %{rel}
Group:		Emulators
License:	MPLv1.1
URL:		http://wiki.winehq.org/Gecko
Source:		http://downloads.sourceforge.net/wine/%{oname}-%{version}-x86.cab
ExclusiveArch:	%ix86
Requires:	wine

%description
A custom version of Mozilla's Gecko Layout Engine for Wine. This package
is needed when running such Windows applications in Wine that display web
pages using embedded IE.

This package is in non-free repository because it uses prebuilt binaries
from the Wine project.

%install
rm -rf %{buildroot}
install -d -m755 %{buildroot}%{_datadir}/wine/gecko
install -m644 %{SOURCE0} %{buildroot}%{_datadir}/wine/gecko/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%dir %{_datadir}/wine/gecko
%{_datadir}/wine/gecko/*.cab
