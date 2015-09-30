YAML

import yaml

yaml.load(file('yaml.yaml'))



a: &v 99

b: *v

q: &ab
  a: 1
  b: 2

w: *ab





set myver [exec gcc --version | head -n1 | awk "{ print \$3 }" ]
puts stderr "Initial $module_name version: $myver"

# Additional conflicts
#conflict name

# Prereqs
# prereq name

# Specific setup goes here, license files, path setup, etc

# FIXME hardcoding these versions for now
set arch x86_64-unknown-linux-gnu

set mpc_version 0.9
set mpfr_version 3.0.1
set gmp_version 5.0.2
set binutils_ver 2.21


# Add gcc and binutils to PATH
prepend-path  PATH             $app_dir/bin
prepend-path  PATH             $apps_root/binutils/$binutils_ver/$distro/bin

# Set the gcc search path (dirs specified via command line -L/dir are searched first)
prepend-path  LIBRARY_PATH     $app_dir/lib/$module_name/$arch/lib
prepend-path  LIBRARY_PATH     $app_dir/lib/$module_name/$arch/lib64

# Add locations of gcc shared libs to load library path
prepend-path  LD_LIBRARY_PATH  $app_dir/lib/$module_name/$arch/$version/32
prepend-path  LD_LIBRARY_PATH  $app_dir/lib/$module_name/$arch/$version
prepend-path  LD_LIBRARY_PATH  $app_dir/lib
prepend-path  LD_LIBRARY_PATH  $app_dir/lib64

# Add locations of external (mpc, mpfr, gmp) shared libs to load library path
prepend-path  LD_LIBRARY_PATH  $apps_root/gmp/$gmp_version/$distro/lib
prepend-path  LD_LIBRARY_PATH  $apps_root/mpfr/$mpfr_version/$distro/lib
prepend-path  LD_LIBRARY_PATH  $apps_root/mpc/$mpc_version/$distro/lib

# Set MANPATH and INFOPATH
prepend-path MANPATH $app_dir/share/man
prepend-path INFOPATH $app_dir/share/info
prepend-path INFOPATH $apps_root/binutils/$binutils_ver/$distro/share/info

set myver [exec gcc --version | head -n1 | awk "{ print \$3 }" ]
puts stderr "Current $module_name version: $myver"
















source [file dirname $::ModulesCurrentModulefile]/../../common/common_setup2.tcl
GeneralAppSetup INTEL/v${version}.app

set app_dir $::env(KAUST_APPS_ROOT)/INTEL/v$version.app/$module_name

#/$module_name/release


#        set app_dir $env(KAUST_APPS_ROOT)/$dir_name/v${version}.app/$name/release
#        set app_dir /opt/share/$dir_name/v${version}.app/$name/release

ReportIntelVersion

set mkl_root $app_dir/mkl
setenv MKLROOT $mkl_root

set ipp_root $app_dir/ipp/em64t

setenv ICC_ROOT $app_dir

prepend-path IPPROOT $ipp_root

prepend-path MANPATH $app_dir/man/en_US

prepend-path INTEL_LICENSE_FILE $app_dir/licenses

prepend-path LIBRARY_PATH $ipp_root/lib
prepend-path LIBRARY_PATH $mkl_root/lib/em64t
prepend-path LIBRARY_PATH $app_dir/lib/intel64

prepend-path LD_LIBRARY_PATH $ipp_root/lib
prepend-path LD_LIBRARY_PATH $mkl_root/lib/em64t
prepend-path LD_LIBRARY_PATH $app_dir/lib/intel64

prepend-path FPATH $mkl_root/include

prepend-path LIB $ipp_root/lib


prepend-path LIB $ipp_root/lib

prepend-path CPATH $mkl_root/include
prepend-path CPATH $ipp_root/include

# appending path for use with Ubuntu -- headers in non-default location
append-path CPATH /usr/include/x86_64-linux-gnu

prepend-path NLSPATH $ipp_root/lib/locale/%l_%t/%N
prepend-path NLSPATH $mkl_root/lib/em64t/locale/%l_%t/%N
prepend-path NLSPATH $app_dir/idb/intel64/locale/%l_%t/%N
prepend-path NLSPATH $app_dir/lib/intel64/locale/%l_%t/%N

prepend-path PATH $app_dir/bin/intel64

prepend-path INCLUDE $mkl_root/include
prepend-path INCLUDE $ipp_root/include

ReportIntelVersion






This message and its contents including attachments are intended solely for the original recipient. If you are not the intended recipient or have received this message in error, please notify me immediately and delete this message from your computer system. Any unauthorized use or distribution is prohibited. Please consider the environment before printing this email.
