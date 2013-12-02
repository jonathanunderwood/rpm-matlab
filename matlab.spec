# Don't generate any debuginfo packages
%global debug_package %{nil}


# Post install checking of installed files is determined by three variables:
#
# __arch_install_post
# __os_install_post
# __spec_install_post
#
# each of which can be examined with rpm --eval %var. The last one
# is the catenation of the first two.
#
# At the least we want to disable rpath checking with
#
# define __arch_install_post /usr/lib/rpm/check-buildroot
#
# which keeps the check for occurences of $RPM_BUILD_ROOT in scripts -
# useful to do this sometimes, but very time consuming
#
%define __arch_install_post %{nil}
%define __os_install_post %{nil}

# Disable automatic dependency and provides information
%define __find_provides %{nil} 
%define __find_requires %{nil} 
%define _use_internal_dependency_generator 0
Autoprov: 0
Autoreq: 0

Name:           matlab
Version:        2012b
Release:        1%{?dist}
Summary:        A high-level technical computing language and environment

Group:          Applications/Engineering
License:        Proprietary
URL:            http://www.mathworks.com

# Source0-3 are the tarred and split contents of the install CD iso by
# eg.
#
# mkdir ~/matlab
# mount -t iso9660 -o loop R2012b_UNIX.iso /mnt
# cd /mnt
# tar -cvf ~/matlab/matlab-2012b.tar .
# cd ~/matlab
# split -b 2G matlab-2012b.tar matlab-2012.tar-part
#
# It's necessary to split the tar archive up as the largest file that
# can be handled by rpm is 4G
#
# Also, it's now necessary to split the binary packages into several
# sub-packages - trying to place all files in the main package results
# in a rpm header greater than 16 MB in size due to the large number
# of files, and rpm gives up. See:
#
# https://bugzilla.redhat.com/show_bug.cgi?id=913099
#
# So, we split out the help and toolbox files into separate
# sub-packages and create tight (circular) dependencies between these
# packages and the main package to ensure they're all upgraded
# together.
Source0:        matlab-%{version}.tar-partaa
Source1:        matlab-%{version}.tar-partab
Source2:        matlab-%{version}.tar-partac

# This file contains the network license server details
Source10:       network.lic

# This file needs to contain the file installation key on one line only
Source11:	install.key

# Icon file
Source20:       matlab.png

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  hicolor-icon-theme
BuildRequires:  desktop-file-utils
BuildRequires:	ImageMagick

Requires:      %{name}-help = %{version}-%release
Requires:      %{name}-toolbox = %{version}-%release

%description
MATLAB is a high-level language and interactive environment that
enables you to perform computationally intensive tasks faster than
with traditional programming languages such as C, C++, and Fortran.

%package help
Summary:        Help files for MATLAB
Requires:	matlab = %{version}-%{release}

%description help
Help files for MATLAB.

%package toolbox
Summary:        Toolbox files for MATLAB
Requires:	matlab = %{version}-%{release}

%description toolbox
MATLAB bundled toolboxes

%prep
%setup -T -c %{name}-%{version}

cat %SOURCE0 %SOURCE1 %SOURCE2 > matlab.tar
tar -xf matlab.tar
chmod -Rf a+rX,u+w,g-w,o-w .
cp -a %SOURCE10 .

%define destdir /opt/MATLAB/R%{version}

%define installkey %(cat %SOURCE11)

cat > answerfile.txt <<EOF
destinationFolder=${RPM_BUILD_ROOT}/%{destdir}
fileInstallationKey=%{installkey}
agreeToLicense=yes
outputFile=matlab_install.log
mode=silent
licensePath=./network.lic
EOF

%build
# Nothing to do - binary distribution


%install
rm -rf $RPM_BUILD_ROOT
./install -inputFile ./answerfile.txt

install -d $RPM_BUILD_ROOT%{_sysconfdir}/profile.d

cat > $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/matlab.sh<<EOF
export PATH=\$PATH:%{destdir}/bin
EOF

# desktop file
install -d $RPM_BUILD_ROOT%{_datadir}/applications

cat > $RPM_BUILD_ROOT%{_datadir}/applications/matlab%{version}.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MATLAB %{version}
Comment=Technical Computing System
Exec=%{destdir}/bin/matlab -desktop
Icon=matlab
Categories=Development;
EOF

desktop-file-validate $RPM_BUILD_ROOT%{_datadir}/applications/matlab%{version}.desktop

# Icons
for i in "32" "64" "128" ; do
    install -d $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps
    convert -resize ${i}x${i} %SOURCE20 $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/matlab.png
done

%clean
rm -rf $RPM_BUILD_ROOT

%post
# Update icon cache with new icons
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
# Update icon cache to reflect removed icons
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
# Update icon cache to reflect removed icons
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%defattr(-,root,root,-)
%{destdir}
%exclude %{destdir}/help
%exclude %{destdir}/toolbox
%{_sysconfdir}/profile.d/*
%{_datadir}/applications/matlab%{version}.desktop
%{_datadir}/icons/hicolor/32x32/apps/*
%{_datadir}/icons/hicolor/64x64/apps/*
%{_datadir}/icons/hicolor/128x128/apps/*

%files help
%{destdir}/help

%files toolbox
%{destdir}/toolbox

%changelog
* Thu Feb 21 2013 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 2012b-1
- Update to version 2012b
- Add icons and desktop file
- Split package up so as not to overrun internal rpm header limit
- Split source tarball up

* Tue Jun 19 2012 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 2012a-3
- Update to version 2012a

