from setuptools import find_packages, setup
import pyqaserver.version as version
setup(
    name='pyqaserver',
    version=version.__version__,
    description='A Bottle-based web interface between Pylinac and Orthanc.',
    long_description='A Bottle-based web interface between Pylinac and Orthanc.',
    author='Denis Brojan',
    author_email='brjdenis2000@gmail.com',
    url='https://github.com/brjdenis/pyqaserver',
    keywords="""medical physics quality assurance linear accelerators
                pylinac bottle orthanc""",
    license='MIT',
    install_requires=[
                    'scipy >= 1.0',
                    'numpy >= 1.14',
                    'matplotlib == 3.3.1',
                    'jinja2',
                    'pylinac == 2.3.2',
                    'httplib2 == 0.18.1',
                    'bokeh == 2.2.1',
                    'waitress == 1.4.4',
                    'passlib',
                    'pandas',
                    'requests'
                     ],
    include_package_data=True,
    packages=find_packages(),
    package_data={
        'pyqaserver': [
            'static/*/*/*',
            'views/*',
            'python_packages/*'
        ],
    },
    entry_points={
        'console_scripts': [
            'pyqaserver = pyqaserver.pyqaserver:main'
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