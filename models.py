from sqlmodel import Field, SQLModel

class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, index=True)

class AreaAction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None, index=True)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login: str = Field(default=None, index=True)
    password: str = Field(default=None, index=True)
    role_id: int | None = Field(default=None, foreign_key="role.id")

class Instructor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    biography: str | None = None
    pfp: bytearray | None = None
    banner: bytearray | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")

class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    description: str = Field(default=None)
    video: bytearray | None = None
    banner: bytearray | None = None
    instructor_id: int | None = Field(default=None, foreign_key="instructor.id")


class InstructorArea(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    instructor_id: int | None = Field(default=None, foreign_key="instructor.id")
    area_id: int | None = Field(default=None, foreign_key="areaaction.id")