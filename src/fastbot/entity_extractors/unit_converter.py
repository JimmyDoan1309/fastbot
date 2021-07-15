from pint import DimensionalityError, UnitRegistry
from typing import Text, Dict


class UnitConverter:
    def __init__(self):
        self.ureg = UnitRegistry()

    def _convert(self, value: int, from_unit: Text, to_unit: Text, unit_type: Text = 'all'):

        try:
            if unit_type == 'temperature':
                _q = self.ureg.Quantity
                _from_temp = _q(value, from_unit)
                return round(_from_temp.to(to_unit).magnitude, ndigits=2)
            else:
                new_value = value * getattr(self.ureg, from_unit)
                return new_value.to(to_unit).magnitude
        except DimensionalityError:
            return value

    def convert(self, inital_value: int, from_unit: Text, to_unit: Text, unit_type: Text = 'all'):
        if isinstance(inital_value, Dict):
            value = {}
            if inital_value.get('from'):
                value['from'] = self._convert(inital_value['from'], from_unit, to_unit, unit_type)
            if inital_value.get('to'):
                value['to'] = self._convert(inital_value['to'], from_unit, to_unit, unit_type)
        else:
            value = self._convert(inital_value, from_unit, to_unit, unit_type)
        return value
