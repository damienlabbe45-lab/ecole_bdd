# -*- coding: utf-8 -*-

"""
Requêtes SQL de Course
"""
from datetime import date
from typing import Callable

from utils.async_session_maker import CustomAsyncSession


async def course_create(
    connection: Callable[[], CustomAsyncSession],
    name: str,
    start_date: date,
    end_date: date,
    teacher_id: int | None = None,
) -> int:
    """Crée en BD l'entité Course."""
    query = """
        INSERT INTO course (name, start_date, end_date, id_teacher)
        VALUES (:name, :start_date, :end_date, :teacher_id)
    """
    async with connection() as session:
        async with session.begin():
            res = await session.execute(
                query,
                {
                    "name": name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "teacher_id": teacher_id,
                },
            )
            return res.lastrowid or 0


async def course_read(
    connection: Callable[[], CustomAsyncSession], id_course: int
) -> str | None:
    """Renvoie le cours correspondant à id_course (ou None)."""
    query = """
        SELECT CONCAT(
            c.name, ' (', c.start_date, ' – ', c.end_date, '), enseigné par ',
            COALESCE(CONCAT(p_t.first_name, ' ', p_t.last_name), "pas d'enseignant affecté"),
            IF(COUNT(p_s.id_person) > 0, CONCAT('\nÉlèves :\n  - ', GROUP_CONCAT(CONCAT(p_s.first_name, ' ',
            p_s.last_name) SEPARATOR '\n  - ')),  "\n  pas d'étudiant"
            )
        )
        FROM course c
        LEFT JOIN teacher t ON c.id_teacher = t.id_teacher
        LEFT JOIN person p_t ON t.id_person = p_t.id_person
        LEFT JOIN takes tk ON c.id_course = tk.id_course
        LEFT JOIN student s ON tk.student_nbr = s.student_nbr
        LEFT JOIN person p_s ON s.id_person = p_s.id_person
        WHERE c.id_course = :id_course
        GROUP BY c.id_course;
    """
    async with connection() as session:
        return await session.scalar(query, {"id_course": id_course})


async def course_update(
    connection: Callable[[], CustomAsyncSession],
    name: str,
    start_date: date,
    end_date: date,
    id_teacher: int | None,
    course_id: int,
) -> bool:
    """Met à jour en BD l'entité Course."""
    query = """
        UPDATE course
        SET name = :name, start_date = :start_date, end_date = :end_date, id_teacher = :id_teacher
        WHERE id_course = :course_id
    """
    async with connection() as session:
        async with session.begin():
            res = await session.execute(
                query,
                {
                    "name": name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "id_teacher": id_teacher,
                    "course_id": course_id,
                },
            )
            return res.rowcount > 0


async def course_delete(
    connection: Callable[[], CustomAsyncSession], course_id: int
) -> bool:
    """Supprime en BD l'entité Course et ses associations."""
    async with connection() as session:
        async with session.begin():
            await session.execute(
                "DELETE FROM takes WHERE id_course = :course_id",
                {"course_id": course_id},
            )
            res = await session.execute(
                "DELETE FROM course WHERE id_course = :course_id",
                {"course_id": course_id},
            )
            return res.rowcount > 0


async def course_read_all(
    connection: Callable[[], CustomAsyncSession]
) -> list[str]:
    """Récupère chaque cours sous forme d'une chaîne texte unique."""
    query = """
        SELECT CONCAT(
            c.name, ' (', c.start_date, ' – ', c.end_date, '), enseigné par ',
            COALESCE(CONCAT(p_t.first_name, ' ', p_t.last_name), "pas d'enseignant affecté"),
            IF(COUNT(p_s.id_person) > 0, CONCAT('\nÉlèves :\n  - ', GROUP_CONCAT(CONCAT(p_s.first_name, ' ',
                p_s.last_name) SEPARATOR '\n  - ')),  "\n  pas d'étudiant"
            )
        )
        FROM course c
        LEFT JOIN teacher t ON c.id_teacher = t.id_teacher
        LEFT JOIN person p_t ON t.id_person = p_t.id_person
        LEFT JOIN takes tk ON c.id_course = tk.id_course
        LEFT JOIN student s ON tk.student_nbr = s.student_nbr
        LEFT JOIN person p_s ON s.id_person = p_s.id_person
        GROUP BY c.id_course;
    """
    async with connection() as session:
        return await session.scalars(query)
