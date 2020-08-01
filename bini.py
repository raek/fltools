from collections import namedtuple
from struct import Struct


Section = namedtuple("Section", "name, entries")
Entry = namedtuple("Entry", "key, values")

HEADER_STRUCT = Struct("<LLL")
SECTION_STRUCT = Struct("<HH")
ENRTY_STRUCT = Struct("<HB")
TYPE_STRUCT = Struct("<B")
INTEGER_STRUCT = Struct("<L")
FLOAT_STRUCT = Struct("<f")
STRING_STRUCT = Struct("<Hxx")

INTEGER_TYPE = 1
FLOAT_TYPE = 2
STRING_TYPE = 3

MAGIC = 0x494e4942 # "BINI"


def load(f):
    # Header
    magic, version, string_table_offset = read_struct(f, HEADER_STRUCT)
    assert magic == MAGIC
    assert version == 1

    # String table
    f.seek(string_table_offset)
    string_table = {}
    string_bytes = f.read()
    current_offset = 0
    while current_offset < len(string_bytes):
        null_offset = string_bytes.find(b"\0", current_offset)
        assert null_offset != -1
        string = string_bytes[current_offset:null_offset].decode("ascii")
        string_table[current_offset] = string
        current_offset = null_offset + 1

    # Entries
    f.seek(HEADER_STRUCT.size)
    sections = []
    while f.tell() < string_table_offset:
        section_index, entry_count = read_struct(f, SECTION_STRUCT)
        section_name = string_table[section_index]
        entries = []
        for _ in range(entry_count):
            key_index, value_count = read_struct(f, ENRTY_STRUCT)
            key_name = string_table[key_index]
            values = []
            for _ in range(value_count):
                type_ = read_struct(f, TYPE_STRUCT)[0]
                if type_ == INTEGER_TYPE:
                    value = read_struct(f, INTEGER_STRUCT)[0]
                elif type_ == FLOAT_TYPE:
                    value = read_struct(f, FLOAT_STRUCT)[0]
                elif type_ == STRING_TYPE:
                    string_index = read_struct(f, STRING_STRUCT)[0]
                    value = string_table[string_index]
                else:
                    raise ValueError("invalid type %d at offset 0x%x" % (type_, f.tell() - TYPE_STRUCT.size))
                values.append(value)
            entries.append(Entry(key_name, values))
        sections.append(Section(section_name, entries))

    assert f.tell() == string_table_offset
    return sections


def read_struct(f, s):
    bs = f.read(s.size)
    assert len(bs) == s.size
    return s.unpack(bs)


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rb") as f:
        for section, entries in load(f):
            print("[%s]" % section)
            for key, values in entries:
                print("%s = %s" % (key, ", ".join(map(str, values))))
            print()
