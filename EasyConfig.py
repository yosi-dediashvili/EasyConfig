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

        def __init__(self, section_name, options = []):
            self.name = section_name
            for option in options:
                self._add_option(option)
            
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
            
        def __iadd__(self, option):
            """
                If option is of type EasyConfig.Option, adds the option to the 
                section (if it's not already present). Otherwise, the operator 
                does nothing.
            """
            if isinstance(option, EasyConfig.Option):
                self._add_option(option)
            return self

        def add_option(self, option_name, option_value):
            """
                Adds a new option with the given option and value, and return 
                True. If option with that name already exists, the function 
                ignores the call, and returns False.
            """
            return self._add_option(
                EasyConfig.Option(option_name, option_value))
            
        def _add_option(self, option):
            """ Unified logic for adding Option to the section. """
            if not self.__dict__.has_key(option.name):
                setattr(self, option.name, option)
                return True
            else:
                return False

        def __str__(self):
            return self.name

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
            self.add_section(EasyConfig.Section(section, options))
    
    def __iter__(self):
        """ Iterate over all the section in the configuration. """
        for section in self.__dict__.values():
            if isinstance(section, EasyConfig.Section):
                yield section  

    def __iadd__(self, section):
        """
            If section is of type EasyConfig.Section, adds the section to the 
            config (if it's not already present). Otherwise, the operator does
            nothing.
        """
        self.add_section(section)
        return self

    def add_section(self, section):
        """
            Adds a new section to the config. If section is str, it's converted
            to Section object. If section is Section, it's left untouched. 

            If a section with the same name does not already exists in the 
            config, it's added, and the function returns True. If such section 
            already exists, the call is ignored, and the function return False.
        """
        if isinstance(section, EasyConfig.Section):
            section_name = section.name
        elif isinstance(section, str):
            section_name = section
            section = EasyConfig.Section(section)
        else:
            raise TypeError("section should be either str or Section")

        if not self.__dict__.has_key(section_name):
            setattr(self, section_name, section)
            return True
        else:            
            return False

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
        if not config:
            if not self.config_path:
                raise RuntimeError(
                    "No output defined (either path or file-like object.")
            config = open(self.config_path, "w")
        elif isinstance(config, basestring):
            config = open(config, "w")

        self.update_parser()
        self.parser.write(config)

    def update_parser(self):
        """
            Updates the state of the internal ConfigParser.
        """
        for section in self:
            if not self.parser.has_section(str(section)):
                self.parser.add_section(str(section))
            for option in section:
                self.parser.set(str(section), str(option), option.value_str)

    def upgrade(self, other_easy_config):
        """
            Adds all the values from the other config to the current config. If
            the other config contains options that are already present in the 
            current config, the new options are ignored.
        """
        for other_section in other_easy_config:
            # False means that such section name already exists.
            if not self.add_section(other_section):
                for other_option in other_section:
                    section = getattr(self, other_section.name)
                    section += other_option


