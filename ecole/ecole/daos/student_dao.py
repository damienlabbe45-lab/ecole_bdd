# -*- coding: utf-8 -*-

"""
requêtes sql de student
"""
from pymysql import Connection


def create_student(connection: Connection, first_name: str, last_name: str, age: int, address_id: int | None) -> int:
    id_student: int = 0
    try:
        with connection.cursor() as cursor:
            # 1. Insertion dans person
            cursor.execute(
                "INSERT IGNORE INTO person (first_name, last_name, age, id_address) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, age, address_id)
                )
            id_person = cursor.lastrowid

            # 2. Insertion dans student
            # à modifier pour créer l'autoincrement en base de donnée directement
            cursor.execute(
                "INSERT IGNORE INTO student (student_nbr, id_person) VALUES (%s, %s)",
                (id_person, id_person)
                )
            id_student = id_person
            connection.commit()
    except Exception as e:
        print(e)
        id_student = 0

    return id_student


def student_read(connection: Connection, student_nbr: int) -> str | None:
    query = """
        SELECT CONCAT(
            p.first_name, ' ', p.last_name, ' (', p.age, ' ans)',
                IF(a.id_address IS NOT NULL, CONCAT(', ', a.street, ', ', a.postal_code, ' ', a.city), ''),
            ', n° étudiant : ', s.student_nbr, ',',
            IF(
                COUNT(c.id_course) > 0,
                CONCAT('\nCours suivis :\n  - ', GROUP_CONCAT(c.name SEPARATOR '\n  - ')),
                ''
            )
        )
        FROM student s
        JOIN person p ON s.id_person = p.id_person
        LEFT JOIN address a ON p.id_address = a.id_address
        LEFT JOIN takes t ON s.student_nbr = t.student_nbr
        LEFT JOIN course c ON t.id_course = c.id_course
        WHERE s.student_nbr = %s
        GROUP BY s.student_nbr;
            """
    with connection.cursor() as cursor:
        cursor.execute(query, (student_nbr,))
        record = cursor.fetchone()
    return record[0] if record is not None else None


def student_update(
        connection: Connection, first_name: str, last_name: str, age: int, address_id: int | None, student_nbr: int,
        course_id: int | None) -> bool:
    """Met à jour en BD l'entité Student correspondant à student"""
    try:
        with connection.cursor() as cursor:
            # 1. Mise à jour des informations personnelles
            cursor.execute(
                """
                UPDATE person p
                JOIN student s ON p.id_person = s.id_person
                SET p.first_name = %s, p.last_name = %s, p.age = %s, p.id_address = %s
                WHERE s.student_nbr = %s
                """,
                (first_name, last_name, age, address_id, student_nbr)
            )
            if course_id is not None:
                cursor.execute("""""DELETE FROM takes where student_nbr = %s and id_course = %s""",
                               (student_nbr, course_id))
            connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def create_student_takes(connection: Connection, student_nbr: int, course_id: int) -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT IGNORE INTO takes (student_nbr, id_course) VALUES (%s, %s)""",
                           (student_nbr, course_id))
            connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def student_delete(connection: Connection, student_nbr: int) -> bool:
    """Supprime en BD l'entité Student correspondant à student"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.id_person, p.id_address 
                FROM person p 
                JOIN student s ON p.id_person = s.id_person 
                WHERE s.student_nbr = %s
                """,
                (student_nbr,)
            )
            record = cursor.fetchone()

            if record:
                cursor.execute("DELETE FROM takes WHERE student_nbr=%s", (student_nbr,))
                cursor.execute("DELETE FROM student WHERE student_nbr=%s", (student_nbr,))
                cursor.execute("DELETE FROM person WHERE id_person=%s", (record[0],))
                if record[1]:
                    cursor.execute("DELETE FROM address WHERE id_address=%s", (record[1],))
                connection.commit()
                return True
            return False
    except Exception as e:
        print(e)
        return False


def student_read_all(connection: Connection) -> list[str]:
    """Récupère chaque étudiant sous forme d'une chaîne texte unique formatée par la BD."""
    query = """
        SELECT CONCAT(
            p.first_name, ' ', p.last_name, ' (', p.age, ' ans)',
            IF(a.id_address IS NOT NULL, CONCAT(', ', a.street, ', ', a.postal_code, ' ', a.city), ''),
            ', n° étudiant : ', s.student_nbr, ',',
            IF(
                COUNT(c.id_course) > 0,
                CONCAT('\nCours suivis :\n  - ', GROUP_CONCAT(c.name SEPARATOR '\n  - ')),
                ''
            )
        )
        FROM student s
        JOIN person p ON s.id_person = p.id_person
        LEFT JOIN address a ON p.id_address = a.id_address
        LEFT JOIN takes t ON s.student_nbr = t.student_nbr
        LEFT JOIN course c ON t.id_course = c.id_course
        GROUP BY s.student_nbr;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]
