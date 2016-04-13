
class AbstractGrammar:

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

	def __init__(self, output_directory):
		self.output_directory = output_directory
		super().__init__()
