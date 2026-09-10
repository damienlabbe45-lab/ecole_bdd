# -*- coding: utf-8 -*-

"""
Requêtes SQL de Address
"""
from typing import Callable

from utils.async_session_maker import CustomAsyncSession


async def address_create(
    connection: Callable[[], CustomAsyncSession],
    street: str,
    city: str,
    postal_code: str,
) -> int:
    """Crée en BD l'entité Address correspondant à l'adresse."""

    async with connection() as session:
        async with session.begin():
            res = await session.execute("""INSERT IGNORE INTO address (street, city, postal_code) VALUES 
            (:street, :city, :postal_code)""", {"street": street, "city": city, "postal_code": postal_code})
            return res.lastrowid or 0


async def address_read(
    connection: Callable[[], CustomAsyncSession], id_address: int
) -> str | None:
    """Renvoie l'adresse correspondant à id_address (ou None)."""

    async with connection() as session:
        return await session.scalar("""SELECT CONCAT(street, ', ', postal_code, ' ', city) FROM address 
        WHERE id_address = :id_address""", {"id_address": id_address})


async def address_update(
    connection: Callable[[], CustomAsyncSession],
    street: str,
    city: str,
    postal_code: str,
    id_address: int,
) -> bool:
    """Met à jour l'entité Address en BD."""

    async with connection() as session:
        async with session.begin():
            res = await session.execute("""UPDATE address SET street = :street, city = :city, 
            postal_code = :postal_code WHERE id_address = :id_address""",
                                        {
                                            "street": street, "city": city, "postal_code": postal_code,
                                            "id_address": id_address})
            return res.rowcount > 0


async def address_delete(
    connection: Callable[[], CustomAsyncSession], id_address: int
) -> bool:
    """Supprime l'entité Address en BD."""
    async with connection() as session:
        async with session.begin():
            # 1. Libérer la référence dans person
            await session.execute("""UPDATE person SET id_address = NULL 
            WHERE id_address = :id_address""", {"id_address": id_address})
            # 2. Supprimer l'adresse
            res = await session.execute("""DELETE FROM address WHERE id_address = :id_address""",
                                        {"id_address": id_address})
            return res.rowcount > 0


async def address_read_all(
    connection: Callable[[], CustomAsyncSession]
) -> list[str]:
    """Récupère chaque adresse sous forme d'une chaîne texte unique formatée par la BD."""
    async with connection() as session:
        return await session.scalars("SELECT CONCAT(street, ', ', postal_code, ' ', city) FROM address")
