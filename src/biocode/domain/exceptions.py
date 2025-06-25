"""Domain-specific exceptions"""

class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class CellException(DomainException):
    """Cell-related exceptions"""
    pass

class TissueException(DomainException):
    """Tissue-related exceptions"""
    pass

class OrganException(DomainException):
    """Organ-related exceptions"""
    pass

class SystemException(DomainException):
    """System-related exceptions"""
    pass
