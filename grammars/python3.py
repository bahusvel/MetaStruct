from compiler.ms_compiler import StructLex, FieldLex
from compiler.grammar import AbstractGrammar
import os

encode_decode_lib = """
import struct

def encode_float(input):
	return struct.pack(">f", input)
	
def encode_double(input):
	return struct.pack(">d", input)
	
def encode_int32(input):
	return struct.pack(">i", input)
	
def encode_uint32(input):
	return struct.pack(">I", input)
	
def encode_int64(input):
	return struct.pack(">l", input)
	
def encode_uint64(input):
	return struct.pack(">L", input)

def encode_bool(input):
	return struct.pack(">B", 1 if input else 0)

def encode_string(input):
	bytes = input.encode("utf-8")
	return encode_uint32(len(bytes)) + bytes

def encode_array(input, element_callback):
	total_bytes = b""
	for element in input:
		total_bytes += element_callback(element)
	return encode_uint32(len(total_bytes)) + total_bytes

def decode_float(bytes):
	return struct.unpack_from(">f", bytes)[0], bytes[4:]
	
def decode_double(bytes):
	return struct.unpack_from(">d", bytes)[0], bytes[8:]
	
def decode_int32(bytes):
	return struct.unpack_from(">i", bytes)[0], bytes[4:]
	
def decode_uint32(bytes):
	return struct.unpack_from(">I", bytes)[0], bytes[4:]
	
def decode_int64(bytes):
	return struct.unpack_from(">l", bytes)[0], bytes[8:]
	
def decode_uint64(bytes):
	return struct.unpack_from(">L", bytes)[0], bytes[8:]

def decode_bool(bytes):
	return struct.unpack_from(">B", bytes)[0] != 0, bytes[1:]

def decode_string(bytes):
	string_length, bytes = decode_uint32(bytes)
	return bytes[:string_length].decode("utf-8"), bytes[string_length:]

def decode_array(bytes, element_callback):
	temporary_array = []
	array_length, bytes = decode_uint32(bytes)
	original_length = len(bytes)
	while original_length - array_length < len(bytes) != 0:
		element, bytes = element_callback(bytes)
		temporary_array.append(element)
	return bytes
"""

package_template = "import libmstruct\n"

struct_template = """
class {struct_name}:

	{encode_method}

	{decode_method}

	def __init__():
		{fields}
"""

field_init = "self.{field_name} = None"

simple_field_encode = "buffer += libmstruct.encode_{field_type}(self.{field_name})"
array_field_encode = "buffer += libmstruct.encode_array(self.{field_name}, lambda element: {element_callback})"
struct_field_encode = "buffer += self.{field_name}.encode()"
simple_field_decode = "instance.{field_name}, buffer = libmstruct.decode_{field_type}(buffer)"
array_field_decode = "instance.{field_name}, buffer = libmstruct.decode_array(buffer, lambda buffer: {element_callback})"
struct_field_decode = "instance.{field_name}, buffer = {field_type}.decode(buffer)"

encode_func = """
	def encode(self):
		buffer = b""
		{fields}
		return buffer
"""

decode_func = """
	@staticmethod
	def decode(buffer):
		instance = {struct_name}()
		{fields}
		return instance, buffer
"""


class PythonGrammar(AbstractGrammar):
	def output_source_library(self):
		super().output_source_library()
		with open(self.output_directory + "libmstruct.py", 'w') as mstruct_lib:
			mstruct_lib.write(encode_decode_lib)

	def compile_field(self, field_lex):
		return field_init.format(field_name=field_lex.name)

	def add_encode(self, field_lexes):
		super().add_encode(field_lexes)
		fields = []
		for field_lex in field_lexes:
			if FieldLex.is_primitive(field_lex.type):
				fields.append(simple_field_encode.format(field_type=field_lex.type, field_name=field_lex.name))
			elif FieldLex.is_array(field_lex.type):
				fields.append(array_field_encode.format(field_type=field_lex.type, field_name=field_lex.name))
			elif FieldLex.is_struct(field_lex.type):
				fields.append(struct_field_encode.format(field_name=field_lex.name))
		field_string = "\n\t\t".join(fields)
		return encode_func.format(fields=field_string)

	def add_decode(self, field_lexes, struct_lex):
		fields = []
		for field_lex in field_lexes:
			if FieldLex.is_primitive(field_lex.type):
				fields.append(simple_field_decode.format(field_type=field_lex.type, field_name=field_lex.name))
			elif FieldLex.is_array(field_lex.type):
				fields.append(array_field_decode.format(field_type=field_lex.type, field_name=field_lex.name))
			elif FieldLex.is_struct(field_lex.type):
				fields.append(struct_field_decode.format(field_type=field_lex.type, field_name=field_lex.name))
		field_string = "\n\t\t".join(fields)
		return decode_func.format(fields=field_string, struct_name=struct_lex.name)

	def compile_struct(self, struct_lex, package_name):
		super().compile_struct(struct_lex, package_name)
		# fields
		fstrings = []
		for field in struct_lex.field_lexes:
			fstrings.append(self.compile_field(field))
		fields_string = '\n\t\t'.join(fstrings)
		# encode
		encode_string = self.add_encode(struct_lex.field_lexes)
		decode_string = self.add_decode(struct_lex.field_lexes, struct_lex)

		struct_string = struct_template.format(struct_name=struct_lex.name, fields=fields_string,
		                                       encode_method=encode_string, decode_method=decode_string)
		print(struct_string)

	def __init__(self, output_directory):
		super().__init__(output_directory)
		self.output_source_library()
