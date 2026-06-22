import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iniparser import INIParser, INIParseError


class TestINIParserBasic(unittest.TestCase):
    def test_empty_config(self):
        parser = INIParser()
        parser.read_string("")
        self.assertEqual(parser.sections(), [])

    def test_single_section(self):
        content = """
[section1]
key1 = value1
key2 = value2
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertEqual(parser.sections(), ["section1"])
        self.assertEqual(parser.keys("section1"), ["key1", "key2"])
        self.assertEqual(parser.get("section1", "key1"), "value1")
        self.assertEqual(parser.get("section1", "key2"), "value2")

    def test_multiple_sections(self):
        content = """
[section1]
key1 = value1

[section2]
key2 = value2
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertEqual(parser.sections(), ["section1", "section2"])
        self.assertTrue(parser.has_section("section1"))
        self.assertTrue(parser.has_section("section2"))
        self.assertFalse(parser.has_section("section3"))

    def test_comments_and_blank_lines(self):
        content = """
# This is a comment
; This is also a comment

[section1]
# Comment in section
key1 = value1
; Another comment
key2 = value2

"""
        parser = INIParser()
        parser.read_string(content)
        self.assertEqual(parser.sections(), ["section1"])
        self.assertEqual(parser.get("section1", "key1"), "value1")
        self.assertEqual(parser.get("section1", "key2"), "value2")


class TestINIParserTypes(unittest.TestCase):
    def test_get_string(self):
        content = """
[test]
str1 = hello world
str2 = 12345
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertEqual(parser.get("test", "str1"), "hello world")
        self.assertEqual(parser.get("test", "str2"), "12345")

    def test_get_int(self):
        content = """
[test]
int1 = 42
int2 = -10
int3 = 0xFF
int4 = 0b1010
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertEqual(parser.get_int("test", "int1"), 42)
        self.assertEqual(parser.get_int("test", "int2"), -10)
        self.assertEqual(parser.get_int("test", "int3"), 255)
        self.assertEqual(parser.get_int("test", "int4"), 10)

    def test_get_int_invalid(self):
        content = """
[test]
bad = not_a_number
"""
        parser = INIParser()
        parser.read_string(content)
        with self.assertRaises(INIParseError) as ctx:
            parser.get_int("test", "bad")
        self.assertIn("not a valid integer", str(ctx.exception))
        self.assertEqual(ctx.exception.line_number, 3)

    def test_get_float(self):
        content = """
[test]
float1 = 3.14
float2 = -2.5
float3 = 1e10
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertAlmostEqual(parser.get_float("test", "float1"), 3.14)
        self.assertAlmostEqual(parser.get_float("test", "float2"), -2.5)
        self.assertAlmostEqual(parser.get_float("test", "float3"), 1e10)

    def test_get_bool(self):
        content = """
[test]
b1 = true
b2 = false
b3 = yes
b4 = no
b5 = 1
b6 = 0
b7 = on
b8 = off
b9 = True
b10 = FALSE
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertTrue(parser.get_bool("test", "b1"))
        self.assertFalse(parser.get_bool("test", "b2"))
        self.assertTrue(parser.get_bool("test", "b3"))
        self.assertFalse(parser.get_bool("test", "b4"))
        self.assertTrue(parser.get_bool("test", "b5"))
        self.assertFalse(parser.get_bool("test", "b6"))
        self.assertTrue(parser.get_bool("test", "b7"))
        self.assertFalse(parser.get_bool("test", "b8"))
        self.assertTrue(parser.get_bool("test", "b9"))
        self.assertFalse(parser.get_bool("test", "b10"))

    def test_get_bool_invalid(self):
        content = """
[test]
bad = maybe
"""
        parser = INIParser()
        parser.read_string(content)
        with self.assertRaises(INIParseError) as ctx:
            parser.get_bool("test", "bad")
        self.assertIn("not a valid boolean", str(ctx.exception))
        self.assertEqual(ctx.exception.line_number, 3)


class TestINIParserDefaults(unittest.TestCase):
    def test_default_missing_section(self):
        parser = INIParser()
        parser.read_string("[section1]\nkey1 = value1")
        self.assertEqual(parser.get("missing", "key", "default"), "default")
        self.assertEqual(parser.get_int("missing", "key", 42), 42)
        self.assertEqual(parser.get_bool("missing", "key", True), True)
        self.assertEqual(parser.get_float("missing", "key", 3.14), 3.14)

    def test_default_missing_key(self):
        parser = INIParser()
        parser.read_string("[section1]\nkey1 = value1")
        self.assertEqual(parser.get("section1", "missing_key", "default"), "default")
        self.assertEqual(parser.get_int("section1", "missing_key", 99), 99)
        self.assertEqual(parser.get_bool("section1", "missing_key", False), False)

    def test_default_none(self):
        parser = INIParser()
        parser.read_string("[section1]\nkey1 = value1")
        self.assertIsNone(parser.get("section1", "missing"))
        self.assertIsNone(parser.get_int("section1", "missing"))
        self.assertIsNone(parser.get_bool("section1", "missing"))


