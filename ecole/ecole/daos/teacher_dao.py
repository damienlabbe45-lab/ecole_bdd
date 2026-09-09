# -*- coding: utf-8 -*-

"""
Classe Dao[Teacher]
"""

from dataclasses import dataclass
from typing import Optional
from daos.dao import Dao
from models.teacher import Teacher
from models.address import Address
from models.course import Course


@dataclass
class TeacherDao(Dao[Teacher]):
    def create(self, teacher: Teacher) -> int:
        """Crée en BD l'entité Teacher correspondant à teacher"""
        id_teacher: int = 0
        address_id = teacher.address.id if teacher.address is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                # 1. Insertion dans person
                cursor.execute(
                    "INSERT IGNORE INTO person (first_name, last_name, age, id_address) VALUES (%s, %s, %s, %s)",
                    (teacher.first_name, teacher.last_name, teacher.age, address_id)
                )
                id_person = cursor.lastrowid

                # 2. Insertion dans teacher
                cursor.execute(
                    "INSERT IGNORE INTO teacher (hiring_date, id_person) VALUES (%s, %s)",
                    (teacher.hiring_date, id_person)
                )
                id_teacher = cursor.lastrowid
                teacher.id = id_teacher
                Dao.connection.commit()
        except Exception as e:
            print(e)
            id_teacher = 0

        return id_teacher

    def read(self, id_teacher: int) -> None | str:
        """Renvoie le professeur correspondant à id_teacher (ou None)"""
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
                    where t.id_teacher = %s
                """
        with self.connection.cursor() as cursor:
            cursor.execute(query, (id_teacher,))
            record = cursor.fetchone()
            return record[0] if record is not None else None

    def add_course(self, teacher: Teacher, course: Course) -> bool:
        """Associe un cours à un enseignant dans la table course."""
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE course SET id_teacher = %s WHERE id_course = %s",
                    (teacher.id, course.id)
                )
                Dao.connection.commit()
                teacher.add_course(course)
            return True
        except Exception as e:
            print(e)
            return False

    def update(self, teacher: Teacher) -> bool:
        """Met à jour l'entité Teacher en BD"""
        address_id = teacher.address.id if teacher.address is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE person p
                    JOIN teacher t ON p.id_person = t.id_person
                    SET p.first_name = %s, p.last_name = %s, p.age = %s, p.id_address = %s
                    WHERE t.id_teacher = %s
                    """,
                    (teacher.first_name, teacher.last_name, teacher.age, address_id, teacher.id)
                )

                cursor.execute(
                    "UPDATE teacher SET hiring_date = %s WHERE id_teacher = %s",
                    (teacher.hiring_date, teacher.id)
                )
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self, teacher: Teacher) -> bool:
        """Supprime l'entité Teacher en BD"""
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.id_person 
                    FROM person p 
                    JOIN teacher t ON p.id_person = t.id_person 
                    WHERE t.id_teacher = %s
                    """,
                    (teacher.id,)
                )
                record = cursor.fetchone()

                if record:
                    cursor.execute("DELETE FROM teacher WHERE id_teacher = %s", (teacher.id,))
                    cursor.execute("DELETE FROM person WHERE id_person = %s", (record[0],))
                    Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def read_all(self) -> list[str]:
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
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
