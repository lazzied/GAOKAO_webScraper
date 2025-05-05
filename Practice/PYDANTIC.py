
from pydantic import BaseModel, EmailStr, validator


class User(BaseModel):
    name: str
    email: EmailStr
    account_id: int

 


user_data = {
    'name': 'Jack',
    'email': 'jack@piwegami.io',
    'account_id': 12345
}

user =  User(**user_data)

