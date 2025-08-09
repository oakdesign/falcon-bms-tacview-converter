from setuptools import setup, find_packages

setup(
    name='falcon-bms-tacview-converter',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A tool to extract airbase and runway data from Falcon BMS game files and generate XML files for Tacview flight data analysis software.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/falcon-bms-tacview-converter',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyproj',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)