# Sharpness Launcher: AI integration

## Built-in assistant

Open **Settings → AI → Assistant** or the **AI Assistant** toolbar button. Enter a full chat-completions URL and a model name. Local HTTP endpoints are supported only on localhost; remote endpoints require HTTPS. Requests are made only after pressing Send, without automatic execution of answers.

Select an instance to include version components, mod filenames and memory settings. Enable **Include latest log** to add its last 64 KiB. **Review context** shows exactly that context before sharing. Log redaction is best effort and cannot guarantee removal of all private information. The API key is held only while the settings page is open and is never saved in launcher settings. Endpoint and model are saved when settings are applied. No provider subscription or model is bundled.

## External agents

**Settings → AI → External agents** generates JSON or TOML using the exact executable and data-directory paths. The native stdio MCP server starts before GUI initialization and does not require Python:

```sh
sharpnesslauncher --mcp --data-dir /absolute/path/to/launcher-data
```

Tools: `list_instances`, `inspect_instance`, `read_latest_log`, `launch_instance`, `set_memory`.

By default only reading is permitted. To allow actions, add `--allow-write` and explicitly pass `confirm: true` on each action. Memory changes require the launcher to be closed, are limited to 256–65536 MiB, and create `instance.cfg.before-ai` before atomic replacement. Move a previous recovery copy aside before making another change. To restore, close the launcher and replace `instance.cfg` with its recovery copy. Do not run another launcher's UI against the same data directory during an operation.

MCP access stops when the client stops the process. There is no network listener. Tools never expose account files or API keys. Paths are constrained to the selected data directory. The current inventory uses its standard `instances` subdirectory; externally configured instance directories are not exposed.

## Extending the launcher

The native tools and transport live in `launcher/ai/AiTools.cpp`; UI and provider requests live in `launcher/ui/pages/global/AiPage.h`. Add tools with explicit schemas and permissions, and cover their observable behavior in `tests/ai/test_native.py`.

An external coding agent can edit and rebuild the fork itself. Automatic arbitrary code execution and control of the Minecraft character/world are not implemented. Horizon controls its own Rust engine; equivalent in-game tools for Java Edition require a separate Minecraft mod and protocol.

## Tests and builds

```powershell
$env:SHARPNESS_EXE = 'C:\absolute\path\sharpnesslauncher.exe'
python -m unittest discover -s tests/ai -v
```

Tests run against the built native executable, including its actual stdio protocol. The GitHub build workflow runs them after the upstream CTest suite. `tools/build-windows.ps1` performs the same checks and deploys Qt into `install`.

The fork uses a separate application ID, data directory, binary name and icon. Official Prism update feeds are disabled on every platform. For Microsoft login set `Launcher_MSA_CLIENT_ID` to an application registered for Sharpness; for CurseForge set `Launcher_CURSEFORGE_API_KEY` to a key issued to this fork. These services cannot be configured with another project's credentials.
