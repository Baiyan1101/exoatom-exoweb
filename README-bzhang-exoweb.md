# Baiyan ExoAtom exoweb workspace

This is Baiyan Zhang's writable ExoAtom work copy on exoweb.

Directory layout:

- `/mnt/data/exomol/repos/exoatom`: Christian's reference clone.
- `/mnt/data/bzhang/exoatom-work`: writable code repository.
- `/mnt/data/bzhang/exoatom_data`: spectral and metadata files.
- `/mnt/data/bzhang/exoatom_runtime`: SQLite database, collected static files, media, and logs.
- `/mnt/data/bzhang/venvs/exoatom`: Python virtual environment.

Useful commands:

```bash
python3 -m venv /mnt/data/bzhang/venvs/exoatom
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Import data after putting files under `/mnt/data/bzhang/exoatom_data`:

```bash
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/res
python import.py
python import_json.py
```

Version control:

```bash
cd /mnt/data/bzhang/exoatom-work
git status
git add .
git commit -m "Update ExoAtom exoweb workspace"
git push origin main
```

## Data Archive Sync

Put source archives under `/mnt/data/bzhang/exoatom_data/incoming`. Generated metadata and copied data files stay under `/mnt/data/bzhang/exoatom_data` and are not committed to Git.

Dry-run an archive first:

```bash
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom
python manage.py sync_exoatom_archive --dataset NIST --source /mnt/data/bzhang/exoatom_data/incoming/NIST-data.zip --dry-run
python manage.py sync_exoatom_archive --dataset Kurucz --source /mnt/data/bzhang/exoatom_data/incoming/Kurucz-data.zip --dry-run
```

Generate `*.adef.json`, update `exoatom.all.json`, and import the database:

```bash
python manage.py sync_exoatom_archive --dataset NIST --source /mnt/data/bzhang/exoatom_data/incoming/NIST-data.zip
python manage.py sync_exoatom_archive --dataset Kurucz --source /mnt/data/bzhang/exoatom_data/incoming/Kurucz-data.zip
```

The command accepts both `Mg_I__NIST.states` and `Mg-I__NIST.states` naming styles and normalizes species slugs to underscores.
