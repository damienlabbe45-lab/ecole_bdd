#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application de gestion d'une école
"""

from business.school import School
from asyncio import run


async def main() -> None:
    """Programme principal."""
    print("""\
--------------------------
Bienvenue dans notre école
--------------------------""")

    school = School()

    print("\n=== LISTE DES COURS ===")
    await school.display_courses_list()

    print("\n=== LISTE DES ENSEIGNANTS ===")
    await school.display_teachers_list()

    print("\n=== LISTE DES ÉTUDIANTS ===")
    await school.display_students_list()

    print("\n=== LISTE DES ADRESSES ===")
    await school.display_address_list()


if __name__ == '__main__':
    run(main())
