import json
import re
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from data.models import DataCollection, Link
from periodic_table.models import Element
from species.models import Species


DEFAULT_KINDS = {"states", "trans", "pf"}

ELEMENTS = [
    ("H", "Hydrogen", 1, 1), ("He", "Helium", 1, 18),
    ("Li", "Lithium", 2, 1), ("Be", "Beryllium", 2, 2), ("B", "Boron", 2, 13), ("C", "Carbon", 2, 14), ("N", "Nitrogen", 2, 15), ("O", "Oxygen", 2, 16), ("F", "Fluorine", 2, 17), ("Ne", "Neon", 2, 18),
    ("Na", "Sodium", 3, 1), ("Mg", "Magnesium", 3, 2), ("Al", "Aluminium", 3, 13), ("Si", "Silicon", 3, 14), ("P", "Phosphorus", 3, 15), ("S", "Sulfur", 3, 16), ("Cl", "Chlorine", 3, 17), ("Ar", "Argon", 3, 18),
    ("K", "Potassium", 4, 1), ("Ca", "Calcium", 4, 2), ("Sc", "Scandium", 4, 3), ("Ti", "Titanium", 4, 4), ("V", "Vanadium", 4, 5), ("Cr", "Chromium", 4, 6), ("Mn", "Manganese", 4, 7), ("Fe", "Iron", 4, 8), ("Co", "Cobalt", 4, 9), ("Ni", "Nickel", 4, 10), ("Cu", "Copper", 4, 11), ("Zn", "Zinc", 4, 12), ("Ga", "Gallium", 4, 13), ("Ge", "Germanium", 4, 14), ("As", "Arsenic", 4, 15), ("Se", "Selenium", 4, 16), ("Br", "Bromine", 4, 17), ("Kr", "Krypton", 4, 18),
    ("Rb", "Rubidium", 5, 1), ("Sr", "Strontium", 5, 2), ("Y", "Yttrium", 5, 3), ("Zr", "Zirconium", 5, 4), ("Nb", "Niobium", 5, 5), ("Mo", "Molybdenum", 5, 6), ("Tc", "Technetium", 5, 7), ("Ru", "Ruthenium", 5, 8), ("Rh", "Rhodium", 5, 9), ("Pd", "Palladium", 5, 10), ("Ag", "Silver", 5, 11), ("Cd", "Cadmium", 5, 12), ("In", "Indium", 5, 13), ("Sn", "Tin", 5, 14), ("Sb", "Antimony", 5, 15), ("Te", "Tellurium", 5, 16), ("I", "Iodine", 5, 17), ("Xe", "Xenon", 5, 18),
    ("Cs", "Caesium", 6, 1), ("Ba", "Barium", 6, 2), ("La", "Lanthanum", None, None), ("Ce", "Cerium", None, None), ("Pr", "Praseodymium", None, None), ("Nd", "Neodymium", None, None), ("Pm", "Promethium", None, None), ("Sm", "Samarium", None, None), ("Eu", "Europium", None, None), ("Gd", "Gadolinium", None, None), ("Tb", "Terbium", None, None), ("Dy", "Dysprosium", None, None), ("Ho", "Holmium", None, None), ("Er", "Erbium", None, None), ("Tm", "Thulium", None, None), ("Yb", "Ytterbium", None, None), ("Lu", "Lutetium", None, None),
    ("Hf", "Hafnium", 6, 4), ("Ta", "Tantalum", 6, 5), ("W", "Tungsten", 6, 6), ("Re", "Rhenium", 6, 7), ("Os", "Osmium", 6, 8), ("Ir", "Iridium", 6, 9), ("Pt", "Platinum", 6, 10), ("Au", "Gold", 6, 11), ("Hg", "Mercury", 6, 12), ("Tl", "Thallium", 6, 13), ("Pb", "Lead", 6, 14), ("Bi", "Bismuth", 6, 15), ("Po", "Polonium", 6, 16), ("At", "Astatine", 6, 17), ("Rn", "Radon", 6, 18),
    ("Fr", "Francium", 7, 1), ("Ra", "Radium", 7, 2), ("Ac", "Actinium", None, None), ("Th", "Thorium", None, None), ("Pa", "Protactinium", None, None), ("U", "Uranium", None, None), ("Np", "Neptunium", None, None), ("Pu", "Plutonium", None, None), ("Am", "Americium", None, None), ("Cm", "Curium", None, None), ("Bk", "Berkelium", None, None), ("Cf", "Californium", None, None), ("Es", "Einsteinium", None, None), ("Fm", "Fermium", None, None), ("Md", "Mendelevium", None, None), ("No", "Nobelium", None, None), ("Lr", "Lawrencium", None, None),
    ("Rf", "Rutherfordium", 7, 4), ("Db", "Dubnium", 7, 5), ("Sg", "Seaborgium", 7, 6), ("Bh", "Bohrium", 7, 7), ("Hs", "Hassium", 7, 8), ("Mt", "Meitnerium", 7, 9), ("Ds", "Darmstadtium", 7, 10), ("Rg", "Roentgenium", 7, 11), ("Cn", "Copernicium", 7, 12), ("Nh", "Nihonium", 7, 13), ("Fl", "Flerovium", 7, 14), ("Mc", "Moscovium", 7, 15), ("Lv", "Livermorium", 7, 16), ("Ts", "Tennessine", 7, 17), ("Og", "Oganesson", 7, 18),
]

