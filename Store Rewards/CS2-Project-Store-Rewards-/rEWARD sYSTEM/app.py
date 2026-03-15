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
    "laptop": 25000, "mouse": 500, "keyboard": 1500, "headphones": 2000,
    "phone": 15000, "charger": 300, "tablet": 12000, "smartwatch": 8000,
    "earbuds": 3000, "usb hub": 800,
    "burger": 150, "pizza": 350, "fries": 80, "soda": 60, "sandwich": 120,
    "ramen": 200, "rice meal": 100, "coffee": 90, "milk tea": 130, "cake slice": 180,
    "t-shirt": 500, "hoodie": 1200, "jeans": 1500, "sneakers": 3500,
    "cap": 400, "socks": 150, "jacket": 2500, "shorts": 600,
    "sunglasses": 800, "wallet": 700, "backpack": 1800, "umbrella": 350,
    "watch": 4500, "belt": 500, "phone case": 250,
    "action figure": 600, "board game": 900, "rubiks cube": 300,
    "lego set": 2500, "playing cards": 150, "yo-yo": 200,
}

reward_items = {
    "gift card": 200, "coffee voucher": 80, "store discount 10%": 120,
    "store discount 20%": 220, "free delivery": 100, "food voucher": 150,
    "gaming mouse": 350, "phone case": 180, "earbuds": 500, "cap": 300,
    "tote bag": 250, "water bottle": 200, "notebook": 100, "pen set": 80,
    "mystery box": 400, "vip membership": 600, "birthday cake": 350, "movie ticket": 250,
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


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    data = accounts[user]
    error = ""
    if request.method == "POST":
        new_password = request.form["password"].strip()
        new_name     = request.form["name"].strip()
        new_age      = request.form["age"].strip()
        new_address  = request.form["address"].strip()
        if not new_password or len(new_password) < 4:
            error = "Password must be at least 4 characters."
        elif not new_name or len(new_name) < 2:
            error = "Full name must be at least 2 characters."
        elif not new_age or not new_age.isdigit() or not (1 <= int(new_age) <= 120):
            error = "Enter a valid age between 1 and 120."
        elif not new_address or len(new_address) < 3:
            error = "Address must be at least 3 characters."
        else:
            accounts[user][0] = new_password
            accounts[user][1] = new_name
            accounts[user][2] = new_age
            accounts[user][3] = new_address
            return render_template("edit_profile.html", username=user, data=accounts[user], success="Profile updated successfully!")
    return render_template("edit_profile.html", username=user, data=data, error=error)


@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    if request.method == "POST":
        confirm = request.form.get("confirm", "").strip()
        if confirm == user:
            del accounts[user]
            session.pop("user", None)
            return render_template("home.html", delete_success="Your account has been deleted.")
        return render_template("delete_account.html", username=user, typed=confirm, error="That username didn't match. Please try again.")
    return render_template("delete_account.html", username=user, typed="")
def delete_account():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    if request.method == "POST":
        confirm = request.form.get("confirm", "").strip()
        if confirm == user:
            del accounts[user]
            session.pop("user", None)
            return render_template("home.html", delete_success="Your account has been deleted.")
        return render_template("delete_account.html", username=user, typed=confirm, error="That username didn't match. Please try again.")
    return render_template("delete_account.html", username=user, typed="")@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    if request.method == "POST":
        confirm = request.form.get("confirm", "").strip()
        if confirm == user:
            del accounts[user]
            session.pop("user", None)
            return render_template("home.html", delete_success="Your account has been deleted.")
        return render_template("delete_account.html", username=user, typed=confirm, error="That username didn't match. Please try again.")
    return render_template("delete_account.html", username=user, typed="")


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
            session["admin"] = True
            return redirect(url_for("admin"))
        admin_attempts += 1
        remaining = 3 - admin_attempts
        if remaining <= 0:
            return render_template("error.html", message="Too many failed attempts. Admin access is locked.")
        return render_template("error.html", message=f"Invalid admin login. {remaining} attempt(s) remaining.")
    if session.get("admin"):
        return render_template("admin.html", accounts=accounts)
    return render_template("admin.html", accounts=None)


@app.route("/admin/edit/<target_user>", methods=["GET", "POST"])
def admin_edit(target_user):
    if not session.get("admin"):
        return redirect(url_for("admin"))
    if target_user not in accounts:
        return render_template("error.html", message="User not found.")
    data = accounts[target_user]
    error = ""
    if request.method == "POST":
        new_password = request.form["password"].strip()
        new_name     = request.form["name"].strip()
        new_age      = request.form["age"].strip()
        new_address  = request.form["address"].strip()
        try:
            new_money  = int(request.form["money"].strip())
            new_points = int(request.form["points"].strip())
        except ValueError:
            error = "Balance and points must be valid numbers."
            return render_template("admin_edit.html", target=target_user, data=data, error=error)
        if not new_password or len(new_password) < 4:
            error = "Password must be at least 4 characters."
        elif not new_name or len(new_name) < 2:
            error = "Full name must be at least 2 characters."
        elif not new_age or not new_age.isdigit() or not (1 <= int(new_age) <= 120):
            error = "Enter a valid age between 1 and 120."
        elif not new_address or len(new_address) < 3:
            error = "Address must be at least 3 characters."
        elif new_money < 0 or new_points < 0:
            error = "Balance and points cannot be negative."
        else:
            accounts[target_user][0] = new_password
            accounts[target_user][1] = new_name
            accounts[target_user][2] = new_age
            accounts[target_user][3] = new_address
            accounts[target_user][4] = new_money
            accounts[target_user][5] = new_points
            return render_template("admin_edit.html", target=target_user, data=accounts[target_user], success=f"Account '{target_user}' updated successfully!")
    return render_template("admin_edit.html", target=target_user, data=data, error=error)


@app.route("/admin/delete/confirm/<target_user>")
def admin_delete_confirm(target_user):
    if not session.get("admin"):
        return redirect(url_for("admin"))
    if target_user not in accounts:
        return render_template("error.html", message="User not found.")
    return render_template("admin_delete_confirm.html", target=target_user)


@app.route("/admin/delete/<target_user>", methods=["POST"])
def admin_delete(target_user):
    if not session.get("admin"):
        return redirect(url_for("admin"))
    if target_user in accounts:
        del accounts[target_user]
        if session.get("user") == target_user:
            session.pop("user", None)
    return render_template("admin.html", accounts=accounts, success=f"Account '{target_user}' has been deleted.")


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("admin", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)