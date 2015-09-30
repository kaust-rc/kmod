


def help_text():
    return """
  ERROR:11: Usage is 'module command  [arguments ...] '

  K-Modules Release 0.0.1 2015-09-30 (Copyright GNU GPL v2 1991):

  Usage: module [ switches ] [ subcommand ] [subcommand-args ]

Switches:
    -H|--help       this usage info
    -V|--version    modules version & configuration options

  Available SubCommands and Args:
    + add|load      modulefile [modulefile ...]
    + rm|unload     modulefile [modulefile ...]
    + display|show  modulefile [modulefile ...]
    + avail         [modulefile [modulefile ...]]
    + purge
    + list
"""


