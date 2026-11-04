"""
Model of the possible entity types for
user content in reMarkable user data
"""


from enum import StrEnum

class EntityType(StrEnum):
    """
    The possible entity types for reMarkable user data
    """
    COLLECTION_TYPE = 'CollectionType'
    DOCUMENT_TYPE = "DocumentType"
