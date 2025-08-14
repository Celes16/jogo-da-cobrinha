# jogo-da-cobrinha — Backend em C e Frontend em Python

## Descrição do Projeto

Este projeto é a implementação de um jogo da cobrinha (Snake) dividido em **duas linguagens distintas** para atender ao requisito acadêmico de integração entre linguagens:

- **Backend (C)** → Implementa a lógica e cálculo do jogo, responsável por atualizar posições da cobrinha, verificar colisões e gerar novas posições de alimento.
- **Frontend (Python + pygame)** → Implementa a interface gráfica, captura entradas do usuário e exibe o jogo de forma visual.

A proposta é **explorar a vocação de cada linguagem**:
- **C**: desempenho, manipulação direta de memória, controle de fluxo rápido.
- **Python**: facilidade na criação de interfaces gráficas, manipulação de eventos e comunicação de alto nível.

---

## 📂 Estrutura do Repositório
├── back.c # Servidor/lógica do jogo (C)

├── front.py # Cliente/interface gráfica (Python)

├── Makefile # Automação de compilação e execução

├── README.md # Este arquivo

└── doc.pdf # Documento explicativo do projeto

---

## Bibliotecas Utilizadas

### **No backend (C)**:
O arquivo `back.c` utiliza as seguintes bibliotecas padrão:
- `stdio.h` → Entrada e saída padrão (`printf`, `sprintf`, etc.).
- `stdlib.h` → Funções utilitárias (`rand`, `malloc`, `free`).
- `string.h` → Manipulação de strings (`memset`, `strcmp`).
- `unistd.h` → Funções de controle de execução e sockets (`close`, `usleep`).
- `time.h` → Controle de tempo e geração de números aleatórios (`time`, `srand`).
- `sys/socket.h` → Criação e gerenciamento de sockets TCP.
- `netinet/in.h` → Estruturas e constantes para comunicação pela rede.
- `arpa/inet.h` → Funções para manipulação de endereços IP.

Essas bibliotecas permitem implementar um **servidor TCP** que processa os cálculos do jogo e se comunica com o frontend.

---

### **No frontend (Python)**:
O arquivo `front.py` utiliza:
- **pygame** → Biblioteca para criação de jogos e interfaces gráficas em Python.
- `socket` → Comunicação com o backend via TCP.
- `threading` → Recepção assíncrona de dados sem travar a interface.
- `sys`, `os`, `time` → Controle do sistema, configuração de ambiente e temporização.

Instalação de dependências do Python:
```bash```
pip install pygame
```bash```

### Comunicação Entre Backend e Frontend:

- A integração é feita por sockets TCP:
- Backend (C) abre um servidor na porta 8080.
- Frontend (Python) conecta-se ao servidor como cliente.
- O frontend envia comandos (U, D, L, R, N, M, Q) para o backend.
- O backend processa o comando, atualiza o estado do jogo e retorna uma string codificada com:
- Estado do jogo (0 = menu, 1 = jogando, 2 = fim de jogo)
- Tamanho da cobra
- Lista de coordenadas (cobra e comida)
- Pontuação e nível
- Este formato fixo permite que o frontend reconstrua fielmente a cena.

### Objetivo do trabalho, demostrar:

- Modularidade na arquitetura de software.

- Comunicação entre linguagens diferentes.

- Separação clara entre processamento lógico e apresentação gráfica.