ELEMENT_NAMES = {symbol: name for symbol, name, _, _ in ELEMENTS}
ELEMENT_ORDER = {symbol: index for index, (symbol, _, _, _) in enumerate(ELEMENTS)}
ROMAN_VALUES = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
    (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
    (5, "V"), (4, "IV"), (1, "I"),
]


class Command(BaseCommand):
    help = "Generate ExoAtom metadata from a NIST/Kurucz archive and import it into Django."

    def add_arguments(self, parser):
        parser.add_argument("--dataset", required=True, help="Dataset name, for example NIST or Kurucz.")
        parser.add_argument("--source", required=True, help="Zip archive or extracted directory containing .states/.trans/.pf files.")
        parser.add_argument("--data-dir", default=settings.EXOATOM_DATA_DIR, help="Directory where data and generated metadata are stored.")
        parser.add_argument("--master", default="exoatom.all.json", help="Master index filename inside data-dir.")
        parser.add_argument("--data-version", dest="data_version", default=datetime.now(timezone.utc).strftime("%Y%m%d"), help="Dataset/index version.")
        parser.add_argument("--keep-existing", action="store_true", help="Keep existing files for this dataset in data-dir.")
        parser.add_argument("--dry-run", action="store_true", help="Discover files and report counts without writing data or database rows.")
        parser.add_argument("--no-db", action="store_true", help="Generate files but do not import them into the Django database.")

    def handle(self, *args, **options):
        dataset = options["dataset"]
        source = Path(options["source"])
        data_dir = Path(options["data_dir"])
        version = int(options["data_version"])

        if not source.exists():
            raise CommandError(f"Source does not exist: {source}")
        data_dir.mkdir(parents=True, exist_ok=True)

        groups = discover_groups(source, dataset)
        if not groups:
            raise CommandError(f"No {dataset} .states/.trans/.pf files found in {source}")

        complete = sum(1 for files in groups.values() if all(kind in files for kind in DEFAULT_KINDS))
        self.stdout.write(f"Discovered {len(groups)} {dataset} species ({complete} with states/trans/pf).")
        if options["dry_run"]:
            for slug in sorted(groups, key=sort_key)[:12]:
                self.stdout.write(f"  {slug}: {', '.join(sorted(groups[slug]))}")
            if len(groups) > 12:
                self.stdout.write(f"  ... {len(groups) - 12} more")
            return

        if not options["keep_existing"]:
            remove_existing_dataset(data_dir, dataset)

        atoms = process_groups(groups, data_dir, dataset, version)
        master_path = data_dir / options["master"]
        master = load_master(master_path, options["master"], version)
        master["ExoAtom"]["version"] = str(version)
        master["atoms"] = merge_master_atoms(master.get("atoms", []), atoms, dataset)
        write_json(master_path, master)

        if not options["no_db"]:
            import_dataset(data_dir, dataset, atoms)
            update_periodic_table(master["atoms"])

        self.stdout.write(self.style.SUCCESS(f"Generated {len(atoms)} {dataset} species in {data_dir}."))


