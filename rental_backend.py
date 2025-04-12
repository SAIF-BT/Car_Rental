import json
from abc import ABC, abstractmethod


class User(ABC):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @abstractmethod
    def get_details(self):
        pass


class Admin(User):
    def __init__(self, username="admin", password="admin"):
        super().__init__(username, password)

    def get_details(self):
        return f"Admin: {self.username}"


class Customer(User):
    def __init__(self, username, password, cnic, phone):
        super().__init__(username, password)
        self.cnic = cnic
        self.phone = phone
        self.rented = False
        self.rentedCar = None
        self.moneySpent = 0
        self.rentalHistory = []

    def get_details(self):
        status = f"Rented: {self.rentedCar}" if self.rented else "No car rented"
        return f"{self.username} | CNIC: {self.cnic} | {status}"


class Car:
    def __init__(self, brand, model, mileage, rent_per_day, licensePlate):
        self.brand = brand
        self.model = model
        self.mileage = mileage
        self.rent_per_day = rent_per_day
        self.licensePlate = licensePlate
        self.available = True
        self.timesRented = 0

    def calculate_profit(self):
        return self.timesRented * self.rent_per_day


class RentalSystem:
    def __init__(self):
        self.cars = []
        self.customers = []
        self.admin = Admin()

    # --- Car Operations ---
    def add_car(self, brand, model, plateNum, mileage, rent_per_day):
        if any(car.licensePlate == plateNum for car in self.cars):
            return False, "License plate already exists."
        car = Car(brand, model, mileage, rent_per_day, plateNum)
        self.cars.append(car)
        self.save_data()
        return True, "Car added successfully."

    def remove_car(self, plateNum):
        for car in self.cars:
            if car.licensePlate == plateNum:
                self.cars.remove(car)
                self.save_data()
                return True, "Car removed successfully."
        return False, "Car not found."

    def get_all_cars(self):
        return self.cars

    def get_available_cars(self):
        return [car for car in self.cars if car.available]

    def get_car_by_plate(self, plate):
        return next((car for car in self.cars if car.licensePlate == plate), None)

    # --- Customer Operations ---
    def register_customer(self, username, password, cnic, phone):
        if not username or not password or not cnic or not phone:
            return False, "All fields are required."

        if any(c.cnic == cnic for c in self.customers):
            return False, "Customer with this CNIC already exists."

        customer = Customer(username, password, cnic, phone)
        self.customers.append(customer)
        self.save_data()
        return True, "Customer registered successfully."

    def login_customer(self, username, password):
        for customer in self.customers:
            if customer.username == username and customer.password == password:
                return customer
        return None

    def get_all_customers(self):
        return self.customers

    # --- Rent & Return ---
    def rent_car(self, customer: Customer, plateNum, days=1):
        if customer.rented:
            return False, "You already have a rented car."

        car = self.get_car_by_plate(plateNum)
        if car and car.available:
            car.available = False
            car.timesRented += 1
            customer.rented = True
            customer.rentedCar = plateNum
            rental_amount = car.rent_per_day * days
            customer.moneySpent += rental_amount
            customer.rentalHistory.append(
                {
                    "car": f"{car.brand} {car.model} ({plateNum})",
                    "days": days,
                    "amount": rental_amount
                }
            )
            self.save_data()
            return True, f"Car {plateNum} rented successfully for {days} day(s)."
        return False, "Car not available."

    def return_car(self, customer: Customer, kilometers):
        if not customer.rented or not customer.rentedCar:
            return False, "You have no car rented."

        car = self.get_car_by_plate(customer.rentedCar)
        if car:
            car.available = True
            car.mileage += kilometers
            customer.rentedCar = None
            customer.rented = False
            self.save_data()
            return True, "Car returned successfully."

        return False, "Rented car not found."

    # --- Reports ---
    def get_rental_report(self, plateNum):
        car = self.get_car_by_plate(plateNum)
        if car:
            return {
                "Model": car.model,
                "Brand": car.brand,
                "Rent per day": car.rent_per_day,
                "Total Profit": car.calculate_profit()
            }
        return None

    def get_filtered_cars(self, times):
        return [car for car in self.cars if car.timesRented > times]

    def get_customer_history(self, customer: Customer):
        return customer.rentalHistory

    # --- Save/Load ---
    def save_data(self):
        data = {
            "cars": [
                {
                    "brand": c.brand,
                    "model": c.model,
                    "licensePlate": c.licensePlate,
                    "mileage": c.mileage,
                    "rent_per_day": c.rent_per_day,
                    "available": c.available,
                    "timesRented": c.timesRented,
                } for c in self.cars
            ],
            "customers": [
                {
                    "username": cu.username,
                    "password": cu.password,
                    "cnic": cu.cnic,
                    "phone": cu.phone,
                    "rented": cu.rented,
                    "rentedCar": cu.rentedCar,
                    "moneySpent": cu.moneySpent,
                    "history": cu.rentalHistory
                } for cu in self.customers
            ]
        }
        with open("rental_data.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open("rental_data.json", "r") as f:
                data = json.load(f)

            self.cars.clear()
            for c in data["cars"]:
                car = Car(c["brand"], c["model"], c["mileage"], c["rent_per_day"], c["licensePlate"])
                car.available = c["available"]
                car.timesRented = c["timesRented"]
                self.cars.append(car)

            self.customers.clear()
            for cu in data["customers"]:
                cust = Customer(cu["username"], cu["password"], cu["cnic"], cu["phone"])
                cust.rented = cu["rented"]
                cust.rentedCar = cu["rentedCar"]
                cust.moneySpent = cu["moneySpent"]
                cust.rentalHistory = cu.get("history", [])
                self.customers.append(cust)

            return True, "Data loaded successfully."

        except Exception as e:
            return False, f"Error loading data: {e}"