class TestINIParserErrors(unittest.TestCase):
    def test_duplicate_key(self):
        content = """
[section1]
key1 = value1
key1 = value2
"""
        parser = INIParser()
        with self.assertRaises(INIParseError) as ctx:
            parser.read_string(content)
        self.assertIn("Duplicate key", str(ctx.exception))
        self.assertIn("key1", str(ctx.exception))
        self.assertEqual(ctx.exception.line_number, 4)

    def test_key_outside_section(self):
        content = """
key1 = value1
[section1]
"""
        parser = INIParser()
        with self.assertRaises(INIParseError) as ctx:
            parser.read_string(content)
        self.assertIn("outside of any section", str(ctx.exception))
        self.assertEqual(ctx.exception.line_number, 2)

    def test_invalid_format(self):
        content = """
[section1]
this is not valid
"""
        parser = INIParser()
        with self.assertRaises(INIParseError) as ctx:
            parser.read_string(content)
        self.assertIn("Invalid INI format", str(ctx.exception))
        self.assertEqual(ctx.exception.line_number, 3)


class TestINIParserLineNumbers(unittest.TestCase):
    def test_line_tracking(self):
        content = """
# comment
[section1]
key1 = value1
key2 = value2

[section2]
key3 = value3
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertEqual(parser.get_line_number("section1", "key1"), 4)
        self.assertEqual(parser.get_line_number("section1", "key2"), 5)
        self.assertEqual(parser.get_line_number("section2", "key3"), 8)
        self.assertIsNone(parser.get_line_number("missing", "key"))
        self.assertIsNone(parser.get_line_number("section1", "missing_key"))


class TestINIParserItems(unittest.TestCase):
    def test_items(self):
        content = """
[section1]
key1 = value1
key2 = value2
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertEqual(parser.items("section1"), {"key1": "value1", "key2": "value2"})
        self.assertEqual(parser.items("missing"), {})


class TestINIParserHasKey(unittest.TestCase):
    def test_has_key(self):
        content = """
[section1]
key1 = value1
"""
        parser = INIParser()
        parser.read_string(content)
        self.assertTrue(parser.has_key("section1", "key1"))
        self.assertFalse(parser.has_key("section1", "missing"))
        self.assertFalse(parser.has_key("missing", "key1"))


class TestINIExampleConfig(unittest.TestCase):
    def test_example_config(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "examples",
            "config.ini"
        )
        parser = INIParser()
        parser.read_file(config_path)

        self.assertEqual(parser.sections(), ["database", "serial_port", "logging"])

        self.assertEqual(parser.get("database", "host"), "localhost")
        self.assertEqual(parser.get_int("database", "port"), 5432)
        self.assertEqual(parser.get("database", "username"), "admin")
        self.assertEqual(parser.get("database", "password"), "secret123")
        self.assertEqual(parser.get("database", "database"), "myapp_db")
        self.assertEqual(parser.get_int("database", "connection_timeout"), 30)
        self.assertTrue(parser.get_bool("database", "use_ssl"))
        self.assertEqual(parser.get_int("database", "max_connections"), 100)
        self.assertFalse(parser.get_bool("database", "auto_commit"))

        self.assertEqual(parser.get("serial_port", "device"), "/dev/ttyUSB0")
        self.assertEqual(parser.get_int("serial_port", "baud_rate"), 115200)
        self.assertEqual(parser.get_int("serial_port", "data_bits"), 8)
        self.assertEqual(parser.get_int("serial_port", "stop_bits"), 1)
        self.assertEqual(parser.get("serial_port", "parity"), "none")
        self.assertEqual(parser.get_int("serial_port", "timeout"), 5000)
        self.assertTrue(parser.get_bool("serial_port", "enable"))

        self.assertEqual(parser.get("logging", "level"), "INFO")
        self.assertEqual(parser.get("logging", "file"), "/var/log/myapp.log")
        self.assertEqual(parser.get_int("logging", "max_file_size"), 10485760)
        self.assertEqual(parser.get_int("logging", "backup_count"), 5)
        self.assertTrue(parser.get_bool("logging", "console_output"))
        self.assertTrue(parser.get_bool("logging", "file_output"))
        self.assertTrue(parser.get_bool("logging", "rotate"))


if __name__ == "__main__":
    unittest.main()
