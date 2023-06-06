# Eve Smarterbombing
An application analyzing Eve Online combat logs and presenting data in a Web interface.

## Quick Start
```shell
poetry install
poetry run python -m smarterbombing
```
Open with your preferred browser:
- Open [Web UI](http://localhost:42069)
- Open [Web UI (Dark Mode)](http://127.0.0.1:42069/?__theme=dark)



### Command line options
| Flag | Valid Values | Default | Description |
|---   |---     |---      | ---         |
| `--mode` | `webui` | `webui` | Which UI mode to run  |
| `--port` | Any valid port | `42069` | Which port to host webui |



## Development (Hot reload)
```shell
poetry install

poetry shell
gradio src/smarterbombing/__main__.py
```


