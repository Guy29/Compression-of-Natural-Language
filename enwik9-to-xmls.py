enwik9_stub = open('enwik9','rb+')

# The "enwik9" file given at http://mattmahoney.net/dc/enwik9.zip is truncated at the 1,000,000,000 byte mark.

# This means that it is not a valid XML file.

# This python script rounds it off with closing tags so that it is easier to process.

import re

stub_contents = enwik9_stub.read()

tags = re.findall(b'(<(/?)\s*([^>\s]*)[^>]*>)', stub_contents)

tag_stack = []
for (whole_match, is_closing_tag, tag_name) in tags:
  if whole_match.endswith(b'/>'): continue
  if is_closing_tag: tag_stack.pop()
  else: tag_stack.append(tag_name)

closing_tags = b''
for indent, tag in reversed(list(enumerate(tag_stack))):
  if tag==b'text': closing_tags += b'</text>'
  else: closing_tags += b'\n' + b'  '*indent + b'</'+tag+b'>'

full_contents = stub_contents + closing_tags

# The full contents of the XML including the closing tags are put into a new file.

open('enwik9.xml','wb+').write(full_contents)

# And smaller versions of the file containing fewer articles are created for testing.

enwik9_split = full_contents.split(b'</page>')

open('enwik9-1k.xml','wb+').write(b'</page>'.join(enwik9_split[:1000]+[enwik9_split[-1]]))

open('enwik9-10k.xml','wb+').write(b'</page>'.join(enwik9_split[:10000]+[enwik9_split[-1]]))