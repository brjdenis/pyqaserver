# pyQAserver

Pyqaserver connects [Pylinac](https://github.com/jrkerns/pylinac) and [Orthanc](https://github.com/jodogne/Orthanc) with a simplistic web interface. It was built to speed up the image analysis process with Pylinac, without having to switch computers or work manually with dicom files. The procedure is easy: acquire the image, send the image from the imaging computer directly to Orthanc, and then analyze it with Pylinac by using pyqaserver. Since all images are stored in Orthanc, you can re-analyze them anytime you want. You can do the analysis on any computer in your network.

Pyqaserver also contains a small database where you can store and review your measurements. And some additional modules that are handy when checking post-maintenance consistency of the linac.

![image](files/image.png)

![image](files/image2.png)

## Compatibility and dependency

It works on Windows 7 and 10. It should work on Linux as well. Currently, it is compatible with Pylinac 2.3.2 and Python 3.8. Because of the way pyqaserver is constructed, it is highly likely that it will not work with newer versions of Pylinac.

Not all Pylinac's capabilities are implemented. Trajectory logs cannot be analyzed, the calibration module is missing, and there are some missing features in other modules. Basically, this are the modules you can use:

* Winston Lutz
* Starshot
* Picket fence
* Planar imaging
* CT
* Dynalog
* Flatness/Symmetry
* VMAT

Additional modules are:

* **Field size** for measuring field size, radiation to light field match and focal spot position.
 
* **Field rotation** for measuring collimator angle calibration in absolute terms, couch rotation and EPID twist.
 

Pyqaserver contains little original code, just enough to connect Pylinac and Orthanc. The code is hideously written! But I will improve it. Some dependencies are included in the distribution of pyqaserver, other dependencies must be installed separately. Orthanc is not included in the distribution of pyqaserver.

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
* [minimumboundingbox.py](https://bitbucket.org/william_rusnack/minimumboundingbox/src/master/)
* [plotly.js](https://plotly.com/javascript/getting-started/)
* [tabulator.js](http://tabulator.info/)


## Installation and running

Pyqaserver can be installed as a Python package starting with version 2.0.0.  See https://pyqaserver.readthedocs.io/en/latest/

~~~
pip install pyqaserver
~~~

The current version of pyqaserver will only work with matplotlib version 3.3.1. So make sure you install exactly this version.

After that you can run pyqaserver with this:

~~~
pyqaserver IP_ADDRESS:PORT PATH_TO_DATABASE_FOLDER
~~~

For example, if you wish to run it as localhost:

~~~
pyqaserver 127.0.0.1:8080 PATH_TO_DATABASE_FOLDER
~~~


The web page is available at http://127.0.0.1:8080 ...
The default username/password is: admin/admin.

PATH_TO_DATABASE_FOLDER must be the full absolute path of pyqserver's database. If you are running pyqaserver for the first time, this should be an empty directory where pyqaserver will install a small sqlite database. Anytime you restart the server, point to the same directory. 

When upgrading to a new version, make a backup copy of the database folder, but do not change it. First, uninstall pyqaserver with

~~~
pip uninstall pyqaserver
~~~

And then install the new version:

~~~
pip install pyqaserver==2.0.1
~~~

Point the server to the same database directory and it should work. If you encounter problem with matplotlib, use version 3.3.1

~~~
pip install matplotlib==3.3.1
~~~


The entrance module for running pyqaserver from forked source is pyqaserver.py. Run it like this:

~~~
python pyqaserver.py 127.0.0.1:8080 PATH_TO_DATABASE_FOLDER
~~~


## Documentation

Documentation is available here:


* [https://pyqaserver.readthedocs.io/en/latest/](https://pyqaserver.readthedocs.io/en/latest/)

Older versions:

* [Version 1.0](https://brjdenis.github.io/pyqaserver/docs/version1.0/html/) , [PDF](/pdf/pyqaserver1.0.pdf)


## Versions

* Version 2.0.1 (latest)
* Version 2.0.0
* Version 1.0 (not on PyPI)


## Bugs and requests

You can contribute to this project with suggestions or bug reports to: brjdenis2000@gmail.com.

The best way to reach me is to send me an email, or you can create a new issue on Github.

What is the point of this project? Well, it started as an experiment. I wanted to do the Winston-Lutz test on an Elekta linac a couple of years ago, but didn't have the faintest idea how to do it. I stumbled upon Pylinac and learned a lot from it. Pylinac is really great because you can see the code, so you can understand how the analysis is performed. I liked this so much that I wanted to make a simple web interface for it. That way I could analyze images while I am still at the linac.


## Some notes on doing tests on Elekta linacs

I put together some personal notes on doing tests on Elekta linacs with Pylinac and QAserver: 

[Notes on doing tests on Elekta linacs](https://synergyqatips.readthedocs.io/en/latest/)


## Dynalog review

You can review MLC dynamic in the web interface by re-analysing stored dynalogs on-the-fly. You get this:

![MLC dynamics](files/dynalog_dynamic.gif)