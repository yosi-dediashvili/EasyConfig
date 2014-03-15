from ConfigParser import SafeConfigParser

class Option(object):
    """ 
        An item under some section. The type of the option is one from the
        following: int, float, bool, list and str. When a value is converted
        to its real type, the type lookup is performed at that order.

        bool options are considered as such if they match any of the string
        defined under SafeConfigParser._boolean_states.
    """

    # The order in this list is crucial, otherwise, we might end up casting 
    # to the wrong type. For example, if we'll try to cast the value "1" to 
    # float before int, we'll get the float type because this is a valid 
    # format for float.
    OPTION_TYPES = [int, float, bool, list, str]

    def __init__(self, name, value):
        """
            Init an Option instance with the given option name, and value. 
            The name should be a string, and value can be either a string
            representation of the supported type, or the type itself. 
        """
        self.name = name
        self.option_type = None
        # Pass the value as string.
        self._set_value(value)

    def __str__(self):
        return self.name

    def __setattr__(self, name, value):
        # If we're not trying to set the value.
        if name != "value":
            object.__setattr__(self, name, value)
        else:
            self._set_value(value)

    @property
    def value_str(self):
        """ Returns the value as str object. """
        return str(self.value)

    def _set_value(self, value):
        """ 
            Set the value of the Option. value is provided as str, and the
            function resolves the real type of the value, and stores it 
            after converting it to that type. 

            If _set_value is called when option_type is not set, it will 
            also set it according to the type that is resolved for value,
            otherwise, the function will only try to convert value to the
            current option_type.
        """
        value = str(value)
        def _try_convert(to_type, value):
            try:
                if to_type == list:
                    v = eval(value)
                    if isinstance(v, list):
                        return v
                elif to_type == bool:
                    return SafeConfigParser._boolean_states[value.lower()]
                else:
                    return to_type(value)
            except (
                ValueError, SyntaxError, KeyError, NameError, TypeError):
                # Ignore the error, we'll return None anyway.
                pass

            return None
        
        # If we haven't already set the the type of the option, resolve it.
        if self.option_type is None:
            for op_type in self.OPTION_TYPES:
                v = _try_convert(op_type, value)
                if v is None:
                    # Try the next one.
                    continue
                else:
                    object.__setattr__(self, "value", v)
                    self.option_type = op_type
                    break

            if self.value is None:
                raise ValueError(
                    "The value \"{0}\" does not match any of the types: {1}"
                    .format(value, self.OPTION_TYPES))
        # Otherwise, we allow only the type that is already set.
        else:
            v = _try_convert(self.option_type, value)
            if v is None:
                raise ValueError(
                    "The value \"{0}\" is not legal {1} value."
                    .format(value, self.option_type))
            else:
                object.__setattr__(self, "value", v)