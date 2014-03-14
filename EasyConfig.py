from ConfigParser import SafeConfigParser

class EasyConfig(object):
    """
        This class is a wrapper for python's SafeConfigParser. The purpose of 
        this class is to allow for more convenient use of the ConfigParser, 
        along with adding built-in support for list type.

        Additionally, the class handle the type conversion implicitly inside
        it, so config items are retrieved with their appropriate type.

        Accessing configuration items with the class is performed as if the 
        items where class members, so, for example, if the configuration file
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
        pass

    class Item(object):
        """ An item under some section. """
        pass

    def __init__(self, config_path = None, config_content = None):
        """ 
            The class is initialized with either a path to a configuration file
            passed via config_path, or configuration content via config_content.
        """
        pass

    def __dir__(self):
        """ Returns all the section that the configuration has. """
        pass

    def __iter__(self):
        """ Iterate over the sections. """
        pass

    def __getattr__(self, name):
        """ Retrieve a section with the given name. """
        pass

    def __setattr__(self, name, value):
        raise NotImplementedError(
            "Changing values from outside the class is not allowed.")

