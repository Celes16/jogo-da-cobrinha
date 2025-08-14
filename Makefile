# ============================================================================
# Alvos para gerar executáveis do backend (C) e frontend (Python) no Linux e Windows
# ============================================================================

# --- Backend em C ---

# Compilar backend no Linux
exe-linux: check-gcc $(BIN_DIR)
	@echo "[BUILD] Compilando backend para Linux..."
	$(CC) $(CFLAGS_COMMON) $(CFLAGS_REL) $(BACK_SRC) -o $(BIN_DIR)/back
	@echo "[OK] Executável gerado em $(BIN_DIR)/back"

# Compilar backend no Windows (usando MinGW no Linux)
exe-win: check-gcc $(BIN_DIR)
	@echo "[BUILD] Compilando backend para Windows (cross-compilation)..."
	@command -v x86_64-w64-mingw32-gcc >/dev/null 2>&1 || { echo "[ERRO] Instale o MinGW cross-compiler: sudo apt install mingw-w64"; exit 1; }
	x86_64-w64-mingw32-gcc $(BACK_SRC) -o $(BIN_DIR)/back.exe
	@echo "[OK] Executável gerado em $(BIN_DIR)/back.exe"

# --- Frontend em Python ---

# Gera executável standalone do frontend no Linux
front-linux:
	@echo "[BUILD] Gerando executável Python para Linux..."
	@command -v pyinstaller >/dev/null 2>&1 || { echo "[ERRO] Instale o PyInstaller: pip install pyinstaller"; exit 1; }
	pyinstaller --onefile --noconsole $(FRONT_SRC)
	@mkdir -p $(BIN_DIR) && cp dist/$(basename $(FRONT_SRC) .py) $(BIN_DIR)/
	@echo "[OK] Executável do frontend gerado em $(BIN_DIR)/$(basename $(FRONT_SRC) .py)"

# Gera executável standalone do frontend no Windows
front-win:
	@echo "[BUILD] Gerando executável Python para Windows..."
	@command -v pyinstaller >/dev/null 2>&1 || { echo "[ERRO] Instale o PyInstaller: pip install pyinstaller"; exit 1; }
	pyinstaller --onefile --noconsole $(FRONT_SRC)
	@mkdir -p $(BIN_DIR) && cp dist/$(basename $(FRONT_SRC) .py).exe $(BIN_DIR)/
	@echo "[OK] Executável do frontend gerado em $(BIN_DIR)/$(basename $(FRONT_SRC) .py).exe"

# --- Atalhos ---

# Gera todos executáveis para Linux
exe-all-linux: exe-linux front-linux

# Gera todos executáveis para Windows
exe-all-win: exe-win front-win
