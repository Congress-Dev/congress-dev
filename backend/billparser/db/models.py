import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sqlalchemy as sa
from sqlalchemy.schema import Index

from billparser.db.caching import CacheableMixin, query_callable, regions

Base = declarative_base()


class CastingArray(ARRAY):
    def bind_expression(self, bindvalue):
        return sa.cast(bindvalue, self)


class BillTypes(enum.Enum):
    Bill = ""
    ConRes = "Continuing Resolution"
    Res = "Resolution"
    JRes = "Joint Resolution"


# This will represent the basic information about each bill
class Bill(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "bill_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "bill"
    bill_id = Column(Integer, primary_key=True)

    chamber = Column(String, index=True)

    bill_type = Column(Enum(BillTypes))
    bill_number = Column(Integer, index=True)
    bill_title = Column(String)
    versions = relationship("BillVersion")


# Each version of the bill, content diffs will reference this.
class BillVersion(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "bill_version_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "bill_version"
    bill_version_id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bill.bill_id", ondelete="CASCADE"))
    bill_version = Column(String)
    base_version_id = Column(
        Integer, ForeignKey("version.version_id", ondelete="CASCADE")
    )
    bill = relationship("Bill", back_populates="versions")


# Versions of the USCODE
class Version(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "version_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "version"
    version_id = Column(Integer, primary_key=True)

    title = Column(String)

    base_id = Column(Integer, ForeignKey("version.version_id", ondelete="CASCADE"))

    bill_version_id = Column(
        Integer,
        ForeignKey("bill_version.bill_version_id", ondelete="CASCADE"),
        index=True,
    )

    def to_dict(self):
        boi = {
            "version_id": self.version_id,
            "title": self.title,
            "base_id": self.base_id,
        }
        return {k: v for (k, v) in boi.items() if v is not None}


class Chapter(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "chapter_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "chapter"

    # Each version of the chapter will be put into the database
    chapter_id = Column(Integer, primary_key=True)

    usc_ident = Column(String)
    usc_guid = Column(String)
    # T1-49
    number = Column(String)

    # The header for this title
    name = Column(String)

    # usc only right now
    document = Column(String)

    # Version String
    version_id = Column(Integer, ForeignKey("version.version_id", ondelete="CASCADE"))

    def to_dict(self):
        boi = {
            "chapter_id": self.chapter_id,
            "ident": self.usc_ident,
            "number": self.number,
            "name": self.name,
            "version": self.version_id,
        }
        return {k: v for (k, v) in boi.items() if v is not None}


class Section(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "section_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "sections"

    section_id = Column(Integer, primary_key=True)
    usc_ident = Column(String)
    usc_guid = Column(String)
    # value attrib of num element
    number = Column(String)
    # innertext of num element
    section_display = Column(String)

    # inner text of heading tag
    heading = Column(String)
    chapter_id = Column(Integer, ForeignKey("chapter.chapter_id", ondelete="CASCADE"))

    # Version String
    version_id = Column(Integer, ForeignKey("version.version_id", ondelete="CASCADE"))

    def to_dict(self):
        boi = {
            "section_id": self.section_id,
            "ident": self.usc_ident,
            "number": self.number,
            "display": self.section_display,
            "heading": self.heading,
            "chapter_id": self.chapter_id,
            "version": self.version_id,
        }
        return {k: v for (k, v) in boi.items() if v is not None}


class BillContent(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "bill_content_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "bill_content"

    bill_content_id = Column(Integer, primary_key=True)
    parent_id = Column(
        Integer,
        ForeignKey("bill_content.bill_content_id", ondelete="CASCADE"),
        index=True,
    )

    order_number = Column(Integer)

    # value attrib of num element
    number = Column(String)
    # innertext of num element
    section_display = Column(String)

    # inner text of heading tag
    heading = Column(String)

    content_str = Column(String)
    # Version String
    bill_version_id = Column(
        Integer,
        ForeignKey("bill_version.bill_version_id", ondelete="CASCADE"),
        index=True,
    )

    content_type = Column(String)

    # parsed data
    action_parse = Column(CastingArray(JSONB))

    def to_dict(self):
        ap = {}
        for obj in self.action_parse:
            keys = [x for x in obj.keys() if x not in ["changed", "parsed_cite"]]
            ap[keys[0]] = obj.get("changed", False)

        boi = {
            "bill_content_id": self.bill_content_id,
            "content_type": self.content_type,
            "order": self.order_number,
            "parent": self.parent_id,
            "number": self.number,
            "display": self.section_display,
            "heading": self.heading,
            "content": self.content_str,
            "version": self.bill_version_id,
            "ap": ap,
        }
        return {k: v for (k, v) in boi.items() if v is not None and v != {}}


class Content(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "content_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "content"

    content_id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.section_id", ondelete="CASCADE"))
    parent_id = Column(Integer, ForeignKey("content.content_id", ondelete="CASCADE"))

    order_number = Column(Integer)
    usc_ident = Column(String)
    usc_guid = Column(String)

    # value attrib of num element
    number = Column(String)
    # innertext of num element
    section_display = Column(String)

    # inner text of heading tag
    heading = Column(String)

    content_str = Column(String)
    # Version String
    version_id = Column(
        Integer, ForeignKey("version.version_id", ondelete="CASCADE"), index=True
    )

    content_type = Column(String)

    def to_dict(self):
        boi = {
            "content_id": self.content_id,
            "content_type": self.content_type,
            "section_id": self.section_id,
            "order": self.order_number,
            "parent": self.parent_id,
            "ident": self.usc_ident,
            "number": self.number,
            "display": self.section_display,
            "heading": self.heading,
            "content": self.content_str,
            "version": self.version_id,
        }
        return {k: v for (k, v) in boi.items() if v is not None}


# This only has data for the column that changes.
class ContentDiff(CacheableMixin, Base):
    cache_label = "default"
    cache_regions = regions
    cache_pk = "diff_id"  # for custom pk
    query_class = query_callable(regions)
    __tablename__ = "content_diff"

    diff_id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("content.content_id", ondelete="CASCADE"))
    section_id = Column(Integer, ForeignKey("sections.section_id", ondelete="CASCADE"))
    chapter_id = Column(Integer, ForeignKey("chapter.chapter_id", ondelete="CASCADE"))
    order_number = Column(Integer)
    number = Column(String)
    # innertext of num element
    section_display = Column(String)

    # inner text of heading tag
    heading = Column(String)

    content_str = Column(String)
    # Version String
    version_id = Column(
        Integer, ForeignKey("version.version_id", ondelete="CASCADE"), index=True
    )

    def to_dict(self):

        boi = {
            "id": self.diff_id,
            "content_id": self.content_id,
            "section_id": self.section_id,
            "chapter_id": self.chapter_id,
            "order": self.order_number,
            "number": self.number,
            "display": self.section_display,
            "heading": self.heading,
            "content": self.content_str,
            "version": self.version_id,
        }
        return {k: v for (k, v) in boi.items() if v is not None}


class BillIngestion(Base):
    __tablename__ = "bill_ingestion"
    bill_ingestion_id = Column(Integer, primary_key=True)
    archive_name = Column(String)
    archive_path = Column(String)
    checksum = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    bill_version_id = Column(
        Integer, ForeignKey("bill_version.bill_version_id"), index=True
    )

