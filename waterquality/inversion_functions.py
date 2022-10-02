# This module contains the functions that will be used to invert from reflectances to water quality parameters
# The dicionary `functions`` will be used by the waterquality module:
# function = {
#   'name_of_the_parameter': {'function': any_function}, 'units': 'units to be displayed in the report',
#   'name_of_the_parameter2': .....
# }

# Any bands can be used to compute the final value. The name of the band must match the internal name used by WaterDetect
# It is enough to put the band name as an argument in the function

# Below is an example extracted from Nechad et al. (2010)
def nechad(Red, a=610.94, c=0.2324):
    spm = a * Red / (1 - (Red / c))
    return spm

functions = {
    'SPM_Nechad': {
        'function': nechad,
        'units': 'mg/l'
    },
}

