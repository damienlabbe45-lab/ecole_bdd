# -*- coding: utf-8 -*-

"""
Classe Dao[Address]
"""

from dataclasses import dataclass
from typing import Optional
from daos.dao import Dao
from models.address import Address


@dataclass
class AddressDao(Dao[Address]):
    def create(self, address: Address) -> int:
        """Crée en BD l'entité Address correspondant à l'adresse"""
        id_address: int = 0
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT IGNORE INTO address (street, city, postal_code) VALUES (%s, %s, %s)",
                    (address.street, address.city, address.postal_code)
                )
                id_address = cursor.lastrowid
                address.id = id_address
                Dao.connection.commit()
        except Exception as e:
            print(e)
            id_address = 0

        return id_address

    def read(self, id_address: int) -> str | None:
        """Renvoie l'adresse correspondant à id_address (ou None)"""
        query = """
                    SELECT CONCAT(street, ', ', postal_code, ' ', city)
                    FROM address;
                """
        with self.connection.cursor() as cursor:
            cursor.execute(query, id_address)
            record = cursor.fetchone()
            return record[0] if record is not None else None

    def update(self, address: Address) -> bool:
        """Met à jour l'entité Address en BD"""
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE address 
                    SET street = %s, city = %s, postal_code = %s 
                    WHERE id_address = %s
                    """,
                    (address.street, address.city, address.postal_code, address.id)
                )
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self, address: Address) -> bool:
        """Supprime l'entité Address en BD"""
        try:
            with Dao.connection.cursor() as cursor:
                # 1. Libérer la référence dans person pour éviter le conflit de clé étrangère
                cursor.execute(
                    "UPDATE person SET id_address = NULL WHERE id_address = %s",
                    (address.id,)
                )
                # 2. Supprimer l'adresse
                cursor.execute(
                    "DELETE FROM address WHERE id_address = %s",
                    (address.id,)
                )
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def read_all(self) -> list[str]:
        """Récupère chaque adresse sous forme d'une chaîne texte unique formatée par la BD."""
        query = """
            SELECT CONCAT(street, ', ', postal_code, ' ', city)
            FROM address;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]