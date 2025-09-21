# GUL Jamón 2025
Material auxiliar para la charla "Introducción al desarrollo de videojuegos
con PyGame" de la GUL Jamón 2025.


## Ejecución
Requiere [Python](https://www.python.org/downloads/) 3.12+.

Con [venv](https://docs.python.org/3/library/venv.html) (_built-in_):
- Linux:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
    ```sh
    python3 bullet_hell.py
    ```

- Windows:
    ```powershell
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```
    ```sh
    python bullet_hell.py
    ```


Con [uv](https://docs.astral.sh/uv/):
```sh
uv sync
```
```sh
uv run bullet_hell.py
```
