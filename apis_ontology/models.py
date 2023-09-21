from collections.abc import Iterable
from collections import defaultdict
from dataclasses import dataclass
from typing import Union, Iterator

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property, Triple
from apis_core.utils import caching

from apis_ontology.helper_functions import remove_extra_spaces
from apis_ontology.middleware.get_request import current_request

# Entity categories


GENERIC = "Allgemein"
# CONCEPTUAL_OBJECTS = "Conceptual Objects"
# PHYSICAL_OBJECTS = "Physical Objects"
ROLE_ORGANISATIONS = "Ämter/Körperschaften"
LIFE_FAMILY = "Leben/Familie"
ART = "Kunst"
MUSIC = "Musik"
ARMOURING = "Harnische/Waffen"
TEXT = "Text"
OTHER = "Andere"


ENTITY = "Entities"
STATEMENT = "Statements"

group_order = [
    GENERIC,
    # CONCEPTUAL_OBJECTS,
    # PHYSICAL_OBJECTS,
    LIFE_FAMILY,
    ROLE_ORGANISATIONS,
    TEXT,
    ART,
    ARMOURING,
    MUSIC,
    OTHER,
]


@reversion.register(follow=["tempentityclass_ptr"])
class Typology(TempEntityClass):
    __entity_group__ = GENERIC
    __entity_type__ = ENTITY

    class Meta:
        pass


@reversion.register(follow=["tempentityclass_ptr"])
class RoleType(Typology):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Amtstyp"
        verbose_name_plural = "Amtstypen"


@reversion.register(follow=["tempentityclass_ptr"])
class ArmsType(Typology):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Harnisches-/Waffentyp"
        verbose_name_plural = "Harnisches-/Waffentypen"


@reversion.register(follow=["tempentityclass_ptr"])
class ManMaxTempEntityClass(TempEntityClass):
    class Meta:
        abstract = True

    created_by = models.CharField(max_length=300, blank=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True, editable=False)
    modified_by = models.CharField(max_length=300, blank=True, editable=False)
    modified_when = models.DateTimeField(auto_now=True, editable=False)
    internal_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal searchable text, for disambiguation. Store information as statements!",
        verbose_name="Interne Notizen",
    )
    schuh_index_id = models.CharField(max_length=500, blank=True, editable=False)
    alternative_schuh_ids = ArrayField(
        models.CharField(max_length=500, blank=True, editable=False), default=list
    )

    def save(self, auto_created=False, *args, **kwargs):
        if auto_created:
            super().save(*args, **kwargs)
        else:
            if not self.created_by:
                self.created_by = current_request().user.username
            self.modified_by = current_request().user.username
            super().save(*args, **kwargs)


@reversion.register(follow=["tempentityclass_ptr"])
class Factoid(ManMaxTempEntityClass):
    class Meta:
        pass


@reversion.register(follow=["tempentityclass_ptr"])
class Person(ManMaxTempEntityClass):
    """Person: a real person, identified by a label and (one or more) URIs. All information about Persons derived from sources
    should be added as types of Statement, with the Person added as a Related Entity to the Statement.
    """

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Personen"

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Place(ManMaxTempEntityClass):
    """Place: a real place, identified by a label and URIs."""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Ort"
        verbose_name_plural = "Orte"


# TODO: sort out this focking hierarchy
@reversion.register(follow=["tempentityclass_ptr"])
class GroupOfPersons(ManMaxTempEntityClass):
    """Group of persons identified by a label and URIs."""

    class Meta:
        verbose_name = "Personengruppe"
        verbose_name_plural = "Personengruppen"

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Organisation(ManMaxTempEntityClass):
    """Organisation: an organisation or other group, identified by a label and URIs."""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Körperschaft"
        verbose_name_plural = "Körperschaften"


@reversion.register(follow=["tempentityclass_ptr"])
class Foundation(Organisation):
    """Foundation: legally constituted entity, identified by a label and URIs."""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Stiftung"
        verbose_name_plural = "Stiftungen"


@reversion.register(follow=["tempentityclass_ptr"])
class Family(ManMaxTempEntityClass):  # TODO: should be group of persons subclass
    family_name = models.CharField(
        max_length=200, blank=True
    )  # TODO: remove this... it's just label

    __entity_group__ = LIFE_FAMILY
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Familie"
        verbose_name_plural = "Familien"


@reversion.register(follow=["tempentityclass_ptr"])
class ConceptualObject(ManMaxTempEntityClass):
    """A Work of art, literature, music, etc. Where possible, use specific subtypes (Artistic Work, Music Work, etc.)"""

    __entity_group__ = OTHER
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Konzeptionelles Objekt"
        verbose_name_plural = "Konzeptionelle Objekte"


