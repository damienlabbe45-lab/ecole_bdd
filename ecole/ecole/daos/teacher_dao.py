# -*- coding: utf-8 -*-

"""
Requêtes SQL de Teacher
"""
from datetime import date
from typing import Callable

from utils.async_session_maker import CustomAsyncSession


async def teacher_create(
        connection: Callable[[], CustomAsyncSession],
        first_name: str,
        last_name: str,
        age: int,
        hiring_date: date,
        address_id: int | None,
) -> int:
    """Crée en BD l'entité Teacher et l'entité Person associée."""
    async with connection() as session:
        async with session.begin():
            # 1. Insertion dans person
            res = await session.execute("""INSERT IGNORE INTO person 
            (first_name, last_name, age, id_address) VALUES (:first_name, :last_name, :age, :address_id)""", {
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                "address_id": address_id,
            })
            id_person = res.lastrowid or 0

            # 2. Insertion dans teacher
            if id_person:
                res_teacher = await session.execute("""INSERT IGNORE INTO teacher (hiring_date, id_person) 
                        VALUES (:hiring_date, :id_person)""", {"hiring_date": hiring_date, "id_person": id_person})
                return res_teacher.lastrowid or 0
            return 0


async def teacher_read(
        connection: Callable[[], CustomAsyncSession], id_teacher: int
) -> str | None:
    """Renvoie le professeur correspondant à id_teacher (ou None si introuvable)."""
    async with connection() as session:
        return await session.scalar("""SELECT CONCAT(
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
        WHERE t.id_teacher = :id_teacher
        GROUP BY t.id_teacher;
    """, {"id_teacher": id_teacher})


async def teacher_add_course(
        connection: Callable[[], CustomAsyncSession], id_teacher: int, course_id: int
) -> bool:
    """Associe un cours à un enseignant dans la table course."""
    async with connection() as session:
        async with session.begin():
            res = await session.execute("""UPDATE course SET id_teacher = :id_teacher WHERE 
            id_course = :course_id""", {"id_teacher": id_teacher, "course_id": course_id})
            return res.rowcount > 0


async def teacher_update(
        connection: Callable[[], CustomAsyncSession],
        first_name: str,
        last_name: str,
        age: int,
        hiring_date: date,
        address_id: int | None,
        id_teacher: int,
) -> bool:
    """Met à jour les informations de l'enseignant et sa fiche personne associée."""
    async with connection() as session:
        async with session.begin():
            res = await session.execute("""UPDATE person p JOIN teacher t ON p.id_person = t.id_person
 SET p.first_name = :first_name, p.last_name = :last_name, p.age = :age, p.id_address = :address_id WHERE 
 t.id_teacher = :id_teacher""", {
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                "address_id": address_id,
                "id_teacher": id_teacher,
            })

            await session.execute("""UPDATE teacher SET hiring_date = :hiring_date WHERE 
            id_teacher = :id_teacher""", {"hiring_date": hiring_date, "id_teacher": id_teacher})
            return res.rowcount > 0


async def teacher_delete(
        connection: Callable[[], CustomAsyncSession], id_teacher: int
) -> bool:
    """Supprime l'enseignant, détache ses cours et supprime la fiche personne/adresse liée."""
    async with connection() as session:
        async with session.begin():
            record = (await session.execute("""
                    SELECT p.id_person, p.id_address 
                    FROM person p 
                    JOIN teacher t ON p.id_person = t.id_person 
                    WHERE t.id_teacher = :id_teacher
                """, {"id_teacher": id_teacher})).fetchone()

            if record:
                id_person, id_address = record[0], record[1]
                # 1. Retirer la référence de l'enseignant dans les cours affectés
                await session.execute("UPDATE course SET id_teacher = NULL WHERE id_teacher = :id_teacher",
                                      {"id_teacher": id_teacher})
                # 2. Supprimer la fiche enseignant, personne et adresse si présente
                await session.execute("DELETE FROM teacher WHERE id_teacher = :id_teacher",
                                      {"id_teacher": id_teacher})
                await session.execute("DELETE FROM person WHERE id_person = :id_person",
                                      {"id_person": id_person})
                if id_address:
                    await session.execute("DELETE FROM address WHERE id_address = :id_address",
                                          {"id_address": id_address},
                                          )
                return True
            return False


async def teacher_read_all(
        connection: Callable[[], CustomAsyncSession]
) -> list[str]:
    """Récupère chaque enseignant sous forme d'une chaîne texte unique formatée par la BD."""
    async with connection() as session:
        return await session.scalars("""
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
    """)
