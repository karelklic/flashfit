SUBDIRS = docs utils

bin_SCRIPTS = flashfit.py

PYTHON_FILES = \
	data_fit.py \
	data_fit_parameter.py \
	data_original.py \
	data.py \
	flashfit.py \
	font.py \
	gui_absorbanceaxis.py \
	gui_absorbancefit.py \
	gui_absorbancegraph.py \
	gui_appearance.py \
	gui_console.py \
	gui_graphicsscene.py \
	gui_graphicsview.py \
	gui_informationtable.py \
	gui_mainwindow.py \
	gui_menubar.py \
	gui_residualsgraph.py \
	gui_settings_compatible.py \
	gui_settings_experimental.py \
	gui_settings.py \
	gui_spinbox.py \
	gui_timeaxis.py \
	gui_timebarline.py \
	gui_timebarpair.py \
	gui_timebar.py \
	gui_timebartriangle.py \
	method_compatible.py \
	method_experimental.py \
	nonneglstsq.py \
	task_fit.py \
	task_changepointcount.py \
	task_loadfile.py \
	task.py \
	variables.py

EXTRA_DIST = $(PYTHON_FILES)

pkgdata_PYTHON = $(PYTHON_FILES)

CLEANFILES = $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

#
# Windows NSIS installer
#
INSTALLERFILE = $(PACKAGE)-$(VERSION).exe
CLEANFILES += $(INSTALLERFILE)

if INSTALLER
all: $(INSTALLERFILE)
endif

$(INSTALLERFILE): flashfit.nsis
	$(MAKENSIS) -DPACKAGE="$(PACKAGE)" -DPACKAGE_NAME="$(PACKAGE_NAME)" -DPACKAGE_VERSION="$(PACKAGE_VERSION)" -DPACKAGE_BUGREPORT="$(PACKAGE_BUGREPORT)" $<

upload: $(INSTALLERFILE) dist-gzip dist-xz
	scp $(INSTALLERFILE) klic.name:/home/karel/public_html/ftp.klic.name/public/flashfit/windows
	make dist-gzip
	scp $(distdir).tar.gz klic.name:/home/karel/public_html/ftp.klic.name/public/flashfit
	make dist-xz
	scp $(distdir).tar.xz klic.name:/home/karel/public_html/ftp.klic.name/public/flashfit

#scp $(distdir).zip klic.name:/home/karel/public_html/ftp.klic.name/public/flashfit
