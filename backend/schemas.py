from pydantic import BaseModel


class JobCreate(BaseModel):

    title: str

    company: str

    email: str

    url: str

    job_description: str