from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import geopy.distance

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    ''' This function is used to get db connection '''
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Address(BaseModel):

    ''' This class is used to validate the data for the address.
    lattitude and longitude are limited to their extremes '''

    address: str = Field(min_length=1, max_length=100)
    lattitude: float = Field(gt=-90, lt=90)
    longitude: float = Field(gt=-180,lt=180)


@app.get("/")
def get_addresses(db: Session = Depends(get_db)):

    '''
    Def: get all the addresses in the address book
    Params:
    Returns: List of all the addresses from the address book
    '''

    return db.query(models.AddressBook).all()


@app.post("/")
def add_address(address: Address, db: Session = Depends(get_db)):

    '''
    Def: Adds address to the address book
    Params: Address dict with keys ['address','lattitude','longitude']
    Returns: returns the address added
    '''
    #get the address model and assign column values before commiting
    address_model = models.AddressBook()
    address_model.address = address.address
    address_model.lattitude = address.lattitude
    address_model.longitude = address.longitude

    db.add(address_model)
    db.commit()

    return address

@app.put("/{address_id}")
def update_address(address_id: int, address: Address, db: Session = Depends(get_db)):

    '''
    Def: Updates the address in the db
    Params: address_id and the Address dict with keys ['address','lattitude','longitude']
    Returns: modified address
    Raises: 404 HTTPException if the target address_id is not found
    '''

    address_model = db.query(models.AddressBook).filter(models.AddressBook.id == address_id).first()
    #check if target address is there or not.
    #if not raise a 404 exception
    if address_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {address_id} : Does not exist"
        )

    address_model.address = address.address
    address_model.lattitude = address.lattitude
    address_model.longitude = address.longitude

    db.add(address_model)
    db.commit()

    return address

@app.delete("/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    '''
    Def: Deletes the address in the db
    Params: address_id to be deleted
    Returns: Null
    Raises: 404 HTTPException if the address to be deleted is not found
    '''

    address_model = db.query(models.AddressBook).filter(models.AddressBook.id == address_id).first()
    #check if target address is there or not.
    #if not raise a 404 exception
    if address_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {address_id} : Does not exist"
        )
    
    #delete the address from db
    db.query(models.AddressBook).filter(models.AddressBook.id == address_id).delete()

    db.commit()

@app.get("/{target_address_id}/{distance_radius_from_target}")
def get_addresses_in_limit(target_address_id:int,distance_radius_from_target:int,db: Session = Depends(get_db)):
    
    '''
    Def: Get addresses that are with in the mentioned distance of the target address
    Params: target_address_id and the limit distance
    Returns: list of addresses that are in the limit
    Raises: 404 HTTPException if the target address_id is not found
    '''
    
    #get all the addresses
    addresses = db.query(models.AddressBook).all()
    
    filtered_addresses = []
    
    target_address = db.query(models.AddressBook).filter(models.AddressBook.id == target_address_id).first()
    
    #check if target address is there or not
    #if not raise a 404 exception
    if target_address is None:
        raise HTTPException(
            status_code=404,
            detail=f"Target Address ID {target_address_id} : Does not exist"
        )
    
    #get the coordinates of the target address and save it as a tuple
    coords_2 = (target_address.longitude,target_address.lattitude)
    
    #loop through all the addresses to check the distance
    for address in addresses:
        #check if the address is not target address
        if address.id!=target_address.id:
            coords_1 = (address.longitude,address.lattitude)
            #get the distance in kms using geopy 
            #check if the distance is within the limit, if yes then append the address to the filtered_address
            if (geopy.distance.geodesic(coords_1, coords_2).km)<=distance_radius_from_target:
                filtered_addresses.append(address)
    return filtered_addresses

