from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(String)
    company = Column(String)
    email = Column(String, unique=True)
    url = Column(String)
    job_description = Column(String)
    sent = Column(
        Boolean,
        default=False
    )
    client = Column(String)
    search_keyword = Column(String)


class HotlistCampaign(Base):

    __tablename__ = "hotlist_campaigns"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    recruiter_email = Column(String, index=True)
    campaign_name = Column(String, index=True)
    sent_at = Column(String)
    status = Column(String)