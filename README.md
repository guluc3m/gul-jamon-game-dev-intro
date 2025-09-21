# GUL Jamón 2025

Material auxiliar para la charla "Introducción al desarrollo de videojuegos
con PyGame" de la GUL Jamón 2025.

## Ejecución

Con venv (built in):

```sh
python -m venv venv
source venv/bin/activate
pip install -e .
```

> [!NOTE]
> En windows, en vez de ejecutar `source venv/bin/activate`, solo poner `venv/bin/activate`.

Con [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

```sh
uv run bullet_hell.py
```