def discover_groups(source, dataset):
    if source.is_dir():
        return discover_files_from_dir(source, dataset)
    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            return discover_files_from_archive(archive, dataset, source)
    raise CommandError(f"{source} is not a directory or zip archive.")


def discover_files_from_dir(base_dir, dataset):
    groups = defaultdict(dict)
    for path in Path(base_dir).rglob("*"):
        if not path.is_file():
            continue
        slug, kind = parse_source_file(path.name, dataset)
        if slug:
            groups[slug][kind] = ("file", path)
    return groups


def discover_files_from_archive(archive, dataset, archive_path):
    groups = defaultdict(dict)
    for info in archive.infolist():
        if info.is_dir():
            continue
        slug, kind = parse_source_file(Path(info.filename).name, dataset)
        if slug:
            groups[slug][kind] = ("zip", archive_path, info.filename)
    return groups


def parse_source_file(filename, dataset):
    match = re.match(rf"^(?P<slug>.+?)__{re.escape(dataset)}\.(?P<kind>states|trans|pf)$", filename, re.IGNORECASE)
    if not match:
        return None, None
    slug = canonical_species_slug(match.group("slug"))
    if not is_valid_species_slug(slug):
        return None, None
    return slug, match.group("kind").lower()


def is_valid_species_slug(slug):
    return re.match(r"^(?:\d+)?[A-Z][a-z]?(?:_[IVXLCDM]+)?$", slug) is not None


def remove_existing_dataset(data_dir, dataset):
    for path in data_dir.glob(f"*__{dataset}.*"):
        if path.is_file():
            path.unlink()


def process_groups(groups, data_dir, dataset, version):
    atoms = []
    for slug in sorted(groups, key=sort_key):
        files = copy_group_files(slug, groups[slug], data_dir, dataset)
        definition = build_definition(slug, files, data_dir, dataset, version)
        definition_path = data_dir / f"{slug}__{dataset}.adef.json"
        definition["files"]["definition"] = definition_path.name
        write_json(definition_path, definition)
        atoms.append(build_master_entry(slug, dataset, version))
    return atoms


def copy_group_files(slug, source_files, data_dir, dataset):
    copied = {}
    for kind, source in source_files.items():
        target = data_dir / f"{slug}__{dataset}.{kind}"
        source_type = source[0]
        if source_type == "file":
            shutil.copyfile(source[1], target)
        else:
            _, archive_path, member = source
            with zipfile.ZipFile(archive_path) as archive:
                with archive.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
        copied[kind] = target.name
    return copied


def build_definition(slug, files, data_dir, dataset, version):
    isotope_mass, symbol, stage_number, charge = parse_species_slug(slug)
    states_stats = stats_states(data_dir / files["states"]) if "states" in files else {}
    trans_stats = stats_trans(data_dir / files["trans"]) if "trans" in files else {}
    pf_stats = stats_pf(data_dir / files["pf"]) if "pf" in files else {}
    return {
        "species": {
            "atom": symbol,
            "ordinary_formula": ion_formula(symbol, charge, isotope_mass),
            "spectroscopic_notation": f"{symbol} {roman(stage_number)}",
            "charge": charge,
            "name": species_name(symbol, charge),
            "mass_in_Da": None,
        },
        "dataset": {
            "name": dataset,
            "version": version,
            "doi": "",
            "max_temperature": pf_stats.get("max_temperature"),
            "n_L_default": 0.5,
            "num_pressure_broadeners": 0,
            "nxsec_files": 0,
            "nkcoeff_files": 0,
            "dipole_available": False,
            "cooling_function_available": False,
            "specific_heat_available": False,
            "uncertainty_available": True,
            "Ionisation": None,
            "states": {
                "number_of_states": states_stats.get("count", 0),
                "max_energy": states_stats.get("max_energy"),
                "lifetime_available": False,
                "lande_g_available": False,
                "num_quanta": None,
                "states_file_fields": [
                    {"name": "ID", "desc": "Unique integer identifier for the energy level"},
                    {"name": "E", "desc": "State energy in cm^-1"},
                    {"name": "gtot", "desc": "State degeneracy"},
                    {"name": "J", "desc": "Total angular momentum quantum number"},
                ],
            },
            "transitions": {
                "number_of_transitions": trans_stats.get("count", 0),
                "number_of_transition_files": 1 if "trans" in files else 0,
                "max_wavenumber": trans_stats.get("max_wavenumber"),
                "transitions_file_fields": [
                    {"name": "i", "desc": "Upper state ID"},
                    {"name": "f", "desc": "Lower state ID"},
                    {"name": "A", "desc": "Einstein A coefficient in s^-1"},
                    {"name": "Wavenumber", "desc": "Transition wavenumber in cm^-1"},
                ],
            },
            "partition_function": {
                "max_partition_function_temperature": pf_stats.get("max_temperature"),
                "partition_function_step_size": pf_stats.get("step_size"),
                "fields": [
                    {"name": "T", "desc": "Temperature in Kelvin"},
                    {"name": "Q(T)", "desc": "Partition function, dimensionless"},
                ],
            },
        },
        "files": dict(sorted(files.items())),
    }


