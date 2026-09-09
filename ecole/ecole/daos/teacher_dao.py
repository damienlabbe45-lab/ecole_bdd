# -*- coding: utf-8 -*-

"""
requêtes sql de teacher
"""
from datetime import date
from pymysql import Connection


def teacher_create(connection: Connection, first_name: str, last_name: str, age: int, hiring_date: date,
                   address_id: int | None) -> int:
    """Crée en BD l'entité Teacher et l'entité Person associée."""
    id_teacher: int = 0
    try:
        with connection.cursor() as cursor:
            # 1. Insertion dans person
            cursor.execute(
                "INSERT IGNORE INTO person (first_name, last_name, age, id_address) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, age, address_id)
            )
            id_person = cursor.lastrowid

            # 2. Insertion dans teacher
            cursor.execute(
                "INSERT IGNORE INTO teacher (hiring_date, id_person) VALUES (%s, %s)",
                (hiring_date, id_person)
            )
            id_teacher = cursor.lastrowid
            connection.commit()
    except Exception as e:
        print(e)
        id_teacher = 0

    return id_teacher


def teacher_read(connection: Connection, id_teacher: int) -> str | None:
    """Renvoie le professeur correspondant à id_teacher (ou None si introuvable)."""
    query = """
        SELECT CONCAT(
            p.first_name, ' ', p.last_name, ' (', p.age, ' ans)',
            IF(a.id_address IS NOT NULL, CONCAT(', ', a.street, ', ', a.postal_code, ' ', a.city), ''),
            ', arrivé(e) le ', t.hiring_date,
            IF(
                COUNT(c.id_course) > 0,
                CONCAT('\nCours enseignés :\n  - ', GROUP_CONCAT(c.name SEPARATOR '\n  - ')),
                ''
            )
        )
        FROM teacher t
        JOIN person p ON t.id_person = p.id_person
        LEFT JOIN address a ON p.id_address = a.id_address
        LEFT JOIN course c ON t.id_teacher = c.id_teacher
        WHERE t.id_teacher = %s
        GROUP BY t.id_teacher;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (id_teacher,))
        record = cursor.fetchone()
    return record[0] if record is not None else None


def teacher_add_course(connection: Connection, id_teacher: int, course_id: int) -> bool:
    """Associe un cours à un enseignant dans la table course."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE course SET id_teacher = %s WHERE id_course = %s",
                (id_teacher, course_id)
            )
            connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def teacher_update(connection: Connection, first_name: str, last_name: str, age: int, hiring_date: date,
                   address_id: int | None, id_teacher: int) -> bool:
    """Met à jour les informations de l'enseignant et sa fiche personne associée."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE person p
                JOIN teacher t ON p.id_person = t.id_person
                SET p.first_name = %s, p.last_name = %s, p.age = %s, p.id_address = %s
                WHERE t.id_teacher = %s
                """,
                (first_name, last_name, age, address_id, id_teacher)
            )

            cursor.execute(
                "UPDATE teacher SET hiring_date = %s WHERE id_teacher = %s",
                (hiring_date, id_teacher)
            )
            connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def teacher_delete(connection: Connection, id_teacher: int) -> bool:
    """Supprime l'enseignant, détache ses cours et supprime la fiche personne/adresse liée."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.id_person, p.id_address 
                FROM person p 
                JOIN teacher t ON p.id_person = t.id_person 
                WHERE t.id_teacher = %s
                """,
                (id_teacher,)
            )
            record = cursor.fetchone()

            if record:
                # 1. Retirer la référence de l'enseignant dans les cours affectés
                cursor.execute("UPDATE course SET id_teacher = NULL WHERE id_teacher = %s", (id_teacher,))
                # 2. Supprimer la fiche enseignant, personne et adresse si présente
                cursor.execute("DELETE FROM teacher WHERE id_teacher = %s", (id_teacher,))
                cursor.execute("DELETE FROM person WHERE id_person = %s", (record[0],))
                if record[1]:
                    cursor.execute("DELETE FROM address WHERE id_address = %s", (record[1],))
                connection.commit()
                return True
            return False
    except Exception as e:
        print(e)
        return False


def teacher_read_all(connection: Connection) -> list[str]:
    """Récupère chaque enseignant sous forme d'une chaîne texte unique formatée par la BD."""
    query = """
        SELECT CONCAT(
            p.first_name, ' ', p.last_name, ' (', p.age, ' ans)',
            IF(a.id_address IS NOT NULL, CONCAT(', ', a.street, ', ', a.postal_code, ' ', a.city), ''),
            ', arrivé(e) le ', t.hiring_date,
            IF(
                COUNT(c.id_course) > 0,
                CONCAT('\nCours enseignés :\n  - ', GROUP_CONCAT(c.name SEPARATOR '\n  - ')),
                ''
            )
        )
        FROM teacher t
        JOIN person p ON t.id_person = p.id_person
        LEFT JOIN address a ON p.id_address = a.id_address
        LEFT JOIN course c ON t.id_teacher = c.id_teacher
        GROUP BY t.id_teacher;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]
