from waterdetect import DWWaterDetect
from waterdetect.InputOutput import DWLoader
from waterdetect.Common import DWutils, DWConfig
from waterquality.Common import DWConfigQuality
import numpy as np
from pathlib import Path
import argparse
import os
import inspect

import matplotlib.pyplot as plt

class DWWaterQuality(DWWaterDetect):
    def __init__(self, *args, **kwargs):

        self.qual_config = DWConfigQuality(kwargs.pop('config_wq'))

        # Initialize the following variables that will store the results and the functions to be used
        self.quality_parameters = None
        self.inversion_functions = None

        super(DWWaterQuality, self).__init__(*args, **kwargs)

    def run_water_quality(self, inversion_functions: dict):
        self.inversion_functions = inversion_functions
        self._detect_water(post_callback=DWWaterQuality.calc_inversion_parameter)

    def parse_bands(self, function):
        """
        Get the bands from the function arguments and check if they are correctly loaded.
        :return: A list with the bands to be used in the fuction. 
        """

        args = inspect.signature(function)
        bands = [arg for arg in args.parameters if args.parameters[arg].default == inspect._empty]
        
        # check the necessary bands
        for band in bands:
            if band not in DWLoader.satellite_Dict[self.loader.product]['bands_names']:
                raise Exception(f'Band {band} not available in product {self.loader.product}')

        # if everything is correct, certify the bandas are loaded
        self.loader.load_raster_bands(bands)

        return bands

    def calc_inversion_parameter(self, dw_image, pdf_merger):
        """
        Calculate the parameter in config.parameter and saves it to the dictionary of bands.
        This will make it easier to make graphs correlating any band with the parameter.
        Also, checks if there are reports, then add the parameter to it.
        """

        # save results to quality_parameters
        self.quality_parameters = {}

        # loop through the functions (inversion functions) to calculate the corresponding parameters
        for parameter_name, func_description in self.inversion_functions.items():
            print(f'Calculating {parameter_name} parameter.')

            try:
                function = func_description['function']

                # get the necessary bands from the function signature
                bands = self.parse_bands(function) 

                # prepare the args
                args = {band: dw_image.bands[band] for band in bands}

                # call the function, passing the necessary  bands
                parameter = function(**args)

                # clear the parameters array and apply the Water mask, with no_data_values
                parameter = DWutils.apply_mask(parameter,
                                               ~(np.where(dw_image.water_mask == -1, 0, dw_image.water_mask).astype(
                                                 bool)),
                                               -9999)

                # save the parameter to be accessed
                self.quality_parameters.update({parameter_name: parameter})

                # save the calculated parameter
                self.saver.save_array(parameter, parameter_name, no_data_value=-9999)

                # prepare the report
                if pdf_merger is not None:

                    max_value, min_value = self.calc_param_limits(parameter)

                    colorbar = self.create_colorbar_pdf(
                        param_name=parameter_name,
                        colormap=self.qual_config.colormap,
                        min_value=min_value,
                        max_value=max_value, 
                        units=func_description['units'] if 'units' in func_description else ''
                    )

                    rgb = self.create_rgb_burn_in_pdf(
                        product_name=parameter_name,
                        burn_in_arrays=parameter,
                        colors=None,
                        fade=1.,
                        min_value=min_value,
                        max_value=max_value,
                        opt_relative_path=None,
                        colormap=self.qual_config.colormap,
                        uniform_distribution=self.qual_config.uniform_distribution,
                        no_data_value=-9999
                    )

                    # append the colorbar and the RGB image to the main PDF
                    pdf_merger.append(colorbar)
                    pdf_merger.append(rgb)
                    
                ## para o caso de uso de chamar direto, vamos gravar um .py chamado functions
                ## o sistema vai pegar todas as funções do .py e processá-las, ou aqueles que estiverem no dicionário
                ## inversion_functions = {}

            except Exception as e:
                print(f'***Error processing function {function.__name__}. Skipping it.')
                print(e)
                pass

    def calc_param_limits(self, parameter, no_data_value=-9999):

        valid = parameter[parameter != no_data_value]
        min_value = np.percentile(valid, 1) if self.qual_config.min_param_value is None else self.qual_config.min_param_value
        # min_value = np.quantile(valid, 0.25) if self.config.min_param_value is None else self.config.min_param_value
        max_value = np.percentile(valid, self.qual_config.max_param_percentile) if self.qual_config.max_param_value is None else self.qual_config.max_param_value
        # max_value = np.quantile(valid, 0.75) if self.config.max_param_value is None else self.config.max_param_value
        return max_value * 1.1, min_value * 0.8

    def plot_param(self, param_name, figsize=(10, 10), **kwargs):
        """
        Plot a parameter using matplotlib. 
        **kwargs will be passed to the imshow function
        """

        parameter = self.quality_parameters[param_name].copy()
        parameter[self.dw_image.water_mask != 1] = np.nan

        plt.figure(figsize=figsize)
        plt.imshow(parameter, **kwargs)


