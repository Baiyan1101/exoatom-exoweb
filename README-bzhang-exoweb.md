# Baiyan ExoAtom exoweb workspace

This document is the operating guide for Baiyan Zhang's ExoAtom work copy on
`exoweb`. The goal is to keep Christian Hill's Wagtail/Django structure as the
reference format, while developing Baiyan's ExoAtom prototype features in a
separate writable repository.

## Directory Layout

- `/mnt/data/exomol/repos/exoatom`: Christian's reference clone. Treat this as
  the standard template and do not edit it for Baiyan's experiments.
- `/mnt/data/bzhang/exoatom-work`: Baiyan's writable Git repository.
- `/mnt/data/bzhang/exoatom_data`: spectral files, generated metadata, source
  archives, and `exoatom.all.json`.
- `/mnt/data/bzhang/exoatom_data/incoming`: place incoming NIST/Kurucz zip files
  here before import.
- `/mnt/data/bzhang/exoatom_runtime`: SQLite database, collected static files,
  media, logs, and other runtime output.
- `/mnt/data/bzhang/venvs/exoatom`: Python virtual environment.

Keep large data and runtime files out of Git. The code repository should only
contain source code, templates, static assets, tests, and documentation.

`exoatom/exoatom/settings/local.py` is an ignored local configuration file for
this exoweb work copy. Keep machine-specific paths and local secrets there; do
not commit it.

## Environment Setup

The virtual environment already lives outside the code repository:

```bash
python3 -m venv /mnt/data/bzhang/venvs/exoatom
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom
pip install -r requirements.txt
python manage.py migrate
python manage.py check
```

Use `python3`, not `python`, if the system shell says `python: command not
found`.

## Running The Website

Start Django on exoweb:

```bash
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom
python manage.py runserver 127.0.0.1:8000
```

From your local computer, open a separate terminal and forward the port:

```bash
ssh -L 8000:127.0.0.1:8000 bzhang@exoweb
```

Then open this in your local browser:

```text
http://127.0.0.1:8000/
```

If port `8000` is already in use, choose another local/remote port pair, for
example `8001`.

## Implemented Pages

- `/`: ExoAtom search page with migrated prototype interactions.
- `/coverage/`: dynamic Kurucz vs NIST coverage matrix.
- `/data/<id>`: dataset detail pages in the existing ExoMol style.
- `/data/preview/<file_path>`: safe text preview for data and metadata files.
- `/data/download/<file_path>`: per-file download endpoint.

Search accepts several ion-stage formats, for example:

```text
Ti VI
Ti-VI
Ti_VI
Ti+5
3He+
```

## Kurucz vs NIST Coverage Matrix

The coverage page is generated from the database rather than from a static
image. It compares dataset availability by element and ionization stage:

- `B`: both Kurucz and NIST are available.
- `K`: Kurucz only.
- `N`: NIST only.

The matrix is intentionally wide. It uses horizontal scrolling, sticky stage
headers, and sticky `Z` / `Element` columns so the full chart remains readable.
Marked cells link back to the normal search page for that species.

After re-importing new NIST or Kurucz archives, refresh `/coverage/` to see the
updated matrix.

## Data Archive Sync

Put source archives under:

```text
/mnt/data/bzhang/exoatom_data/incoming
```

Recommended filenames:

```text
NIST-data.zip
Kurucz-data.zip
```

Dry-run first:

```bash
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom

python manage.py sync_exoatom_archive --dataset NIST --source /mnt/data/bzhang/exoatom_data/incoming/NIST-data.zip --dry-run
python manage.py sync_exoatom_archive --dataset Kurucz --source /mnt/data/bzhang/exoatom_data/incoming/Kurucz-data.zip --dry-run
```

Then import for real:

```bash
python manage.py sync_exoatom_archive --dataset NIST --source /mnt/data/bzhang/exoatom_data/incoming/NIST-data.zip
python manage.py sync_exoatom_archive --dataset Kurucz --source /mnt/data/bzhang/exoatom_data/incoming/Kurucz-data.zip
```

The sync command:

- extracts/copies supported files into `/mnt/data/bzhang/exoatom_data`;
- generates `*.adef.json`;
- updates `exoatom.all.json`;
- imports or updates the database records;
- accepts both names such as `Mg_I__NIST.states` and `Mg-I__NIST.states`;
- normalizes species slugs to underscores.

If you update the contents of either zip file later, rerun the corresponding
sync command.

## File Preview And Download

Dataset detail pages show each linked data file. The filename opens the safe
preview page, while the download icon downloads the raw file.

The preview and download endpoints only serve files inside
`/mnt/data/bzhang/exoatom_data`. This prevents accidental access to code,
runtime files, or files from Christian's reference repository.

## Useful Checks

Run these before committing:

```bash
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom
python manage.py check
```

Quick smoke checks from Django's test client:

```bash
python manage.py shell -c "from django.test import Client; c=Client(HTTP_HOST='localhost'); print(c.get('/').status_code); print(c.get('/coverage/').status_code)"
```

Expected output:

```text
200
200
```

## Version Control

Only work in Baiyan's repository:

```bash
cd /mnt/data/bzhang/exoatom-work
git status
git add <files>
git commit -m "Describe the change"
git push origin main
```

At the time of writing, the remote is:

```text
origin  https://github.com/Baiyan1101/exoatom-exoweb.git
```

This repository is separate from Christian's clone, so commits here do not
modify Christian's Git history.

If `git push` fails with:

```text
fatal: could not read Username for 'https://github.com'
```

then GitHub authentication is not configured on exoweb. Configure a GitHub
personal access token for HTTPS, or switch `origin` to an SSH remote after
adding an SSH key to GitHub.

## Current Migration Status

Completed:

- writable exoweb repository under `/mnt/data/bzhang/exoatom-work`;
- external data/runtime directories under `/mnt/data/bzhang`;
- migrated prototype search interface;
- NIST/Kurucz archive sync command;
- dataset file preview and download controls;
- search normalization for common ion-stage query formats;
- dynamic Kurucz vs NIST coverage matrix.

Next likely work:

- add focused tests for the archive sync command and search normalization;
- polish page copy with supervisor feedback;
- decide whether the coverage matrix should also export CSV/PNG for talks or
  reports.
