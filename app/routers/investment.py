from app import schemas
from fastapi import status, HTTPException, Response, APIRouter, Depends, Query
from ..config import database
from typing import List, Optional
from .. import oauth2

router = APIRouter(
    prefix="/investments",
    tags=["Investments"]
)

@router.get("/", response_model=List[schemas.ResponseModelInvestment])
def get_investments(current_user: int = Depends(oauth2.get_current_user), search_filter: Optional[str] = Query(None, alias="search-filter")):
    conn, cursor = database.Database().connect()
    query = f"SELECT * FROM investments WHERE user_id = {current_user['id']}"
    if search_filter:
        query += f" AND token = '{search_filter}'"
    cursor.execute(query)
    investments = cursor.fetchall()
    return investments

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseModelInvestment)
def add_investment(investment: schemas.CreateInvestment, current_user: int = Depends(oauth2.get_current_user)):
    conn, cursor = database.Database().connect()
    print(current_user["id"])
    cursor.execute("""INSERT INTO investments (investment_name, token, amount, user_id) VALUES (%s, %s, %s, %s) RETURNING * """,
                  (investment.investment_name, investment.token, investment.amount,current_user["id"]))
    new_investment = cursor.fetchone()
    conn.commit()

    return new_investment

@router.get("/{id}", response_model=schemas.ResponseModelInvestment)
def get_investment(id: int, current_user: int = Depends(oauth2.get_current_user)):
    conn, cursor = database.Database().connect()
    cursor.execute("""SELECT user_id FROM investments WHERE id = %s""", [str(id)])
    investment_id = cursor.fetchone()

    if current_user["id"] != investment_id["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")
    else:
        cursor.execute("""SELECT * FROM investments WHERE id = %s""", [str(id)])
        investment = cursor.fetchone()
        if not investment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"investment with id: {id} was not found.")
    return investment


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(id: int, current_user: int = Depends(oauth2.get_current_user)):
    conn, cursor = database.Database().connect()
    cursor.execute("""SELECT user_id FROM investments WHERE id = %s""", [str(id)])
    investment_id = cursor.fetchone()

    if investment_id == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'investment with id {id} does not exist.')
    if current_user["id"] != investment_id["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")
    else:
        cursor.execute("""DELETE FROM investments WHERE id = %s RETURNING *""", [str(id)])
        conn.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.ResponseModelInvestment)
def update_investment(id: int, investment: schemas.UpdateInvestment, current_user: int = Depends(oauth2.get_current_user)):
    conn, cursor = database.Database().connect()
    cursor.execute("""SELECT user_id FROM investments WHERE id = %s""", [str(id)])
    investment_id = cursor.fetchone()

    if investment_id == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'investment with id {id} does not exist.')
    if current_user["id"] != investment_id["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")
    else:
        cursor.execute("""UPDATE investments SET amount=%s WHERE id=%s RETURNING *""",
        (investment.amount, str(id)))
        updated_investment = cursor.fetchone()
        conn.commit()

    
    return updated_investment