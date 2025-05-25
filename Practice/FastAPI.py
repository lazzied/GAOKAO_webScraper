from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI () #initialize an api object

"""
An API is an Application Programming Interface, 
which is a way to provide information for other applications (communication among applications).
A server is any machine running some process that will execute some service for you

Endpoint: an API endpoint is the point of entry in a communication channel when two systems are interacting. it refers to touchpoints of the communication between an API and a server

http: hypertext transfer protocol
"""
class Item(BaseModel):
    name: str
    price: float
    brand: Optional[str] = None

class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional [float] = None
    brand: Optional [str] = None


@app.get("/")
def home():
    return {"data":"test"} #automatically is converted to a json file

@app.get("/about")
def about():
    return {"data":"about"}


inventory = {
    1: {
        "name": "Milk",
        "price": 3.99,
        "brand": "regular"
    }
}


@app.get("/get-item/{item_id}")
def get_item(
    item_id: int = Path(..., description="The ID of the item you'd like to view")
):
    return inventory[item_id]


@app.get("/get-by-name")
def get_item(name:str):
    for item_id in inventory:
        if inventory[item_id]["name"] == name:
            return inventory[item_id]
    raise HTTPException(status_code =404, detail="item ID is not here")
#/get-by-name?name=tim

@app.post("/create-item/{item_id}")
def create_item(item_id:int, item: Item):
    if item_id in inventory:
        return {"error": "item ID already exists."}
    inventory [item_id]= {"name": item.name, "brand": item.brand, "price": item.price}
    return inventory[item_id]


@app.put("/update-item/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in inventory:
        return {"Error": "Item ID does not exists."}
    if item.name != None:
        inventory[item_id].name = item.name
    if item.price != None:
        inventory[item_id].price = item.price
    if item.brand != None:
        inventory[item_id].brand = item.brand
    return inventory[item_id]



@app.delete("/delete-item")
def delete_item(item_id: int = Query(...,descritpion ="the ID of the item to delete")):
    if item_id not in inventory:
        return {"Error":"ID does not exist."}
    del inventory[item_id]
    return {"Success": "Item deleted!"}