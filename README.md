# MetaStruct
Dead simple binary encoding format
MetaStruct aims to provide as simple as possible binary data format that can be implemented and parsed in any programming language/hardware that is capable of operating on bytes, without compromising performance and compact sizes of binary formats. MetaStruct is statically typed and requires a struct definition that is used to encode the messages. 

# Encoding
Each struct is encoded field by field without any field tags, type tags or any other overhead (similar to how C structs look in memory), fields of variable length (arrays, strings, byte arrays) are prepended with their length (uint32) in bytes. Finally the encoded struct itself is prepended with its own length (uint32) in bytes allowing MetaStructs to be self delimiting and easy to parse in a streaming scenario. The MetaStruct definition file is required when parsing or encoding a struct as there are no delimiters available in the encoded binary data.

# Supported Data Types
- float, double
- byte
- int32, uint32
- int64, uint64
- bool (occupies 1 byte)
- string ()
- dynamic length arrays of all of the above
- nested structs
- Enums (as int32)
