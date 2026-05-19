from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from models.database import get_conn
from api.auth import get_current_user

router = APIRouter()


class PostRequest(BaseModel):
    title: str
    content: str


class CommentRequest(BaseModel):
    content: str


@router.get("")
def list_posts(page: int = Query(default=1, ge=1), sort: str = Query(default="latest")):
    offset = (page - 1) * 10
    order = "like_count DESC" if sort == "popular" else "created_at DESC"
    conn = get_conn()
    rows = conn.execute(
        f"""
        SELECT p.id, p.title, p.view_count, p.like_count, p.created_at,
               u.nickname,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
        FROM community_posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY {order}
        LIMIT 10 OFFSET ?
        """,
        (offset,),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) as c FROM community_posts").fetchone()["c"]
    conn.close()
    return {"total": total, "page": page, "posts": [dict(r) for r in rows]}


@router.get("/{post_id}")
def get_post(post_id: int):
    conn = get_conn()
    conn.execute("UPDATE community_posts SET view_count = view_count + 1 WHERE id = ?", (post_id,))
    conn.commit()
    post = conn.execute(
        """
        SELECT p.*, u.nickname
        FROM community_posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
        """,
        (post_id,),
    ).fetchone()
    if not post:
        conn.close()
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    comments = conn.execute(
        """
        SELECT c.id, c.content, c.created_at, u.nickname
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC
        """,
        (post_id,),
    ).fetchall()
    conn.close()
    return {"post": dict(post), "comments": [dict(c) for c in comments]}


@router.post("")
def create_post(req: PostRequest, current_user: dict = Depends(get_current_user)):
    if not req.title.strip() or not req.content.strip():
        raise HTTPException(status_code=400, detail="제목과 내용을 입력해주세요.")
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO community_posts (user_id, title, content) VALUES (?, ?, ?)",
        (current_user["id"], req.title.strip(), req.content.strip()),
    )
    conn.commit()
    post_id = cur.lastrowid
    conn.close()
    return {"id": post_id, "title": req.title}


@router.post("/{post_id}/comments")
def create_comment(post_id: int, req: CommentRequest, current_user: dict = Depends(get_current_user)):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="댓글 내용을 입력해주세요.")
    conn = get_conn()
    post = conn.execute("SELECT id FROM community_posts WHERE id = ?", (post_id,)).fetchone()
    if not post:
        conn.close()
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    cur = conn.execute(
        "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
        (post_id, current_user["id"], req.content.strip()),
    )
    conn.commit()
    comment_id = cur.lastrowid
    conn.close()
    return {"id": comment_id, "content": req.content}


@router.post("/{post_id}/like")
def like_post(post_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_conn()
    conn.execute("UPDATE community_posts SET like_count = like_count + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return {"ok": True}
