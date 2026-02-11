#!/usr/bin/env python
"""
Script pour vérifier et corriger l'encodage de la base de données MySQL
"""

import mysql.connector
from mysql.connector import Error

def check_and_fix_encoding():
    try:
        # Connexion à MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='aguipexdb'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Vérifier l'encodage actuel de la base de données
            cursor.execute("SHOW CREATE DATABASE aguipexdb")
            db_info = cursor.fetchone()
            print("Encodage actuel de la base de données:")
            print(db_info[1])
            print()
            
            # Vérifier l'encodage des tables
            cursor.execute("SHOW TABLE STATUS")
            tables = cursor.fetchall()
            
            print("Encodage des tables:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                table_info = cursor.fetchone()
                print(f"{table_name}: {table_info[1]}")
            print()
            
            # Vérifier l'encodage des colonnes de la table actualite
            cursor.execute("SHOW FULL COLUMNS FROM core_actualite")
            columns = cursor.fetchall()
            
            print("Encodage des colonnes de core_actualite:")
            for column in columns:
                col_name = column[0]
                col_type = column[1]
                col_collation = column[2]
                print(f"{col_name}: {col_type} - {col_collation}")
            print()
            
            # Vérifier les variables de session
            cursor.execute("SHOW VARIABLES LIKE 'character_set%'")
            charset_vars = cursor.fetchall()
            
            print("Variables de jeu de caractères:")
            for var in charset_vars:
                print(f"{var[0]}: {var[1]}")
            print()
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_and_fix_encoding()
