from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from eth_account.messages import encode_defunct
from web3.auto import w3
from server.models.user import UserSchema as User
from server.database.user import retrieve_user, add_user, update_user
from server.models.auth import TokenData, UserNaunce, LoginModel, Token
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter
import configparser
import random



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

config_path ='./backend.ini'
config = configparser.ConfigParser()
config.read(config_path)

SECRET_KEY = config['token']['SECRET_KEY']
ALGORITHM = config['token']['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(config['token']['ACCESS_TOKEN_EXPIRE_MINUTES'])

sys_random = random.SystemRandom()

def get_random_string(k=35):
    letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    return ''.join(sys_random.choices(letters, k=k))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = await retrieve_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


router = APIRouter()


@router.post("/token", response_model=Token)
async def login_metamask(meta_login:LoginModel):
    unautherized_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect user or signature",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await retrieve_user(meta_login.pubkey) 
    if not user:
        raise unautherized_exp
    
    print(user)

    try:
        message = encode_defunct(text=user["naunce"])
        pub2 = w3.eth.account.recover_message(message, signature=meta_login.signature)
    except Exception as e:
        # todo except detaild exception
        print(e)
        raise unautherized_exp

    if pub2 == meta_login.pubkey:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["id"]}, expires_delta=access_token_expires
        )   
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise unautherized_exp

    
@router.get("/naunce", response_model=UserNaunce)
async def getnaunce(pubkey:str):
    # todo: check if valid address
    is_new = False
    naunce = get_random_string(k=12)
    user = await retrieve_user(pubkey)
    if user is None:
        # create it if it not exists as set isnew flag  
        is_new= True
        user = User(
            id=pubkey,
            username=pubkey,
            naunce=naunce
        )
        user = jsonable_encoder(user)
        user = await add_user(user)
    else:
        user = await update_user(pubkey,{"naunce":naunce})
    print(user)
    # send the naunce 
    return {"pubkey":pubkey,"naunce":naunce,"is_new":is_new}

