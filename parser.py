import re

# as the name implies, this is the beginning of a parsing module
# i'm not huge on object orientation right now, just looking to get
# something going for being able to break down and analyze strings
# in a regular way

def breakdown(text):
	'''Chops up text into a list containing the sentences, with their
	punctuation stripped, that were in the original text. Empty sentences
	are removed automatically. The letters are converted to lower case.'''
	sentences = [x.strip().lower() for x in text.split(".")]
	return [re.sub('[^a-z0-9" ]', "", x) for x in sentences if x != ""]

def has_words(text_list, word_list):
	'''Looking at the sentences now in text_list, search for matches of
	the words in word_list, including pluralizations. Returns a list
	containing the words it found, if it happened to find any. Otherwise
	it returns None object.'''
	resultant = []
	for word in word_list:
		for sentence in text_list:
			if sentence.find(word) != -1:
				resultant.append(word)
	if resultant != []: return resultant
	else: return None

def exclusion_criteria(sentence, word):
	'''If a sentence contains a gendered slur, then perform a quick
	exclusion text to make sure it's actually a slur used out of an
	appropriate context. Returns True if the slur is being used
	inappropriately.'''
	if word.find("bitch") != -1:
		if re.search('"[^"]{0,30}bitch', sentence):
			# if the above expression matches, it was probably
			# being used within a quote
			return False
		if re.search('bitch face', sentence):
			return False
	if word.find("slut") != -1:
		if re.search('slut sham(e|ing)', sentence):
			return False
	if word.find("dick") != -1:
		if re.search('(my|his|her|your) dick', sentence):
			return False
	if word.find("cunt") != -1:
		if re.search('(my|his|her|your) cunt', sentence):
			return False
	return True

def slur_detect(text_list):
	'''Looking at the sentences in text_list, apply regular expressions
	to look for gendered slurs (heuristically exclude probable non-slurs)
	and return them as a list if there were any detected; or, return None
	if none were detected.'''
	resultant = []
	for sentence in text_list:
		match = re.search('(bitchy?|whore|slut|dickhead|dick' + \
			'|fag|cunt) ', sentence)
		if match:
			word = match.group(1)
			if exclusion_criteria(sentence, word): continue
			resultant.append(match.group(1))
	if resultant != []: return resultant
	else: return None
