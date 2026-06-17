from PyQt6.QtWidgets import (
    QApplication, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QWidget
)
import sys
import sqlite3
from PyQt6.QtCore import Qt


class BankingProgram(QWidget):
    def __init__(self):
        super().__init__()
        self.db_connect()   # veritabanı başlangıçta kurulsun
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Banking App")

        # Widgetlar
        self.balance_info = QLabel("Balance:", self)

        # Kullanıcı adını gireceğin input (placeholder ile)
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Kullanıcı adını giriniz (ör: Hakan)")

        self.check_balance_btn = QPushButton("Display balance", self)
        self.withdraw_btn = QPushButton("Para çek", self)

        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Çekilecek parayı giriniz (sadece rakam)")

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.balance_info)
        vbox.addWidget(self.username_input)
        vbox.addWidget(self.check_balance_btn)
        vbox.addWidget(self.amount_input)
        vbox.addWidget(self.withdraw_btn)

        self.setLayout(vbox)

        # Style
        self.setStyleSheet("""
            QLabel {
                font-size: 30px;
                color: red;
                font-family: Calibri;
            }
            QPushButton {
                font-size: 22px;
                color: blue;
                font-family: Calibri;
                background-color: black;
            }
            QLineEdit {
                font-size: 18px;
            }
        """)

        # Signal-slot bağlantıları
        self.check_balance_btn.clicked.connect(self.show_balance)
        self.withdraw_btn.clicked.connect(self.withdraw_money)

    # --- Slot fonksiyonlar ---
    def show_balance(self):
        """Girilen kullanıcı adının bakiyesini göster"""
        username = self.username_input.text().strip()
        if not username:
            self.balance_info.setText("Lütfen kullanıcı adını giriniz.")
            return

        conn = sqlite3.connect("bankingapp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name, balance FROM Bilgiler WHERE name = ?", (username,))
        row = cursor.fetchone()

        if row:
            self.balance_info.setText(f"{row[0]} Bakiye: {row[1]}")
        else:
            self.balance_info.setText(f"Kullanıcı bulunamadı: {username}")

        conn.close()

    def withdraw_money(self):
        """Girilen kullanıcıdan miktarı düş"""
        username = self.username_input.text().strip()
        if not username:
            self.balance_info.setText("Lütfen kullanıcı adını giriniz.")
            return

        amount_text = self.amount_input.text().strip()
        if not amount_text:
            self.balance_info.setText("Lütfen çekilecek miktarı giriniz.")
            return

        # Rakam kontrolü (negatif ve ondalıklı kontrolü)
        if not amount_text.isdigit():
            self.balance_info.setText("Miktar pozitif tamsayı olmalıdır.")
            return

        amount = int(amount_text)
        if amount <= 0:
            self.balance_info.setText("Miktar sıfırdan büyük olmalı.")
            return

        conn = sqlite3.connect("bankingapp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM Bilgiler WHERE name = ?", (username,))
        row = cursor.fetchone()

        if row:
            balance = row[0]
            if balance >= amount:
                new_balance = balance - amount
                cursor.execute(
                    "UPDATE Bilgiler SET balance = ? WHERE name = ?",
                    (new_balance, username)
                )
                conn.commit()
                self.balance_info.setText(f"{username} Yeni Bakiye: {new_balance}")
            else:
                self.balance_info.setText("Yetersiz bakiye!")
        else:
            self.balance_info.setText(f"Kullanıcı bulunamadı: {username}")

        conn.close()

    def db_connect(self):
        """Veritabanını ve başlangıç kayıtlarını oluştur"""
        conn = sqlite3.connect("bankingapp.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bilgiler(
                name TEXT PRIMARY KEY,
                balance INTEGER
            )
        """)

        data = [
            ("Hakan", 100),
            ("Mehmet", 10000),
            ("Canan", 40000),
            ("Elif", 100),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO Bilgiler VALUES (?, ?)", data
        )

        conn.commit()
        conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    banking_app = BankingProgram()
    banking_app.show()
    sys.exit(app.exec())
