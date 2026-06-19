"""Script to create the database and user for the restaurant menu app."""
import psycopg2
import sys

def main():
    # Connect as postgres superuser - adjust password as needed
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='',
            dbname='postgres'
        )
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. The postgres user password is correct (currently empty)")
        print("3. PostgreSQL is listening on localhost:5432")
        sys.exit(1)
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create database
    try:
        cursor.execute('CREATE DATABASE restaurant_menu')
        print("Database 'restaurant_menu' created successfully!")
    except psycopg2.Error as e:
        print(f"Database 'restaurant_menu' already exists or error: {e}")
    
    # Create user
    try:
        cursor.execute("CREATE USER menu WITH PASSWORD 'menu_secret'")
        print("User 'menu' created successfully!")
    except psycopg2.Error as e:
        print(f"User 'menu' already exists or error: {e}")
    
    # Grant privileges
    try:
        cursor.execute('GRANT ALL PRIVILEGES ON DATABASE restaurant_menu TO menu')
        print("Privileges granted to 'menu' user")
    except psycopg2.Error as e:
        print(f"Error granting privileges: {e}")
    
    # Grant schema privileges
    try:
        cursor.execute('GRANT ALL ON SCHEMA public TO menu')
        print("Schema privileges granted to 'menu' user")
    except psycopg2.Error as e:
        print(f"Error granting schema privileges: {e}")
    
    conn.close()
    print("\nDatabase setup complete!")

if __name__ == '__main__':
    main()
