import click


@click.group()
def mstruct():
	print("Welcome to mStruct")

@click.command()
def validate():
	pass

@click.command()
def compile():
	pass

mstruct.add_command(compile)
mstruct.add_command(validate)

if __name__ == '__main__':
	mstruct()
