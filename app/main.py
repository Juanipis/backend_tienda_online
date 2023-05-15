from fastapi import FastAPI

#Now we import the router from the auth.py file
from app.routers import auth, register, user, products, cart

app = FastAPI()

#We add the router to the app with the prefix /auth and the tags
app.include_router(auth.router)
app.include_router(register.router)
app.include_router(user.router)
app.include_router(products.router)
app.include_router(cart.router)
@app.get("/")
async def root():
    return {"message": "Hola mundo en azureeee"}