def build_master_entry(slug, dataset, version):
    isotope_mass, symbol, stage_number, charge = parse_species_slug(slug)
    formula = base_species_slug(slug)
    return {
        "name": species_name(symbol, charge),
        "formula": formula,
        "num_isotopes": 1,
        "isotopes": [
            {
                "iso_slug": slug,
                "iso_formula": ion_formula(symbol, charge, isotope_mass),
                "dataset": dataset,
                "version": version,
            }
        ],
    }


def stats_states(path):
    count = 0
    max_energy = None
    for columns in iter_columns(path):
        count += 1
        max_energy = max_float(max_energy, columns, 1)
    return {"count": count, "max_energy": max_energy}


def stats_trans(path):
    count = 0
    max_wavenumber = None
    for columns in iter_columns(path):
        count += 1
        max_wavenumber = max_float(max_wavenumber, columns, 3)
    return {"count": count, "max_wavenumber": max_wavenumber}


def stats_pf(path):
    temperatures = []
    for columns in iter_columns(path):
        value = parse_float(columns, 0)
        if value is not None:
            temperatures.append(value)
    step = round(temperatures[1] - temperatures[0], 6) if len(temperatures) >= 2 else None
    return {"max_temperature": max(temperatures) if temperatures else None, "step_size": step}


def iter_columns(path):
    with Path(path).open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                yield stripped.split()


def max_float(current, columns, index):
    value = parse_float(columns, index)
    if value is None:
        return current
    return value if current is None else max(current, value)


def parse_float(columns, index):
    if len(columns) <= index:
        return None
    try:
        return float(columns[index])
    except ValueError:
        return None


def parse_species_slug(slug):
    match = re.match(r"^(?P<isotope>\d+)?(?P<symbol>[A-Z][a-z]?)(?:_(?P<roman>[IVXLCDM]+))?$", slug)
    if not match:
        raise CommandError(f"Invalid species slug: {slug}")
    isotope_mass = match.group("isotope")
    symbol = match.group("symbol")
    stage_number = roman_to_int(match.group("roman") or "I")
    charge = stage_number - 1
    return isotope_mass, symbol, stage_number, charge


def species_name(symbol, charge):
    name = ELEMENT_NAMES.get(symbol, symbol)
    return f"{name} Ion ({roman(charge + 1)})" if charge else name


def roman(number):
    result = []
    remaining = number
    for value, numeral in ROMAN_VALUES:
        while remaining >= value:
            result.append(numeral)
            remaining -= value
    return "".join(result)


def roman_to_int(value):
    index = 0
    total = 0
    value = value.upper()
    for amount, numeral in ROMAN_VALUES:
        while value[index:index + len(numeral)] == numeral:
            total += amount
            index += len(numeral)
            if index >= len(value):
                return total
    if index != len(value):
        raise CommandError(f"Unsupported ionization stage: {value}")
    return total


def ion_formula(symbol, charge, isotope_mass=None):
    formula = f"{isotope_mass or ''}{symbol}"
    if charge <= 0:
        return formula
    if charge == 1:
        return f"{formula}+"
    return f"{formula}{charge}+"


