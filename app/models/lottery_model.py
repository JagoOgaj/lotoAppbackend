from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db
from sqlalchemy import func

from app.tools.status_tools import Status


class Lottery(db.Model):
    """
    Représente une loterie.

    Cette classe correspond à la table 'lotteries' dans la base de données.
    Elle stocke les informations relatives à une loterie, y compris le nom,
    les dates de début et de fin, le statut, le prix de la récompense,
    et le nombre maximum de participants.

    Attributes:
        id (int): Identifiant unique de la loterie (clé primaire).
        _name (str): Nom de la loterie.
        _start_date (datetime): Date de début de la loterie.
        _end_date (datetime): Date de fin de la loterie.
        _status (str): Statut actuel de la loterie (ex. : "active", "terminated").
        _reward_price (int): Montant de la récompense pour cette loterie.
        _max_participants (int): Nombre maximum de participants autorisés.
        created_at (datetime): Date de création de la loterie.
        updated_at (datetime): Date de la dernière mise à jour de la loterie.
        entries (list): Liste des inscriptions associées à cette loterie.
        results (LotteryResult): Résultat associé à cette loterie.

    Properties:
        name (str): Getter et setter pour le nom de la loterie.
        start_date (datetime): Getter et setter pour la date de début.
        end_date (datetime): Getter et setter pour la date de fin.
        status (str): Getter et setter pour le statut de la loterie.
        reward_price (int): Getter et setter pour le prix de la récompense.
        max_participants (int): Getter et setter pour le nombre maximum de participants.
        participant_count (int): Compte le nombre de participants actuels.
        is_active (bool): Indique si la loterie est actuellement active.

    Methods:
        __repr__(): Retourne une représentation en chaîne de l'objet Lottery.

    Example:
        lottery = Lottery(name="Loterie de Noël", start_date=datetime(2024, 12, 1), end_date=datetime(2024, 12, 25), status="active", reward_price=1000, max_participants=100)
    """

    __tablename__ = "lotteries"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    _name = Column("name", String, nullable=False)
    _start_date = Column("start_date", DateTime, nullable=True)
    _end_date = Column("end_date", DateTime, nullable=True)
    _status = Column("status", String, nullable=False)
    _reward_price = Column("reward_price", Integer, nullable=False)
    _max_participants = Column("max_participants", Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    entries = relationship("Entry", back_populates="lottery")
    results = relationship("LotteryResult", back_populates="lottery", uselist=False)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def reward_price(self):
        return self._reward_price

    @reward_price.setter
    def reward_price(self, value):
        self._reward_price = value

    @property
    def max_participants(self):
        return self._max_participants

    @max_participants.setter
    def max_participants(self, value):
        self._max_participants = value

    @property
    def participant_count(self):
        return len(self.entries)

    @hybrid_property
    def is_active(self):
        if self._status == Status.SIMULATION.value:
            return False
        return self.start_date <= datetime.now() <= self.end_date

    @is_active.expression
    def is_active(cls):
        return func.now().between(cls._start_date, cls._end_date)
