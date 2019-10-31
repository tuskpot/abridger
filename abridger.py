import re
import sys
import xml.etree.ElementTree as ET

def main(folder):
	veto_files = [
		"titlepage.xhtml",
		"imprint.xhtml",
		"etymology.xhtml", # moby dick
		"extracts.xhtml",  # moby dick
		"epigraph.xhtml",
		"dedication.xhtml",
		"halftitle.xhtml",
		"endnotes.xhtml",
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
	
	text = extract_text_from_se_book(folder, veto_files, veto_tags)
	abridged = abridge_text(text, white_space)
	
	print(abridged)

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
	

main(sys.argv[1])