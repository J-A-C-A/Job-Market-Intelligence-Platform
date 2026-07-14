import enum

class ContractType(enum.Enum):
    B2B = "B2B"
    UOP = "UOP"

class OfferStatus(enum.Enum):
    ACTIVE = "Active"
    EXPIRED = "Expired"

class ExperienceLevel(enum.Enum):
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"

class WorkMode(enum.Enum):
    STATIONARY = "Stationary"
    REMOTE = "Remote"
    HYBRID = "Hybrid"

