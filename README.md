# athor-sketches
Repository containing my sketches (mostly woordworking)

## Projektuppsättning

1. **Skapa en virtuell miljö med korrekt python version (>=3.9 och <3.13, kan ändras framgent)**  
   ```bash
   python3.12 -m venv .venv
   ```

2. **Aktivera miljön**  
   - **macOS/Linux**  
     ```bash
     source .venv/bin/activate
     ```  
   - **Windows (PowerShell)**  
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```

3. **Uppgradera pip**  
   ```bash
   pip install --upgrade pip
   ```

4. **Installera paket i “editable” mode**  
   (läser `pyproject.toml`/`setup.py` och installerar beroenden)  
   ```bash
   pip install -e .
   ```

5. **Verifiera installationen**  
   ```bash
   python --version    # Bör visa 3.12.x
   pip list            # Ska lista cadquery, CQ-editor m.fl.
   ```
