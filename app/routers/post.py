from typing import List, Optional
from fastapi import APIRouter, status, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


# @router.get("/", response_model=List[schemas.Post])
# def get_post(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
@router.get("/", response_model=List[schemas.PostOut])
def get_post(db: Session = Depends(get_db)):
    # cur.execute(""" SELECT * FROM posts """)
    # posts = cur.fetchall()
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    result = (db.query(models.Post, func.count(models.Votes.post_id).label('votes')).
              join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).all())
    return result


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    # cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #             (post.title, post.content, post.published))
    # new_post = cur.fetchone()
    # conn.commit()
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.Post)
def retrieve_post(id: int, db: Session = Depends(get_db)):
    # cur.execute(f"""SELECT * FROM posts WHERE id={id}""")
    # the above code will be vulnerable to sql injection
    # cur.execute("""SELECT * FROM posts WHERE id=%s""", (str(id),))
    # post = cur.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = (db.query(models.Post, func.count(models.Votes.post_id).label('votes')).
              join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).
            filter(models.Post.id == id).first())
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {id} not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f'post with id {id} not found'}
    return post


@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # cur.execute("""DELETE FROM posts WHERE id=%s RETURNING *""", (str(id),))
    # index = cur.fetchone()
    # conn.commit()
    print(current_user)
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorized to perform requested action")
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    # cur.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
    #             (post.title, post.content, post.published, str(id),))
    # updated_post = cur.fetchone()
    # conn.commit()
    print(current_user.id)
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorized to perform requested action")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
