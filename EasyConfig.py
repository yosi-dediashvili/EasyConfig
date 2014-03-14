import ConfigParser
from ConfigParser import SafeConfigParser


class EasyConfig(object):
    """
        This class is a wrapper for python's SafeConfigParser. The purpose of 
        this class is to allow for more convenient use of the ConfigParser, 
        along with adding built-in support for list type.

        Additionally, the class handle the type conversion implicitly inside
        it, so config options are retrieved with their appropriate type.

        Accessing configuration options with the class is performed as if the 
        options where class members, so, for example, if the configuration file
        as the following section and item:

        [SomeSection]
        some_item = some_value

        Then, accessing the item will look like that:

        conf = EasyConfig("path_to_config.ini")
        print conf.SomeSection.some_item # Will print "some_value"
        conf.SomeSection.some_item = 3.14 
        print conf.SomeSection.some_item # Will print 3.14
        conf.SomeSection.some_item += 0.01
        print conf.SomeSection.some_item # Will print 3.15

        A list config item is written as if it was a python's legit list deler-
        ation. For example:

        [SomeSection]
        some_list = [1, 2, 3]
    """
    
    class Section(object):
        """ A section inside the configuration. """

        def __init__(self, section_name, options):
            self.section_name = section_name
            for option in options:
                setattr(self, option.name, option)
            
        def __iter__(self):
            """ Iterate over all the Options under the section. """
            for option in self.__dict__.values():
                if isinstance(option, EasyConfig.Option):
                    yield option

        def __getattribute__(self, name):
            """ 
                If name is Option, will retrieve its value, otherwise, will 
                retrieve the object itself.
            """
            attr = object.__getattribute__(self, name)
            if isinstance(attr, EasyConfig.Option):
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
            if not isinstance(option, EasyConfig.Option):
                object.__setattr__(self, name, value)
            # It's an Option object.
            else:
                option.value = value
            
        def __str__(self):
            return self.section_name

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
            self.name = name
            self.option_type = None
            self._set_value(value)

        def __str__(self):
            return self.name

        def __setattr__(self, name, value):
            # If we're not trying to set the value.
            if name != "value":
                object.__setattr__(self, name, value)
            else:
                self._set_value(value)

        def __getattribute__(self, name):
            return object.__getattribute__(self, name)

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
                    converted_value = _try_convert(op_type, value)
                    if converted_value is None:
                        # Try the next one.
                        continue
                    else:
                        object.__setattr__(self, "value", converted_value)
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


    def __init__(self, config):
        """ 
            The class is initialized with a path to a configuration file passed 
            via config, or a file-like object.
        """
        self.parser = SafeConfigParser()

        if isinstance(config, basestring):
            self.config_path = config
            parser = open(self.config_path, "r")
        else:
            self.config_path = None

        self.parser.readfp(config)

        for section in self.parser.sections():
            options = self.parser.items(section)
            options = map(lambda op: EasyConfig.Option(*op), options)
            # Push the Section object.
            setattr(self, section, EasyConfig.Section(section, options))
    
    def __iter__(self):
        """ Iterate over all the section in the configuration. """
        for section in self.__dict__.values():
            if isinstance(section, EasyConfig.Section):
                yield section  

    def save(self, config = None):
        """
            Will pass the configuration to the ConfigParser module, and save 
            the configuration.

            If config is none, the configuration will be saved in the path 
            with which the object was initialized.

            If config is a path to a file, the configuration will be saved in
            that file. If config is a file-like object, it will be written to 
            it.
        """
        for section in self:
            for option in section:
                self.parser.set(str(section), str(option), option.value_str)

        if not config:
            if not self.config_path:
                raise RuntimeError(
                    "No output defined (either path or file-like object.")
            config = open(self.config_path, "w")
        elif isinstance(config, basestring):
            config = open(config, "w")

        self.parser.write(config)