@reversion.register(follow=["conceptualobject_ptr"])
class CompositeConceptualObject(ConceptualObject):
    """A Work of art, literature, music, etc., comprised of individually identifiable sub-works"""

    __entity_group__ = OTHER
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Zusammengesetztes konzeptionelles Objekt"
        verbose_name_plural = "Zusammengesetzte konzeptionelle Objekte"


@reversion.register(follow=["tempentityclass_ptr"])
class PhysicalObject(ManMaxTempEntityClass):
    """A physical object (rather than a conceptual object). Where possible, use specific subtypes (Work, Music Work, Armour)"""

    __entity_group__ = OTHER
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Physisches Objekt"
        verbose_name_plural = "Physische Objekte"


@reversion.register(follow=["physicalobject_ptr"])
class CompositePhysicalObject(PhysicalObject):
    """An object composed of more than one other objects"""

    __entity_group__ = OTHER
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Zusammengesetztes physisches Objekt"
        verbose_name_plural = "Zusammengesetzte physische Objekte"


@reversion.register(follow=["tempentityclass_ptr"])
class Role(ManMaxTempEntityClass):
    """A Role in an Organisation, occupied by one or more Person in RoleOccupation, or assigned/removed via AssignmentToRole/RemovalFromRole"""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Amt"
        verbose_name_plural = "Ämter"


@reversion.register(follow=["tempentityclass_ptr"])
class Task(ManMaxTempEntityClass):
    """A task, fulfilled by person, potentially as part of a Role"""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Tätigkeit"
        verbose_name_plural = "Tätigkeiten"


@reversion.register(follow=["tempentityclass_ptr"])
class FictionalPerson(ConceptualObject):
    __entity_type__ = ENTITY
    __entity_group__ = GENERIC

    class Meta:
        verbose_name = "Fiktive Person"
        verbose_name_plural = "Fiktive Personen"


#### GENERIC STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class GenericStatement(ManMaxTempEntityClass):
    """A Generic Statement about a Person (to be used when nothing else will work)."""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    head_statement = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Do not use"
        verbose_name_plural = "Definitely do not use"


@reversion.register(follow=["genericstatement_ptr"])
class CommunicatesWith(GenericStatement):
    """A Person or Organisation communicating with another"""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    method = models.CharField(
        max_length=50,
        choices=(("verbal", "Verbal"), ("written", "Written")),
        blank=True,
    )

    class Meta:
        verbose_name = "Mitteilung"
        verbose_name_plural = "Mitteilungen"


@reversion.register(follow=["tempentityclass_ptr"])
class GenericEvent(ManMaxTempEntityClass):
    """A Generic event reified as an entity (distinct from Activity)"""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Ereignis"
        verbose_name_plural = "Ereignisse"


@reversion.register(follow=["genericstatement_ptr"])
class Activity(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Handlung"
        verbose_name_plural = "Handlungen"


@reversion.register(follow=["activity_ptr"])
class OwnershipTransfer(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Besitztransfer"
        verbose_name_plural = "Besitztransfere"


@reversion.register(follow=["ownershiptransfer_ptr"])
class GiftGiving(OwnershipTransfer):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Schenkung"
        verbose_name_plural = "Schenkungen"


@reversion.register(follow=["activity_ptr"])
class CreationCommission(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Herstellungsauftrag"
        verbose_name_plural = "Herstellungsaufträge"


@reversion.register(follow=["genericstatement_ptr"])
class Naming(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    forename = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Vorname",
        help_text="der Vorname, Taufname, Rufname o.ä.",
    )
    surname = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Familienname",
        help_text="der Name, der Familienzugehörigkeit beschreibt, im Gegensatz zum individuellen Vornamen. Zur Verwendung von Herkunfts- oder Berufsbezeichnungen als Famliennamen vgl. die Kodierungsrichtlinien",
    )
    role_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Titel",
        help_text="bezeichnet eine spezifische Rolle, ein Rang in der Gesellschaft, mit der eine Person identifiziert werden kann",
    )
    add_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Beiname(n)",
        help_text="enthält ergänzende Namensbestandteile wie Spitznamen, Beinamen, Alias oder beschreibende Bestandteile von einem Namen ('Katharina <addName>die Große</addName>')",
    )

    class Meta:
        verbose_name = "Nennung"
        verbose_name_plural = "Nennungen"


