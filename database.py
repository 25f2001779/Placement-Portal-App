import sqlite3
def get_db():
    conn = sqlite3.connect("placement.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Admin table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    # Student table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        contact TEXT,
        resume TEXT,
        status TEXT NOT NULL DEFAULT 'active'
    )
    """)

    # Company table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        website TEXT,
        hr_contact TEXT,
        status TEXT NOT NULL DEFAULT 'pending'
    )
    """)

    # Placement Drives
    cur.execute("""
        CREATE TABLE IF NOT EXISTS drives(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        job_title TEXT,
        skills TEXT,
        experience TEXT,
        salary TEXT,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )
    """)

    # Applications
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        drive_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Applied',
        UNIQUE(student_id, drive_id),
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(drive_id) REFERENCES drives(id) ON DELETE CASCADE
    )
    """)

    # Create default admin
    cur.execute("SELECT * FROM admin")
    admin = cur.fetchone()

    if not admin:
        cur.execute(
            "INSERT INTO admin (username,password) VALUES (?,?)",
            ("admin", "admin123")
        )

    conn.commit()
    conn.close()