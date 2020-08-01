from collections import namedtuple
from struct import Struct, pack, unpack


Section = namedtuple("Section", "name, entries")
Entry = namedtuple("Entry", "key, values")
Value = namedtuple("Value", "type, data")

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
    magic, version, stroff = read_struct(f, HEADER_STRUCT)
    assert magic == MAGIC
    assert version == 1

    # Entries
    raw_sections = []
    while f.tell() < stroff:
        section_index, entry_count = read_struct(f, SECTION_STRUCT)
        raw_entries = []
        for _ in range(entry_count):
            key_index, value_count = read_struct(f, ENRTY_STRUCT)
            raw_values = []
            for _ in range(value_count):
                type_ = read_struct(f, TYPE_STRUCT)[0]
                if type_ == INTEGER_TYPE:
                    raw_data = read_struct(f, INTEGER_STRUCT)[0]
                elif type_ == FLOAT_TYPE:
                    raw_data = read_struct(f, FLOAT_STRUCT)[0]
                elif type_ == STRING_TYPE:
                    raw_data = read_struct(f, STRING_STRUCT)[0]
                else:
                    raise ValueError("invalid type %d at offset 0x%x" % (type_, f.tell() - TYPE_STRUCT.size))
                raw_values.append(Value(type_, raw_data))
            raw_entries.append(Entry(key_index, raw_values))
        raw_sections.append(Section(section_index, raw_entries))

    # String table
    assert f.tell() == stroff
    string_table = {}
    string_bytes = f.read()
    current_offset = 0
    while current_offset < len(string_bytes):
        null_offset = string_bytes.find(b"\0", current_offset)
        assert null_offset != -1
        string = string_bytes[current_offset:null_offset].decode("ascii")
        string_table[current_offset] = string
        current_offset = null_offset + 1

    # Replace string indices with string values
    sections = []
    for section_index, raw_entries in raw_sections:
        entries = []
        for key_index, raw_values in raw_entries:
            values = []
            for type_, raw_data in raw_values:
                if type_ == STRING_TYPE:
                    value = string_table[raw_data]
                else:
                    value = raw_data
                values.append(value)
            entries.append(Entry(string_table[key_index], values))
        sections.append(Section(string_table[section_index], entries))
    return sections


def read_struct(f, s):
    bs = f.read(s.size)
    assert len(bs) == s.size
    return s.unpack(bs)


def int_to_float(u32):
    return struct.unpack("<f", struct.pack)


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rb") as f:
        for section, entries in load(f):
            print("[%s]" % section)
            for key, values in entries:
                print("%s = %s" % (key, ", ".join(map(str, values))))
            print()
