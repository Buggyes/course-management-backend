from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Field, SQLModel, LargeBinary, Column

class AreaAction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, index=True)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login: str = Field(default=None, index=True)
    password: str = Field(default=None)

class Instructor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=str, index=True)
    biography: str = Field(default=None)
    pfp: bytes = Field(sa_column=Column(LargeBinary))
    banner: bytes = Field(sa_column=Column(LargeBinary))

class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=str, index=True)
    description: str = Field(default=None)
    banner: bytes = Field(sa_column=Column(LargeBinary))
    instructor_id: int = Field(foreign_key="instructor.id")
    area_id: int = Field(foreign_key="areaaction.id")

class InstructorArea(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    instructor_id: int = Field(foreign_key="instructor.id")
    area_id: int = Field(foreign_key="areaaction.id")


# DTOs

class AreaActionDTO(BaseModel):
    name: str

class UserDTO(BaseModel):
    login: str
    password: str

class CourseDTO(BaseModel):
    name: str
    description: str
    banner: bytes
    instructor_id: int

class CourseUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    banner: Optional[str] = None
    instructor_id: Optional[int] = None
    area_id: Optional[int] = None

class InstructorDTO(BaseModel):
    name: str
    biography: Optional[str]
    pfp: bytes
    banner: bytes
    areas_id: List[int] = []

class InstructorUpdateDTO(BaseModel):
    name: Optional[str] = None
    biography: Optional[str] = None
    pfp: Optional[bytes] = None
    banner: Optional[bytes] = None
    courses: Optional[List[CourseDTO]] = None
    areas_id: Optional[List[int]] = None