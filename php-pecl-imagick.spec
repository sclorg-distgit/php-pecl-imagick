# centos/sclo spec file for php-pecl-imagick, from:
#
# remirepo spec file for php-pecl-imagick
#
# Copyright (c) 2008-2020 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%global sub_prefix sclo-%{scl_prefix}
%if "%{scl}" == "rh-php72"
%global sub_prefix sclo-php72-
%endif
%if "%{scl}" == "rh-php73"
%global sub_prefix sclo-php73-
%endif
%scl_package       php-pecl-imagick
%endif

%global pecl_name  imagick
%global ini_name   40-%{pecl_name}.ini

Summary:       Extension to create and modify images using ImageMagick
Name:          %{?sub_prefix}php-pecl-imagick
Version:       3.4.4
Release:       3%{?dist}
License:       PHP
Group:         Development/Languages
URL:           http://pecl.php.net/package/imagick
Source:        http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz

BuildRequires: %{?scl_prefix}php-devel
BuildRequires: %{?scl_prefix}php-pear
BuildRequires: pcre-devel
BuildRequires: ImageMagick-devel >= 6.5.3

Requires:      %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:      %{?scl_prefix}php(api) = %{php_core_api}

Provides:      %{?scl_prefix}php-%{pecl_name} = %{version}%{?prever}
Provides:      %{?scl_prefix}php-%{pecl_name}%{?_isa} = %{version}%{?prever}
Provides:      %{?scl_prefix}php-pecl(%{pecl_name}) = %{version}%{?prever}
Provides:      %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}%{?prever}
Provides:      %{?scl_prefix}php-pecl-%{pecl_name} = %{version}-%{release}
Provides:      %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa} = %{version}-%{release}
Conflicts:     %{?scl_prefix}php-pecl-gmagick

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
Imagick is a native php extension to create and modify images
using the ImageMagick API.

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%package devel
Summary:       %{pecl_name} extension developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      %{?scl_prefix}php-devel%{?_isa}
Provides:      %{?scl_prefix}php-pecl-%{pecl_name}-devel = %{version}-%{release}
Provides:      %{?scl_prefix}php-pecl-%{pecl_name}-devel%{?_isa} = %{version}-%{release}

%description devel
These are the files needed to compile programs using %{pecl_name} extension.


%prep
%setup -q -c

mv %{pecl_name}-%{version}%{?prever} NTS

# don't install any font (and test using it)
# don't install empty file (d41d8cd98f00b204e9800998ecf8427e)
sed -e '/anonymous_pro_minus.ttf/d' \
    -e '/015-imagickdrawsetresolution.phpt/d' \
    -e '/OFL.txt/d' \
    -i package.xml

if grep '\.ttf' package.xml
then : "Font files detected!"
     exit 1
fi

cd NTS

