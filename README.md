# QAserver

QAserver connects Pylinac and Orthanc with a simplistic web interface. It was built to speed up the image analysis process with Pylinac, without having to switch computers or work manually with dicom files. The procedure is easy: acquire the image, send the image from the imaging computer directly to Orthanc, and then analyze it with Pylinac by using QAserver. Since all images are stored in Orthanc, you can re-analyze them anytime you want. You can do the analysis on any computer in your network.

![image](image.png)

It works on Windows 7 and 10.

Not all Pylinac's capabilities are implemented. Trajectory logs cannot be analyzed, the calibration module is missing, and there are some missing features in other modules.

QAserver contains little original code, just enough to connect Pylinac and Orthanc. Some dependencies are included in the distribution of QAserver, other dependencies must be installed separately.


# Download

QAserver cannot be installed as a Python package. You must download the zip archive and follow installation instructions given below.

* [Version 1.0](/versions/qaserver1.0.zip)

# Installation and user guide

Installation instructions and a user guide are available at:

* [Version 1.0](https://brjdenis.github.io/qaserver/docs/version1.0/html/) , [PDF](/pdf/qaserver1.0.pdf)

# Bugs and requests

You can contribute to this project with suggestions or bug reports: 

