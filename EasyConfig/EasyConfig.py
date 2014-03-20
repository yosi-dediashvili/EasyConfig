from ConfigParser import SafeConfigParser

from Option import Option
from Section import Section

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

    def __init__(self, config):
        """ 
            The class is initialized with a path to a configuration file passed 
            via config, or a file-like object.
        """
        self.parser = SafeConfigParser()

        if isinstance(config, basestring):
            self.config_path = config
            config = open(self.config_path, "r")
        else:
            self.config_path = None

        self.parser.readfp(config)

        for section in self.parser.sections():
            options = self.parser.items(section)
            options = map(lambda op: Option(*op), options)
            self.add_section(Section(section, options))
    
    def __iter__(self):
        """ Iterate over all the section in the configuration. """
        for section in self.__dict__.values():
            if isinstance(section, Section):
                yield section  

    def __iadd__(self, section):
        """
            If section is of type Section, adds the section to the 
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
        if isinstance(section, Section):
            section_name = section.name
        elif isinstance(section, str):
            section_name = section
            section = Section(section)
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


