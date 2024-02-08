rule = {}

rule['char']  = set('abcdef')
rule['digit'] = set('012345')

rule['anything'] = {('',), ('char', 'anything')}
rule['number']   = {('',), ('digit', 'number')}

rule['title']         = {('    <title>', 'anything', '</title>\n')}
rule['id']            = {('    <id>', 'number', '</id>\n')}
rule['restrictions']  = {('    <restrictions>', 'anything', '</restrictions>\n')}
rule['revision']      = {('    <revision>\n', 'anything', '    </revision>\n')}

rule['optional_restrictions'] = {('',), ('restrictions',)}
rule['page']  = {('  <page>\n', 'title', 'id', 'optional_restrictions', 'revision', '  </page>\n')}
rule['pages'] = {('',), ('page','pages')}

rule['siteinfo']  = {('  <siteinfo>\n', '', '  </siteinfo>\n')}
rule['mediawiki'] = {('<mediawiki>\n', 'siteinfo', 'pages', '</mediawiki>')}

from random import choice

def generate(rule_name):
  out = ''
  production = choice(list(rule[rule_name]))
  for part in production:
    if part in rule: out += generate(part)
    else: out += part
  return out

print(generate('mediawiki'))