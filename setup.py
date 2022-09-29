from builtins import RuntimeError
from waterquality import __version__
import setuptools

short_description = 'The waterquality package extends the functionality of the waterdetect package to calculate ' \
                    'water quality parameters over the identified water mask. To do so, it is mandatory to have ' \
                    'waterdetect package installed (pip install waterdetect).'

long_description = short_description

setuptools.setup(
    name="waterquality", # Replace with your own username
    version=__version__,
    author="Maurício Cordeiro",
    author_email="cordmaur@gmail.com",
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cordmaur/WaterQuality",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['waterquality=waterquality.WaterQuality:main'],
    },
    include_package_data=True,
    package_data={'waterquality': ['WaterQuality.ini', 'inversion_functions.py']},
    install_requires=[
        'waterdetect>=1.5.12',
        'numpy>=1.17',
        'scikit_learn>=0.23',
        'matplotlib>=3.3',
        'PyPDF2>=1.26',
        'lxml>=4.5.0',
        'pillow>=7.0.0',
        'pandas'
    ]
)