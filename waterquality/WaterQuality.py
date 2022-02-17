from waterquality import Inversion
from waterdetect import DWWaterDetect
from waterdetect.Common import DWutils, DWConfig
from waterquality.Common import DWConfigQuality
import numpy as np
from pathlib import Path
import argparse
import os


class DWWaterQuality(DWWaterDetect):
    def __init__(self, *args, **kwargs):

        self.qual_config = DWConfigQuality(kwargs.pop('config_wq'))

        super(DWWaterQuality, self).__init__(*args, **kwargs)

    @classmethod
    def run_water_quality(cls, input_folder, output_folder, single_mode, shape_file=None, product='S2_THEIA',
                          config_wd=None, config_wq=None, pekel=None):
        """
        @param input_folder: If single_mode=True, this is the uncompressed image product. If single_mode=False, this
        is the folder that contains all uncompressed images.
        @param output_folder: Output directory
        @param single_mode: For batch processing (multiple images at a time), single_mode should be set to False
        @param shape_file: Shape file to clip the image (optional).
        @param product: The product to be processed (S2_THEIA, L8_USGS, S2_L1C or S2_S2COR)
        @param config_wd: Configuration WaterDetect file. If not specified WaterDetect.ini from current dir and used
                          as default
        @param config_wq: Configuration WaterQuality file. If not specified WaterQuality.ini from current dir and used
                          as default
        @param pekel: Optional path for an occurrence base map like Pekel
        @return:
        """

        super().run_water_detect(input_folder=input_folder,
                                 output_folder=output_folder,
                                 shape_file=shape_file,
                                 product=product,
                                 config_file=config_wd,
                                 config_wq=config_wq,
                                 post_callback=cls.callback_inversions,
                                 single_mode=single_mode)


    def callback_inversions(self, dw_image, pdf_merger):
        # test if the .ini file has the inversion section
        try:
            if self.qual_config.inversion:
                # If there is the section and inversion is ON
                try:
                    self.calc_inversion_parameter(dw_image, pdf_merger)
                except Exception as err:
                    print('****** ERROR CALCULATING INVERSION PARAMETER ********')
                    print(err)
            else:
                print('Inversion flag is set to False in WaterQuality.ini')

        except Exception as err:
            print('****** MISSING INVERSION PARAMETERS IN WATERDETECT.INI ********')
            print('No Inversion section or inversion flag in WaterQuality.ini. Update it with waterquality -GC')

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

        # save results to quality_parameters
        self.quality_parameters = {}

        for quality_param in self.qual_config.parameter.replace(' ', '').split(','):
            print(f'Calculating {quality_param} parameter.')

            # before calling the inversion function, certify that the necessary bands are loaded
            self.loader.load_raster_bands(inversion_algos.invert_funcs[quality_param]['bands'])

            # Ask for DWInversionAlgos to calculate the parameter matrix
            parameter = inversion_algos.invert_param(quality_param,
                                                     self.loader.product,
                                                     self.loader.raster_bands,
                                                     self.loader.invalid_mask,
                                                     self.qual_config.negative_values)

            if parameter is not None:
                # clear the parameters array and apply the Water mask, with no_data_values
                parameter = DWutils.apply_mask(parameter,
                                               ~(np.where(dw_image.water_mask == 255, 0, dw_image.water_mask).astype(
                                                 bool)),
                                               -9999)

                # save the parameter to be accessed
                self.quality_parameters.update({quality_param: parameter})

                # save the calculated parameter
                self.saver.save_array(parameter, quality_param, no_data_value=-9999)

                if pdf_merger_image is not None:

                    max_value, min_value = self.calc_param_limits(parameter)

                    pdf_merger_image.append(self.create_colorbar_pdf(product_name='colorbar_' + quality_param,
                                                                     colormap=self.qual_config.colormap,
                                                                     min_value=min_value,
                                                                     max_value=max_value))

                    pdf_merger_image.append(self.create_rgb_burn_in_pdf(product_name=quality_param,
                                                                        burn_in_arrays=parameter,
                                                                        colors=None,
                                                                        fade=1.,
                                                                        min_value=min_value,
                                                                        max_value=max_value,
                                                                        opt_relative_path=None,
                                                                        colormap=self.qual_config.colormap,
                                                                        uniform_distribution=self.qual_config.uniform_distribution,
                                                                        no_data_value=-9999))
        return parameter

    def calc_param_limits(self, parameter, no_data_value=-9999):

        valid = parameter[parameter != no_data_value]
        min_value = np.percentile(valid, 1) if self.qual_config.min_param_value is None else self.qual_config.min_param_value
        # min_value = np.quantile(valid, 0.25) if self.config.min_param_value is None else self.config.min_param_value
        max_value = np.percentile(valid, 75) if self.qual_config.max_param_value is None else self.qual_config.max_param_value
        # max_value = np.quantile(valid, 0.75) if self.config.max_param_value is None else self.config.max_param_value
        return max_value * 1.1, min_value * 0.8


def main():
    """
    The main function is just a wrapper to create a entry point script called waterquality.
    With the package installed you can just call waterquality -h in the command prompt to see the options.
    """
    parser = argparse.ArgumentParser(description='The waterquality adds a post-processing function to waterdetect '
                                                 'package to calc water quality parameters. '
                                                 'Waterdetect should be installed in the environment.',
                                     epilog="The waterquality uses the same WaterQuality.ini configuration file used "
                                            "in the waterdetect package, added with a [inversion] section."
                                            "To copy the package's default .ini file into the current directory, type:"
                                            ' `waterquality -GC .` without other arguments and it will copy  '
                                            'WaterQDetect.ini into the current directory.')

    parser.add_argument("-GC", "--GetConfig", help="Copy the WaterQuality.ini and the WaterDetect.ini into the current "
                                                   "directory and skips the processing. Once copied you can edit the "
                                                   ".ini file and launch the waterquality without -c option.",
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

    # product type (theia, sen2cor, landsat, etc.)
    # optional shape file
    # generate graphics (boolean)
    # name of config file with the bands-list for detecting, saving graphics, etc. If not specified, use default name
    #   if clip MIR or not, number of pixels to plot in graph, number of clusters, max pixels to process, etc.
    # name of the configuration .ini file (optional, default is WaterQuality.ini in the same folder

    args = parser.parse_args()

    # If GetConfig option, just copy the WaterQuality.ini to the current working directory
    if args.GetConfig:
        src = Path(__file__).parent/'WaterQuality.ini'
        dst = Path(os.getcwd())/'WaterQuality.ini'

        print(f'Copying {src} into current dir.')
        dst.write_text(src.read_text())
        print(f'WaterQuality.ini copied into {dst.parent}.')

        # Get the WaterDetect.ini using the waterdetect script
        os.system('waterdetect -GC')

    else:
        if (args.input is None) or (args.out is None):
            print('Please specify input and output folders (-i, -o)')

        else:
            DWWaterQuality.run_water_quality(input_folder=args.input, output_folder=args.out, shape_file=args.shp,
                                             product=args.product, config_wd=args.config_wd, config_wq=args.config_wq,
                                             single_mode=args.single)


# if called as a script, point to the main function of the WaterDetect package
if __name__ == '__main__':
    main()
