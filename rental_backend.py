import json

class Admin:
    def __init__(self, username="admin", password="admin"):
        self.username = username
        self.password = password

class Car:
    def __init__(self, brand, model, mileage, rent, licensePlate):
        self.brand = brand
        self.model = model
        self.mileage = mileage
        self.rent = rent
        self.licensePlate = licensePlate
        self.available = True
        self.timesRented = 0

    def calculate_profit(self):
        return self.timesRented * self.rent

class Customer:
    def __init__(self, userName, password, cnic, phone):
        self.userName = userName
        self.password = password
        self.cnic = cnic
        self.phone = phone
        self.rented = False
        self.rentedCar = None
        self.moneySpent = 0

class RentalSystem:
    def __init__(self):
        self.cars = []
        self.customers = []
        self.admin = Admin()

    def add_car(self, brand, model, plateNum, mileage, rent):
        if any(car.licensePlate == plateNum for car in self.cars):
            return False, "License plate already exists."
        car = Car(brand, model, mileage, rent, plateNum)
        self.cars.append(car)
        return True, "Car added successfully."

    def remove_car(self, plateNum):
        for car in self.cars:
            if car.licensePlate == plateNum:
                self.cars.remove(car)
                return True, "Car removed successfully."
        return False, "Car not found."

    def get_all_cars(self):
        return self.cars

    def get_available_cars(self):
        return [car for car in self.cars if car.available]

    def get_car_by_plate(self, plate):
        for car in self.cars:
            if car.licensePlate == plate:
                return car
        return None

    def register_customer(self, userName, password, cnic, phone):
        if any(c.cnic == cnic for c in self.customers):
            return False, "Customer with this CNIC already exists."
        customer = Customer(userName, password, cnic, phone)
        self.customers.append(customer)
        return True, "Customer registered."

    def login_customer(self, username, password):
        for customer in self.customers:
            if customer.userName == username and customer.password == password:
                return customer
        return None

    def rent_car(self, customer, plateNum):
        if customer.rented:
            return False, "Customer already has a rented car."

        car = self.get_car_by_plate(plateNum)
        if car and car.available:
            car.available = False
            car.timesRented += 1
            customer.rented = True
            customer.rentedCar = plateNum
            customer.moneySpent += car.rent
            return True, f"Car {plateNum} rented successfully."
        return False, "Car not available."

    def return_car(self, customer, kilometers):
        if not customer.rented or not customer.rentedCar:
            return False, "Customer did not rent a car."

        car = self.get_car_by_plate(customer.rentedCar)
        if car:
            car.available = True
            car.mileage += kilometers
            customer.rentedCar = None
            customer.rented = False
            return True, "Car returned successfully."

        return False, "Rented car not found."

    def get_rental_report(self, plateNum):
        car = self.get_car_by_plate(plateNum)
        if car:
            return {
                "Model": car.model,
                "Brand": car.brand,
                "Rent": car.rent,
                "Profit": car.calculate_profit()
            }
        return None

    def get_all_customers(self):
        return self.customers

    def save_data(self):
        data = {
            "cars": [
                {
                    "brand": c.brand,
                    "model": c.model,
                    "licensePlate": c.licensePlate,
                    "mileage": c.mileage,
                    "rent": c.rent,
                    "available": c.available,
                    "timesRented": c.timesRented,
                } for c in self.cars
            ],
            "customers": [
                {
                    "userName": cu.userName,
                    "password": cu.password,
                    "cnic": cu.cnic,
                    "phone": cu.phone,
                    "rented": cu.rented,
                    "rentedCar": cu.rentedCar,
                    "moneySpent": cu.moneySpent,
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
                car = Car(c["brand"], c["model"], c["mileage"], c["rent"], c["licensePlate"])
                car.available = c["available"]
                car.timesRented = c["timesRented"]
                self.cars.append(car)

            self.customers.clear()
            for cu in data["customers"]:
                cust = Customer(cu["userName"], cu["password"], cu["cnic"], cu["phone"])
                cust.rented = cu["rented"]
                cust.rentedCar = cu["rentedCar"]
                cust.moneySpent = cu["moneySpent"]
                self.customers.append(cust)

            return True, "Data loaded successfully."

        except Exception as e:
            return False, f"Error loading data: {e}"