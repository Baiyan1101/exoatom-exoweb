import os
import sys
from conf import exoatom_path, DATA_DIR
sys.path.append(exoatom_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'exoatom.settings.base'

# Prepare the Django models
import django
django.setup()

from species.models import Species
from data.models import Link, DataCollection

from glob import glob
import json

search_path = os.path.join(str(DATA_DIR), "*", "*", "*.json")
json_files = glob(search_path)
for json_file in json_files:
    print(json_file, end=' : ')
    fields = json_file.split("/")
    filename = fields[-1]
    atom_slug, dataset = os.path.splitext(filename)[0].split('__')
    dc = DataCollection.objects.get(species__slug=atom_slug, dataset=dataset)
    print(atom_slug, dataset, dc)
    if atom_slug == "Ag" and dataset == "NIST":
        continue
    dc.metadata = json.loads(open(json_file).read())
    dc.save()
