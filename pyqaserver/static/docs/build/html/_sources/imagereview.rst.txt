.. index: 

Image review
=============
This is a complementary module that can be used to extract image pixel data.  It is not part of Pylinac.

Chose the image you wish to inspect and click Display. In the resulting diagram you can:

* use the crosshair to observe profiles,
* draw a rectangle with the select box to get pixel statistics,
* change the gray-scale display by moving slider level,
* calculate pixel value histogram.

If needed, you can invert the image or convert HU back to pixel data.

.. image:: _static/images/imgreview.png
	:align: center

.. image:: _static/images/imgreview2.png
	:align: center
	
The histogram will have 2^n bins, where n is the BitsStored dicom tag. If this tag does not have a value, 16 bits will be assumed.