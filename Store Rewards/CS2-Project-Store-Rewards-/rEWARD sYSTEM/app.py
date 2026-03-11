from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.secret_key = "secret123"
accounts = {
    "@shai2": ["smooth123", "SGA", "27", "Canada", 5000, 400]
}
ADMIN_USER = "GabEllima"
ADMIN_PASS = "2sday"
admin_attempts = 0

store_items = {
    # Tech
    "laptop": 25000,
    "mouse": 500,
    "keyboard": 1500,
    "headphones": 2000,
    "phone": 15000,
    "charger": 300,
    "tablet": 12000,
    "smartwatch": 8000,
    "earbuds": 3000,
    "usb hub": 800,
    # Food
    "burger": 150,
    "pizza": 350,
    "fries": 80,
    "soda": 60,
    "sandwich": 120,
    "ramen": 200,
    "rice meal": 100,
    "coffee": 90,
    "milk tea": 130,
    "cake slice": 180,
    # Clothing
    "t-shirt": 500,
    "hoodie": 1200,
    "jeans": 1500,
    "sneakers": 3500,
    "cap": 400,
    "socks": 150,
    "jacket": 2500,
    "shorts": 600,
    # Accessories
    "sunglasses": 800,
    "wallet": 700,
    "backpack": 1800,
    "umbrella": 350,
    "watch": 4500,
    "belt": 500,
    "phone case": 250,
    # Toys
    "action figure": 600,
    "board game": 900,
    "rubiks cube": 300,
    "lego set": 2500,
    "playing cards": 150,
    "yo-yo": 200,
}

reward_items = {
    # Vouchers
    "gift card": 200,
    "coffee voucher": 80,
    "store discount 10%": 120,
    "store discount 20%": 220,
    "free delivery": 100,
    "food voucher": 150,
    # Items
    "gaming mouse": 350,
    "phone case": 180,
    "earbuds": 500,
    "cap": 300,
    "tote bag": 250,
    "water bottle": 200,
    "notebook": 100,
    "pen set": 80,
    # Special
    "mystery box": 400,
    "vip membership": 600,
    "birthday cake": 350,
    "movie ticket": 250,
}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]
        age = request.form["age"]
        address = request.form["address"]
        if username in accounts:
            return render_template("register.html", error="Username already exists. Please choose another.")
        accounts[username] = [password, name, age, address, 0, 0]
        return render_template("register.html", success="Account created successfully! You can now log in.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in accounts and accounts[username][0] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password. Please try again.")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    data = accounts[user]
    return render_template("dashboard.html", username=user, name=data[1], money=data[4], points=data[5])

@app.route("/atm", methods=["GET", "POST"])
def atm():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    message = ""
    if request.method == "POST":
        try:
            amount = int(request.form["amount"])
            if amount <= 0:
                message = "Enter a valid amount"
            else:
                accounts[user][4] += amount
                message = f"Deposited ₱{amount:,} successfully!"
        except ValueError:
            message = "Invalid input!"
    return render_template("atm.html", money=accounts[user][4], message=message)

@app.route("/store", methods=["GET", "POST"])
def store():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    message = ""
    search = request.args.get("search", "")
    category = request.args.get("category", "all")

    categories = {
        "tech":        ["laptop", "mouse", "keyboard", "headphones", "phone", "charger", "tablet", "smartwatch", "earbuds", "usb hub"],
        "food":        ["burger", "pizza", "fries", "soda", "sandwich", "ramen", "rice meal", "coffee", "milk tea", "cake slice"],
        "clothing":    ["t-shirt", "hoodie", "jeans", "sneakers", "cap", "socks", "jacket", "shorts"],
        "accessories": ["sunglasses", "wallet", "backpack", "umbrella", "watch", "belt", "phone case"],
        "toys":        ["action figure", "board game", "rubiks cube", "lego set", "playing cards", "yo-yo"],
    }

    filtered = store_items
    if category != "all" and category in categories:
        filtered = {k: v for k, v in store_items.items() if k in categories[category]}
    if search:
        filtered = {k: v for k, v in filtered.items() if search.lower() in k.lower()}

    if request.method == "POST":
        item = request.form["item"]
        try:
            quantity = int(request.form.get("quantity", 1))
            if quantity <= 0:
                message = "Enter a valid quantity"
            elif item in store_items:
                price = store_items[item]
                total = price * quantity
                if accounts[user][4] >= total:
                    accounts[user][4] -= total
                    points = (total // 50) * 10
                    accounts[user][5] += points
                    message = f"Purchased {quantity}x {item} for ₱{total:,}! +{points} points"
                else:
                    message = f"Insufficient funds! You need ₱{total:,} but only have ₱{accounts[user][4]:,}"
            else:
                message = "Item not found"
        except ValueError:
            message = "Invalid quantity"

    return render_template("store.html", items=filtered, message=message, money=accounts[user][4], points=accounts[user][5], category=category, search=search)

@app.route("/rewards", methods=["GET", "POST"])
def rewards():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    message = ""
    if request.method == "POST":
        item = request.form["item"]
        if item in reward_items:
            cost = reward_items[item]
            if accounts[user][5] >= cost:
                accounts[user][5] -= cost
                message = f"You redeemed: {item}!"
            else:
                message = f"Insufficient points! You need {cost} pts but only have {accounts[user][5]} pts"
        else:
            message = "Item not found"
    return render_template("rewards.html", items=reward_items, message=message, points=accounts[user][5])

@app.route("/admin", methods=["GET", "POST"])
def admin():
    global admin_attempts
    if admin_attempts >= 3:
        return render_template("error.html", message="Too many failed attempts. Admin access is locked.")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USER and password == ADMIN_PASS:
            admin_attempts = 0
            return render_template("admin.html", accounts=accounts)
        admin_attempts += 1
        remaining = 3 - admin_attempts
        if remaining <= 0:
            return render_template("error.html", message="Too many failed attempts. Admin access is locked.")
        return render_template("error.html", message=f"Invalid admin login. {remaining} attempt(s) remaining.")
    return render_template("admin.html", accounts=None)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)