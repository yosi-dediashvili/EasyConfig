CONFIG_0_BEFORE = """
[ListSection]
list_item = [1, 2, 3]
empty_list = []
""".strip()
CONFIG_0_AFTER = """
[ListSection]
list_item = [1, 2, 3, 4]
empty_list = [1]
""".strip()

CONFIG_1_BEFORE = """
[SomeSection]
int_item = 1
str_item = str1
""".strip()
CONFIG_1_AFTER = """
[SomeSection]
int_item = 2
str_item = str2
""".strip()

from EasyConfig import EasyConfig
from StringIO import StringIO

conf = EasyConfig(StringIO(CONFIG_0_BEFORE))
assert(type(conf.ListSection.list_item))
conf.ListSection.list_item.append(4)
conf.ListSection.empty_list.append(1)
new = StringIO()
conf.save(new)

if CONFIG_0_AFTER != new.getvalue().strip():
	print "CONFIG_0 failed:"
	print new.getvalue()
else:
	print "CONFIG_0 succeeded."

conf = EasyConfig(StringIO(CONFIG_1_BEFORE))
conf.SomeSection.int_item = 2
conf.SomeSection.str_item = "str2"
new = StringIO()
conf.save(new)
if CONFIG_1_AFTER != new.getvalue().strip():
	print "CONFIG_1 failed."
	print new.getvalue()
else:
	print "CONFIG_1 succeeded."