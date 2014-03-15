from Option import Option

class Section(object):
    """ A section inside the configuration. """

    def __init__(self, section_name, options = []):
        self.name = section_name
        for option in options:
            self._add_option(option)
        
    def __iter__(self):
        """ Iterate over all the Options under the section. """
        for option in self.__dict__.values():
            if isinstance(option, Option):
                yield option

    def __getattribute__(self, name):
        """ 
            If name is Option, will retrieve its value, otherwise, will 
            retrieve the object itself.
        """
        attr = object.__getattribute__(self, name)
        if isinstance(attr, Option):
            return attr.value
        else:
            return attr

    def __setattr__(self, name, value):
        """
            If name point to Option, will verify that value matches the 
            type of option, and if not, will throw ValueError. In other
            cases, will simply store the value under the name.
        """
        option = self.__dict__.get(name)
        if not isinstance(option, Option):
            object.__setattr__(self, name, value)
        # It's an Option object.
        else:
            option.value = value
        
    def __iadd__(self, option):
        """
            If option is of type Option, adds the option to the 
            section (if it's not already present). Otherwise, the operator 
            does nothing.
        """
        if isinstance(option, Option):
            self._add_option(option)
        return self

    def add_option(self, option_name, option_value):
        """
            Adds a new option with the given option and value, and return 
            True. If option with that name already exists, the function 
            ignores the call, and returns False.
        """
        return self._add_option(
            Option(option_name, option_value))
        
    def _add_option(self, option):
        """ Unified logic for adding Option to the section. """
        if not self.__dict__.has_key(option.name):
            setattr(self, option.name, option)
            return True
        else:
            return False

    def __str__(self):
        return self.name