SUBDIRS = docs utils tests

nodist_bin_SCRIPTS = flashfit

PYTHON_FILES = \
	data.py \
	data_fit.py \
	data_fit_parameter.py \
	data_original.py \
	flashfit.py \
	font.py \
	gui_console.py \
	gui_fit.py \
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
	gui_textitems.py \
	gui_timeaxis.py \
	gui_timebar.py \
	gui_timebarline.py \
	gui_timebarpair.py \
	gui_timebartriangle.py \
	gui_valueaxis.py \
	gui_valuegraph.py \
	method_compatible.py \
	method_experimental.py \
	task.py \
	task_changepointcount.py \
	task_changemode.py \
	task_fit.py \
	task_loadfile.py \
	variables.py

EXTRA_DIST = $(PYTHON_FILES) flashfit.in

pkgdata_PYTHON = $(PYTHON_FILES)

CLEANFILES = $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

flashfit: flashfit.in Makefile
	sed -e 's|@pkgdatadir[@]|$(pkgdatadir)|g' $< > $@
	chmod +x $@

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

upload: $(INSTALLERFILE)
	scp $(INSTALLERFILE) klic.name:/var/ftp/flashfit/windows
	make dist-gzip
	scp $(distdir).tar.gz klic.name:/var/ftp/flashfit
	make dist-zip
	scp $(distdir).zip klic.name:/var/ftp/flashfit
	make dist-xz
	scp $(distdir).tar.xz klic.name:/var/ftp/flashfit

RPM_DIRS = --define "_sourcedir `pwd`" \
           --define "_rpmdir `pwd`" \
           --define "_specdir `pwd`" \
           --define "_builddir `pwd`" \
           --define "_srcrpmdir `pwd`"

EXTRA_DIST += flashfit.spec.in
rpm: dist-xz flashfit.spec
	rpmbuild $(RPM_DIRS) -ba flashfit.spec
srpm: dist-xz btparser.spec
	rpmbuild $(RPM_DIRS) -bs flashfit.spec
