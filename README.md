# ExoAtom exoweb workspace

This repository is Baiyan Zhang's writable ExoAtom development copy for the
exoweb host. It keeps Christian Hill's exoweb/Wagtail project structure, while
adding the migrated prototype search, dataset browsing, file preview/download,
archive sync, and Kurucz vs NIST coverage views.

Christian's reference clone is kept separately at:

```text
/mnt/data/exomol/repos/exoatom
```

This repository should be used for Baiyan's code changes:

```text
/mnt/data/bzhang/exoatom-work
```

Large data files are intentionally stored outside Git:

```text
/mnt/data/bzhang/exoatom_data
```

Runtime outputs such as the SQLite database, collected static files, media, and
logs are also outside Git:

```text
/mnt/data/bzhang/exoatom_runtime
```

## Main Features

- ExoAtom search page integrated into the Wagtail/Django project.
- Element and ion-stage searching, including forms such as `Ti VI`, `Ti-VI`,
  `Ti_VI`, and `Ti+5`.
- Dataset detail pages for NIST and Kurucz collections.
- Safe text preview for `.states`, `.trans`, `.pf`, `.json`, and related files.
- Per-file download links on dataset detail pages.
- Archive sync command for NIST and Kurucz zip files.
- Dynamic Kurucz vs NIST coverage matrix at `/coverage/`.

## Quick Start On exoweb

```bash
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom
python manage.py check
python manage.py runserver 127.0.0.1:8000
```

If you are connecting from your local computer, forward the remote port:

```bash
ssh -L 8000:127.0.0.1:8000 bzhang@exoweb
```

Then open:

```text
http://127.0.0.1:8000/
```

Useful pages:

```text
/                         Search and dataset results
/coverage/                Kurucz vs NIST coverage matrix
/data/preview/<file>      Safe file preview
/data/download/<file>     File download
```

## Updating Data

Put incoming source archives here:

```text
/mnt/data/bzhang/exoatom_data/incoming
```

Then run:

```bash
source /mnt/data/bzhang/venvs/exoatom/bin/activate
cd /mnt/data/bzhang/exoatom-work/exoatom

python manage.py sync_exoatom_archive --dataset NIST --source /mnt/data/bzhang/exoatom_data/incoming/NIST-data.zip
python manage.py sync_exoatom_archive --dataset Kurucz --source /mnt/data/bzhang/exoatom_data/incoming/Kurucz-data.zip
```

Use `--dry-run` first if you want to check what will be imported without
changing files or database records.

Generated files such as `*.adef.json` and `exoatom.all.json` are produced by
the sync/import workflow and stay under `/mnt/data/bzhang/exoatom_data`.

## Version Control

This work copy is separate from Christian's reference clone. Normal Git work
should happen in:

```bash
cd /mnt/data/bzhang/exoatom-work
git status
git add <files>
git commit -m "Describe the change"
git push origin main
```

At the time this documentation was updated, the remote was:

```text
https://github.com/Baiyan1101/exoatom-exoweb.git
```

If `git push` asks for GitHub credentials on exoweb, configure a GitHub token or
switch the remote to SSH before pushing.

## More Notes

See `README-bzhang-exoweb.md` for the longer exoweb-specific operating guide.
