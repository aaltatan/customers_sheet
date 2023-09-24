import sqlite3
import hashlib


initial_query = \
    """CREATE TABLE IF NOT EXISTS
            users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                user_password TEXT NOT NULL,
                create_date TEXT DEFAULT CURRENT_TIMESTAMP,
                is_admin INTEGER BLOB DEFAULT 0,
                is_activated INTEGER DEFAULT 0
            );
        CREATE TABLE IF NOT EXISTS
            customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                create_date TEXT DEFAULT CURRENT_TIMESTAMP
            );
        CREATE TABLE IF NOT EXISTS
            customers_transactions (
                customer_id INTEGER NOT NULL,
                transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
                amount INTEGER DEFAULT 0,
                user_id INTEGER NOT NULL,
                CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
    """

add_admin_query = \
    """INSERT INTO 
            users(
                username,
                user_password,
                is_admin,
                is_activated
            )
        VALUES
            (?,?,1,1)
    """

admin_exists_query = \
    """SELECT 
            *
        FROM
            users
        WHERE
            is_admin = 1
    """

get_user_by_username_query = \
    """SELECT 
            *
        FROM
            users
        WHERE
            username = ?
        LIMIT
            1
    """

get_user_by_username_login_query = \
    """SELECT 
            *
        FROM
            users
        WHERE
            username = ?
        AND
            is_activated = 1
        LIMIT
            1
    """

get_deactivated_user_by_id_query = \
    """SELECT 
            *
        FROM
            users
        WHERE
            user_id = ?
        AND
            is_activated = 0
        LIMIT
            1
    """

get_users_by_id_except_query = \
    """SELECT 
            *
        FROM
            users
        WHERE
            user_id != ?
    """

get_user_by_id_query = \
    """SELECT 
            *
        FROM
            users
        WHERE
            user_id = ?
        LIMIT
            1
    """

update_user_with_password_query = \
    """UPDATE 
            users 
        SET 
            username = ?,
            user_password = ?
        WHERE
            user_id = ?
    """

update_user_without_password_query = \
    """UPDATE 
            users 
        SET 
            username = ?
        WHERE
            user_id = ?
    """

update_user_password_query = \
    """UPDATE 
            users 
        SET 
            user_password = ?
        WHERE
            user_id = ?
    """

activate_user_query = \
    """UPDATE 
            users 
        SET 
            is_activated = 1
        WHERE
            user_id = ?
    """

deactivate_user_query = \
    """UPDATE 
            users 
        SET 
            is_activated = 0
        WHERE
            user_id = ?
    """

get_customer_by_name_query = \
    """SELECT 
            *
        FROM
            customers
        WHERE
            customer_name = ?
        LIMIT
            1
    """

get_customer_by_id_query = \
    """SELECT 
            *
        FROM
            customers
        WHERE
            customer_id = ?
        LIMIT
            1
    """

add_customer_query = \
    """INSERT INTO 
            customers(customer_name)
        VALUES
            (?)
    """

add_customer_transaction_query = \
    """INSERT INTO 
            customers_transactions(customer_id,amount,user_id)
        VALUES
            (?,?,?)
    """

get_next_customer_id_query = \
    """SELECT seq FROM sqlite_sequence WHERE `name` = 'customers'"""

get_customers_nets_query = \
    """SELECT 
            c.customer_id,
            c.customer_name,
            t.last_transaction_date,
            t.net
        FROM
            customers c
        JOIN
            (
                SELECT
                    customer_id,
                    MAX(transaction_date) AS last_transaction_date,
                    SUM(amount) AS net
                FROM
                    customers_transactions
                GROUP BY
                    customer_id
            ) t ON c.customer_id = t.customer_id
        WHERE
            t.net != 0
        ORDER BY
            c.customer_name
    """

get_customers_closed_query = \
    """SELECT 
            c.customer_id,
            c.customer_name
        FROM
            customers c
        JOIN
            (
                SELECT
                    customer_id,
                    SUM(amount) AS net
                FROM
                    customers_transactions
                GROUP BY
                    customer_id
            ) t ON c.customer_id = t.customer_id
        WHERE
            t.net == 0
        ORDER BY
            c.customer_name
    """

get_customers_nets_with_zeros_query = \
    """SELECT 
            c.customer_id,
            c.customer_name,
            t.last_transaction_date,
            t.net
        FROM
            customers c
        JOIN
            (
                SELECT
                    customer_id,
                    MAX(transaction_date) AS last_transaction_date,
                    SUM(amount) AS net
                FROM
                    customers_transactions
                GROUP BY
                    customer_id
            ) t ON c.customer_id = t.customer_id
        ORDER BY
            c.customer_name
    """

get_customer_total_query = \
    """SELECT 
            SUM(amount)
        FROM
            customers_transactions
    """

get_customer_ledger_query = \
    """SELECT 
        customers.customer_name,
        customers_transactions.transaction_date,
        users.username,
        customers_transactions.amount
    FROM
        customers_transactions
    LEFT JOIN
        customers
    ON
        customers_transactions.customer_id = customers.customer_id
    LEFT JOIN
        users
    ON
        users.user_id = customers_transactions.user_id
    WHERE
        customers.customer_id = ?
"""

delete_all_customer_transactions = \
    """DELETE FROM customers_transactions WHERE customer_id = ?"""

delete_customer = \
    """DELETE FROM customers WHERE customer_id = ?"""

get_all_customers_query = \
    """SELECT 
            *
        FROM
            customers
        ORDER BY
            customer_name
        ASC
    """

is_admin_query = \
    """SELECT 
            is_admin
        FROM
            users
        WHERE
            user_id = ?
        AND
            is_admin = 1
        LIMIT
            1
    """

add_regular_user_query = \
    """INSERT INTO users(username,user_password,is_activated) VALUES (?,?,1)"""

get_all_users_query = \
    """SELECT * FROM users WHERE is_admin != 1"""


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
