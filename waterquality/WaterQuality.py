from waterquality import Inversion
from waterdetect import DWWaterDetect
from waterdetect.Common import DWutils

import numpy as np
from pathlib import Path
import argparse
import os


class DWWaterQuality(DWWaterDetect):

    def run_batch(self):

        # # if there is an inversion, create an instance of Algorithms class, None otherwise
        # self.inversion_algos = DWInversion.DWInversionAlgos() if self.config.inversion else None

        super().run_batch(self.callback_inversions)

    def callback_inversions(self, dw_image, pdf_merger):

        # test if the .ini file has the inversion section
        try:
            if self.config.inversion:
                # If there is the section and inversion is ON
                try:
                    self.calc_inversion_parameter(dw_image, pdf_merger)
                except Exception as err:
                    print('****** ERROR CALCULATING INVERSION PARAMETER ********')
                    print(err)
            else:
                print('Inversion flag is set to False in WaterDetect.ini')

        except Exception as err:
            print('****** MISSING INVERSION PARAMETERS IN WATERDETECT.INI ********')
            print('No Inversion section or inversion flag in WaterDetect.ini. Update it with waterquality -GC')

        return

    def calc_inversion_parameter(self, dw_image, pdf_merger_image):
        """
        Calculate the parameter in config.parameter and saves it to the dictionary of bands.
        This will make it easier to make graphs correlating any band with the parameter.
        Also, checks if there are reports, then add the parameter to it.
        :return: The parameter matrix
        """

        inversion_algos = Inversion.DWInversionAlgos()

        # POR ENQUANTO BASTA PASSARMOS O DICIONÁRIO DE BANDAS E O PRODUTO PARA TODOS
        mask = self.loader.invalid_mask

        for quality_param in self.config.parameter.replace(' ', '').split(','):
            print(f'Calculating {quality_param} parameter.')

            # Ask for DWInversionAlgos to calculate the parameter matrix
            parameter = inversion_algos.invert_param(quality_param, self.loader.product, self.loader.raster_bands)

            if parameter is not None:
                # clear the parameters array and apply the Water mask, with no_data_values
                parameter = DWutils.apply_mask(parameter,
                                           ~(np.where(dw_image.water_mask == 255, 0, dw_image.water_mask).astype(
                                             bool)),
                                           -9999)

                # save the calculated parameter
                self.saver.save_array(parameter, quality_param, no_data_value=-9999)

                if pdf_merger_image is not None:

                    max_value, min_value = self.calc_param_limits(parameter)

                    pdf_merger_image.append(self.create_colorbar_pdf(product_name='colorbar_' + quality_param,
                                                                     colormap=self.config.colormap,
                                                                     min_value=min_value,
                                                                     max_value=max_value))

                    pdf_merger_image.append(self.create_rgb_burn_in_pdf(product_name=quality_param,
                                                                        burn_in_array=parameter,
                                                                        color=None,
                                                                        fade=0.8,
                                                                        min_value=min_value,
                                                                        max_value=max_value,
                                                                        opt_relative_path=None,
                                                                        colormap=self.config.colormap,
                                                                        uniform_distribution=self.config.uniform_distribution,
                                                                        no_data_value=-9999))
        return

    def calc_param_limits(self, parameter, no_data_value=-9999):

        valid = parameter[parameter != no_data_value]
        min_value = np.percentile(valid, 1) if self.config.min_param_value is None else self.config.min_param_value
        #min_value = np.quantile(valid, 0.25) if self.config.min_param_value is None else self.config.min_param_value
        max_value = np.percentile(valid, 75) if self.config.max_param_value is None else self.config.max_param_value
        #max_value = np.quantile(valid, 0.75) if self.config.max_param_value is None else self.config.max_param_value
        return max_value * 1.1, min_value * 0.8

def main():
    """
    The main function is just a wrapper to create a entry point script called waterquality.
    With the package installed you can just call waterquality -h in the command prompt to see the options.
    """
    parser = argparse.ArgumentParser(description='The waterquality adds a post-processing function to waterdetect '
                                                 'package to calc water quality parameters. '
                                                 'Waterdetect should be installed in the environment.',
                                     epilog="The waterquality uses the same WaterDetect.ini configuration file used "
                                            "in the waterdetect package, added with a [inversion] section."
                                            "To copy the package's default .ini file into the current directory, type:"
                                            ' `waterquality -GC .` without other arguments and it will copy  '
                                            'WaterQDetect.ini into the current directory.')

    parser.add_argument("-GC", "--GetConfig", help="Copy the new WaterDetect.ini from the package into the current "
                                                   "directory and skips the processing. Once copied you can edit the "
                                                   ".ini file and launch the waterquality without -c option.",
                        action="store_true")
    parser.add_argument("-i", "--input", help="The products input folder. Required.", required=False, type=str)
    parser.add_argument("-o", "--out", help="Output directory. Required.", required=False, type=str)
    parser.add_argument("-s", "--shp", help="SHP file. Optional.", type=str)
    parser.add_argument("-p", "--product", help='The product to be processed (S2_THEIA, L8_USGS, S2_L1C or S2_S2COR)',
                        default='S2_THEIA', type=str)
    parser.add_argument('-c', '--config', help='Configuration .ini file. If not specified WaterQuality.ini '
                                               'from current dir and used as default.', type=str)

    # product type (theia, sen2cor, landsat, etc.)
    # optional shape file
    # generate graphics (boolean)
    # name of config file with the bands-list for detecting, saving graphics, etc. If not specified, use default name
    #   if clip MIR or not, number of pixels to plot in graph, number of clusters, max pixels to process, etc.
    # name of the configuration .ini file (optional, default is WaterDetect.ini in the same folder

    args = parser.parse_args()

    # If GetConfig option, just copy the WaterDetect.ini to the current working directory
    if args.GetConfig:
        src = Path(__file__).parent/'WaterDetect.ini'
        dst = Path(os.getcwd())/'WaterDetect.ini'

        print(f'Copying {src} into current dir.')
        dst.write_text(src.read_text())
        print(f'WaterDetect.ini copied into {dst.parent}.')

    else:
        if (args.input is None) or (args.out is None):
            print('Please specify input and output folders (-i, -o)')

        else:
            water_quality = DWWaterQuality(input_folder=args.input, output_folder=args.out, shape_file=args.shp,
                                         product=args.product, config_file=args.config)
            water_quality.run_batch()


# if called as a script, point to the main function of the WaterDetect package
if __name__ == '__main__':
    main()
