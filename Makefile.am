SUBDIRS = docs utils

bin_SCRIPTS = flashfit.py

PYTHON_FILES = \
	data.py \
	data_fit.py \
	data_fit_parameter.py \
	data_original.py \
	flashfit.py \
	font.py \
	gui_absorbanceaxis.py \
	gui_absorbancefit.py \
	gui_absorbancegraph.py \
	gui_console.py \
	gui_graphicsscene.py \
	gui_graphicsview.py \
	gui_informationtable.py \
	gui_mainwindow.py \
	gui_menubar.py \
	gui_residualsgraph.py \
	gui_settings.py \
	gui_settings_axes.py \
	gui_settings_bars.py \
	gui_settings_compatible.py \
	gui_settings_experimental.py \
	gui_settings_informationbox.py \
	gui_spinbox.py \
	gui_timeaxis.py \
	gui_timebar.py \
	gui_timebarline.py \
	gui_timebarpair.py \
	gui_timebartriangle.py \
	method_compatible.py \
	method_experimental.py \
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
EXTRA_DIST += flashfit.nsis

if INSTALLER
all: $(INSTALLERFILE)
endif

$(INSTALLERFILE): flashfit.nsis
	$(MAKENSIS) -DPACKAGE="$(PACKAGE)" -DPACKAGE_NAME="$(PACKAGE_NAME)" -DPACKAGE_VERSION="$(PACKAGE_VERSION)" -DPACKAGE_BUGREPORT="$(PACKAGE_BUGREPORT)" $<

upload: $(INSTALLERFILE) dist-gzip dist-xz
	scp $(INSTALLERFILE) klic.name:/var/ftp/flashfit/windows
	make dist-gzip
	scp $(distdir).tar.gz klic.name:/var/ftp/flashfit
	make dist-zip
	scp $(distdir).zip klic.name:/var/ftp/flashfit
	make dist-xz
	scp $(distdir).tar.xz klic.name:/var/ftp/flashfit
