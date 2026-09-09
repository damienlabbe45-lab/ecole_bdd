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

    # --- ADRESSES ---

    async def add_address(
        self,
        street: str,
        city: str,
        postal_code: str,
    ) -> int:
        """Ajoute une adresse en BD."""
        from daos.address_dao import address_create

        return await address_create(self.connection, street, city, postal_code)

    async def get_address_by_id(self, id_address: int) -> str | None:
        """Récupère une adresse par son identifiant."""
        from daos.address_dao import address_read

        return await address_read(self.connection, id_address)

    async def update_address(
        self,
        street: str,
        city: str,
        postal_code: str,
        id_address: int,
    ) -> bool:
        """Met à jour une adresse."""
        from daos.address_dao import address_update

        return await address_update(
            self.connection, street, city, postal_code, id_address
        )

    async def delete_address(self, id_address: int) -> bool:
        """Supprime une adresse."""
        from daos.address_dao import address_delete

        return await address_delete(self.connection, id_address)

    async def display_address_list(self) -> None:
        """Affiche la liste de toutes les adresses."""
        from daos.address_dao import address_read_all

        for address in await address_read_all(self.connection):
            print(address)

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

        for course in await course_read_all(self.connection):
            print(course)

    # --- ÉTUDIANTS ---

    async def add_student(
        self,
        first_name: str,
        last_name: str,
        age: int,
        address_id: int | None = None,
    ) -> int:
        """Ajoute un étudiant en BD."""
        from daos.student_dao import student_create

        return await student_create(
            self.connection, first_name, last_name, age, address_id
        )

    async def get_student_by_id(self, student_nbr: int) -> str | None:
        """Récupère un étudiant par son numéro d'étudiant."""
        from daos.student_dao import student_read

        return await student_read(self.connection, student_nbr)

    async def update_student(
        self,
        first_name: str,
        last_name: str,
        age: int,
        address_id: int | None,
        student_nbr: int,
        course_id: int | None = None,
    ) -> bool:
        """Met à jour un étudiant."""
        from daos.student_dao import student_update

        return await student_update(
            self.connection,
            first_name,
            last_name,
            age,
            address_id,
            student_nbr,
            course_id,
        )

    async def add_student_to_course(
        self, student_nbr: int, course_id: int
    ) -> bool:
        """Inscrit un étudiant à un cours."""
        from daos.student_dao import create_student_takes

        return await create_student_takes(
            self.connection, student_nbr, course_id
        )

    async def delete_student(self, student_nbr: int) -> bool:
        """Supprime un étudiant."""
        from daos.student_dao import student_delete

        return await student_delete(self.connection, student_nbr)

    async def display_students_list(self) -> None:
        """Affiche la liste de tous les étudiants."""
        from daos.student_dao import student_read_all

        for student in await student_read_all(self.connection):
            print(student)

    # --- ENSEIGNANTS ---

    async def add_teacher(
        self,
        first_name: str,
        last_name: str,
        age: int,
        hiring_date: date,
        address_id: int | None = None,
    ) -> int:
        """Ajoute un enseignant en BD."""
        from daos.teacher_dao import teacher_create

        return await teacher_create(
            self.connection, first_name, last_name, age, hiring_date, address_id
        )

    async def get_teacher_by_id(self, id_teacher: int) -> str | None:
        """Récupère un enseignant par son identifiant."""
        from daos.teacher_dao import teacher_read

        return await teacher_read(self.connection, id_teacher)

    async def assign_teacher_to_course(
        self, id_teacher: int, course_id: int
    ) -> bool:
        """Affecte un enseignant à un cours."""
        from daos.teacher_dao import teacher_add_course

        return await teacher_add_course(self.connection, id_teacher, course_id)

    async def update_teacher(
        self,
        first_name: str,
        last_name: str,
        age: int,
        hiring_date: date,
        address_id: int | None,
        id_teacher: int,
    ) -> bool:
        """Met à jour un enseignant."""
        from daos.teacher_dao import teacher_update

        return await teacher_update(
            self.connection,
            first_name,
            last_name,
            age,
            hiring_date,
            address_id,
            id_teacher,
        )

    async def delete_teacher(self, id_teacher: int) -> bool:
        """Supprime un enseignant."""
        from daos.teacher_dao import teacher_delete

        return await teacher_delete(self.connection, id_teacher)

    async def display_teachers_list(self) -> None:
        """Affiche la liste de tous les enseignants."""
        from daos.teacher_dao import teacher_read_all

        for teacher in await teacher_read_all(self.connection):
            print(teacher)