from sqlmodel import Field, SQLModel

class Instructor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    biography: str = Field(default=None)
    pfp: bytearray = Field(default=None)
    banner: bytearray = Field(default=None)

class AreaAction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

class InstructorArea(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    instructor_id: int | None = Field(default=None, foreign_key="instructor.id")
    area_id: int | None = Field(default=None, foreign_key="areaaction.id")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login: str = Field(default=None, index=True)
    password: str = Field(default=None, index=True)
    role_id: int | None = Field(default=None, foreign_key="areaaction.id")