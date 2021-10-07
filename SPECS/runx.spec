Summary: runx - Run containers as VMs
Name:    runx
Version: 2021.1
Release: 1.0%{?dist}
License: ASL 1.0
URL:     https://github.com/xcp-ng/runx

Source0: runx-2021.1.tar.gz
Source1: linux-5.4.tar.xz
Source2: busybox-1.32.0.tar.bz2

BuildRequires: bc
BuildRequires: bison
BuildRequires: cpio
BuildRequires: elfutils-libelf-devel
BuildRequires: flex
BuildRequires: gcc
BuildRequires: glibc-static
BuildRequires: go
BuildRequires: make
BuildRequires: openssl-devel

Requires:      daemonize
Requires:      jq
Requires:      socat
Requires:      xen-dom0-tools

# XCP-ng patches
Patch1000: 0001-patch-pvcalls_enable.patch
Patch1001: runx-2021.1.0-xcp-ng-integration.XCP-ng.patch

%description
OCI Runtime Spec compliant containers runtime that runs containers as VMs.

%prep
%setup              # Extract and cd in runx dir.
%setup -q -a 1 -a 2 # Extract kernel and busybox in runx dir.
cd linux-5.4
%patch -P 1000 -p1
cd ..
%patch -P 1001 -p1

# WORKAROUND: We must force version of container/container-wrapper.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1626473
# Fixed in version 2.7.1-11 of "patch" command: https://centos.pkgs.org/7/centos-x86_64/patch-2.7.1-12.el7_7.x86_64.rpm.html
chmod 0755 files/container
chmod 0755 files/container-wrapper

%build
./build.sh --busybox-path busybox-1.32.0 --kernel-path linux-5.4

%install
mkdir -p %{buildroot}/{%{_sysconfdir},%{_bindir},%{_datadir}}
cp target/etc/runx.conf %{buildroot}/%{_sysconfdir}
cp target/usr/bin/runx %{buildroot}/%{_bindir}
cp -R target/usr/share/runx %{buildroot}/%{_datadir}

# Custom kernel must be located in /boot/guest folder (required by xapi).
mkdir -p %{buildroot}/boot/guest
ln -s %{_datadir}/runx %{buildroot}/boot/guest/runx

# Compatibility with docker and podman.
mkdir -p %{buildroot}/%{_sysconfdir}/containers
cp config/libpod.conf %{buildroot}/%{_sysconfdir}/containers/

mkdir -p %{buildroot}/%{_sysconfdir}/cni/net.d
cp config/99-podman-runx.conflist %{buildroot}/%{_sysconfdir}/cni/net.d/

ln -s %{_bindir}/runx %{buildroot}/%{_bindir}/docker-runc

%files
%config(noreplace) %{_sysconfdir}/runx.conf
%config(noreplace) %{_sysconfdir}/containers/libpod.conf
%config %{_sysconfdir}/cni/net.d/99-podman-runx.conflist
/boot/guest/runx
%{_bindir}/docker-runc
%{_bindir}/runx
%{_datadir}/runx/container
%{_datadir}/runx/container-wrapper
%{_datadir}/runx/create
%{_datadir}/runx/delete
%{_datadir}/runx/initrd
%{_datadir}/runx/kernel
%{_datadir}/runx/mount
%{_datadir}/runx/pause
%{_datadir}/runx/sendfd
%{_datadir}/runx/serial_start
%{_datadir}/runx/start
%{_datadir}/runx/state

%changelog
* Thu Oct 7 2021 Ronan Abhamon <ronan.abhamon@vates.fr> - 2021.1.0-1.0
- Inital runx beta
