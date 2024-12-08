import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                phone VARCHAR(15) NOT NULL UNIQUE
            );
        """)
        conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s) RETURNING id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]

        if phones:
            phones = list(set(phones))
            for phone in phones:
                add_phone(conn, client_id, phone)  # Проверка на наличие будет выполнена внутри функции add_phone

    conn.commit()
    return client_id


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM phones WHERE phone = %s", (phone,))
        exists = cur.fetchone()[0] > 0
        if exists:
            print(f"Телефон {phone} уже существует для клиента {client_id}.")
            return
        cur.execute("""
            INSERT INTO phones (client_id, phone)
            VALUES (%s, %s);
        """, (client_id, phone))
    conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("UPDATE clients SET first_name = %s WHERE id = %s;", (first_name, client_id))
        if last_name:
            cur.execute("UPDATE clients SET last_name = %s WHERE id = %s;", (last_name, client_id))
        if email:
            cur.execute("UPDATE clients SET email = %s WHERE id = %s;", (email, client_id))
        conn.commit()


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM clients WHERE id = %s;", (client_id,))
        conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    query = "SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c LEFT JOIN phones p ON c.id = p.client_id WHERE "
    conditions = []
    params = []

    if first_name:
        conditions.append("c.first_name = %s")
        params.append(first_name)
    if last_name:
        conditions.append("c.last_name = %s")
        params.append(last_name)
    if email:
        conditions.append("c.email = %s")
        params.append(email)
    if phone:
        conditions.append("p.phone = %s")
        params.append(phone)

    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


with psycopg2.connect(database="clients", user="postgres", password="725090") as conn:
    create_db(conn)

    client_id = add_client(conn, "Иван", "Иванов", "ivanov@example.com", phones=["123456789", "987654378"])
    print(f"Добавлен клиент с ID: {client_id}")

    change_client(conn, client_id, email="ivanov_new@example.com")

    clients = find_client(conn, first_name="Иван")
    print("Найденные клиенты:", clients)

    delete_phone(conn, client_id, "123456789")

    delete_client(conn, client_id)

conn.close()



