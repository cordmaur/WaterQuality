from waterdetect.Common import DWBaseConfig


class DWConfigQuality(DWBaseConfig):

    _config_file = 'WaterQuality.ini'

    @property
    def inversion(self):
        return self.get_option('Inversion', 'inversion', evaluate=True)

    @property
    def parameter(self):
        if self.inversion:
            return self.get_option('Inversion', 'parameter', evaluate=False)
        else:
            return ''

    @property
    def parameter_unit(self):

        return self._units[self.parameter]

    @property
    def negative_values(self):
        return self.get_option('Inversion', 'negative_values', evaluate=False)

    @property
    def min_param_value(self):
        return self.get_option('Inversion', 'min_param_value', evaluate=True)

    @property
    def max_param_value(self):
        return self.get_option('Inversion', 'max_param_value', evaluate=True)

    @property
    def max_param_percentile(self):
        return self.get_option('Inversion', 'max_param_percentile', evaluate=True)

    @property
    def colormap(self):
        return self.get_option('Inversion', 'colormap', evaluate=False)

    @property
    def uniform_distribution(self):
        return self.get_option('Inversion', 'uniform_distribution', evaluate=True)

