
class FieldLex:

	@staticmethod
	def line_to_lex(line):
		return FieldLex()

	def __init__(self, type, name):
		super().__init__()
		self.type = type
		self.name = name


class StructLex:
	def __init__(self, name, field_lexes):
		super().__init__()
		self.name = name
		self.field_lexes = field_lexes


def parse(file_lines):
	structs = []

	for lnumber, line in enumerate(file_lines):
		if line.strip().startswith("struct"):
			for elnumber, eline in enumerate(file_lines[lnumber:]):
				if "}" in eline:
					structs.append(file_lines[lnumber:lnumber + elnumber+1])
					break

	for struct in structs:
		header = struct[0]
		spos = header.find("struct ")
		if spos == -1:
			raise Exception("Invalid Header Format: " + header)
		namepos = spos + len("struct ")
		bracketpos = header.find("{", namepos)
		if bracketpos == -1:
			raise Exception("Opening bracket \"{\" must be on the same line: " + header)
		struct_name = header[namepos:bracketpos].strip()
		print(struct_name)
		fields = struct[1:-1]


def compile_file(file_path):
	file_lines = ""
	with open(file_path, 'r') as structfile:
		file_lines = structfile.readlines()
	parse(file_lines)


compile_file("test.struct")