KAUST ENVIRONMENT MODULES
=========================

Better for user
 * Allows grouping, and bundles of module loading
 * More aestheticly pleasing listing of modules and version
 * (maybe) More informative tab completion
 * Can display a "Message of the day" to users given the module they load, which is very useful when planning upgrades or making changes to that module in particular

Better for staff
 * Separates data and logic for installers
 * Uses modern standard for config files: yaml
 * Built in reporting of modules installed, including default applications
 * Automatic reporting of modules used, and by whom
 * Designed to work with git for versioning and transparency
 * Better control of version conflicts

Possibly
 * Can link to Jenkins server to execute separate test scripts


Usage
-----
kmodule load gcc
kmodule load gcc 5.1
kmodule unload gcc
kmodule avail
kmodule purge

How it works
------------
executes bash function  "eval $(python k-env-module.py load gcc)"
which resolves
export PATH=/opt/share/gcc:/bin:etc:etc


#Execute the output of k-env-modules
kmodule (){ eval $(python k-env-modules.py $*); }

#debug module
dmodule (){ echo $(python k-env-modules.py debug $*); }


