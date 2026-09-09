# -*- coding: utf-8 -*-

"""
requêtes sql de Adress
"""
from pymysql import Connection


def address_create(connection: Connection, street: str, city: str, postal_code: str) -> int:
    """Crée en BD l'entité Address correspondant à l'adresse"""
    id_address: int
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT IGNORE INTO address (street, city, postal_code) VALUES (%s, %s, %s)",
                (street, city, postal_code)
            )
            id_address = cursor.lastrowid
            connection.commit()
    except Exception as e:
        print(e)
        id_address = 0

    return id_address


def address_read(connection: Connection, id_address: int) -> str | None:
    """Renvoie l'adresse correspondant à id_address (ou None)"""
    query = """
                SELECT CONCAT(street, ', ', postal_code, ' ', city)
                FROM address
                where id_address = %s;
            """
    with connection.cursor() as cursor:
        cursor.execute(query, (id_address,))
        record = cursor.fetchone()
    return record[0] if record is not None else None


def address_update(connection: Connection, street: str, city: str, postal_code: str, id_address: int) -> bool:
    """Met à jour l'entité Address en BD"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE address 
                SET street = %s, city = %s, postal_code = %s 
                WHERE id_address = %s
                """,
                (street, city, postal_code, id_address)
            )
            connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def address_delete(connection: Connection, id_address: int) -> bool:
    """Supprime l'entité Address en BD"""
    try:
        with connection.cursor() as cursor:
            # 1. Libérer la référence dans person pour éviter le conflit de clé étrangère
            cursor.execute(
                "UPDATE person SET id_address = NULL WHERE id_address = %s",
                (id_address,)
            )
            # 2. supprimer l'adresse
            cursor.execute(
                 "DELETE FROM address WHERE id_address = %s", (id_address,)
            )
            connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def address_read_all(connection: Connection) -> list[str]:
    """Récupère chaque adresse sous forme d'une chaîne texte unique formatée par la BD."""
    query = """
        SELECT CONCAT(street, ', ', postal_code, ' ', city)
        FROM address;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]
