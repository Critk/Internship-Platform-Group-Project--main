from pathlib import Path

possible_paths = [
    Path(".venv/lib/python3.11/site-packages/flask_uploads.py"),  # Linux/Mac/Render
    Path(".venv/Lib/site-packages/flask_uploads.py"),             # Windows
]

target_path = next((p for p in possible_paths if p.exists()), None)

if not target_path:
    print("Couldn't find flask_uploads.py in known locations.")
    exit(1)

print(f"Found flask_uploads.py at: {target_path}")

content = target_path.read_text()

if "from werkzeug.utils import secure_filename" in content:
    print("Already patched.")
else:
    # Replace the old import
    content = content.replace(
        "from werkzeug import secure_filename, FileStorage",
        "from werkzeug.datastructures import FileStorage\nfrom werkzeug.utils import secure_filename"
    )
    target_path.write_text(content)
    print("Patched flask_uploads.py successfully.")