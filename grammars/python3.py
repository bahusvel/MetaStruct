from compiler.ms_compiler import StructLex, FieldLex
from compiler.grammar import AbstractGrammar
import os

encodes = {
	'float': 	'{output} += struct.pack(">f", {input})',
	'double': 	'{output} += struct.pack(">d", {input})',
	'int32': 	'{output} += struct.pack(">i", {input})',
	'uint32':	'{output} += struct.pack(">I", {input})',
	'int64':	'{output} += struct.pack(">l", {input})',
	'uint64':	'{output} += struct.pack(">L", {input})',
	'bool':		'{output} += struct.pack(">B", 1 if {input} else 0)',
	'struct':	'{output} += {input}.encode()'
}
encodes['string'] = 'string_bytes = {input}.encode("utf-8")\n' + encodes['uint32'].format(output='{output}', input='len(string_bytes)') + '\n{output} += string_bytes'


def encode_array(type):
	real_type = type[2:]
	array_string = 'tmp_buffer = b""\nfor element in {input}:\n\t'
	if FieldLex.is_primitive(real_type):
		array_string += encodes[real_type].format(output="tmp_buffer", input="element")
	elif FieldLex.is_array(real_type):
		raise Exception("Nested arrays are not yet supported")
	elif FieldLex.is_struct(real_type):
		array_string += encodes["struct"].format(output="tmp_buffer", input="element")
	array_string += "\n" + encodes["uint32"].format(output="{output}", input="len(tmp_buffer")
	array_string += "\n{output} += tmp_buffer"
	return array_string

decodes = {
	'float': 	'{output} = struct.unpack_from(">f", bytes, offset={offset})[0]\n{offset} += 4',
	'double': 	'{output} = struct.unpack_from(">d", bytes, offset={offset})[0]\n{offset} += 8',
	'int32': 	'{output} = struct.unpack_from(">i", bytes, offset={offset})[0]\n{offset} += 4',
	'uint32': 	'{output} = struct.unpack_from(">I", bytes, offset={offset})[0]\n{offset} += 4',
	'int64': 	'{output} = struct.unpack_from(">l", bytes, offset={offset})[0]\n{offset} += 8',
	'uint64': 	'{output} = struct.unpack_from(">L", bytes, offset={offset})[0]\n{offset} += 8',
	'bool': 	'{output} = struct.unpack_from(">B", bytes)[0] != 0\n{offset} += 8',
	'struct':	'{output}, {offset} = {field_type}.decode(bytes, offset={offset})'
}
decodes['string'] = decodes['uint32'].format(output="string_length", offset="{offset}") + '\n{output} = bytes[{offset}:string_length].decode("utf-8")\n{offset} += string_length'


def decode_array(type):
	real_type = type[2:]
	array_string = 'temporary_array = []\n'
	array_string += decodes['uint32'].format(output="array_length", offset="{offset}")
	array_string += '\noriginal_offset = {offset}\nwhile (original_offset + array_length) > {offset}\n\t'
	if FieldLex.is_primitive(real_type):
		array_string += re_indent(decodes[real_type].format(output="element", offset="{offset}"), ntabs=1)
	elif FieldLex.is_array(real_type):
		raise Exception("Nested arrays are not yet supported")
	elif FieldLex.is_struct(real_type):
		array_string += re_indent(encodes["struct"].format(output="element", offset="{offset}", field_type=real_type), ntabs=1)
	array_string += 'temporary_array.append(element)\n{output} = temporary_array'
	return array_string

package_template = "import struct\n"

struct_template = """
class {struct_name}:

	def encode(self):
		buffer = b""
		{encode_fields}
		return buffer

	@staticmethod
	def decode(buffer, offset=0):
		instance = {struct_name}()
		{decode_fields}
		return instance, offset

	def __init__():
		{init_fields}
"""

field_init = "self.{field_name} = None"


def re_indent(original_string, ntabs=2):
	re_indented = ""
	for line in original_string.split("\n"):
		re_indented += line + "\n" + ("\t" * ntabs)
	return re_indented


class PythonGrammar(AbstractGrammar):
	def compile_field(self, field_lex):
		return field_init.format(field_name=field_lex.name)

	def add_encode(self, field_lexes):
		super().add_encode(field_lexes)
		fields = []
		for field_lex in field_lexes:
			if FieldLex.is_primitive(field_lex.type):
				fields.append(encodes[field_lex.type].format(input="self."+field_lex.name, output="buffer"))
			elif FieldLex.is_array(field_lex.type):
				fields.append(encode_array(field_lex.type).format(input="self."+field_lex.name, output="buffer"))
			elif FieldLex.is_struct(field_lex.type):
				fields.append(encodes['struct'].format(input="self."+field_lex.name, output="buffer"))
		field_string = "\n".join(fields)
		return re_indent(field_string)

	def add_decode(self, field_lexes):
		fields = []
		for field_lex in field_lexes:
			if FieldLex.is_primitive(field_lex.type):
				fields.append(decodes[field_lex.type].format(offset="offset", output="instance."+field_lex.name))
			elif FieldLex.is_array(field_lex.type):
				fields.append(decode_array(field_lex.type).format(offset="offset", output="instance."+field_lex.name))
			elif FieldLex.is_struct(field_lex.type):
				fields.append(decodes['struct'].format(offset="offset", field_type=field_lex.type, output="instance."+field_lex.name))
		field_string = "\n".join(fields)
		return re_indent(field_string)

	def compile_struct(self, struct_lex, package_name):
		super().compile_struct(struct_lex, package_name)
		# fields
		fstrings = []
		for field in struct_lex.field_lexes:
			fstrings.append(self.compile_field(field))
		fields_string = '\n'.join(fstrings)
		fields_string = re_indent(fields_string)
		# encode
		encode_fields = self.add_encode(struct_lex.field_lexes)
		decode_fields = self.add_decode(struct_lex.field_lexes)

		struct_string = struct_template.format(struct_name=struct_lex.name, init_fields=fields_string,
		                                       encode_fields=encode_fields, decode_fields=decode_fields)
		print(struct_string)

	def __init__(self, output_directory):
		super().__init__(output_directory)
		self.output_source_library()
