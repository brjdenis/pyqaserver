.. index: 

#########
Changelog
#########

***************
Version 2.0.0
***************

QAserver has been renamed to pyqaserver and is now part of PyPI. 



************
Version 1.1
************

Bug fixes
==========

* (Winston Lutz) `#2 <https://github.com/brjdenis/pyqaserver/issues/2>`_ With Use Pylinac? checked the clip box option did not work. 
* (Winston Lutz) Non-integer angles for Pylinac are now rounded to integers.
* (General) `#3 <https://github.com/brjdenis/pyqaserver/issues/3>`_ It was not possible to collect anonymized images from Orthanc because date/time were empty strings.
* (Catphan) `#6 <https://github.com/brjdenis/pyqaserver/issues/6>`_ Fixed how LCV tolerance is applied.
* (Picket Fence) `#7 <https://github.com/brjdenis/pyqaserver/issues/7>`_ Red cross is now showing Pylinac's CAX, that is the center of the image shifted by the XRayImageReceptorTranslation.

Winston Lutz
============
* Added the option of selecting images within a series. 
* Changed the colormap for image display so that the BB is more visible on low contrast images. Users can choose from several mpl colormaps.
* Added image numbers when *Use Pylinac?* is checked so that it is possible to follow Pylinac's ordering.
* Changed how EPID dots are shown on the scatter plot. Now they are relative to the field CAX, instead of the BB.
* Users can now disable yellow dots on the scatter plot.

Image Review
============
* Added colormaps.
* Added a dot on the profiles that follow the crosshair. Also, crosshair position and pixel values are printed in a separate table.
* Changing window/level now also changes profile plot ranges.
* Added the option of calculating pixel value histograms.
* Added pixel value data for current mouse position.

Planar imaging
===============
* Changed the colormap for image display so that the ROIs are more easily seen. Users can choose from several mpl colormaps.

Catphan
========

Dynalogs
=========

* Location of the database folder can now be defined in the configuration file.
* Added several search options.
* Added histograms for error distributions.
* Prettytable module is no longer used to produce HTML strings, Pandas is used instead.

Picket Fence
=============

Bug Fixes
----------

Web server
==========

* Added image description. The text is copied from RTImageDescription Dicom tag from the last instance in the series.


************
Version 1.0
************

The initial release.