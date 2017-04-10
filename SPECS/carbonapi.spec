%define carbon_user carbon
%define carbon_group carbon
%define carbon_loggroup adm

%global commit             1443a4759dd1a80776348fa9738d98d7a697577a
%global shortcommit        %(c=%{commit}; echo ${c:0:7})

Name:	        carbonapi
Version:	0.7.0
Release:	0.1.git%{shortcommit}%{?dist}
Summary:	API server for carbonzipper or built-in carbonserver in go-carbon

Group:		Development/Tools
License:	BSD-2-Clause License
URL:		https://github.com/lomik/carbonapi

# NOTE: We use "git clone" in %prep instead of having tarball here
# since we need .git directory to use "go get ./..." to build carbonapi.
#Source0:	https://github.com/dgryski/carbonapi/archive/%{commit}.tar.gz#/%{name}-%{commit}.tar.gz

Source1:	carbonapi.yaml
Source2:	carbonapi.service

# NOTE: We do not use logrotate yet. We plan to use logrotate with graceful restart
# of carbonapi with https://github.com/lestrrat/go-server-starter.
# To achieve this, we must first implement graceful shutdown in carbonapi.
#Source3:	logrotate

BuildRequires:  golang >= 1.8
BuildRequires:  git

%description
CarbonAPI supports a significant subset of graphite functions. In our testing it has shown to be
5x-10x faster than requesting data from graphite-web.

%prep
%{__rm} -rf %{_builddir}

# NOTE: To use go "get ./..." to install dependencies,
# we need .git directory in carbonapi source directory.
%{__mkdir} -p %{_builddir}/%{name}/go/src/github.com/dgryski
cd %{_builddir}/%{name}/go/src/github.com/dgryski
git clone https://github.com/dgryski/%{name}
cd %{_builddir}/%{name}/go/src/github.com/dgryski/%{name}
git checkout %{commit}

%build
export GOPATH=%{_builddir}/%{name}/go
cd %{_builddir}/%{name}/go/src/github.com/dgryski/%{name}
go get ./...

%install
%{__rm} -rf %{buildroot}
%{__mkdir} -p %{buildroot}%{_sbindir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}

%{__install} -pD -m 755 %{_builddir}/%{name}/go/bin/%{name} \
    %{buildroot}%{_sbindir}/%{name}
%{__install} -pD -m 644 %{SOURCE1} %{buildroot}/%{_sysconfdir}/%{name}.yaml
%{__install} -pD -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service

%files
%defattr(-,root,root,-)
%{_sbindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.yaml
%attr(0755,root,root) %dir %{_localstatedir}/log/%{name}
%{_unitdir}/%{name}.service

%pre
# Add the "carbon" user
getent group %{carbon_group} >/dev/null || groupadd -r %{carbon_group}
getent passwd %{carbon_user} >/dev/null || \
    useradd -r -g %{carbon_group} -s /sbin/nologin \
    --no-create-home -c "carbon user"  %{carbon_user}
exit 0

%post
%systemd_post %{name}.service
if [ $1 -eq 1 ]; then
    # Touch and set permisions on default log files on installation

    if [ -d %{_localstatedir}/log/%{name} ]; then
        if [ ! -e %{_localstatedir}/log/%{name}/%{name}.log ]; then
            touch %{_localstatedir}/log/%{name}/%{name}.log
            %{__chmod} 640 %{_localstatedir}/log/%{name}/%{name}.log
            %{__chown} %{carbon_user}:%{carbon_loggroup} %{_localstatedir}/log/%{name}/%{name}.log
        fi
    fi
fi

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun

%changelog
* Mon Apr 10 2017 <hnakamur@gmail.com> - 0.7.0-0.1.git1443a47
- Initial release
