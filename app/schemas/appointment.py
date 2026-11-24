from datetime import date, datetime
from pydantic import (
    BaseModel, 
    Field, 
    field_validator,
    model_validator,
)
from app.schemas.customer import validate_customer_name, validate_taiwan_mobile


class GuestAppointmentLookup(BaseModel):
    # phone_number: str
    # birthday: date
    #以下三行新增的
    phone_number: str
    birthday: date | None = None
    name: str | None = None

    
    # @field_validator("phone_number")
    # @classmethod
    # def validate_phone(cls, value: str) -> str:
    #     return validate_taiwan_mobile(value)
    
    #以下新增的class
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_taiwan_mobile(value)

    @field_validator("name")
    @classmethod
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_customer_name(value)

    @model_validator(mode="after")
    def require_lookup_identity(self):
        if self.birthday is None and not self.name:
            raise ValueError("請提供生日，或提供姓名作為查詢資料")
        return self

class GuestAppointmentCreate(GuestAppointmentLookup):
    name: str = Field(min_length=1, max_length=100)
    starts_at: datetime
    service_name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return validate_customer_name(value)

    @field_validator("service_name")
    @classmethod
    def trim_service_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Service name cannot be empty")
        return value


class GuestAppointmentOut(BaseModel):
    id: int
    starts_at: datetime
    service_name: str
    status: str

    class Config:
        from_attributes = True


class AppointmentAdminOut(BaseModel):
    id: int
    customer_id: int
    #以下一行新增
    customer_name: str
    starts_at: datetime
    service_name: str
    status: str
    internal_note: str | None = None

    class Config:
        from_attributes = True

class GuestAppointmentLast3Search(BaseModel):
    phone_last3: str = Field(pattern=r"^[0-9]{3}$")


class GuestAppointmentLast3Lookup(GuestAppointmentLast3Search):
    customer_id: int
    birthday: date


class GuestAppointmentCandidateOut(BaseModel):
    customer_id: int
    masked_name: str


class GuestAppointmentCancel(GuestAppointmentLookup):
    appointment_id: int


class GuestAppointmentCandidateSearch(GuestAppointmentLast3Search):
    birthday: date


class GuestAppointmentLast3Create(GuestAppointmentLast3Lookup):
    starts_at: datetime
    service_name: str = Field(min_length=1, max_length=100)

    @field_validator("service_name")
    @classmethod
    def trim_service_name(cls, value: str) -> str:
        return GuestAppointmentCreate.trim_service_name(value)
