
class AbstractGrammar:
	def compile_package(self, struct_lexes, package_name):
		pass

	def compile_struct(self, struct_lex, package_name):
		print("Processing " + repr(struct_lex))

	def output_source_library(self):
		pass

	def compile_field(self, field_lex):
		pass

	def add_encode(self, field_lexes):
		pass

	def add_decode(self, field_lexes):
		pass

	def __init__(self):
		super().__init__()
