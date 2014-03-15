import sys
sys.path.append("..")

from StringIO import StringIO
import unittest

from EasyConfig import EasyConfig
EasyConfig = EasyConfig.EasyConfig
from EasyConfig import Option
Option = Option.Option
from EasyConfig import Section
Section = Section.Section

InitConfig = """
[InitSection]
bool_option = True
int_option = 20
float_option = 3.14
list_option = [1, 2, 3]
str_option = test
"""

UpgradeConfig = """
[InitSection]
bool_option = True
int_option = 20
upgrade_bool_option = False
[UpgradeSection]
some_int_option = 12512
some_float_option = 1.262
"""

UpgradedConfig = """
[InitSection]
bool_option = True
int_option = 20
float_option = 3.14
list_option = [1, 2, 3]
str_option = test
upgrade_bool_option = False
[UpgradeSection]
some_int_option = 12512
some_float_option = 1.262
"""

def get_config_str(config):
	s = StringIO()
	config.save(s)
	return s.getvalue()

class TestEasyConfig(unittest.TestCase):
	def setUp(self):
		self.config = EasyConfig(StringIO(InitConfig))

	def test_IterOptions(self):
		values = [True, 20, 3.14, [1, 2, 3], "test"]
		for option in self.config.InitSection:
			self.assertTrue(option.value in values)

	def test_IAddSection(self):
		self.config += Section("TestSection")
		self.assertEqual(len(list(self.config)), 2)

	def test_AddSectionNotPresent(self):
		self.config.add_section("TestSection")
		self.assertEqual(len(list(self.config)), 2)

	def test_AddSectionPresent(self):
		self.assertFalse(self.config.add_section("InitSection"))

	def test_IAddOption(self):
		self.config.InitSection += Option("new_bool_option", False)
		self.assertEqual(self.config.InitSection.new_bool_option, False)

	def test_AddOption(self):
		self.config.InitSection.add_option("new_bool_option", False)
		self.assertEqual(self.config.InitSection.new_bool_option, False)

	def test_Upgrade(self):
		upgrade_conf = EasyConfig(StringIO(UpgradeConfig))
		self.config.upgrade(upgrade_conf)
		upgraded_conf = EasyConfig(StringIO(UpgradedConfig))
		self.config.update_parser()

		# Verify all the data exists.
		for section in upgraded_conf:
			self.assertTrue(self.config.parser.has_section(str(section)))
			for option in section:
				self.assertTrue(
					self.config.parser.has_option(str(section), str(option)))
		
		# Verify that the original values was not changed.
		for section in self.config:
			upgrade_section = getattr(upgraded_conf, str(section))
			for option in section:
				upgrade_option = getattr(upgrade_section, str(option))
				self.assertEqual(option.value, upgrade_option)

if __name__ == "__main__":
	unittest.main(verbosity=10)