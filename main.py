
# Python
from uuid import UUID
from datetime import (
    date, datetime)
from typing import Optional, List
import json
import os

# Pydantic
from pydantic import (
    BaseModel, EmailStr, Field,
    validator
)

## Files

USERS_FILE_NAME = 'users.json'
USERS_DB = os.path.join(os.path.dirname(__file__), USERS_FILE_NAME)

TWEETS_FILE_NAME = 'tweets.json'
TWEETS_DB = os.path.join(os.path.dirname(__file__), TWEETS_FILE_NAME)


# FastAPI
from fastapi import FastAPI, status, Body, Path

app = FastAPI()


# Models


class UserBase(BaseModel):
    user_id: UUID = Field(...)
    email: EmailStr = Field(
        ...,
        example="manuel@gmail.com"
        )
    

class User(UserBase):

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="Emilio"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="Contentillo"
    )
    birth_date: Optional[date] = Field(
        default=None,
        example="1994-11-04"
    )
    # Decorador de pydantic para hacer validaciones personalizadas
    # https://pydantic-docs.helpmanual.io/usage/validators/
    @validator('birth_date')  
    def is_over_eighteen(cls, v):
        todays_date = date.today()
        delta = todays_date - v

        if delta.days/365 <= 18:
            raise ValueError('Must be over 18!')
        else:
            return v

# class UserLogin(UserBase):
#     password: str = Field(
#         ...,
#         min_length=8,
#         max_length=64
#     )

# class UserRegister(User):
    # password: str = Field(
    #     ...,
    #     min_length=8,
    #     max_length=64
    # )

# Otra manera de meter passwrd sin repetir ese atributo y sus validaciones

# Creamos una clase passwd

class PasswordMixin(BaseModel):   # Creamos este nuevo modelo
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        example='password'
    )

class UserLogin(PasswordMixin, UserBase):  # Utilizamos la herencia de clases para añadir password aquí.
    pass

class UserRegister(PasswordMixin, User):  # Utilizamos la herencia de clases para añadir password aquí.
    pass




class Tweet(BaseModel):
    tweet_id: UUID = Field(...)
    content: str = Field(
        ...,
        min_length=1,
        max_length=256
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)


# Path Operations

## Users

### Register a user

@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a User",
    tags=["Users"]
    )
def signup(user: UserRegister = Body(...)):
    """
    Signup

    Register a user in the app

    Parameters:
        - Request body parameter
            - user: UserRegister

    Returns a json with the basic user info:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - las_name: str
        - birth_day: str
    """
    ## r+ es lectura y escritura
    with open(USERS_DB, "r+", encoding="utf-8") as f:
        # results = json.loads(f.read()) # loads (load string), mejor usamos el otro metodo
        results = json.load(f) # Leemos y guardamos ell file en results
        user_dict = user.dict() # Pasamos el Body obj (param de la func) a dict   
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])

        results.append(user_dict)
        f.seek(0)
        json.dump(results,f)
    return user
    

### Login a user
@app.post(
    path="/login",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Login a User",
    tags=["Users"]
    )
def login():
    pass


### Show all users
@app.get(
    path="/users",
    response_model=List[User], #Con list digo que responda con una lista de Users
    status_code=status.HTTP_200_OK,
    summary="Show all users",
    tags=["Users"]
    )
def show_all_users():
    """
    Shows all users in the app

    Parameters:
        - 
    
    Returns a json list with all the user in the app with the following keys
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - las_name: str
        - birth_day: str
    """
    with open(USERS_DB, "r", encoding="utf-8") as f:
        results = json.load(f)
        return results


### Show a user
@app.get(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Show a User",
    tags=["Users"]
    )
def show_a_user(
    user_id: UUID = Path(
        ...,
        title="user id",
        description="This is the user id. It's a UUID",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6"
        )
):
    """
    Show a user

    Shows a user in the app

    Parameters:
        - user_id: UUID
    
    Returns a json list with the user in the app with the following keys
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - las_name: str
        - birth_day: str
    """
    users = show_all_users()

    user = [user for user in users if user["user_id"] == str(user_id)]
    
    # FastAPI es capaz de convertir el dict (user[0]) al response model User, no hay
    # necesidad de instanciar de nuevo la clase con User(**user[0])
    return user[0] # User(**user[0])


### Delete a user
@app.delete(
    path="/users/{user_id}/delete",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Delete a User",
    tags=["Users"]
    )
def delete_a_user(
        user_id: UUID = Path(
        ...,
        title="user id",
        description="This is the user id. It's a UUID",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6"
        )
):
    """
    Delete a user

    Delete a user in the app

    Parameters:
        - user_id: UUID
    
    Returns a json list with the deleted user in the app with the following keys
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - las_name: str
        - birth_day: str
    """
    users = show_all_users()

    user_to_delete = [user for user in users if user["user_id"] == str(user_id)][0]

    users.remove(user_to_delete)

    with open(USERS_DB, "w", encoding="utf-8") as f:
        # Funcionó sin la necesidad de convertir uuid y fechas a strings
        # pues estas nunca dejaron de serlo, users que viene de show_all_users
        # devuelve el json en str, esa conversión toca hacerla cuando recibimos
        # el user con instancia de User (cuando entra como un body y le hacemos
        # user.dict())
        json.dump(users,f)

    return user_to_delete


### Update a user
@app.put(
    path="/users/{user_id}/update",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a User",
    tags=["Users"]
    )
def update_a_user(
    user_id: UUID = Path(
        ...,
        title="user id",
        description="This is the user id. It's a UUID",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6"
        ),
    user: UserRegister = Body(...)
):
    pass


## Tweets

### Show all users
@app.get(
    path="/",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets",
    tags=["Tweets"]
    )
def home():
    return {"Twitter API": "Working"}


### Post a tweet
@app.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a tweet",
    tags=["Tweets"]
    )
def post(tweet: Tweet = Body(...)):
    """
    Post a tweet

    Post a new tweet in the app

    Parameters:
        - Request body parameter
            - tweet: Tweet

    Returns a json with the basic tweet info:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetie]
        - by: User
    """
    ## r+ es lectura y escritura
    with open(TWEETS_DB, "r+", encoding="utf-8") as f:
        # results = json.loads(f.read()) # loads (load string), mejor usamos el otro metodo
        results = json.load(f) # Leemos y guardamos ell file en results
        tweet_dict = tweet.dict() # Pasamos el Body obj (param de la func) a dict   

        ## Con el param default de json.dump nos ahorramos toda esta conversión a strings
        # tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        # tweet_dict["created_at"] = str(tweet_dict["created_at"])

        # if tweet_dict["updated_at"]:
        #     tweet_dict["updated_at"] = str(tweet_dict["updated_at"])

        # tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        # tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])
        
        results.append(tweet_dict)
        f.seek(0)
        json.dump(results, f, default=str, indent=4)
    return tweet


### Show a tweet
@app.get(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Show a tweet",
    tags=["Tweets"]
    )
def show_a_tweet():
    pass


### Delete a tweet
@app.delete(
    path="/tweets/{tweet_id}", #No hay que poner el /delete al final, ya el método http nos dice qué hace
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    tags=["Tweets"]
    )
def delete_a_tweet():
    pass


### Update a tweet
@app.put(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a tweet",
    tags=["Tweets"]
    )
def update_a_tweet():
    pass