extver=$(sed -n '/#define PHP_IMAGICK_VERSION/{s/.* "//;s/".*$//;p}' php_imagick.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension = %{pecl_name}.so

; Documentation: http://php.net/imagick

; Don't check builtime and runtime versions of ImageMagick
imagick.skip_version_check=1

; Fixes a drawing bug with locales that use ',' as float separators.
;imagick.locale_fix=0

; Used to enable the image progress monitor.
;imagick.progress_monitor=0
EOF


%build
: Standard NTS build
cd NTS
%{_bindir}/phpize
%configure --with-imagick=%{prefix} --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
make install INSTALL_ROOT=%{buildroot} -C NTS

# Drop in the bit of configuration
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -p -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Test & Documentation
for i in $(grep 'role="test"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
# ========DIFF========
# 001+ php: unable to acquire cache view `No such file or directory' @ fatal/cache-view.c/AcquireAuthenticCacheView/121.
# 001- success
# See https://bugzilla.redhat.com/1228034
: ignore failed test with ImageMagick 6.7.8
rm ?TS/tests/bug20636.phpt
# ========DIFF======== (only minor size diff)
# 003+ x : 55
# 004+ y : 47
# 003- x : 50
# 004- y : 50
rm ?TS/tests/151_Imagick_subImageMatch_basic.phpt
# See https://bugzilla.redhat.com/1743658
rm ?TS/tests/034_Imagick_annotateImage_basic.phpt
rm ?TS/tests/177_ImagickDraw_composite_basic.phpt
rm ?TS/tests/206_ImagickDraw_setFontSize_basic.phpt
rm ?TS/tests/207_ImagickDraw_setFontFamily_basic.phpt
rm ?TS/tests/208_ImagickDraw_setFontStretch_basic.phpt
rm ?TS/tests/209_ImagickDraw_setFontWeight_basic.phpt
rm ?TS/tests/210_ImagickDraw_setFontStyle_basic.phpt
rm ?TS/tests/212_ImagickDraw_setGravity_basic.phpt
rm ?TS/tests/222_ImagickDraw_setTextAlignment_basic.phpt
rm ?TS/tests/223_ImagickDraw_setTextAntialias_basic.phpt
rm ?TS/tests/224_ImagickDraw_setTextUnderColor_basic.phpt
rm ?TS/tests/225_ImagickDraw_setTextDecoration_basic.phpt
rm ?TS/tests/241_Tutorial_psychedelicFont_basic.phpt
rm ?TS/tests/244_Tutorial_psychedelicFontGif_basic.phpt
rm ?TS/tests/266_ImagickDraw_getFontResolution_basic.phpt

: simple module load test for NTS extension
cd NTS
%{__php} --no-php-ini \
    --define extension_dir=%{buildroot}%{php_extdir} \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}

: upstream test suite for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
%{__php} -n run-tests.php --show-diff


%files
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%files devel
%doc %{pecl_testdir}/%{pecl_name}
%{php_incldir}/ext/%{pecl_name}


%changelog
* Fri Apr 10 2020 Remi Collet <remi@fedoraproject.org> - 3.4.4-3
- rebuid for new ImageMagick in 7.8

* Fri Oct 25 2019 Remi Collet <remi@fedoraproject.org> - 3.4.4-2
- build for sclo-php73
- ignore test failing because of https://bugzilla.redhat.com/1743658

* Mon May  6 2019 Remi Collet <remi@fedoraproject.org> - 3.4.4-1
- update to 3.4.4

* Thu Nov 15 2018 Remi Collet <remi@remirepo.net> - 3.4.3-3
- build for sclo-php72

* Thu Aug 10 2017 Remi Collet <remi@remirepo.net> - 3.4.3-2
- change for sclo-php71

* Fri Feb  3 2017 Remi Collet <remi@fedoraproject.org> - 3.4.3-1
- update to 3.4.3 (stable for PHP 5 and 7)
- add support for rh-php70 collection
- drop support for php54 and php55 collections

* Thu Jan 21 2016 Remi Collet <remi@fedoraproject.org> - 3.3.0-1
- cleanup for SCLo build

* Fri Dec  4 2015 Remi Collet <remi@fedoraproject.org> - 3.3.0-1
- update to 3.3.0

* Thu Aug 13 2015 Remi Collet <remi@fedoraproject.org> - 3.3.0-0.5.RC2
- rebuild

* Fri Jun 19 2015 Remi Collet <remi@fedoraproject.org> - 3.3.0-0.4.RC2
- allow build against rh-php56 (as more-php56)

* Tue Jun  2 2015 Remi Collet <remi@fedoraproject.org> - 3.3.0-0.3.RC2
- update to 3.3.0RC2

* Mon Mar 30 2015 Remi Collet <remi@fedoraproject.org> - 3.3.0-0.2.RC1
- update to 3.3.0RC1
- drop runtime dependency on pear, new scriptlets
- set imagick.skip_version_check=1 in default configuration

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.10.RC1
- Fedora 21 SCL mass rebuild

* Mon Aug 25 2014 Remi Collet <rpms@famillecollet.com> - 3.2.0-0.9.RC1
- rebuild against new ImageMagick-last version 6.8.7-4

* Mon Aug 25 2014 Remi Collet <rcollet@redhat.com> - 3.2.0-0.8.RC1
- improve SCL build

* Wed Jul 23 2014 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.7.RC1
- ignore tests/bug20636.phpt with IM 6.7.8.9
- add fix for php 5.6 https://github.com/mkoppanen/imagick/pull/35

* Mon Apr 14 2014 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.6.RC1
- rebuild for ImageMagick

* Wed Apr  9 2014 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.5.RC1
- add numerical prefix to extension configuration file

* Wed Mar 19 2014 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.4.RC1
- allow SCL build

* Mon Mar 10 2014 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.3.RC1
- cleanups for Copr

* Tue Nov 26 2013 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.2.RC1
- Update to 3.2.0RC1 (beta)
- add devel sub-package

* Sat Nov  2 2013 Remi Collet <rpms@famillecollet.com> - 3.1.2-2
- rebuild against new ImageMagick-last version 6.8.7-4
- install doc in pecl doc_dir

* Sun Oct 20 2013 Remi Collet <remi@fedoraproject.org> - 3.2.0-0.1.b2
- Update to 3.2.0b2
- install doc in pecl doc_dir
- install tests in pecl test_dir

* Wed Sep 25 2013 Remi Collet <remi@fedoraproject.org> - 3.1.2-1
- Update to 3.1.2
- add LICENSE to doc

* Sun Sep 22 2013 Remi Collet <remi@fedoraproject.org> - 3.1.1-1
- Update to 3.1.1
- open some upstream bugs
  https://bugs.php.net/65734 - Please Provides LICENSE file
  https://bugs.php.net/65736 - Link to sources
  https://bugs.php.net/65736 - Broken ZTS build

* Sun Sep  8 2013 Remi Collet <rpms@famillecollet.com> - 3.1.0-1
- update to 3.1.0 (beta)

* Sun Jun  2 2013 Remi Collet <rpms@famillecollet.com> - 3.1.0-0.10.RC2
- rebuild against new ImageMagick-last version 6.8.5-9

* Sat Apr  6 2013 Remi Collet <rpms@famillecollet.com> - 3.1.0-0.9.RC2
- rebuild against new ImageMagick-last version 6.8.4-6
- improve dependency on ImageMagick library

* Wed Mar 13 2013 Remi Collet <rpms@famillecollet.com> - 3.1.0-0.8.RC2
- rebuild against new ImageMagick-last version 6.8.3.9

* Fri Nov 30 2012 Remi Collet <remi@fedoraproject.org> - 3.1.0-0.5.RC2
- also provides php-imagick

* Sat Sep  8 2012 Remi Collet <remi@fedoraproject.org> - 3.1.0-0.4.RC2
- Obsoletes php53*, php54* on EL

* Thu Aug 16 2012 Remi Collet <rpms@famillecollet.com> - 3.1.0-0.3.RC2
- rebuild against new ImageMagick-last version 6.7.8.10

* Sat Jun 02 2012 Remi Collet <Fedora@FamilleCollet.com> - 3.1.0-0.2.RC2
- update to 3.1.0RC1

* Fri Nov 18 2011 Remi Collet <Fedora@FamilleCollet.com> - 3.1.0-0.1.RC1
- update to 3.1.0RC1 for php 5.4

* Mon Oct 03 2011 Remi Collet <Fedora@FamilleCollet.com> - 3.0.1-3.1
- spec cleanup

* Wed Aug 24 2011 Remi Collet <Fedora@FamilleCollet.com> - 3.0.1-3
- build zts extension

* Mon Dec 27 2010 Remi Collet <rpms@famillecollet.com> 3.0.1-2
- relocate using phpname macro

* Fri Nov 26 2010 Remi Collet <rpms@famillecollet.com> 3.0.1-1.1
- rebuild against latest ImageMagick 6.6.5.10

* Thu Nov 25 2010 Remi Collet <rpms@famillecollet.com> 3.0.1-1
- update to 3.0.1

* Mon Jul 26 2010 Remi Collet <rpms@famillecollet.com> 3.0.0-1
- update to 3.0.0

* Wed Aug 26 2009 Remi Collet <rpms@famillecollet.com> 2.3.0-2
- build against ImageMagick2 6.5.x

* Mon Aug 24 2009 Remi Collet <rpms@famillecollet.com> 2.3.0-1
- update to 2.3.0

* Tue Jun 30 2009 Remi Collet <rpms@famillecollet.com> 2.2.2-3.###.remi
- rebuild for PHP 5.3.0 (API = 20090626)

* Sat Apr 25 2009 Remi Collet <rpms@famillecollet.com> 2.2.2-2.fc11.remi
- F11 rebuild for PHP 5.3.0RC1

* Wed Feb 25 2009 Remi Collet <rpms@famillecollet.com> 2.2.2-1.fc10.remi
- update to 2.2.2 for php 5.3.0beta1

* Thu Jan 29 2009 Remi Collet <rpms@famillecollet.com> 2.2.1-1.fc10.remi.2
- rebuild for php 5.3.0beta1

* Sat Dec 13 2008 Remi Collet <rpms@famillecollet.com> 2.2.1-1.fc#.remi.1
- rebuild with php 5.3.0-dev
- add imagick-2.2.1-php53.patch

* Sat Dec 13 2008 Remi Collet <rpms@famillecollet.com> 2.2.1-1
- update to 2.2.1

* Sat Jul 19 2008 Remi Collet <rpms@famillecollet.com> 2.2.0-1.fc9.remi.1
- rebuild with php 5.3.0-dev

* Sat Jul 19 2008 Remi Collet <rpms@famillecollet.com> 2.2.0-1
- update to 2.2.0

* Thu Apr 24 2008 Remi Collet <rpms@famillecollet.com> 2.1.1-1
- Initial package

