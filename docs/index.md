Mostly Notes to myself for now
==============================

KMod was developed at KAUST (King Abdullah University of Science and Technology) in Thuwal, Saudi Arabia.  It was started by Niall OByrnes and driven by the opaque nature of tcl scripting when trying to maintain module files for multiple clusters, with multiple archictures.

The main differnce between Environemnt Modules and LMod is the separation of logic from data, while maintaining scripting functionality through extensibility.  This allows the data to be presented to the admins and the users in neat, explicit formats.  KMod also provides much more verbose feedback to the administrator, if desired.  The module data can then include user help, and display the versions in web/wiki format, removing the need to maintain a separate wiki, with available applicaions, and versions.



KMod is written in python with YAML chosen for the module files and is based around the idea that the data to modify the environemnt looks like a document and could be organised through a simple upsert function  (inspired by MongoDB's upsert).  The rest of the benefits fall from the obvious.  The YAML files were designed to be managed through git (though not necessary).


The KAUST experience shows that 95% of all desired functionality can he handeled with the built-in functions, but any extra functionality can be providied throughh simple python inheritance.

It was developed to be completely transparent to the user.


Why kmod and not YAMOD (Yet Another MODule Editor)?




The YAML file
=============

Simple rules, do not try to overcomplicate


The keys in the dictionary are overwritten.


inherit: gcc/4.1.1
version=5.4.1:
 - inherit: gcc/4.5.6

If module load gcc/5.4.1 is loaded will result in gcc/4.5.6 being preloaded, ie the top-level inherit will be over written.



inherit: gcc/4.1.1
version=5.4.1:
 - inherit: gcc/4.5.6
version=6.2.1:
 - inherit: version=5.4.1

So, here, in the conditional method, the top-level inherit will be overwritten an internal version case, but no regression is done, so it will fail.

This will work, but is probably not that efficient.
inherit: gcc/4.1.1
version=5.4.1:
 - inherit: gcc/4.5.6
version=6.2.1:
 - inherit: gcc/5.4.1

But it will result in kmod loading the inheritance, which allows regression, however it would be more explicit, to write the parameters in the case keyword, than to use inheritance.  If too much new data is required, tehn create a new file.





This applies to all paramteres, except the function parameters, prepend, postpend etc.







Documentation


Class KMod



Class LoadYaml

The load method firstly loads common.yaml which intreprets the input arguments and creates variables for use within the yaml files.

It then looks for multiple yaml files module* and module/* 

