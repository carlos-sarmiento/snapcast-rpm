Name: snapcast
Version:        0.29.0
Release:        %autorelease
License:        GPL-3.0
Group:          Productivity/Multimedia/Sound/Players
Summary:        Snapcast is a multi-room time-synced client-server audio player
Url:            https://github.com/badaix/%{name}
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  alsa-lib-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  avahi-devel
BuildRequires:  libvorbis-devel
BuildRequires:  flac-devel
BuildRequires:  boost-devel >= 1.74
BuildRequires:  opus-devel
BuildRequires:  soxr-devel
BuildRequires:  zlib-devel
Requires(pre):  pwdutils
BuildRequires:  systemd
BuildRequires:  systemd-rpm-macros

%description
Snapcast is a multi-room client-server audio player, where all clients are time synchronized with the server to play perfectly synced audio. It is not a standalone player, but an extension that turns your existing audio player into a Sonos-like multi-room solution. The server's audio input is a named pipe /tmp/snapfifo. All data that is fed into this file will be send to the connected clients. One of the most generic ways to use Snapcast is in conjunction with the music player daemon (MPD) or Mopidy, which can be configured to use a named pipe as audio output.

%package -n snapserver
Summary:        Snapcast server

%description -n snapserver
Snapcast is a multi-room client-server audio player, where all clients are
time synchronized with the server to play perfectly synced audio. It's not a
standalone player, but an extension that turns your existing audio player into
a Sonos-like multi-room solution.  The server's audio input is a named
pipe `/tmp/snapfifo`. All data that is fed into this file will be send to
the connected clients. One of the most generic ways to use Snapcast is in
conjunction with the music player daemon, MPD, or Mopidy, which can be configured
to use a named pipe as audio output.
This package contains the server to which clients connect.

%package -n snapclient
Summary:        Snapcast client

%description -n snapclient
Snapcast is a multi-room client-server audio player, where all clients are
time synchronized with the server to play perfectly synced audio. It's not a
standalone player, but an extension that turns your existing audio player into
a Sonos-like multi-room solution.
This package contains the client which connects to the server and plays the audio.

%prep
%autosetup -p1

%build
%cmake -GNinja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DWERROR=ON -DBUILD_TESTS=OFF
%cmake_build

%install
%cmake_install

chmod 755 %{buildroot}%{_datadir}/snapserver/plug-ins/meta_mpd.py
install -D -m 0644 extras/package/rpm/snapclient.service %{buildroot}%{_unitdir}/snapclient.service
install -D -m 0644 extras/package/rpm/snapserver.service %{buildroot}%{_unitdir}/snapserver.service
install -D -m 0644 extras/package/rpm/snapserver.default %{buildroot}/etc/default/snapserver.default
install -D -m 0644 extras/package/rpm/snapclient.default %{buildroot}/etc/default/snapclient.default

%pre -n snapclient
getent passwd snapclient >/dev/null || %{_sbindir}/useradd --user-group --system --groups audio snapclient

%pre -n snapserver
mkdir -p %{_sharedstatedir}/snapserver
getent passwd snapserver >/dev/null || %{_sbindir}/useradd --user-group --system --home-dir %{_sharedstatedir}/snapserver snapserver
chown snapserver %{_sharedstatedir}/snapserver
chgrp snapserver %{_sharedstatedir}/snapserver

%post -n snapclient
%systemd_post snapclient.service

%post -n snapserver
%systemd_post snapserver.service

%preun -n snapclient
%systemd_preun snapclient.service

%preun -n snapserver
%systemd_preun snapserver.service

%postun -n snapclient
%systemd_postun_with_restart snapclient.service
if [ $1 -eq 0 ]; then
   userdel --force snapclient 2> /dev/null; true
fi

%postun -n snapserver
%systemd_postun_with_restart snapserver.service

%files -n snapserver
%{_bindir}/snapserver
%{_datadir}
%config(noreplace) /usr/etc/snapserver.conf
%config(noreplace) /etc/default/snapserver.default
%{_unitdir}/snapserver.service

%files -n snapclient
%{_bindir}/snapclient
%{_mandir}/man1/snapclient.1.*
%config(noreplace) /etc/default/snapclient.default
%{_unitdir}/snapclient.service

%changelog
%autochangelog
