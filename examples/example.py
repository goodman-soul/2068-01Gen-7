import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iniparser import INIParser, INIParseError


def main():
    parser = INIParser()

    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        parser.read_file(config_path)
    except INIParseError as e:
        print(f"配置文件解析错误: {e}")
        sys.exit(1)

    print("=" * 60)
    print("INI 配置读取库 - 使用示例")
    print("=" * 60)

    print(f"\n所有 Section: {parser.sections()}")

    print("\n" + "-" * 60)
    print("数据库配置 (database section)")
    print("-" * 60)
    print(f"  Host:              {parser.get('database', 'host')}")
    print(f"  Port:              {parser.get_int('database', 'port')}")
    print(f"  Username:          {parser.get('database', 'username')}")
    print(f"  Password:          {parser.get('database', 'password')}")
    print(f"  Database:          {parser.get('database', 'database')}")
    print(f"  Timeout:           {parser.get_int('database', 'connection_timeout')}秒")
    print(f"  Use SSL:           {parser.get_bool('database', 'use_ssl')}")
    print(f"  Max Connections:   {parser.get_int('database', 'max_connections')}")
    print(f"  Auto Commit:       {parser.get_bool('database', 'auto_commit')}")
    print(f"  Port (行号):       {parser.get_line_number('database', 'port')}")

    print("\n" + "-" * 60)
    print("串口配置 (serial_port section)")
    print("-" * 60)
    print(f"  Device:            {parser.get('serial_port', 'device')}")
    print(f"  Baud Rate:         {parser.get_int('serial_port', 'baud_rate')}")
    print(f"  Data Bits:         {parser.get_int('serial_port', 'data_bits')}")
    print(f"  Stop Bits:         {parser.get_int('serial_port', 'stop_bits')}")
    print(f"  Parity:            {parser.get('serial_port', 'parity')}")
    print(f"  Timeout:           {parser.get_int('serial_port', 'timeout')}ms")
    print(f"  Enable:            {parser.get_bool('serial_port', 'enable')}")

    print("\n" + "-" * 60)
    print("日志配置 (logging section)")
    print("-" * 60)
    print(f"  Level:             {parser.get('logging', 'level')}")
    print(f"  Log File:          {parser.get('logging', 'file')}")
    print(f"  Max File Size:     {parser.get_int('logging', 'max_file_size')} bytes")
    print(f"  Backup Count:      {parser.get_int('logging', 'backup_count')}")
    print(f"  Format:            {parser.get('logging', 'format')}")
    print(f"  Console Output:    {parser.get_bool('logging', 'console_output')}")
    print(f"  File Output:       {parser.get_bool('logging', 'file_output')}")
    print(f"  Rotate:            {parser.get_bool('logging', 'rotate')}")

    print("\n" + "-" * 60)
    print("默认值演示")
    print("-" * 60)
    print(f"  不存在的 section:  {parser.get('nonexistent', 'key', default='默认值')}")
    print(f"  不存在的 key:      {parser.get('database', 'nonexistent_key', default='fallback')}")
    print(f"  默认整数:          {parser.get_int('database', 'retries', default=3)}")
    print(f"  默认布尔值:        {parser.get_bool('database', 'debug', default=False)}")

    print("\n" + "-" * 60)
    print("错误处理演示")
    print("-" * 60)
    bad_config = """
[test]
invalid_value = not_a_number
"""
    p = INIParser()
    p.read_string(bad_config)
    try:
        p.get_int('test', 'invalid_value')
    except INIParseError as e:
        print(f"  捕获到解析错误: {e}")

    print("\n" + "=" * 60)
    print("示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