def html_formula(symbol, charge, isotope_mass=None):
    mass = f"<sup>{isotope_mass}</sup>" if isotope_mass else ""
    if charge <= 0:
        return f"{mass}{symbol}"
    charge_label = "+" if charge == 1 else f"{charge}+"
    return f"{mass}{symbol}<sup>{charge_label}</sup>"


def sort_key(slug):
    isotope_mass, symbol, stage_number, _ = parse_species_slug(slug)
    isotope_order = int(isotope_mass) if isotope_mass else 0
    return (ELEMENT_ORDER.get(symbol, 999), stage_number, isotope_order, slug)


def canonical_species_slug(slug):
    return slug.replace("-", "_")


def base_species_slug(slug):
    _, symbol, stage_number, _ = parse_species_slug(slug)
    return f"{symbol}_{roman(stage_number)}"


def load_master(path, master_name, version):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"ExoAtom": {"ID": Path(master_name).name, "version": str(version)}, "atoms": []}


def merge_master_atoms(existing_atoms, new_atoms, dataset):
    merged = {}
    for atom in existing_atoms:
        atom = dict(atom)
        atom["formula"] = canonical_species_slug(atom["formula"])
        atom["isotopes"] = [
            normalize_isotope_entry(isotope)
            for isotope in atom.get("isotopes", [])
            if isotope.get("dataset") != dataset
        ]
        if atom["isotopes"]:
            merged[atom["formula"]] = atom
    for atom in new_atoms:
        formula = atom["formula"]
        target = merged.setdefault(formula, {"name": atom["name"], "formula": formula, "num_isotopes": 0, "isotopes": []})
        target["name"] = atom["name"]
        for isotope in atom.get("isotopes", []):
            target["isotopes"].append(normalize_isotope_entry(isotope))
    atoms = []
    for atom in sorted(merged.values(), key=lambda item: sort_key(item["formula"])):
        atom["isotopes"] = sorted(atom["isotopes"], key=lambda isotope: (isotope["dataset"], sort_key(isotope["iso_slug"])))
        atom["num_isotopes"] = len({isotope["iso_slug"] for isotope in atom["isotopes"]})
        atoms.append(atom)
    return atoms


def normalize_isotope_entry(isotope):
    isotope = dict(isotope)
    isotope["iso_slug"] = canonical_species_slug(isotope["iso_slug"])
    return isotope


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def import_dataset(data_dir, dataset, atoms):
    with transaction.atomic():
        for atom in atoms:
            for isotope in atom.get("isotopes", []):
                if isotope.get("dataset") != dataset:
                    continue
                slug = isotope["iso_slug"]
                definition_path = data_dir / f"{slug}__{dataset}.adef.json"
                definition = json.loads(definition_path.read_text(encoding="utf-8"))
                isotope_mass, symbol, _, charge = parse_species_slug(slug)
                isotope_label = f"{isotope_mass}{symbol}" if isotope_mass else ""
                species, _ = Species.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "atom": symbol,
                        "charge": charge,
                        "isotope": isotope_label,
                        "html": html_formula(symbol, charge, isotope_mass),
                    },
                )
                collection, _ = DataCollection.objects.update_or_create(
                    dataset=dataset,
                    species=species,
                    defaults={"metadata": definition},
                )
                collection.links.clear()
                for kind, filename in sorted(definition.get("files", {}).items()):
                    path = data_dir / filename
                    size = path.stat().st_size if path.exists() else None
                    link, _ = Link.objects.update_or_create(
                        url=filename,
                        defaults={
                            "size": size,
                            "description": file_description(kind, species, dataset),
                        },
                    )
                    collection.links.add(link)


def file_description(kind, species, dataset):
    label = str(species)
    descriptions = {
        "pf": "Partition function",
        "states": "Energy levels",
        "trans": "Transitions",
        "definition": "Metadata definition file",
    }
    return f"{descriptions.get(kind, kind)} for {label} from the {dataset} dataset."


def update_periodic_table(master_atoms):
    available = {parse_species_slug(atom["formula"])[1] for atom in master_atoms}
    for atomic_number, (symbol, name, period, group) in enumerate(ELEMENTS, start=1):
        link = f"/?q={symbol}&all_charges=true" if symbol in available else ""
        Element.objects.update_or_create(
            atomic_number=atomic_number,
            defaults={"symbol": symbol, "name": name, "group": group, "link": link},
        )
