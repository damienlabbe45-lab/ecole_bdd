# -*- coding: utf-8 -*-

"""
Requêtes SQL de Student
"""
from typing import Callable

from utils.async_session_maker import CustomAsyncSession


async def student_create(
        connection: Callable[[], CustomAsyncSession],
        first_name: str,
        last_name: str,
        age: int,
        address_id: int | None,
) -> int:
    """Crée en BD l'entité Student et la Person associée."""
    async with connection() as session:
        async with session.begin():
            # 1. Insertion dans person
            res = await session.execute("""INSERT IGNORE INTO person (first_name, last_name, age, id_address) 
            VALUES (:first_name, :last_name, :age, :address_id)""", {
                                            "first_name": first_name, "last_name": last_name, "age": age,
                                            "address_id": address_id})
            id_person = res.lastrowid or 0

            # 2. Insertion dans student
            if id_person:
                await session.execute("""INSERT IGNORE INTO student (student_nbr, id_person) 
                VALUES (:student_nbr, :id_person)""", {"student_nbr": id_person, "id_person": id_person})
            return id_person


async def student_read(
        connection: Callable[[], CustomAsyncSession], student_nbr: int
) -> str | None:
    """Renvoie l'étudiant correspondant à student_nbr (ou None)."""
    async with connection() as session:
        return await session.scalar("""
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
        WHERE s.student_nbr = :student_nbr
        GROUP BY s.student_nbr;
    """, {"student_nbr": student_nbr})


async def student_update(
        connection: Callable[[], CustomAsyncSession],
        first_name: str,
        last_name: str,
        age: int,
        address_id: int | None,
        student_nbr: int,
        course_id: int | None,
) -> bool:
    """Met à jour en BD l'entité Student correspondant à student."""
    async with connection() as session:
        async with session.begin():
            res = await session.execute(
                """
                    UPDATE person p
                    JOIN student s ON p.id_person = s.id_person
                    SET p.first_name = :first_name, p.last_name = :last_name, p.age = :age, p.id_address = :address_id
                    WHERE s.student_nbr = :student_nbr
                """, {
                    "first_name": first_name, "last_name": last_name, "age": age, "address_id": address_id,
                    "student_nbr": student_nbr}
            )
            if course_id is not None:
                await session.execute(
                    "DELETE FROM takes WHERE student_nbr = :student_nbr AND id_course = :course_id",
                    {"student_nbr": student_nbr, "course_id": course_id})
            return res.rowcount > 0


async def create_student_takes(
        connection: Callable[[], CustomAsyncSession],
        student_nbr: int,
        course_id: int,
) -> bool:
    """Associe un étudiant à un cours dans la table takes."""
    async with connection() as session:
        async with session.begin():
            res = await session.execute(
                "INSERT IGNORE INTO takes (student_nbr, id_course) VALUES (:student_nbr, :course_id)",
                {"student_nbr": student_nbr, "course_id": course_id})
            return res.rowcount > 0


async def student_delete(
        connection: Callable[[], CustomAsyncSession], student_nbr: int
) -> bool:
    """Supprime en BD l'entité Student correspondant à student."""
    async with connection() as session:
        async with session.begin():
            res = await session.execute(
                """
                    SELECT p.id_person, p.id_address 
                    FROM person p 
                    JOIN student s ON p.id_person = s.id_person 
                    WHERE s.student_nbr = :student_nbr
                """,
                {"student_nbr": student_nbr},
            )
            record = res.fetchone()

            if record:
                id_person, id_address = record[0], record[1]
                await session.execute(
                    "DELETE FROM takes WHERE student_nbr = :student_nbr",
                    {"student_nbr": student_nbr},
                )
                await session.execute(
                    "DELETE FROM student WHERE student_nbr = :student_nbr",
                    {"student_nbr": student_nbr},
                )
                await session.execute(
                    "DELETE FROM person WHERE id_person = :id_person",
                    {"id_person": id_person},
                )
                if id_address:
                    await session.execute(
                        "DELETE FROM address WHERE id_address = :id_address",
                        {"id_address": id_address},
                    )
                return True
            return False


async def student_read_all(
        connection: Callable[[], CustomAsyncSession]
) -> list[str]:
    """Récupère chaque étudiant sous forme d'une chaîne texte unique formatée par la BD."""
    async with connection() as session:
        return await session.scalars("""
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
    """)
