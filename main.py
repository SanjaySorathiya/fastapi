from fastapi import FastAPI, Query, HTTPException
from models import MenuItem, MenuResponse
from data import menu_items
from typing import Literal

app = FastAPI(
    title="Barista Coffee Point menu API",
    description="Read only menu API for Kiosk displays and mobile app"
)

@app.get("/")
def root():
    return {"message": "Welcome to Barista Coffee Point Menu API"}


# /menu -> path
# /menu?cateory=coffee

@app.get("/menu", response_model=MenuResponse)
def get_menu(category: Literal["coffee", "snacks", "combos"] | None = Query(None, description="Filter by coffee, snacks or combos")):
    if category:
        filtered = [item for item in menu_items if item["category"] == category]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No item found in category: {category}")
        items = [MenuItem.model_validate(item) for item in filtered]
        # return MenuResponse(count=len(filtered), items=filtered)
        return MenuResponse(count=len(items), items=items)
        
    items = [MenuItem.model_validate(item) for item in menu_items]
    #return MenuResponse(count=len(menu_items), items=list[MenuItemData])
    return MenuResponse(count=len(items), items=items)


@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int):
    for item in menu_items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Menu item with id {item_id} not found")    
    