@reversion.register(follow=["genericstatement_ptr"])
class Gendering(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    GENDERS = (
        ("weiblich", "Weiblich"),
        ("männlich", "Männlich"),
        ("unbekannt", "Unbekannt"),
    )
    gender = models.CharField(
        max_length=10, choices=GENDERS, blank=True, verbose_name="Geschlecht"
    )


@reversion.register(follow=["activity_ptr"])
class CreationAct(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Herstellung"
        verbose_name_plural = "Herstellungen"


@reversion.register(follow=["creationact_ptr"])
class CreationOfOrganisation(CreationAct):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Gründung einer Körperschaft"
        verbose_name_plural = "Gründungen von Körperschaften"


@reversion.register(follow=["creationact_ptr"])
class AssemblyOfCompositeObject(CreationAct):
    __entity_group__ = OTHER
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Kombinierung mehrerer Objekte"
        verbose_name_plural = "Kombinierungen mehrerer Objekte"


# ARMOUR TYPES


@reversion.register(follow=["physicalobject_ptr"])
class ArmourPart(PhysicalObject):
    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY

    armour_type = models.CharField(max_length=300)

    class Meta:
        verbose_name = "Rüstungsteil"
        verbose_name_plural = "Rüstungsteile"


@reversion.register(follow=["compositephysicalobject_ptr"])
class Armour(CompositePhysicalObject):
    """Suit of armour, comprising possibly many pieces"""

    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Harnisch"
        verbose_name_plural = "Harnische"

    # armour_type = models.CharField(max_length=300)


@reversion.register(follow=["physicalobject_ptr"])
class Arms(PhysicalObject):
    """Suit of armour, comprising possibly many pieces"""

    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Waffe"
        verbose_name_plural = "Waffen"


@reversion.register(follow=["event_ptr"])
class Battle(GenericEvent):
    """A named battle"""

    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Schlacht"
        verbose_name_plural = "Schlachten"


@reversion.register(follow=["event_ptr"])
class MilitaryCampaign(GenericEvent):
    """A named military campaign"""

    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Feldzug"
        verbose_name_plural = "Feldzüge"


@reversion.register(follow=["event_ptr"])
class Tournament(GenericEvent):
    """A specific, named tournament, in which Persons participate"""

    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Turnier"
        verbose_name_plural = "Turniere"


@reversion.register(follow=["event_ptr"])
class Festivity(GenericEvent):
    """A specific, named festivity, in which Persons participate"""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Fest"
        verbose_name_plural = "Feste"


@reversion.register(follow=["genericstatement_ptr"])
class ParticipationInEvent(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    # TODO: add participation to other events

    class Meta:
        verbose_name = "Teilnahme"
        verbose_name_plural = "Teilnahmen"


@reversion.register(follow=["genericstatement_ptr"])
class UtilisationInEvent(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Verwendung"
        verbose_name_plural = "Verwendungen"


@reversion.register(follow=["genericstatement_ptr"])
class DecorationOfArmour(CreationAct):
    __entity_group__ = ARMOURING
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Verzierung von Harnisch/Waffe"
        verbose_name_plural = "Verzierung von Harnischen/Waffen"


@reversion.register(follow=["genericstatement_ptr"])
class TransportationOfObject(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Transport eines Objekts"
        verbose_name_plural = "Transporte von Objekten"


@reversion.register(follow=["genericstatement_ptr"])
class TransportationOfArmour(TransportationOfObject):
    __entity_group__ = ARMOURING
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Transport von Harnisch/Waffe"
        verbose_name_plural = "Transporte von Harnischen/Waffen"


@reversion.register(follow=["genericstatement_ptr"])
class RepairOfArmour(CreationAct):
    __entity_group__ = ARMOURING
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Reparatur von Harnisch/Waffe"
        verbose_name_plural = "Reparaturen von Harnischen/Waffen"


@reversion.register(follow=["creationact_ptr"])
class ArmourCreationAct(CreationAct):
    __entity_group__ = ARMOURING
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Herstellung eines Rüstungsteiles"
        verbose_name_plural = "Herstellung von Rüstungsteilen"


@reversion.register(follow=["assemblyofcompositeobject_ptr"])
class ArmourAssemblyAct(AssemblyOfCompositeObject):
    __entity_group__ = ARMOURING
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Zusammenstellung von Rüstungsteilen"
        verbose_name_plural = "Zusammenstellungen von Rüstungsteilen"

    # TODO: remove?


# Print


@reversion.register(follow=["conceptualobject_ptr"])
class Image(ConceptualObject):
    __entity_type__ = GENERIC
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Bild"
        verbose_name_plural = "Bilder"


@reversion.register(follow=["image_ptr"])
class Woodcut(Image):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Holzschnitt"
        verbose_name_plural = "Holzschnitte"


@reversion.register(follow=["compositephysicalobject_ptr"])
class PrintedWork(CompositePhysicalObject):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Druckwerk"
        verbose_name_plural = "Druckwerke"


@reversion.register(follow=["printedwork_ptr"])
class Leaflet(PrintedWork):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Flugblatt"
        verbose_name_plural = "Flugblätter"


@reversion.register(follow=["printedwork_ptr"])
class Book(PrintedWork):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Buch"
        verbose_name_plural = "Bücher"


@reversion.register(follow=["compositephysicalobject_ptr"])
class Manuscript(CompositePhysicalObject):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Handschrift"
        verbose_name_plural = "Handschriften"


@reversion.register(follow=["conceptualobject_ptr"])
class TextualWork(ConceptualObject):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Text"
        verbose_name_plural = "Texte"


@reversion.register(follow=["textualwork_ptr"])
class Poem(TextualWork):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Gedicht"
        verbose_name_plural = "Gedichte"


@reversion.register(follow=["compositetextualwork_ptr"])
class CompositeTextualWork(CompositeConceptualObject):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Sammelwerk"
        verbose_name_plural = "Sammelwerke"


@reversion.register(follow=["textualwork_ptr"])
class Preface(TextualWork):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Vorwort"
        verbose_name_plural = "Vorworte"


@reversion.register(follow=["textualwork_ptr"])
class DedicatoryText(TextualWork):
    __entity_group__ = TEXT
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Werk mit Widmung"
        verbose_name_plural = "Werke mit Widmungen"


@reversion.register(follow=["genericstatement_ptr"])
class Dedication(GenericStatement):
    __entity_group__ = TEXT
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Widmung"
        verbose_name_plural = "Widmungen"


@reversion.register(follow=["creationact_ptr"])
class TextualCreationAct(CreationAct):
    __entity_group__ = TEXT
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Textschöpfung"
        verbose_name_plural = "Textschöpfungen"


@reversion.register(follow=["textualcreationact_ptr"])
class Authoring(TextualCreationAct):
    __entity_group__ = TEXT
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Autorenschaft"
        verbose_name_plural = "Autorenschaften"


@reversion.register(follow=["textualcreationact_ptr"])
class Printing(TextualCreationAct):
    __entity_group__ = TEXT
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Druck"
        verbose_name_plural = "Drucke"


@reversion.register(follow=["textualcreationact_ptr"])
class SecretarialAct(TextualCreationAct):
    __entity_group__ = TEXT
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Schreibarbeit"
        verbose_name_plural = "Schreibarbeiten"


@reversion.register(follow=["textualcreationact_ptr"])
class Redacting(TextualCreationAct):
    __entity_group__ = TEXT
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Bearbeitung"
        verbose_name_plural = "Bearbeitungen"


@reversion.register(follow=["textualcreationact_ptr"])
class PreparationOfConceptualText(TextualCreationAct):
    __entity_group__ = TEXT
    __entity_type__ = STATEMENT

    # TODO: think of this someone else!


# Base Work subtypes


@reversion.register(follow=["conceptualobject_ptr"])
class MusicWork(ConceptualObject):
    """A piece of music"""

    __entity_group__ = MUSIC
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Musikwerk"
        verbose_name_plural = "Musikwerke"


@reversion.register(follow=["physicalobject_ptr"])
class ArtisticWork(PhysicalObject):
    """A work of art"""

    __entity_group__ = ART
    __entity_type__ = ENTITY

    class Meta:
        verbose_name = "Kunstwerk"
        verbose_name_plural = "Kunstwerke"


@reversion.register(follow=["genericstatement_ptr"])
class Birth(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Geburt"
        verbose_name_plural = "Geburten"


@reversion.register(follow=["genericstatement_ptr"])
class Death(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Tod"
        verbose_name_plural = "Tode"


@reversion.register(follow=["genericstatement_ptr"])
class OrganisationLocation(GenericStatement):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Ort einer Körperschaft"
        verbose_name_plural = "Ort von Körperschaften"


@reversion.register(follow=["genericstatement_ptr"])
class AcceptanceOfOrder(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    # AcceptanceOfOrder # Befehlsannahme
    class Meta:
        verbose_name = "Befehlsannahme"
        verbose_name_plural = "Befehlsannahmen"


@reversion.register(follow=["genericstatement_ptr"])
class Election(GenericStatement):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Wahl"
        verbose_name_plural = "Wahlen"


@reversion.register(follow=["activity_ptr"])
class PerformanceOfTask(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Ausübung einer Tätigkeit"
        verbose_name_plural = "Ausübungen von Tätigkeiten"


@reversion.register(follow=["activity_ptr"])
class PerformanceOfWork(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Aufführung eines Werkes"
        verbose_name_plural = "Aufführungen von Werken"


@reversion.register(follow=["genericstatement_ptr"])
class RoleOccupation(GenericStatement):
    """Describes the occupation of a Role by a Person"""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Bekleidung eines Amtes"
        verbose_name_plural = "Bekleidung von Ämtern"


@reversion.register(follow=["genericstatement_ptr"])
class AssignmentToRole(GenericStatement):
    """Describes the assignment of a Role to a Person (assignee), by an Person (assigner)"""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Amtseinsetzung"
        verbose_name_plural = "Amtseinsetzungen"

    # description = models.CharField(max_length=200)


@reversion.register(follow=["genericstatement_ptr"])
class RemovalFromRole(GenericStatement):
    """Describes the removal from a Role of a Person (role occupier), by an Person (remover)"""

    class Meta:
        verbose_name_plural = "Removals from Role"

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Amtsenthebung"
        verbose_name_plural = "Amtsenthebungen"


@reversion.register(follow=["genericstatement_ptr"])
class FamilialRelation(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Familiäre Verbindung"
        verbose_name_plural = "Familiäre Verbindungen"


@reversion.register(follow=["familialrelation_ptr"])
class ParentalRelation(FamilialRelation):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT
    PARENTAL_TYPES = (
        ("mutter", "Mutter"),
        ("vater", "Vater"),
        ("stiefmutter", "Stiefmutter"),
        ("stiefvater", "Stiefvater"),
        ("ziehmutter", "Ziehmutter"),
        ("ziehvater", "Ziehvater"),
        ("unbekannt", "Unbekannt"),
    )
    parental_type = models.CharField(
        max_length=15,
        choices=PARENTAL_TYPES,
        blank=True,
        verbose_name="Art des Verhältnisses",
    )

    class Meta:
        verbose_name = "Elternschaft"
        verbose_name_plural = "Elternschaften"


@reversion.register(follow=["familialrelation_ptr"])
class SiblingRelation(FamilialRelation):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT
    SIBLING_TYPE = (
        ("bruder", "Bruder"),
        ("schwester", "Schwester"),
        ("halbbruder", "Halbbruder"),
        ("stiefbruder", "Stiefbruder"),
        ("halbschwester", "Halbschwester"),
        ("stiefschwester", "Stiefschwester"),
        ("unbekannt", "Unbekannt"),
    )

    sibling_type = models.CharField(
        max_length=14,
        choices=SIBLING_TYPE,
        blank=True,
        verbose_name="Art des Verhältnisses",
    )

    class Meta:
        verbose_name = "Geschwisterverhältnis"
        verbose_name_plural = "Geschwisterverhältnisse"


@reversion.register(follow=["familialrelation_ptr"])
class MarriageBeginning(FamilialRelation):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Eheschließung"
        verbose_name_plural = "Eheschließungen"


@reversion.register(follow=["familialrelation_ptr"])
class MarriageEnd(FamilialRelation):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Ende der Ehe"
        verbose_name_plural = "Enden der Ehen"


@reversion.register(follow=["genericstatement_ptr"])
class FamilyMembership(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Familienmitgliedschaft"
        verbose_name_plural = "Familienmitgliedschaften"


@reversion.register(follow=["genericstatement_ptr"])
class Payment(GenericStatement):
    """Payment of money for Item, Work, Acquisition, or other Activity"""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    amount = models.CharField(max_length=200, blank=True)
    currency = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Zahlung"
        verbose_name_plural = "Zahlungen"


@reversion.register(follow=["genericstatement_ptr"])
class Order(GenericStatement):
    """An order given by someone to do something"""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Befehl"
        verbose_name_plural = "Befehle"


""" DUPLICATE OF OWNERSHIP TRANSFER
@reversion.register(follow=["genericstatement_ptr"])
class Acquisition(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT
"""

# Art Statements


@reversion.register(follow=["creationact_ptr"])
class ArtworkCreationAct(CreationAct):
    __entity_group__ = ART
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Herstellung eines Kunstwerkes"
        verbose_name_plural = "Herstellung von Kunstwerken"


""" REMOVED: adds nothing above Acquisition
@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkAcquisition(Acquisition):
    __entity_group__ = ART_STATEMENTS
"""

# Music Statements


@reversion.register(follow=["genericstatement_ptr"])
class MusicPerformance(GenericStatement):
    __entity_group__ = MUSIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Musikaufführung"
        verbose_name_plural = "Musikaufführungen"


overridden_properties = defaultdict(lambda: set())


def build_property(
    name: str,
    name_reverse: str,
    subj_class: type[TempEntityClass] | Iterable[type[TempEntityClass]],
    obj_class: type[TempEntityClass] | Iterable[type[TempEntityClass]],
    overrides: Property | Iterable[Property] | None = None,
):
    """Convenience function for defining properties"""
    global overridden_properties
    prop = Property.objects.get_or_create(
        name=name,
        name_reverse=name_reverse,
    )[0]

    prop.subj_class.clear()
    if isinstance(subj_class, Iterable):
        for sclass in subj_class:
            prop.subj_class.add(ContentType.objects.get_for_model(sclass))

            if overrides:
                # print(overrides)

                if isinstance(overrides, Iterable):
                    for override in overrides:
                        overridden_properties[sclass].add(override)
                else:
                    overridden_properties[sclass].add(overrides)

    else:
        prop.subj_class.add(ContentType.objects.get_for_model(subj_class))
        if overrides:
            if isinstance(overrides, Iterable):
                for override in overrides:
                    overridden_properties[subj_class].add(override)
            else:
                overridden_properties[subj_class].add(overrides)

    prop.obj_class.clear()
    if isinstance(obj_class, Iterable):
        for oclass in set(obj_class):
            prop.obj_class.add(ContentType.objects.get_for_model(oclass))

    else:
        prop.obj_class.add(ContentType.objects.get_for_model(obj_class))

    return prop


def subclasses(model: type[TempEntityClass]) -> Iterable[type[TempEntityClass]]:
    sc = [model]
    for subclass in model.__subclasses__():
        sc += [subclass, *subclasses(subclass)]
    return set(sc)


def construct_properties():
    # Generic Statement attached to Factoid

    armour_has_armour_type = build_property(
        "Harnisches-Waffentyp",
        "instantiates type",
        [Arms, Armour, ArmourPart],
        ArmsType,
    )

    armour_type_is_subtype_of_armour_type = build_property(
        "unterkategories von", "is supertype of", ArmsType, ArmsType
    )

    role_has_role_type = build_property("amtstyp", "instantiates type", Role, RoleType)

    role_type_is_subtype_of_role_type = build_property(
        "unterkategorie von", "is supertype of", RoleType, RoleType
    )

    role_is_part_of_organisation = build_property(
        "teil einer körperschaft", "organisation has role", Role, Organisation
    )

    factoid_has_statement = build_property(
        "has_statement", "is_statement_of", Factoid, subclasses(GenericStatement)
    )

    activity_carried_out_by = build_property(
        "Handlung ausgeführt von",
        "carried out activity",
        subclasses(Activity),
        [Person, Organisation, Family],
    )

    activity_has_place = build_property(
        "Ort der Handlung", "activity took place in", subclasses(Activity), Place
    )

    creation_act_carried_out_by_person_or_org = build_property(
        "Ausgeführt von",
        "person/org carrying out act",
        subclasses(CreationAct),
        [Person, Organisation],
        overrides=[activity_carried_out_by],
    )

    creation_act_thing_created = build_property(
        "Produkt",
        "was created in",
        subclasses(CreationAct),
        [*subclasses(PhysicalObject), *subclasses(ConceptualObject)],
    )

    text_authored = build_property(
        "verfasster Text", "was authored in", Authoring, subclasses(TextualWork)
    )

    printed_work_printed = build_property(
        "gedrucktes Werk", "was printed in", Printing, subclasses(PrintedWork)
    )

    secretarial_act_contributed_to = build_property(
        "betreffender Text",
        "was concerned in secretarial act",
        SecretarialAct,
        subclasses(TextualWork),
    )

    redacting_contributed_to = build_property(
        "betreffender Text",
        "was concerned in redacting",
        Redacting,
        subclasses(TextualWork),
    )

    preparation_of_conceptual_text_of = build_property(
        "betreffender Text",
        "was prepared as conceptual text in",
        PreparationOfConceptualText,
        subclasses(TextualWork),
    )

    assembly_of_composite_object = build_property(
        "zusammengesetztes Objekt",
        "was assembled in",
        AssemblyOfCompositeObject,
        [*subclasses(CompositeConceptualObject), *subclasses(CompositePhysicalObject)],
        overrides=[creation_act_thing_created],
    )

    ownership_transfer_what = build_property(
        "überstragenes Objekt",
        "had ownership transferred in",
        subclasses(OwnershipTransfer),
        subclasses(PhysicalObject),
    )
    ownership_transfer_from_whom = build_property(
        "vorbesitzer",
        "was previous owner in transfer",
        subclasses(OwnershipTransfer),
        [Person, *subclasses(Organisation)],
    )
    ownership_transfer_to_whom = build_property(
        "empfänger",
        "new owner in transfer",
        subclasses(OwnershipTransfer),
        [Person, *subclasses(Organisation)],
    )

    naming_of_person = build_property("genammte Person", "was named in", Naming, Person)

    gendering_of_person = build_property("person", "was gendered in", Gendering, Person)

    dedication_to_dedicatory_text = build_property(
        "enthalten in", "contains dedictation", Dedication, DedicatoryText
    )
    dedication_to_person = build_property(
        "adressat der Widmung", "has dedication", Dedication, Person
    )

    birth_of_person = build_property("geborene Person", "was born in", Birth, Person)
    place_of_birth = build_property(
        "Ort der Geburt", "is location of birth", Birth, Place
    )

    death_of_person = build_property("verstorbene Person", "died in", Death, Person)
    place_of_death = build_property(
        "Ort des Todes", "is location of death", Death, Place
    )

    organisation_location_organisation = build_property(
        "Körperschaft",
        "was located in",
        OrganisationLocation,
        subclasses(Organisation),
    )
    organisation_location_place = build_property(
        "Ort", "is location of organisation", OrganisationLocation, Place
    )

    organisation_creation_creates_organisation = build_property(
        "Körperschaft",
        "was created by",
        CreationOfOrganisation,
        Organisation,
        overrides=[creation_act_thing_created],
    )

    election_by = build_property(
        "election by",
        "was responsible for election of",
        Election,
        [*subclasses(GroupOfPersons), *subclasses(Organisation), Person],
    )
    election_to_role = build_property("Amt", "was occupied by election", Election, Role)
    election_of_person = build_property(
        "gewählte Person", "was elected in", Election, Person
    )
    election_leads_to_role_occupation = build_property(
        "bekleidetes Amt", "was begun by election", Election, RoleOccupation
    )

    performance_of_task_task = build_property(
        "ausgeführte Tätigkeit", "was performed in", PerformanceOfTask, Task
    )
    performance_of_task_person_group = build_property(
        "Ausführende",
        "involved in task performance",
        PerformanceOfTask,
        [Person, *subclasses(Organisation), GroupOfPersons],
    )

    performance_of_work_work = build_property(
        "aufgeführtes Werk", "was performed in", PerformanceOfWork, [MusicWork, Poem]
    )
    performance_of_work_person_group = build_property(
        "Aufführende",
        "involved in performance of work",
        PerformanceOfWork,
        [Person, *subclasses(Organisation)],
    )

    role_occupation_role = build_property(
        "Amt", "role occupied in", RoleOccupation, Role
    )
    role_occupation_person = build_property(
        "Amtsträger", "has role occupation", RoleOccupation, Person
    )

    assignment_to_role_role = build_property(
        "Amt", "was assigned in", AssignmentToRole, Role
    )
    assignment_to_role_assigner = build_property(
        "Amtsverleiher",
        "assigned role in",
        AssignmentToRole,
        [Person, *subclasses(Organisation)],
    )
    assignment_to_role_assignee = build_property(
        "Amtsempfänger", "was assigned role in", AssignmentToRole, Person
    )
    assignment_to_role_starts_role_occupation = build_property(
        "bekleidetes Amt",
        "was started by",
        AssignmentToRole,
        RoleOccupation,
    )

    removal_from_role_role = build_property(
        "enthobenes Amt", "was removed from person in", RemovalFromRole, Role
    )
    removal_from_role_remover = build_property(
        "Amtsentheber",
        "removed role in",
        RemovalFromRole,
        [Person, *subclasses(Organisation)],
    )
    removal_from_role_removee = build_property(
        "betroffene Person", "removed from role in", RemovalFromRole, Person
    )
    removal_from_role_ends_role_occupation = build_property(
        "bekleidetes Amt",
        "was ended by",
        RemovalFromRole,
        RoleOccupation,
    )

    parental_relation_parent = build_property(
        "Elternteil", "is parent in relationship", ParentalRelation, Person
    )
    parental_relation_child = build_property(
        "Kind", "is child in relationship", ParentalRelation, Person
    )

    sibling_relation_person_a = build_property(
        "Person mit Geschwisterteil",
        "has sibling in relationship",
        SiblingRelation,
        Person,
    )
    sibling_relation_person_b = build_property(
        "Geschwisterteil", "has sibling_in_relationship", SiblingRelation, Person
    )

    marriage_beginning_person = build_property(
        "Ehepartner", "has marriage beginning in", MarriageBeginning, Person
    )
    marriage_beginning_place = build_property(
        "Ort der Eheschließung", "is place of marriage", MarriageBeginning, Place
    )

    marriage_end_person = build_property(
        "Ehemalige Ehepartner", "has marriage ending in", MarriageEnd, Person
    )

    family_membership_family = build_property(
        "Familie", "is member of family", FamilyMembership, Family
    )

    family_membership_person = build_property(
        "Person", "has family membership", FamilyMembership, Person
    )

    payment_for_act = build_property(
        "Zahlungsgrund",
        "was paid for in",
        Payment,
        [
            PerformanceOfTask,
            PerformanceOfWork,
            RoleOccupation,
            CreationAct,
            OwnershipTransfer,
            *subclasses(Activity),
        ],
    )
    payment_by_person = build_property(
        "Zahlender", "made payment in", Payment, [Person, *subclasses(Organisation)]
    )
    payment_to_person = build_property(
        "Zahlungsempfänger",
        "received payment in",
        Payment,
        [Person, *subclasses(Organisation)],
    )
    payment_source_of_money = build_property(
        "Zahlungsquelle",
        "was source of money for payment",
        Payment,
        [Person, *subclasses(Organisation), Family],
    )

    order_for = build_property(
        "befohlene Tätigkeit",
        "was ordered in",
        subclasses(Order),
        [
            PerformanceOfTask,
            MusicPerformance,
            *subclasses(CreationAct),
            *subclasses(CreationCommission),
            Death,
            AssignmentToRole,
            RemovalFromRole,
            Payment,
            Order,
        ],
    )
    ordered_by = build_property(
        "Befehlsgeber", "gave order", Order, [Person, *subclasses(Organisation)]
    )
    order_received_by = build_property(
        "Befehlsempfänger",
        "received order",
        Order,
        [Person, *subclasses(Organisation)],
    )

    armour_creation_act_armour = build_property(
        "Hergestellter Harnisch",
        "was created in",
        ArmourCreationAct,
        [ArmourPart, Armour],
        overrides=[
            creation_act_thing_created,
        ],
    )
    armour_assembly_act_armour_pieces = build_property(
        "Rüstungsteile",
        "was assembled to suit in",
        ArmourAssemblyAct,
        ArmourPart,
    )
    armour_assembly_act_armour_suit = build_property(
        "Endprodukt",
        "was assembled in",
        ArmourAssemblyAct,
        Armour,
        overrides=[assembly_of_composite_object, creation_act_thing_created],
    )

    creation_commission_creation_act_commissions = build_property(
        "Beauftragte Herstellung",
        "was commissioned in",
        CreationCommission,
        subclasses(CreationAct),
    )

    acceptance_of_statement_generic_statement = build_property(
        "angenommener Befehl",
        "was accepted in",
        AcceptanceOfOrder,
        subclasses(Order),
    )
    acceptance_of_statement_by_person = build_property(
        "Befehlsempfänger",
        "was accepted by",
        AcceptanceOfOrder,
        [Person, Organisation, GroupOfPersons],
    )

    use_in_battle_battle = build_property(
        "Schlacht", "has use in", UtilisationInEvent, Battle
    )
    use_in_battle_item = build_property(
        "Verwendetes Objekt",
        "had use in",
        UtilisationInEvent,
        [ArmourPart, Armour, Arms],
    )

    participation_in_event_event = build_property(
        "Ereignis", "has participation", ParticipationInEvent, subclasses(GenericEvent)
    )
    participation_in_event_person = build_property(
        "Teilnehmer",
        "has participation",
        ParticipationInEvent,
        [Person, Organisation, Family],
    )

    decoration_of_object_object = build_property(
        "repariertes Objekt",
        "was repaired in",
        RepairOfArmour,
        [Armour, ArmourPart, Arms],
    )
    decoration_of_object_person = build_property(
        "Reparateur",
        "was involved in repair",
        RepairOfArmour,
        [Person, Organisation, GroupOfPersons],
    )

    decoration_of_object_object = build_property(
        "verziertes Objekt",
        "was decorated in",
        DecorationOfArmour,
        [Armour, ArmourPart, Arms],
    )
    decoration_of_object_person = build_property(
        "Verzierer",
        "was involved in decoration",
        DecorationOfArmour,
        [Person, *subclasses(Organisation), GroupOfPersons],
    )

    # statement_has_related_statement = build_property("has related statement", "has related statement", subclasses(GenericStatement), subclasses(GenericStatement))

    communicates_with_sender = build_property(
        "Absender",
        "is sender of communication",
        CommunicatesWith,
        [Person, GroupOfPersons, *subclasses(Organisation)],
    )
    communicates_with_recipient = build_property(
        "Empfänger",
        "is receiver of communication",
        CommunicatesWith,
        [Person, GroupOfPersons, *subclasses(Organisation)],
    )
    communicates_with_statement = build_property(
        "Betreff",
        "is subject of commuication",
        CommunicatesWith,
        subclasses(GenericStatement),
    )
    communicates_with_sender_place = build_property(
        "Ausstellungsort", "is origin place of communication", CommunicatesWith, Place
    )
    communicates_with_recipient_place = build_property(
        "Zielort", "is reception place of communication", CommunicatesWith, Place
    )

    transportation_of_object_object = build_property(
        "Transportiertes Objekt",
        "was transported in",
        TransportationOfObject,
        subclasses(PhysicalObject),
    )
    transportation_of_object_by = build_property(
        "Transporteur",
        "was involved in transportation",
        TransportationOfObject,
        [Person, *subclasses(Organisation), Family],
    )
    transportation_of_object_from_person = build_property(
        "Absender",
        "object transported from",
        TransportationOfObject,
        [Person, *subclasses(Organisation), Family],
    )
    transportation_of_object_from_place = build_property(
        "Ausgangsort", "object transported from place", TransportationOfObject, Place
    )
    transportation_of_object_to_person = build_property(
        "Empfänger",
        "object transported to",
        TransportationOfObject,
        [Person, *subclasses(Organisation), Family],
    )
    transportation_of_object_to_place = build_property(
        "Zielort", "object transported to place", TransportationOfObject, Place
    )

    transportation_of_armour_armour = build_property(
        "Transportierte Harnische/Waffen",
        "was transported in",
        TransportationOfArmour,
        [Arms, ArmourPart, Armour],
        overrides=[transportation_of_object_object],
    )
    # transportation_of_object_by = build_property("transported by", "was involved in transportation", TransportationOfObject, [Person, *subclasses(Organisation), Family, GroupOfPersons])
