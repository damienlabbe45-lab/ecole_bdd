# -*- coding: utf-8 -*-

"""
Classe School
"""

from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from utils.async_session_maker import CustomAsyncSession


class School:
    """Couche métier de l'application de gestion d'une école."""

    connection: sessionmaker[CustomAsyncSession] = sessionmaker(
        bind=create_async_engine("mysql+asyncmy://root:@localhost/ecole", echo=False),  # nosonar
        class_=CustomAsyncSession,
        expire_on_commit=False,
    )

    # --- COURS ---

    async def add_course(
        self,
        name: str,
        start_date: date,
        end_date: date,
        teacher_id: int | None = None,
    ) -> int:
        """Ajoute un cours en BD."""
        from daos.course_dao import course_create

        return await course_create(
            self.connection, name, start_date, end_date, teacher_id
        )

    async def get_course_by_id(self, id_course: int) -> str | None:
        """Récupère un cours et ses détails par son identifiant."""
        from daos.course_dao import course_read

        return await course_read(self.connection, id_course)

    async def update_course(
        self,
        name: str,
        start_date: date,
        end_date: date,
        teacher_id: int | None,
        course_id: int,
    ) -> bool:
        """Met à jour un cours."""
        from daos.course_dao import course_update

        return await course_update(
            self.connection, name, start_date, end_date, teacher_id, course_id
        )

    async def delete_course(self, course_id: int) -> bool:
        """Supprime un cours."""
        from daos.course_dao import course_delete

        return await course_delete(self.connection, course_id)

    async def display_courses_list(self) -> None:
        """Affiche la liste de tous les cours."""
        from daos.course_dao import course_read_all

        courses = await course_read_all(self.connection)
        for course in courses:
            print(course)