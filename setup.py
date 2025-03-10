from setuptools import find_packages, setup
from pyqaserver.version import __version__
setup(
    name='pyqaserver',
    version=__version__,
    description='A Flask-based web interface between Pylinac and Orthanc.',
    long_description='A Flask-based web interface between Pylinac and Orthanc.',
    author='Denis Brojan',
    author_email='brjdenis2000@gmail.com',
    url='https://github.com/brjdenis/pyqaserver',
    keywords="""medical physics quality assurance linear accelerators
                pylinac bottle orthanc""",
    license='MIT',
    install_requires=[

    ],
    include_package_data=True,
    packages=find_packages(),
    package_data={
        'pyqaserver': [
            'modules/*/*/*/*/*',
            'models/*'
        ],
    },
    entry_points={
        'console_scripts': [
            'pyqaserver = pyqaserver.main:main'
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        "Natural Language :: English",
        "Programming Language :: Python"
    ],
    zip_safe=False,
)
