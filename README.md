# MetaStruct
Dead simple binary encoding format
MetaStruct aims to provide as simple as possible binary data format that can be implemented and parsed in any programming language/hardware that is capable of operating on bytes. MetaStrcuts purposefully avoids complex encoding techniques such as varints or bit packing in order to allow the implementation to be simple. MetaStructs are statically typed and require a struct definition file that is used to encode and parse the messages. 

# Example
MetaStructs uses *.struct datastrcutre definition files in order to represent the format. You are encouraged to document those files providing a reasonable definition and documentation for your protocol that utilizes MetaStructs.
```
// C Style comments
struct Message {
  int32   id;
  string  data;
}
```

# Encoding
Each struct is encoded field by field without any field tags, type tags or any other overhead (similar to how C structs look in memory), fields of variable length (arrays, strings, byte arrays) are prepended with their length (uint32) in bytes. Finally the encoded struct itself is prepended with its own length (uint32) in bytes allowing MetaStructs to be self delimiting and easy to parse in a streaming scenario.

# Supported Data Types
- float, double
- byte
- int32, uint32 (stored as 4 bytes, no varint encoding)
- int64, uint64 (stored as 8 bytes, no varint encoding)
- bool (occupies 1 byte)
- string ()
- dynamic length arrays of all of the above
- nested structs
- Enums (as int32)
- Cyclical structs are not allowed

# Extensibility
Order of elements in the struct matters, elements that are appended to the existing struct at the end is the only form of extension for MetaStructs, allowing older message formats to remain backwards compatible:
```
// Old message:
struct Message {
  int32   id;
  string  data;
}
// New message:
struct Message {
  int32   id;
  string  data;
  string  from;
}
```
In this example new message is backwards compatible with the old message, if the new message was sent to a system using the old message format old message would be decoded with the fields defined in its format and the rest(string from) would be stored as unencoded data in special field, so when the message is stored to forwarded to another client with the new protocol it could be decoded correctly.
