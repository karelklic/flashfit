AC_INIT([flashfit], [0.8], [karelklic@gmail.com])

AM_INIT_AUTOMAKE([-Wall -Werror foreign])

AM_PATH_PYTHON
if test -z "$PYTHON"; then
    echo "*** Essential program python not found" 1>&2
    exit 1
fi

AC_ARG_ENABLE([installer],
	AS_HELP_STRING([--enable-installer],[Build NSIS installer [yes]]),
	[ enable_installer=${enableval} ], [ enable_installer=no ])
AM_CONDITIONAL(INSTALLER, test "x$enable_installer" = "xyes")
AC_MSG_CHECKING([whether to build NSIS installer])
AC_MSG_RESULT([${enable_installer}])

AC_ARG_WITH(makensis, [AS_HELP_STRING([--with-makensis], [Path to makensis])])

if test "x$enable_installer" = "xyes" ; then
	if test "x$with_makensis" = "x" ; then
		AC_CHECK_TOOL([MAKENSIS], [makensis], [no])
		if test "x$MAKENSIS" = "xno" ; then
			AC_MSG_ERROR([makensis not found])
		fi
	else
		AC_MSG_CHECKING([for makensis])
		AC_MSG_RESULT([${with_makensis}])
		AC_SUBST([MAKENSIS], [${with_makensis}])
	fi
fi

AC_CONFIG_FILES([
        Makefile
	docs/Makefile
	utils/Makefile
])

AC_OUTPUT
