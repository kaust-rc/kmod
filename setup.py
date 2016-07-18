from setuptools import setup, find_packages

setup(
    name='KMod',
    version='0.0.1',
    description='KMod is the KAUST Environment Module",
    url='https://github.com/kaust-rc/kmod',
    author='Niall OByrnes',
    author_email='nobyrnes@icloud.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='environment module manipulate application data web',
    include_package_data = True,    # include everything in source control
    packages = ['kmod'],  # include all packages under src
    package_data = {
        '': ['*.css','*.html'],
        #'public': ['css/*.css'],
    },
    install_requires=[
        "cherrypy",
        #"jinja2",
    ]
)
