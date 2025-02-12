# po-data-processing-tkinter
- install requirements
  ```bash
  pip install -r requirements.txt
  ```
- run untuk buat kunci
  ```bash
  python '.\buat kunci.py'
  ```
- run enkripsi
  ```bash
  python enkripsi.py
  ```
- build app
  ```bash
  python -m PyInstaller --onefile --noconsole --collect-submodules=tkinter --collect-submodules=PIL --collect-submodules=pandas --exclude-module pandas.tests loader.py
  ```
