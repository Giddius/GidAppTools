from pathlib import Path
import re

import pp

a = """
peewee-erd==0.1.3
pep517
pipdeptree~=0.1.0.post0
pipreqs<=0.1.2
pp-ez>=0.2.0
tzdata==2021.5
"""


p = re.compile(r"(?P<name>.*)?(?P<specifier>[\=\~\>\<]\=)(?P<version>.*)")

for line in a.splitlines():
    if not line:
        continue
    match = p.match(line)
    if not match:
        pp(line)
    else:
        pp(match.groupdict())
