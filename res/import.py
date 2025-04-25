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

exts = {'.json': "Metadata definition file",
        ".pf": "Partition function",
        ".states": "Energy levels",
        ".trans": "Transitions"
        }

sps = os.listdir(DATA_DIR)
for sp in sps:
    if not os.path.isdir(DATA_DIR / sp):
        continue
    if sp in ("H", "He"):
        # These atoms have isotope-resolved data
        pass
    charge = 0
    if sp.endswith("_p"):
        charge = 1
        atom = sp[:-2]
    else:
        atom = sp
    species, created = Species.objects.get_or_create(atom=atom, charge=charge)
    dss = os.listdir(DATA_DIR / sp)
    for ds in dss:
        if not os.path.isdir(DATA_DIR / sp / ds):
            continue
        files = os.listdir(DATA_DIR / sp / ds)
        if not files:
            continue
        dc, created = DataCollection.objects.get_or_create(dataset=ds, species=species)
        for file in files:
            if not file.startswith(sp):
                continue
            url = f"{sp}/{ds}/{file}"
            size = os.path.getsize(DATA_DIR / sp / ds / file)
            ext = os.path.splitext(file)[1]
            description = f"{exts[ext]} for {species} from the {ds} dataset."
            link, created = Link.objects.get_or_create(url=url, size=size, description=description)
            dc.links.add(link)
            print(f"{ds} {species}", url, size)
            print(description)
            print(); print()
