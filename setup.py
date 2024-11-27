import setuptools
import io
import os


package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, 'README.md')
with io.open(readme_filename, encoding='utf-8') as readme_file:
    readme = readme_file.read()


setuptools.setup(
    name="gcp_adc_util",
    version="0.0.1",
    author="Sal Rashid",
    author_email="salrashid123@gmail.com",
    description="Utility library for GCP Application Default Credentials",
    long_description=readme,
    long_description_content_type='text/markdown',
    url="https://github.com/salrashid123/gcp_adc_util",
    install_requires=[
          'google-auth>=2.36.0',
          'requests'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',

        "Programming Language :: Python",
        "Programming Language :: Python :: 3.11",

        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
