from flask import Flask, redirect, render_template, request, session
from flask_restful import Api, Resource
from flask_session import Session
from datetime import timedelta
from quires import *
import sqlite3
import hashlib
import re
import os


def run_query(query, solo_query=True, params: tuple = (), count=False):

    db = sqlite3.connect("./app.db")
    cr = db.cursor()

    if solo_query:
        cr.execute(query, params) if params else cr.execute(query)
    else:
        cr.executescript(query, params) if params \
            else cr.executescript(query)

    result = cr.rowcount if count else cr.fetchall()

    db.commit()

    return result


def sha1(string: str) -> str:
    """ Generate hash password from a string"""
    return hashlib.sha1(string.encode('utf-8')).hexdigest()


# set the database
run_query(initial_query, solo_query=False)
admin_exists = run_query(admin_exists_query)
not len(admin_exists) and run_query(
    add_admin_query,
    params=("admin", sha1("Qazasd@123"))
)


# set the flask app
templates_dir = os.path.join("./templates")
static_dir = os.path.join("./static")

app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
app.secret_key = "Qazasd@123"
app.config['SESSION_TYPE'] = 'filesystem'
api = Api(app)
Session(app)


# set routes
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("user_session"):
        return redirect("/login")

    if request.full_path == "/?zero=True":
        customers = run_query(get_customers_nets_with_zeros_query)
    else:
        customers = run_query(get_customers_nets_query)

    total = 0

    session["errors"] = []

    if customers:
        customers = map(
            lambda x: tuple(
                list(x)[:-1] + [f"{int(list(x)[-1]):,}"] + [list(x)[-1]]
            ),
            customers
        )
        total = f"{run_query(get_customer_total_query)[0][0]:,}" 

    all_customers = run_query(get_all_customers_query)

    return render_template("index.html",
                           navbar="True",
                           page_title="Sheet",
                           customers=customers,
                           total=total,
                           all_customers=all_customers
                           )


@app.route("/users", methods=["GET", "POST"])
def users():

    is_admin = run_query(is_admin_query, params=(session.get("user_session"),))

    do = request.args.get("do") or "Manage"

    session["user"] = None

    users = run_query(get_all_users_query)

    if do == "Manage":
        if not len(is_admin):
            return redirect("/")

    elif do == "Insert":

        if not len(is_admin):
            return redirect("/")

        if request.method == "POST":

            username_reg = re.compile(r"^[a-z][a-z0-9\.\_]{3,}$")
            [inputted_username, inputted_password] = request.form.values()

            errors = []

            not re.search(username_reg, inputted_username) and \
                errors.append(
                    "Username must have at least 4 characters and must start with lower case letter and can include period or underscore")
            len(inputted_password) < 8 and errors.append(
                "Password must be at least 8 characters")

            user_exists = run_query(
                get_user_by_username_query, params=(inputted_username,))

            len(user_exists) and errors.append(
                f"{inputted_username} is exists.")

            if not len(errors):

                run_query(
                    add_regular_user_query,
                    params=(inputted_username, sha1(inputted_username))
                )
                session["errors"] = []
                return redirect("/users")

            else:

                session["errors"] = errors

    elif do == "Edit":

        if not len(is_admin):
            return redirect("/")

        userid = request.args.get("id") or 0
        user_exists = run_query(get_user_by_id_query, params=(userid,))
        if len(user_exists):
            session["user"] = user_exists[0]
        else:
            return redirect("/users")

    elif do == "Update":

        if not len(is_admin):
            return redirect("/")

        if request.method == "POST":

            username_reg = re.compile(r"^[a-z][a-z0-9\.\_]{3,}$")
            [userid, inputted_username, inputted_password] = request.form.values()

            errors = []

            user_exists = run_query(
                get_user_by_id_query, params=(userid,))

            not len(user_exists) and errors.append("The user does not exists")

            not re.search(username_reg, inputted_username) and \
                errors.append(
                    "Username must have at least 4 characters and must start with lower case letter and can include period or underscore")

            (len(inputted_password) < 8 and len(inputted_password) != 0) and errors.append(
                "Password must be at least 8 characters")

            another_user_exists = run_query(
                get_users_by_id_except_query, params=(userid,))

            another_user_exists = list(
                map(lambda x: x[1], another_user_exists))

            inputted_username in another_user_exists and errors.append(
                f"{inputted_username} is exists.")

            if not len(errors):

                if len(inputted_password) == 0:
                    run_query(
                        update_user_without_password_query,
                        params=(inputted_username, userid)
                    )
                else:
                    run_query(
                        update_user_with_password_query,
                        params=(
                            inputted_username,
                            sha1(inputted_password),
                            userid
                        )
                    )

                session["errors"] = []
                return redirect("/users")

            else:
                session["errors"] = errors

    elif do == "Activate":

        if not len(is_admin):
            return redirect("/")

        userid = request.args.get("id") or 0
        user_exists = run_query(get_user_by_id_query, params=(userid,))

        if len(user_exists):
            run_query(activate_user_query, params=(userid,))

        return redirect("/users")

    elif do == "Deactivate":

        if not len(is_admin):
            return redirect("/")

        userid = request.args.get("id") or 0
        user_exists = run_query(get_user_by_id_query, params=(userid,))

        if len(user_exists):
            run_query(deactivate_user_query, params=(userid,))

        return redirect("/users")

    elif do == "UpdatePassword":

        userid = session["user_session"]
        user_exists = run_query(get_user_by_id_query, params=(userid,))

        errors = []

        if len(user_exists) and request.method == "POST":

            [inputted_last_password,inputted_new_password] = request.form.values()
            password = run_query(get_user_by_id_query,params=(userid,))[0][2]

            sha1(inputted_last_password) != password and errors.append("كلمة السر القديمة غير مطابقة")
            len(inputted_new_password) < 8 and errors.append("يجب ان تكون كلمة السر الجديدة 8 احرف او أكثر")
            inputted_last_password == inputted_new_password and errors.append("يجب ان تكون كلمة السر الجديدة مختلفة عن القديمة")

            if len(errors):
                session["errors"] = errors
            else:
                run_query(update_user_password_query,params=(sha1(inputted_new_password),userid,))
                session["errors"] = []
                return redirect("/logout")

        else:
            return redirect("/")
        
    elif do == "EditPassword":

        userid = session["user_session"]
        user_exists = run_query(get_user_by_id_query, params=(userid,))
        if not len(user_exists):
            return redirect("/users")

    return render_template(
        "users.html",
        page_title="Add User",
        navbar="True",
        do=do,
        users=users
    )


