#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application de gestion d'une école
"""

from business.school import School


def main() -> None:
    """Programme principal."""
    print("""\
--------------------------
Bienvenue dans notre école
--------------------------""")

    school = School()

    print("\n=== LISTE DES COURS ===")
    school.display_courses_list()

    print("\n=== LISTE DES ENSEIGNANTS ===")
    school.display_teachers_list()

    print("\n=== LISTE DES ÉTUDIANTS ===")
    school.display_students_list()

    print("\n=== LISTE DES ADRESSES ===")
    school.display_address_list()


if __name__ == '__main__':
    main()
