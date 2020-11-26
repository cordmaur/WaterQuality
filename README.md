# WaterQuality

[![DOI](https://zenodo.org/badge/224832878.svg)](https://zenodo.org/badge/latestdoi/224832878)
![Screenshot](fig1.PNG)

## Synopsis

The WaterQuality package extends the functionalities of the WaterDetect[1] package (https://github.com/cordmaur/WaterDetect) to calculate continental water quality parameters from satellite reflectances. It has been specially conceived for L2A Sentinel 2 imagery from [MAJA](https://logiciels.cnes.fr/en/content/maja)<sup>1</sup>  processor, and the parameter is calculated just where there exist water, according to the waterdetect mask. Several inversion algorithms from the literature have been implemented:<br>
* Chlorophyll - Lins
* Chlorophyll - Gitelson
* CDOM absorption - Brezonik
* Turbidity - Dogliotti
* SPM - adapted from Nechad at the GET laboratory


All the details and tests has been described in the article <b>Automatic Water Detection from Multidimensional Hierarchical Clustering for Sentinel-2 Images and a Comparison with Level 2A Processors</b>, under revision by the journal Remote Sensing of Environment.

<b>How to cite ("accepted by Remote Sensing of Environment, pending publication"):</b><br>
Cordeiro, M.C.R, Martinez, J.-M., Pena Luque, S., 2020. Automatic Water Detection from Multidimensional Hierarchical Clustering for Sentinel-2 Images and a Comparison with Level 2A Processors. Remote Sensing of Environment XX, XX. 


## Dependencies
The required libraries are:
```
GDAL>=3.0.2
matplotlib>=3.1.2
PyPDF2>=1.26.0
scipy>=1.3.2
scikit-learn>=0.22
skimage>=0.16.2
numpy>=1.17
waterdetect>=1.5
```

### Note 1:
Scikit-Image is only necessary to run Otsu threshold method. 

## Instalation
The easiest way to install waterquality package is with `pip` command:<br>
`pip install waterquality`

Alternatively, you can clone the repository and install from its root throught the following commands:
```
git clone https://github.com/cordmaur/WaterQuality.git
cd WaterQuality
pip install .
```

### Note:
Make sure waterdetect is already installed, following the instructions in https://github.com/cordmaur/WaterDetect.


Once installed, a `waterquality` entry point is created in the path of the environment.
One can check the installation and options by running `waterquality --help`. Check also the waterdetect instalation. GDAL will be necessary for waterquality package.

```
usage: waterquality [-h] [-GC] [-i INPUT] [-o OUT] [-s SHP] [-p PRODUCT]
                    [-c CONFIG]

The waterquality adds a post-processing function to waterdetect package to
calc water quality parameters. Waterdetect should be installed in the
environment.

optional arguments:
  -h, --help            show this help message and exit
  -GC, --GetConfig      Copy the new WaterDetect.ini from the package into the
                        current directory and skips the processing. Once
                        copied you can edit the .ini file and launch the
                        waterquality without -c option.
  -i INPUT, --input INPUT
                        The products input folder. Required.
  -o OUT, --out OUT     Output directory. Required.
  -s SHP, --shp SHP     SHP file. Optional.
  -p PRODUCT, --product PRODUCT
                        The product to be processed (S2_THEIA, L8_USGS, S2_L1C
                        or S2_S2COR)
  -c CONFIG, --config CONFIG
                        Configuration .ini file. If not specified
                        WaterQuality.ini from current dir and used as default.

The waterquality uses the same WaterDetect.ini configuration file usedin the
waterdetect package, added with a [inversion] section.To copy the package's
default .ini file into the current directory, type: `waterquality -GC .`
without other arguments and it will copy WaterQDetect.ini into the current
directory.
```

## Usage
To use it, you should clone the project to your repository and run "python runWaterColor.py --help"
```
usage: runWaterColor.py [-h] -i INPUT -o OUT [-s SHP] [-p PRODUCT] [-g]
                        [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The products input folder. Required.
  -o OUT, --out OUT     Output directory. Required.
  -s SHP, --shp SHP     SHP file. Optional.
  -p PRODUCT, --product PRODUCT
                        The product to be processed (S2_Theia, Landsat,
                        S2_L1C)
  -g, --off_graphs      Turns off the scatter plot graphs
  -c CONFIG, --config CONFIG
                        Configuration .ini file. If not specified
                        WaterDetect.ini is used as default
```

### Config File
The waterdetect needs the same config file WaterDetect.ini from waterdetect package added with a [Inversion] section that specifies the parameters to calculate, boundaries for the colorbar and others.
To obtain the default version of this file, one can use `waterquality -GC` and the file WaterDetect.ini will be copied into the current working folder.

## Usage as Script
The basic usage for the waterquality is:<br>
`waterquality -i c:/input_folder -i -c:/output_folder -p S2_THEIA [-s any_shape.shp]`

The input directory should contain the uncompressed folders for the images. The script will loop through all folders in the input directory and save the water masks, graphs and reports to the output folder. The output folder must be created beforehand.

If the config file is not specified, the script will search for WaterDetect.ini in the current folder.

## Usage from Console
*** Under Construction ***

## Contributors
> Author: Maurício Cordeiro (ANA/GET)<br>
> Supervisor: Jean-Michel Martinez (IRD/GET)<br>
> Contributor: Marion Holst (IRD/GET)<br>

### Institutions
* ANA - Agência Nacional de Águas (https://www.gov.br/ana/en/)
* GET - Géosciences Environnement Toulouse (https://www.get.omp.eu/)
* IRD - Institut de Recherche pour le Développement (https://en.ird.fr/)
* CNES - Centre National d'Études Spatiales (https://cnes.fr/fr)

## License
This code is licensed under the [GNU General Public License v3.0](https://github.com/cordmaur/WaterDetect/blob/master/LICENSE) license. Please, refer to GNU's webpage  (https://www.gnu.org/licenses/gpl-3.0.en.html) for details.

## Reference
[1] Cordeiro, M.C.R, Martinez, J.-M., Pena Luque, S., 2020. Automatic Water Detection from Multidimensional Hierarchical Clustering for Sentinel-2 Images and a Comparison with Level 2A Processors. Remote Sensing of Environment (Pending publication)
