import mysql.connector

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",       # Change if using a remote server
            user="your_username",   # Replace with your MySQL username
            password="your_password", # Replace with your MySQL password
            database="hospital_db"  # Replace with your database name
        )
        if conn.is_connected():
            print("Connected to MySQL Database!")
            return conn
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

# Test the connection
if __name__ == "__main__":
    connect_db()
