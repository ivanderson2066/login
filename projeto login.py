import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QStackedWidget, QMessageBox
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
import sqlite3

class BancoDeDados:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.criar_tabela()

    def criar_tabela(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS usuarios
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome_usuario TEXT NOT NULL UNIQUE,
                            senha TEXT NOT NULL)''')

    def verificar_existencia_nome_usuario(self, nome_usuario):
        cursor = self.conn.execute("SELECT * FROM usuarios WHERE nome_usuario = ?", (nome_usuario,))
        result = cursor.fetchone()
        return result is not None

    def cadastrar_usuario(self, nome_usuario, senha):
        try:
            if self.verificar_existencia_nome_usuario(nome_usuario):
                raise Exception("Nome de usuário já está em uso.")

            self.conn.execute("INSERT INTO usuarios (nome_usuario, senha) VALUES (?, ?)", (nome_usuario, senha))
            self.conn.commit()

        except sqlite3.Error as error:
            raise Exception(f"Ocorreu um erro ao cadastrar o usuário: {str(error)}")

    def verificar_login(self, nome_usuario, senha):
        cursor = self.conn.execute("SELECT * FROM usuarios WHERE nome_usuario = ? AND senha = ?", (nome_usuario, senha))
        result = cursor.fetchone()
        return result is not None

    def fechar(self):
        self.conn.close()

class PaginaBoasVindas(QWidget):
    def __init__(self, parent, nome_usuario):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel(f"Bem-vindo, {nome_usuario}!")
        label.setFont(QFont("Arial", 16))
        layout.addWidget(label)
        self.setLayout(layout)

class PaginaLogin(QWidget):
    def __init__(self, parent, banco_dados):
        super().__init__(parent)
        self.banco_dados = banco_dados
        layout = QVBoxLayout()
        label = QLabel("Login:")
        label.setFont(QFont("Arial", 16))
        self.campo_nome_usuario = QLineEdit()
        self.campo_senha = QLineEdit()
        self.campo_senha.setEchoMode(QLineEdit.Password)
        botao_login = QPushButton("Login")
        botao_login.clicked.connect(self.login)
        botao_cadastro_pagina = QPushButton("Novo Cadastro")
        botao_cadastro_pagina.clicked.connect(lambda: parent.setCurrentIndex(1))
        layout.addWidget(label)
        layout.addWidget(QLabel("Nome de Usuário:"))
        layout.addWidget(self.campo_nome_usuario)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.campo_senha)
        layout.addWidget(botao_login)
        layout.addWidget(botao_cadastro_pagina)
        self.setLayout(layout)

    def login(self):
        nome_usuario = self.campo_nome_usuario.text()
        senha = self.campo_senha.text()
        if self.banco_dados.verificar_login(nome_usuario, senha):
            janela_principal = self.parent().parent()
            janela_principal.exibir_pagina_boas_vindas(nome_usuario)
            print("Login realizado com sucesso.")
        else:
            QMessageBox.critical(self, "Erro", "Nome de usuário ou senha inválidos.")

class PaginaCadastro(QWidget):
    def __init__(self, parent, banco_dados):
        super().__init__(parent)
        self.banco_dados = banco_dados
        layout = QVBoxLayout()
        label = QLabel("Cadastro:")
        label.setFont(QFont("Arial", 16))
        self.campo_nome_usuario = QLineEdit()
        self.campo_senha = QLineEdit()
        self.campo_senha.setEchoMode(QLineEdit.Password)
        botao_cadastrar = QPushButton("Cadastrar")
        botao_cadastrar.clicked.connect(self.cadastrar_usuario)
        botao_login_pagina = QPushButton("Login")
        botao_login_pagina.clicked.connect(lambda: parent.setCurrentIndex(0))
        layout.addWidget(label)
        layout.addWidget(QLabel("Nome de Usuário:"))
        layout.addWidget(self.campo_nome_usuario)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.campo_senha)
        layout.addWidget(botao_cadastrar)
        layout.addWidget(botao_login_pagina)
        self.setLayout(layout)

    def cadastrar_usuario(self):
        nome_usuario = self.campo_nome_usuario.text()
        senha = self.campo_senha.text()
        try:
            if nome_usuario == "" or senha == "":
                raise Exception("Por favor, preencha todos os campos.")

            self.banco_dados.cadastrar_usuario(nome_usuario, senha)
            QMessageBox.information(self, "Sucesso", "Usuário cadastrado com sucesso.")
            self.limpar_campos()

        except Exception as error:
            QMessageBox.critical(self, "Erro", str(error))

    def limpar_campos(self):
        self.campo_nome_usuario.clear()
        self.campo_senha.clear()

class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Login e Cadastro")
        self.set_palette()
        self.banco_dados = BancoDeDados()
        self.stacked_widget = QStackedWidget()
        self.criar_paginas()
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(10, 20, 20, 40)
        self.setMinimumSize(400, 200)
        self.setLayout(layout)

    def set_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.Button, QColor(50, 150, 250))
        palette.setColor(QPalette.ButtonText, Qt.black)
        self.setPalette(palette)

    def criar_paginas(self):
        pagina_login = PaginaLogin(self.stacked_widget, self.banco_dados)
        pagina_cadastro = PaginaCadastro(self.stacked_widget, self.banco_dados)
        self.stacked_widget.addWidget(pagina_login)
        self.stacked_widget.addWidget(pagina_cadastro)

    def criar_pagina_boas_vindas(self, nome_usuario):
        pagina_boas_vindas = PaginaBoasVindas(self.stacked_widget, nome_usuario)
        self.stacked_widget.addWidget(pagina_boas_vindas)
        self.stacked_widget.setCurrentWidget(pagina_boas_vindas)

    def exibir_pagina_boas_vindas(self, nome_usuario):
        self.criar_pagina_boas_vindas(nome_usuario)

    def closeEvent(self, event):
        self.banco_dados.fechar()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec_())