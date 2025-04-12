import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QMessageBox, QStackedWidget, QFormLayout, QInputDialog
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

from rental_backend import RentalSystem

rental = RentalSystem()
rental.load_data()


# Splash screen
class SplashScreen(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()
        logo = QLabel()
        pixmap = QPixmap("logo.png")
        logo.setPixmap(pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("Online Car Rental System")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(logo)
        layout.addWidget(title)
        self.setLayout(layout)

        QTimer.singleShot(2500, self.show_main)

    def show_main(self):
        self.stack.setCurrentIndex(1)


# Main menu
class MainMenu(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()

        title = QLabel("Main Menu")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        btnAdmin = QPushButton("Login as Admin")
        btnCustomer = QPushButton("Login as Customer")
        btnRegister = QPushButton("Register as New Customer")
        btnExit = QPushButton("Exit")

        btnAdmin.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btnCustomer.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btnRegister.clicked.connect(lambda: self.stack.setCurrentIndex(6))
        btnExit.clicked.connect(lambda: sys.exit())

        layout.addWidget(title)
        layout.addWidget(btnAdmin)
        layout.addWidget(btnCustomer)
        layout.addWidget(btnRegister)
        layout.addWidget(btnExit)
        self.setLayout(layout)


# Admin login
class AdminLogin(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QFormLayout()
        self.user = QLineEdit()
        self.passwd = QLineEdit()
        self.passwd.setEchoMode(QLineEdit.Password)
        layout.addRow("Username:", self.user)
        layout.addRow("Password:", self.passwd)
        btnLogin = QPushButton("Login")
        btnLogin.clicked.connect(self.check_login)
        layout.addRow(btnLogin)
        self.setLayout(layout)

    def check_login(self):
        if self.user.text() == rental.admin.username and self.passwd.text() == rental.admin.password:
            self.stack.setCurrentIndex(4)
        else:
            QMessageBox.warning(self, "Error", "Invalid admin credentials")


# Admin dashboard
class AdminDashboard(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()

        title = QLabel("Admin Dashboard")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)

        btnView = QPushButton("View Cars")
        btnAdd = QPushButton("Add Car")
        btnEditCar = QPushButton("Edit Car Details")
        btnReports = QPushButton("View Car Rental Report")
        btnFilterReport = QPushButton("View Cars Rented More Than X Times")
        btnCustomers = QPushButton("View All Customers")
        btnEditCustomer = QPushButton("Edit Customer Details")
        btnSave = QPushButton("Save Data")
        btnLoad = QPushButton("Load Data")
        btnBack = QPushButton("Logout")

        self.carList = QLabel("")
        self.carList.setWordWrap(True)

        btnView.clicked.connect(self.view_cars)
        btnAdd.clicked.connect(self.add_car)
        btnEditCar.clicked.connect(self.edit_car)
        btnReports.clicked.connect(self.show_report)
        btnFilterReport.clicked.connect(self.filtered_report)
        btnCustomers.clicked.connect(self.view_customers)
        btnEditCustomer.clicked.connect(self.edit_customer)
        btnSave.clicked.connect(self.save_all)
        btnLoad.clicked.connect(self.load_all)
        btnBack.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(title)
        layout.addWidget(btnView)
        layout.addWidget(btnAdd)
        layout.addWidget(btnEditCar)
        layout.addWidget(btnReports)
        layout.addWidget(btnFilterReport)
        layout.addWidget(btnCustomers)
        layout.addWidget(btnEditCustomer)
        layout.addWidget(btnSave)
        layout.addWidget(btnLoad)
        layout.addWidget(self.carList)
        layout.addWidget(btnBack)
        self.setLayout(layout)

    def view_cars(self):
        cars = rental.get_all_cars()
        if not cars:
            self.carList.setText("No cars added yet.")
        else:
            text = ""
            for car in cars:
                status = "Available" if car.available else "Rented"
                text += f"{car.brand} {car.model} | {car.licensePlate} | Rent: {car.rent} | {status}\n"
            self.carList.setText(text)

    def add_car(self):
        try:
            brand, _ = QInputDialog.getText(self, "Brand", "Enter car brand:")
            model, _ = QInputDialog.getText(self, "Model", "Enter car model:")
            plate, _ = QInputDialog.getText(self, "Plate", "Enter license plate:")
            mileage, _ = QInputDialog.getInt(self, "Mileage", "Enter mileage:")
            rent, _ = QInputDialog.getInt(self, "Rent", "Enter rent per day:")
            success, msg = rental.add_car(brand, model, plate, mileage, rent)
            QMessageBox.information(self, "Add Car", msg)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def edit_car(self):
        plate, ok = QInputDialog.getText(self, "Edit Car", "Enter plate number to edit:")
        if ok:
            car = rental.get_car_by_plate(plate)
            if not car:
                QMessageBox.warning(self, "Error", "Car not found.")
                return
            brand, _ = QInputDialog.getText(self, "Brand", "New brand:", text=car.brand)
            model, _ = QInputDialog.getText(self, "Model", "New model:", text=car.model)
            mileage, _ = QInputDialog.getInt(self, "Mileage", "New mileage:", value=car.mileage)
            rent, _ = QInputDialog.getInt(self, "Rent", "New rent:", value=car.rent)
            car.brand = brand
            car.model = model
            car.mileage = mileage
            car.rent = rent
            QMessageBox.information(self, "Updated", "Car updated.")

    def show_report(self):
        plate, ok = QInputDialog.getText(self, "Report", "Enter license plate:")
        if ok:
            report = rental.get_rental_report(plate)
            if report:
                msg = f"Model: {report['Model']}\nBrand: {report['Brand']}\nRent: {report['Rent']}\nProfit: {report['Profit']}"
                QMessageBox.information(self, "Rental Report", msg)
            else:
                QMessageBox.warning(self, "Not Found", "No car with that plate.")

    def filtered_report(self):
        times, ok = QInputDialog.getInt(self, "Filter", "Show cars rented more than:", value=0)
        if ok:
            cars = [c for c in rental.cars if c.timesRented > times]
            text = "\n".join([f"{c.brand} {c.model} | Rented: {c.timesRented}x" for c in cars]) or "None"
            QMessageBox.information(self, "Filtered Cars", text)

    def view_customers(self):
        customers = rental.get_all_customers()
        text = "\n".join([f"{c.userName} | CNIC: {c.cnic} | Phone: {c.phone}" for c in customers]) or "None"
        QMessageBox.information(self, "Customers", text)

    def edit_customer(self):
        cnic, ok = QInputDialog.getText(self, "Edit", "Enter CNIC:")
        if ok:
            customer = next((c for c in rental.customers if c.cnic == cnic), None)
            if not customer:
                QMessageBox.warning(self, "Error", "Customer not found.")
                return
            name, _ = QInputDialog.getText(self, "Username", "New name:", text=customer.userName)
            phone, _ = QInputDialog.getText(self, "Phone", "New phone:", text=customer.phone)
            password, _ = QInputDialog.getText(self, "Password", "New password:", text=customer.password)
            customer.userName = name
            customer.phone = phone
            customer.password = password
            QMessageBox.information(self, "Updated", "Customer updated.")

    def save_all(self):
        rental.save_data()
        QMessageBox.information(self, "Saved", "Data saved to file.")

    def load_all(self):
        success, msg = rental.load_data()
        QMessageBox.information(self, "Load", msg)


# Customer Login
class CustomerLogin(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QFormLayout()
        self.user = QLineEdit()
        self.passwd = QLineEdit()
        self.passwd.setEchoMode(QLineEdit.Password)
        layout.addRow("Username:", self.user)
        layout.addRow("Password:", self.passwd)
        btnLogin = QPushButton("Login")
        btnLogin.clicked.connect(self.check_login)
        layout.addRow(btnLogin)
        self.setLayout(layout)

    def check_login(self):
        user = rental.login_customer(self.user.text(), self.passwd.text())
        if user:
            self.stack.customer_user = user
            self.stack.setCurrentIndex(5)
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")


# Customer Register
class CustomerRegister(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QFormLayout()
        self.user = QLineEdit()
        self.passwd = QLineEdit()
        self.passwd.setEchoMode(QLineEdit.Password)
        self.cnic = QLineEdit()
        self.phone = QLineEdit()
        layout.addRow("Username:", self.user)
        layout.addRow("Password:", self.passwd)
        layout.addRow("CNIC:", self.cnic)
        layout.addRow("Phone:", self.phone)
        btnRegister = QPushButton("Register")
        btnRegister.clicked.connect(self.register_user)
        layout.addRow(btnRegister)
        self.setLayout(layout)

    def register_user(self):
        success, msg = rental.register_customer(
            self.user.text(), self.passwd.text(), self.cnic.text(), self.phone.text()
        )
        QMessageBox.information(self, "Registration", msg)
        if success:
            self.stack.setCurrentIndex(1)


# Customer Dashboard
class CustomerDashboard(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()
        label = QLabel("Customer Dashboard")
        label.setFont(QFont("Arial", 16))
        layout.addWidget(label)

        btnView = QPushButton("View Available Cars")
        btnRent = QPushButton("Rent Car")
        btnReturn = QPushButton("Return Car")
        btnBack = QPushButton("Logout")

        self.output = QLabel("")
        self.output.setWordWrap(True)

        btnView.clicked.connect(self.show_cars)
        btnRent.clicked.connect(self.rent_car)
        btnReturn.clicked.connect(self.return_car)
        btnBack.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(btnView)
        layout.addWidget(btnRent)
        layout.addWidget(btnReturn)
        layout.addWidget(self.output)
        layout.addWidget(btnBack)
        self.setLayout(layout)

    def show_cars(self):
        cars = rental.get_available_cars()
        if not cars:
            self.output.setText("No cars available.")
        else:
            text = "\n".join([f"{c.brand} {c.model} | {c.licensePlate} | Rent: {c.rent}" for c in cars])
            self.output.setText(text)

    def rent_car(self):
        plate, ok = QInputDialog.getText(self, "Rent", "Enter plate number:")
        if ok:
            success, msg = rental.rent_car(self.stack.customer_user, plate)
            QMessageBox.information(self, "Rent Car", msg)

    def return_car(self):
        kms, ok = QInputDialog.getInt(self, "Return", "KM driven:")
        if ok:
            success, msg = rental.return_car(self.stack.customer_user, kms)
            QMessageBox.information(self, "Return Car", msg)


# Main App
class CarRentalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Car Rental System")
        self.setGeometry(300, 100, 600, 500)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.stack.customer_user = None

        self.stack.addWidget(SplashScreen(self.stack))       # 0
        self.stack.addWidget(MainMenu(self.stack))           # 1
        self.stack.addWidget(AdminLogin(self.stack))         # 2
        self.stack.addWidget(CustomerLogin(self.stack))      # 3
        self.stack.addWidget(AdminDashboard(self.stack))     # 4
        self.stack.addWidget(CustomerDashboard(self.stack))  # 5
        self.stack.addWidget(CustomerRegister(self.stack))   # 6

        self.stack.setCurrentIndex(0)


# Run App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CarRentalApp()
    win.show()
    sys.exit(app.exec_())
self.setWindowIcon(QIcon("logo.png"))
