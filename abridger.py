import re
import sys
import xml.etree.ElementTree as ET

class Error(Exception):
	pass

class InputError(Error):
	def __init__(self, message):
		self.message = message

def main(args):
	
	action = "abridge"
	folder = ""
	for arg in args[1:]:
		if arg == "--help":
			print_usage()
			exit()
		elif arg == "-f":
			action = "full text"
		elif arg == "-l":
			action = "list files"
		elif arg[0] == "-":
			raise(InputError("Unknown argument"))
		elif folder == "":
			folder = arg
		else:
			raise(InputError("Too many folder parameters"))
	
	if folder == "":
		raise(InputError("Folder parameter is missing"))
			
	
	veto_files = [
		"titlepage.xhtml",
		"imprint.xhtml",
		"etymology.xhtml", # moby dick
		"extracts.xhtml",  # moby dick
		"preamble.xhtml",     # alice in wonderland
		"preface.xhtml",
		"editors-preface.xhtml", # jeeves stories
		"introduction.xhtml",
		"frontispiece.xhtml",
		"epigraph.xhtml",
		"dedication.xhtml",
		"halftitle.xhtml",
		"endnotes.xhtml",
		# "conclusion.xhtml", # alice in wonderland, not silas marner
		"loi.xhtml",
		"colophon.xhtml",
		"uncopyright.xhtml",
	]
	veto_tags = [
		"h1",
		"h2",
		"h3",
		"title",
		"a",
	]
	white_space = r" —\n"
	
	if action in ("list files",):
		all_files = get_text_files(folder, [])
		body_files = get_text_files(folder, veto_files)
		text = ""
		for file_name in all_files:
			if file_name not in body_files:
				text += "# "
			text += file_name + "\n"
	
	if action in ("abridge", "full text"):
		text = extract_text_from_se_book(folder, veto_files, veto_tags)
	
	if action in ("abridge",):
		text = abridge_text(text, white_space)
	
	print(text)

def print_usage():
	print("Usage:")
	print(" python3 abridger.py [-f] <source_folder>")
	print("   -f  Export the full text of the ebook after removing xml tags")
	print("   -l  List files that will be included in the full text")
	print("   <source_folder>")
	print("       The location of the Standard Ebooks source folder")
	print("   --help")
	print("       Print this usage and exit")

def abridge_text(text, white_space):
	pattern = "(.*?[" + white_space + "])(.*)"
	result = ""
	while True:
		match = re.search(pattern, text, re.DOTALL)
		if match:
			result += match.group(1)
			next_pattern = "[" + white_space + "](" + re.escape(match.group(1)) + ")(.*)"
			next_match = re.search(next_pattern, match.group(2), re.DOTALL)
			if next_match:
				text = next_match.group(2)
			else:
				text = match.group(2)
		else:
			result += text
			break
	return result

def extract_text_from_se_book(folder, veto_files, veto_tags):
	files = get_text_files(folder, veto_files)

	text = ""
	for file in files:
		text += get_deep_text(ET.parse(file).getroot(), veto_tags)
	text = clean_whitespace(text)
	
	return text

def get_text_files(folder, veto_files):
	text_folder = folder + "src/epub/text/"
	content = open(folder + "src/epub/content.opf")
	
	files = []
	for line in content.readlines():
		match = re.search('<itemref idref="(.*)"/>', line)
		if match and match.group(1) not in veto_files:
			files.append(text_folder + match.group(1))
	
	return files

def get_deep_text(element, veto_tags):
	text = ''
	if element.tag.split("}")[1] not in veto_tags:
		text = element.text or ''
		for subelement in element:
			text += get_deep_text(subelement, veto_tags)
		text += element.tail or ''
	return text

def clean_whitespace(text):
	text = text.replace('\t', '')
	text = ' '.join([x for x in text.split(' ') if x != ''])
	text = '\n'.join([x for x in text.split('\n') if x != ''])
	return text

try:
	main(sys.argv)
except InputError as e:
	print(e.message)
	print_usage()
