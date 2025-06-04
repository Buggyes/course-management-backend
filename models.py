from sqlmodel import Field, SQLModel, LargeBinary, Column

class AreaAction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, index=True)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login: str = Field(default=None, index=True)
    password: str = Field(default=None, index=True)

class Instructor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    biography: str | None = None
    pfp: bytes = Field(sa_column=Column(LargeBinary))
    banner: bytes = Field(sa_column=Column(LargeBinary))

class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    description: str = Field(default=None)
    banner: bytes = Field(sa_column=Column(LargeBinary))
    instructor_id: int | None = Field(default=None, foreign_key="instructor.id")

class InstructorArea(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    instructor_id: int | None = Field(default=None, foreign_key="instructor.id")
    area_id: int | None = Field(default=None, foreign_key="areaaction.id")