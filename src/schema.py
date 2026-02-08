from pydantic import BaseModel, Field, EmailStr
from typing import List,Dict,Optional
class ScanRequestSchema(BaseModel):
    url:str = Field(...)
    category:str = Field("general")
    allergy:str = Field("")
class CompareRequestSchema(BaseModel):
    url1:str = Field(...)
    url2:str = Field(...)
    usecase:str = Field(...)
    category:str = Field("general")
    allergy:str = Field("")

class Ingredients(BaseModel):
    name:str
    Itype:str
    description:str
    health_score:int=Field(...,ge=0,le=10)
class ScanImageResponseSchema(BaseModel):
    is_safe:bool=Field(...,description="is it safe for user")
    url:str=Field(...,description="url of the image")
    product_name:str=Field(...,description="name of the product")
    description:str=Field(...,description="about the product and its effect")
    ingredients:List[Ingredients]
    nutrition_estimate:Dict[str,int]
    health_score:int=Field(...,ge=0,le=10)

class SignupSchema(BaseModel):
    email:EmailStr
    password:str
    name:str
class LoginSchema(BaseModel):
    email:EmailStr
    password:str
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
# class Nutritions(BaseModel):
#     calory:Optional[int]=Field(0,description="Calories in kcal")
#     energy:Optional[int]=Field(0,description="Energy in kJ")
#     protein:Optional[int]=Field(0,description="Protein in g")
#     sugar:Optional[int]=Field(0,description="Sugar in g")
#     fat:Optional[int]=Field(0,description="Fat in g")
#     fiber:Optional[int]=Field(0,description="Fiber in g")


class VisionModelSchema(BaseModel):
    status:Optional[bool]=Field(True)
    name:str
    ingredients:List[str]
    nutrition_estimate:Dict[str,int]

class ResponseModelSchema(BaseModel):
    is_safe:bool=Field(...)
    product_name:str
    description:str
    ingredients:List[Ingredients]
    health_score:int=Field(...,ge=0,le=10) 
    status:Optional[bool]=Field(True)

class RefreshTokenRequest(BaseModel):
    refresh_token:str = Field(...)

class RefreshTokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    expires_in:int
    user_id:str


class CompareModelOutputSchema(BaseModel):
    status:Optional[bool] = Field(True)
    best_product:str=Field(...,description="name of the better product")
    is_safe1:bool = Field(...,description="is the first product is safe for you")
    is_safe2:bool = Field(...,description="is the second product is safe for you")
    health_score1:int = Field(...,ge=0,le=10,description="health score of the first product") 
    health_score2:int = Field(...,ge=0,le=10,description="health score of the second product") 
    description1:str = Field(...,description="description about the first product")
    description2:str = Field(...,description="description about the second product")
    preferred_for_you:str = Field(...,description="which one is safer and why")

class CompareOutputSchema(CompareModelOutputSchema):
    url1:str=Field(...)
    url2:str=Field(...)

class ConfirmRequest(BaseModel):
    token:str