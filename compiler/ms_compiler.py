import re


class FieldLex:

	PRIMITIVE_TYPES = ["float", "double", "byte", "int32", "uint32", "int64", "uint64", "bool", "string"]

	@staticmethod
	def is_primitive(type):
		return type in FieldLex.PRIMITIVE_TYPES

	@staticmethod
	def is_array(type):
		return type.startswith("[]")

	@staticmethod
	def is_struct(type):
		return (not FieldLex.is_primitive(type)) and (not FieldLex.is_array(type))

	@staticmethod
	def line_to_lex(line):
		processed = line.strip().split(" ")
		type = processed[0]
		name = processed[-1]
		if type == "" or name == "":
			return None
		return FieldLex(type, name)

	def validate(self, struct_types):
		if not FieldLex.validate_type(self.type, struct_types):
			raise Exception("Invalid Type for: " + repr(self))

	@staticmethod
	def validate_type(type, struct_types):
		if FieldLex.is_primitive(type):
			return True
		if FieldLex.is_array(type):
			return FieldLex.validate_type(type[2:], struct_types)
		if type in struct_types:
			return True
		return False

	def __repr__(self):
		return "field{" + self.type + ", " + self.name + "}"

	def __init__(self, type, name):
		super().__init__()
		self.type = type
		self.name = name


class StructLex:

	@staticmethod
	def lines_to_lex(line_number, all_lines):
		struct_lines = None
		for elnumber, eline in enumerate(all_lines[line_number:]):
			if "}" in eline:
				struct_lines = all_lines[line_number:line_number + elnumber+1]
				break
		if struct_lines is None:
			raise Exception("Invalid Struct Declaration: " + all_lines[line_number])

		header = struct_lines[0]
		spos = header.find("struct ")
		if spos == -1:
			raise Exception("Invalid Header Format: " + header)
		namepos = spos + len("struct ")
		bracketpos = header.find("{", namepos)
		if bracketpos == -1:
			raise Exception("Opening bracket \"{\" must be on the same line: " + header)
		struct_name = header[namepos:bracketpos].strip()

		fields = struct_lines[1:-1]
		field_lexes = []
		for field in fields:
			field_lex = FieldLex.line_to_lex(field)
			if field_lex is not None:
				field_lexes.append(field_lex)
		return StructLex(struct_name, field_lexes)

	def validate(self, all_struct_types):
		if len(self.field_lexes) == 0:
			raise Exception("Empty Struct: " + self.name)
		for field_lex in self.field_lexes:
			field_lex.validate(all_struct_types)

	def __repr__(self):
		return "struct:" + self.name + repr(self.field_lexes)

	def __init__(self, name, field_lexes):
		super().__init__()
		self.name = name
		self.field_lexes = field_lexes


def parse(file_lines):
	# remove comments
	line_string = "".join(file_lines)
	line_string = re.sub("//.*", "", line_string)
	line_string = re.sub("/\*.*\*/", "", line_string, flags=re.M | re.S)
	# remove empties
	file_lines = list(filter(lambda line: line != "" and line != "\n", line_string.splitlines()))
	# parse out structs
	structs = []
	for lnumber, line in enumerate(file_lines):
		if line.strip().startswith("struct"):
			structs.append(StructLex.lines_to_lex(lnumber, file_lines))
	return structs


def validate(structs):
	all_struct_types = list(map(lambda s: s.name, structs))
	for struct in structs:
		struct.validate(all_struct_types)


def compile_file(file_path, grammar):
	file_lines = []
	with open(file_path, 'r') as structfile:
		file_lines = structfile.readlines()
	structs = parse(file_lines)
	print(structs)
	validate(structs)
	for struct in structs:
		grammar.compile_struct(struct, structfile)

if __name__ == "__main__":
	from grammars.c import CGRammar
	compile_file("../test.struct", CGRammar("./"))