import re
from typing import Any, Dict, Optional, List, Tuple


class INIParseError(Exception):
    def __init__(self, message: str, line_number: int, line_content: str = ""):
        self.line_number = line_number
        self.line_content = line_content
        if line_content:
            super().__init__(f"Line {line_number}: {message} - '{line_content}'")
        else:
            super().__init__(f"Line {line_number}: {message}")


class INIParser:
    _SECTION_RE = re.compile(r'^\s*\[([^\]]+)\]\s*$')
    _KEY_VALUE_RE = re.compile(r'^\s*([^=;\s][^=;]*?)\s*=\s*(.*?)\s*$')
    _COMMENT_RE = re.compile(r'^\s*[;#]')
    _EMPTY_RE = re.compile(r'^\s*$')

    def __init__(self):
        self._data: Dict[str, Dict[str, Tuple[str, int]]] = {}
        self._sections_order: List[str] = []

    def read_file(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self._parse(content)

    def read_string(self, content: str) -> None:
        self._parse(content)

    def _parse(self, content: str) -> None:
        lines = content.splitlines()
        current_section: Optional[str] = None
        seen_keys: Dict[str, set] = {}

        for idx, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            if self._EMPTY_RE.match(line) or self._COMMENT_RE.match(line):
                continue

            section_match = self._SECTION_RE.match(raw_line)
            if section_match:
                current_section = section_match.group(1).strip()
                if current_section not in self._data:
                    self._data[current_section] = {}
                    self._sections_order.append(current_section)
                    seen_keys[current_section] = set()
                continue

            kv_match = self._KEY_VALUE_RE.match(raw_line)
            if kv_match:
                if current_section is None:
                    raise INIParseError(
                        "Key-value pair found outside of any section",
                        idx, raw_line
                    )
                key = kv_match.group(1).strip()
                value = kv_match.group(2)

                if key in seen_keys[current_section]:
                    raise INIParseError(
                        f"Duplicate key '{key}' in section '{current_section}'",
                        idx, raw_line
                    )

                seen_keys[current_section].add(key)
                self._data[current_section][key] = (value, idx)
                continue

            raise INIParseError("Invalid INI format", idx, raw_line)

    def sections(self) -> List[str]:
        return list(self._sections_order)

    def has_section(self, section: str) -> bool:
        return section in self._data

    def keys(self, section: str) -> List[str]:
        if section not in self._data:
            return []
        return list(self._data[section].keys())

    def has_key(self, section: str, key: str) -> bool:
        return section in self._data and key in self._data[section]

    def get(self, section: str, key: str, default: Optional[str] = None) -> Optional[str]:
        if section in self._data and key in self._data[section]:
            return self._data[section][key][0]
        return default

    def get_int(self, section: str, key: str, default: Optional[int] = None) -> Optional[int]:
        raw_value = self.get(section, key, None)
        if raw_value is None:
            return default
        try:
            return int(raw_value, 0)
        except ValueError:
            _, line_no = self._data[section][key]
            raise INIParseError(
                f"Value '{raw_value}' for key '{key}' is not a valid integer",
                line_no, raw_value
            )

    def get_float(self, section: str, key: str, default: Optional[float] = None) -> Optional[float]:
        raw_value = self.get(section, key, None)
        if raw_value is None:
            return default
        try:
            return float(raw_value)
        except ValueError:
            _, line_no = self._data[section][key]
            raise INIParseError(
                f"Value '{raw_value}' for key '{key}' is not a valid float",
                line_no, raw_value
            )

    def get_bool(self, section: str, key: str, default: Optional[bool] = None) -> Optional[bool]:
        raw_value = self.get(section, key, None)
        if raw_value is None:
            return default
        value_lower = raw_value.strip().lower()
        if value_lower in ('true', 'yes', '1', 'on'):
            return True
        if value_lower in ('false', 'no', '0', 'off'):
            return False
        _, line_no = self._data[section][key]
        raise INIParseError(
            f"Value '{raw_value}' for key '{key}' is not a valid boolean. "
            f"Use one of: true/false, yes/no, 1/0, on/off",
            line_no, raw_value
        )

    def get_line_number(self, section: str, key: str) -> Optional[int]:
        if section in self._data and key in self._data[section]:
            return self._data[section][key][1]
        return None

    def get_section_line_number(self, section: str) -> Optional[int]:
        if section in self._data and self._data[section]:
            first_key = next(iter(self._data[section]))
            return self._data[section][first_key][1]
        return None

    def items(self, section: str) -> Dict[str, str]:
        if section not in self._data:
            return {}
        return {k: v[0] for k, v in self._data[section].items()}
