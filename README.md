# QAserver

QAserver connects [Pylinac](https://github.com/jrkerns/pylinac) and [Orthanc](https://github.com/jodogne/Orthanc) with a simplistic web interface. It was built to speed up the image analysis process with Pylinac, without having to switch computers or work manually with dicom files. The procedure is easy: acquire the image, send the image from the imaging computer directly to Orthanc, and then analyze it with Pylinac by using QAserver. Since all images are stored in Orthanc, you can re-analyze them anytime you want. You can do the analysis on any computer in your network.

![image](image.png)

## Compatibility and dependency

It works on Windows 7 and 10. Currently, it is compatible with Pylinac 2.2.7 and Python 3.7. Because of the way QAserver is constructed, it is highly likely that it will not work with newer versions of Pylinac. 

Not all Pylinac's capabilities are implemented. Trajectory logs cannot be analyzed, the calibration module is missing, and there are some missing features in other modules. Basically, this are the modules you can use:

* Winston Lutz
* Starshot
* Picket fence
* Planar imaging
* CT
* Dynalog
* Flatness/Symmetry
* VMAT

With an additional derivative module I call "Fieldsize".

QAserver contains little original code, just enough to connect Pylinac and Orthanc. Some dependencies are included in the distribution of QAserver, other dependencies must be installed separately. Orthanc is not included in the distribution of QAserver.

Here is a list of some of the software used (common packages like scipy, numpy etc. are not listed):

* [Pylinac](https://github.com/jrkerns/pylinac)
* [Bottle](https://bottlepy.org/docs/dev/)
* [httplib2](https://github.com/httplib2/httplib2)
* [prettytable](https://github.com/jazzband/prettytable)
* [Resttoolbox.py](https://github.com/jodogne/OrthancMirror/tree/master/Resources/Samples/Python)
* [Bokeh](https://docs.bokeh.org/en/latest/index.html)
* [mpld3](https://mpld3.github.io/)
* [Bootstrap](https://getbootstrap.com/docs/3.4/)
* [Bootstrap-datepicker](https://bootstrap-datepicker.readthedocs.io/en/latest/)
* [Popper](https://popper.js.org/)
* [math.js](https://mathjs.org/)


## Download

QAserver cannot be installed as a Python package. You must download the zip archive and follow installation instructions given below.

* [Version 1.0](/versions/qaserver1.0.zip)

## Installation and user guide

Installation instructions and the user guide are available at:

* [Version 1.0](https://brjdenis.github.io/qaserver/docs/version1.0/html/) , [PDF](/pdf/qaserver1.0.pdf)

## Bugs and requests

You can contribute to this project with suggestions or bug reports to: brjdenis2000@gmail.com.

I don't really understand how github works, so the best way to reach me is to send me an email.

What is the point of this project? Well, it started as an experiment. I wanted to do the Winston-Lutz test on an Elekta linac a couple of years ago, but didn't have the faintest idea how to do it. I stumbled upon Pylinac and learned a lot from it. So I put all the modules that I use into the web interface... I have too much time and not enough life.


# Some notes on doing tests on Elekta linacs

First, you should get to know your Elekta linac. I don't mean just the basic stuff like how to turn it on and off. I mean you should read all the manuals, all the technical stuff that a physicist must know. Second, configure both imaging workstation to enable Export to Orthanc. You do this by modifying sri.ini and mergecom.app. If you have problems, you can contact me.

## Winston-Lutz

I started by using the Flexmap MV sequence (find it in Stored beams in Service). This is the standard sequence of gantry/collimator angles that represents the minimum set of images that are necessary to find the MV isocenter. For SRS, I am using a similar sequence, except that the field size is 2 cm x 2 cm. I suggest that you create a IMAT field and let iView collect 8 images automatically.

For 6 MV, 10 MV, 15 MV and 6 FFF use the max dose rate, otherwise you will be testing less clinical conditions. You may get artifacts when using FFF beams. You can clear the edges of the image with the clip box option.

You can do the test like this:

* Put the BB on the couch. Put HexaPod, if you have it, into drive and put the Reference frame on. Align the BB with the lasers. Make a CBCT scan of the BB. Create a special reconstruction preset for this. You can shrink the reconstruction window, and increase the resolution, but be careful because some combinations don't work. Change the reconstruction voxel size to, say, 0.5 mm or 1 mm. ReconstructionDataType should be set to float, and ProjectionDownSizeFactor should be set to 1. Then register the scan with the reference image that Elekta supplies. Try to be accurate. Make the shifts with HexaPOD (or you can use micrometer screws). Then acquire MV image of the BB for the WL test. After you are done acquiring 8 images, put gantry and collimator to 0 and acquire several images of the BB with the same field size as before, but at different couch angles - this will be a test of the couch rotation.

![image](/files/image.png)

* Put the BB on the couch and acquire 8 MV image as explained. Calculate the shifts that minimize deviations. Make the shifts with the micrometer screws. Repeat the procedure until the shifts are as small as possible. Then make a cbct scan of the BB and register the scan with the reference image. The registration shifts will tell you the difference between the MV isocenter and the position of this isocenter as seen by XVI. If it is too large, a re-calibration of XVI will be necessary. I should warn you that Elekta's flexmap software calculates the longitudinal shifts differently than Pylinac, don't be surprised if you see a difference of 0.3 mm.

## Picket fence

You have to create your own picket fence beam. iCOM CAT comes in handy for that. I am using something like this: ![file](/files/ElektaAgilityPicketFence.efs.efs). It think there should be more control points in this beam, but I didn't have the time to figure it out. Maybe you can. The results of the test should be excellent for Agility collimators.


## Catphan

You must check all three FOVs. Don't just check Small FOV. Prepare a special preset for image acquisition. Since XVI allows CW and CC acquisition, you should have 6 presets altogether. The same goes for the cbct scans of the BB. Why? Because each FOV and each direction of rotation has its own flexmap calibration.
Anyway, the preset should have the largest window (S20, M20, L20), an exposure of, say, 20 ms/20 mA with half speed (660 frames). The reconstruction preset should be similar to CAT Geometric or better. Don't use clinical presets, try to follow the same acquisition protocol that the CAT is using.

Align the Catphan so that the center of the phantom is in the center of the image. I think that should be the second or third mark from gantry end. When exporting the image to Orthanc, use a slice thickness of 2 mm.

A note: if you notice that MFOV and LFOV have worse image quality than SFOV, check the isocenter with the BB (see WL test). You should notice that the 3D image of the BB will be smeared for MFOV and LFOV. And if you look at the projections, the isocenter (violet cross) will not be at the center of the BB. Can you guess why?














