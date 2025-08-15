# Makefile para Jogo da Cobrinha Multiplataforma

# ======================
#  CONFIGURAÇÕES PRINCIPAIS
# ======================
BACKEND_SRC = back.c
FRONTEND_SRC = front.py

# Nomes dos executáveis
BACKEND_LINUX = back
FRONTEND_LINUX = front
BACKEND_WIN = back.exe
FRONTEND_WIN = front.exe

# ======================
#  LINUX
# ======================

# Instalar dependências no Linux
install-deps:
	@echo "Instalando dependências..."
	sudo apt update && sudo apt install -y build-essential python3 python3-pip
	pip install pyinstaller pygame

# Compilar backend para Linux
build-backend-linux:
	@echo "Compilando backend para Linux..."
	gcc $(BACKEND_SRC) -o $(BACKEND_LINUX) -lpthread
	chmod +x $(BACKEND_LINUX)

# Criar executável frontend para Linux
build-frontend-linux:
	@echo "Criando executável frontend para Linux..."
	pyinstaller --onefile --noconsole $(FRONTEND_SRC) --name $(FRONTEND_LINUX)
	chmod +x dist/$(FRONTEND_LINUX)

# Compilar tudo para Linux
build-linux: build-backend-linux build-frontend-linux

# Executar servidor
run-server:
	./$(BACKEND_LINUX)

# Executar cliente
run-client:
	./dist/$(FRONTEND_LINUX)

# ======================
#  WINDOWS
# ======================

# Compilar backend para Windows
build-backend-win:
	@echo "Compilando backend para Windows..."
	x86_64-w64-mingw32-gcc $(BACKEND_SRC) -o $(BACKEND_WIN) -lws2_32

# Criar executável frontend para Windows
build-frontend-win:
	@echo "Criando executável frontend para Windows..."
	wine pyinstaller --onefile --noconsole $(FRONTEND_SRC) --name $(FRONTEND_WIN)

# Compilar tudo para Windows
build-win: build-backend-win build-frontend-win

# ======================
#  UTILITÁRIOS
# ======================

# Executar jogo completo (Linux)
run-game:
	@echo "Iniciando servidor..."
	@./$(BACKEND_LINUX) & SERVER_PID=$$!; \
	sleep 1; \
	echo "Iniciando cliente..."; \
	./dist/$(FRONTEND_LINUX); \
	kill $$SERVER_PID

# Limpar arquivos gerados
clean:
	@echo "Limpando arquivos..."
	rm -f $(BACKEND_LINUX) $(BACKEND_WIN)
	rm -rf __pycache__ build dist *.spec

.PHONY: all run install-deps \
        build-backend-linux build-frontend-linux build-linux \
        build-backend-win build-frontend-win build-win \
        run-server run-client run-game clean
