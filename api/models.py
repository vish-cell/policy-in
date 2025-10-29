import mysql.connector
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='root123',
        database='insurance_db'
    )

def create_metadata(name, type_, pii_tags, compliance_tags, created_by):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO metadata_assets (name, type, pii_tags, compliance_tags, created_by) VALUES (%s,%s,%s,%s,%s)",
            (name, type_, pii_tags, compliance_tags, created_by)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        raise e

def read_metadata():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM metadata_assets")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        raise e

def update_metadata(mid, name, type_, pii_tags, compliance_tags):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE metadata_assets SET name=%s, type=%s, pii_tags=%s, compliance_tags=%s WHERE id=%s",
            (name, type_, pii_tags, compliance_tags, mid)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        raise e

def delete_metadata(mid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metadata_assets WHERE id=%s", (mid,))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        raise e

def search_metadata(tag):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM metadata_assets 
            WHERE name LIKE %s OR pii_tags LIKE %s OR compliance_tags LIKE %s
        """
        cursor.execute(query, (f"%{tag}%", f"%{tag}%", f"%{tag}%"))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        raise e