def main():
    """
    The main function is just a wrapper to create a entry point script called waterquality.
    With the package installed you can just call waterquality -h in the command prompt to see the options.
    """

    parser = argparse.ArgumentParser(description='The waterquality adds a post-processing function to waterdetect '
                                                 'package to calc water quality parameters. '
                                                 'Waterdetect should be installed in the environment.',
                                     epilog="The waterquality uses the WaterQuality.ini configuration file as well as "
                                            "WaterDetect.ini from waterdetect package."
                                            "To copy the package's default .ini files into the current directory, type:"
                                            ' `waterquality -GC .` without other arguments and it will copy  '
                                            'WaterDetect.ini and WaterQuality.ini into the current directory.'
                                            'The file inversion_functions.py should be updated with the necessary inversion functions.')

    parser.add_argument("-GC", "--GetConfig", help="Copy the inversion_functions.py, WaterQuality.ini and the WaterDetect.ini  "
                                                   "into the current directory and skips the processing. Once copied you  "
                                                   "can edit the .ini file and launch the waterquality without -c option.",
                        action="store_true")
    parser.add_argument("-i", "--input", help="The products input folder. Required.", required=False, type=str)
    parser.add_argument("-o", "--out", help="Output directory. Required.", required=False, type=str)
    parser.add_argument("-s", "--shp", help="SHP file. Optional.", type=str)
    parser.add_argument("-sm", "--single", help="Run WaterDetect over only one image instead of a directory of images. "
                                                "Optional.", action='store_true')
    parser.add_argument("-p", "--product", help='The product to be processed (S2_THEIA, L8_USGS, S2_L1C or S2_S2COR)',
                        default='S2_THEIA', type=str)
    parser.add_argument('-cwd', '--config_wd', help='WaterDetect configuration file (.ini). Only needed if running WD.'
                                                    'If not passed, WaterDetect.ini from current dir is used as '
                                                    'default.', type=str)

    parser.add_argument('-cwq', '--config_wq', help='WaterQuality configuration file (.ini). '
                                                    'If not passed, WaterQuality.ini from current dir is used as '
                                                    'default.', type=str)

    args = parser.parse_args()

    # If GetConfig option, just copy the WaterQuality.ini to the current working directory
    if args.GetConfig:
        src = Path(__file__).parent/'WaterQuality.ini'
        dst = Path(os.getcwd())/'WaterQuality.ini'

        print(f'Copying {src} into current dir.')
        dst.write_text(src.read_text())

        src = Path(__file__).parent/'inversion_functions.py'
        dst = Path(os.getcwd())/'inversion_functions.py'

        print(f'Copying {src} into current dir.')
        dst.write_text(src.read_text())

        print(f'WaterQuality.ini and inversion_functions.py copied into {dst.parent}.')

        # Get the WaterDetect.ini using the waterdetect script
        os.system('waterdetect -GC')

    else:
        if (args.input is None) or (args.out is None):
            print('Please specify input and output folders (-i, -o)')

        else:
            # Add current path to the system paths (to force getting the correct inversion_functions.py module)
            import sys
            sys.path.insert(0, '.')
            from inversion_functions import functions

            wq = DWWaterQuality(
                input_folder=args.input,
                output_folder=args.out,
                shape_file=args.shp,
                product=args.product,
                config_file=args.config_wd,
                config_wq=args.config_wq,
                single_mode=args.single,
                post_callback=DWWaterQuality.calc_inversion_parameter
            )

            # run water quality
            wq.run_water_quality(
                inversion_functions=functions
            )


# if called as a script, point to the main function of the WaterDetect package
if __name__ == '__main__':
    main()
