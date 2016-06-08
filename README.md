KAUST ENVIRONMENT MODULES
=========================

Better for user
 * Allows grouping, and bundles of module loading
 * More aestheticly pleasing listing of modules and version
 * Can display a "Message of the day" to users given the module they load, (useful when planning upgrades or making changes to that module in particular)
 * Explicit display of version loaded by default
 * (maybe) More informative tab completion
 * Easier for user to write and maintain their own scripts 


Better for admins
 * Separates data and logic for admins and installers
 * Uses modern standard for config files: yaml
 * Built in reporting of modules installed, including default applications
 * Automatic reporting of modules used, and by whom
 * Designed to work with git for versioning and transparency of the yaml config files
 * Better control of version conflicts

Possibly
 * Can link to Jenkins server to execute separate test scripts


Usage
-----
 * module load gcc
 * module load gcc 5.1
 * module load gcc/5.1
 * module unload gcc
 * module avail
 * module purge
 * kmodule * (debug version for admins)


How it works
------------
executes bash function  "eval $(python k-env-module.py load gcc)"
which resolves
export PATH=/opt/share/gcc:/bin:etc:etc

So add this to your ~/.bashrc file


KMODULESROOT=/opt/share/modules/yaml

#Execute the output of k-env-modules
module (){ eval $(python k_env_modules.py $*); }

#Execute in debug for admins
kmodule (){ echo $(python k_env_modules.py debug $*); }






TODO Notes: 
 * Maintain documentation in same directory
 * Maintain install notes/scripts in same directory
 * Maintain test scripts in the same directory
 * Make contents of yaml file available to users



DEVELOPER NOTES
===============
Uses nosetests and pylint
To Install: sudo pip install nose pylint
to Run: nosetests



