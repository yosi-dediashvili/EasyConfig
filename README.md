EasyConfig
==========

A wrapper class for python's ConfigParser class that represent the config items as objects.

Usage:

Given the following config file:
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

A list config item is written as if it was a python's legit list declaration. For example:

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