@app.route("/ledger", methods=["GET"])
def ledger():
    customer_id = request.args.get("id")
    customer_exists = run_query(
        get_customer_by_id_query,
        params=(customer_id,)
    )

    if len(customer_exists):
        data = run_query(
            get_customer_ledger_query,
            params=(customer_id,)
        )
        data = list(map(lambda x: tuple(list(x) + [f"{int(x[-1]):,}"]), data))

        net = 0
        new_data = []
        for row in data:
            net += int(row[-2])
            new_data.append(row + (net, f"{net:,}",))

        data = new_data

    else:
        return redirect("/")

    all_customers = run_query(get_all_customers_query)

    return render_template(
        "ledger.html",
        navbar="True",
        page_title="كشف حساب " + data[0][0],
        data=data,
        all_customers=all_customers
    )


@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":

        [customer_name, amount] = request.form.values()
        customer_exists = run_query(
            get_customer_by_name_query, params=(customer_name,))

        if len(customer_exists):

            customer_id = customer_exists[0][0]
            run_query(
                add_customer_transaction_query,
                params=(customer_id, amount, session["user_session"])
            )

        else:

            customer_id = run_query(get_next_customer_id_query)
            customer_id = 1 if not len(customer_id) else customer_id[0][0] + 1
            run_query(add_customer_query, params=(customer_name,))
            run_query(
                add_customer_transaction_query,
                params=(customer_id, amount, session["user_session"])
            )

        return redirect("/")


@app.route("/logout")
def logout():
    session["user_session"] = None
    session["username"] = None
    session["is_admin"] = None
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_session"):
        return redirect("/")

    errors = []

    if request.method == "POST":
        [inputted_user, inputted_password] = request.form.values()

        user_exists = run_query(
            get_user_by_username_query,
            params=(inputted_user,)
        )

        if len(user_exists):
            user_id = run_query(
                get_user_by_username_query,
                params=(inputted_user,)
            )[0][0]
            user_password = run_query(
                get_user_by_username_query,
                params=(inputted_user,)
            )[0][2]

            if user_password == sha1(inputted_password):
                session["user_session"] = user_id
                session["username"] = inputted_user

                is_admin = run_query(is_admin_query, params=(
                    session.get("user_session"),))
                if len(is_admin):
                    session["is_admin"] = 1

                return redirect("/")
            else:
                errors.append(f"Password incorrect for {inputted_user}.")
                return render_template(
                    "login.html",
                    errors=errors,
                    page_title="Login",
                    navbar="False"
                )
        else:
            errors.append(f"{inputted_user} not found")
            return render_template(
                "login.html",
                errors=errors,
                page_title="Login",
                navbar="False"
            )

    return render_template(
        "login.html",
        page_title="Login",
        navbar="False"
    )


if __name__ == "__main__":
    app.run(debug=True, port=4500, host="0.0.0.0")
