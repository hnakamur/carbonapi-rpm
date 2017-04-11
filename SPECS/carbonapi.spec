%define carbon_user carbon
%define carbon_group carbon
%define carbon_loggroup adm

%define debug_package %{nil}

%global commit             1a0d3f9ecd9e7bebcdd51795f38bb8d76182689d
%global shortcommit        %(c=%{commit}; echo ${c:0:7})

Name:	        carbonapi
Version:	0.7.0
Release:	0.5.git%{shortcommit}%{?dist}
Summary:	API server for carbonzipper or built-in carbonserver in go-carbon

Group:		Development/Tools
License:	BSD-2-Clause License
URL:		https://github.com/go-graphite/carbonapi

# NOTE: carbonapi.tar.gz was created with the following commands.
# NOTE: "go get -d ./..." is needed after "dep ensure" since
# "dep ensure" does not install all of dependencies currently for carbonapi.
#
# export GOPATH=$PWD/carbonapi/go
# mkdir -p carbonapi/go/src/github.com/go-graphite
# pushd $GOPATH/src/github.com/go-graphite
# git clone https://github.com/go-graphite/carbonapi
# cd carbonapi
# git checkout 1a0d3f9ecd9e7bebcdd51795f38bb8d76182689d
# dep ensure
# go get -d ./...
# popd
# rm -rf carbonapi/go/pkg
# find carbonapi/go/src -name .git -type d | xargs rm -rf
# tar zcf carbonapi.tar.gz carbonapi
Source0:	carbonapi.tar.gz

Source1:	carbonapi.yaml
Source2:	carbonapi.service
Source3:	logrotate

# NOTE: We do not use logrotate yet. We plan to use logrotate with graceful restart
# of carbonapi with https://github.com/lestrrat/go-server-starter.
# To achieve this, we must first implement graceful shutdown in carbonapi.
#Source3:	logrotate

BuildRequires:  golang >= 1.8
BuildRequires:  cairo-devel

%description
CarbonAPI supports a significant subset of graphite functions. In our testing it has shown to be
5x-10x faster than requesting data from graphite-web.

%prep
%setup -n %{name}

%build
export GOPATH=%{_builddir}/%{name}/go
cd %{_builddir}/%{name}/go/src/github.com/go-graphite/%{name}
go build

%install
%{__rm} -rf %{buildroot}
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir} -p %{buildroot}%{_localstatedir}/run/%{name}

%{__install} -pD -m 755 %{_builddir}/%{name}/go/src/github.com/go-graphite/%{name}/%{name} \
    %{buildroot}%{_sbindir}/%{name}
%{__install} -pD -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}.yaml
%{__install} -pD -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -pD -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%files
%defattr(-,root,root,-)
%{_sbindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.yaml
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %dir %{_localstatedir}/log/%{name}
%attr(0755,%{carbon_user},%{carbon_group}) %dir %{_localstatedir}/run/%{name}
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
* Tue Apr 11 2017 <hnakamur@gmail.com> - 0.7.0-0.5.git1a0d3f9
- Update repository URL of carbonapi in systemd unit file

* Tue Apr 11 2017 <hnakamur@gmail.com> - 0.7.0-0.4.git1a0d3f9
- Update to 1a0d3f9ecd9e7bebcdd51795f38bb8d76182689d

* Tue Apr 11 2017 <hnakamur@gmail.com> - 0.7.0-0.3.git1443a47
- Add logrotate

* Mon Apr 10 2017 <hnakamur@gmail.com> - 0.7.0-0.2.git1443a47
- Create pid file and enable graceful restart

* Mon Apr 10 2017 <hnakamur@gmail.com> - 0.7.0-0.1.git1443a47
- Initial release
