EasyConfig
==========

A wrapper class for [python's ConfigParser class](http://docs.python.org/2.7/library/configparser.html) that represent the configuration items as objects.

## Usage:

### Accessing configuration items:
Given the following configuration file:
```ini
[SomeSection]
some_item = some_value
```

Then, accessing the item will look like that:

```Python
conf = EasyConfig("path_to_config.ini")
print conf.SomeSection.some_item # Will print "some_value"
conf.SomeSection.some_item = 3.14 
print conf.SomeSection.some_item # Will print 3.14
conf.SomeSection.some_item += 0.01
print conf.SomeSection.some_item # Will print 3.15
```

A list option is written as if it was a python's legit list declaration. For example:

```ini
[SomeSection]
some_list = [1, 2, 3]
```

And, accessing it is as simple as:

```python
# Evaluates to True.
conf.SomeSection.some_list[0] == 1 

conf.SomeSection.some_list.append(4)
# Will print [1, 2, 3, 4]
print conf.SomeSection.some_list
```

### Adding new configuration items:

Adding Option to the configuration is performed as followed:

```python
conf.SomeSection += EasyConfig.Option("new_list_option", [1, 2, 3])
# Evaluates to True.
conf.SomeSection.new_list_option == [1, 2, 3]

# Another method
conf.SomeSection.add_option("new_list_option", [1, 2, 3])
```

Adding Section is done the same way:

```python
conf += EasyConfig.Section("new_section")
# Another method
conf.add_section("new_section")
```
