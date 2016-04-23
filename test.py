from first import TestMessage, AnotherMessage

with open('test.meta', 'wb+') as meta_file:
	message = TestMessage()
	message.id = 1234
	message.message = "Hello"
	meta_file.write(message.encode())
	meta_file.seek(0)
	read_buffer = meta_file.read()
	read_message = TestMessage.decode(read_buffer)[0]
	print(read_message.id)
	print(read_message.message)
