#%Module 1.0 -*- tcl -*-
#
#  INTEL icc  module for use with 'environment-modules' package:

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

