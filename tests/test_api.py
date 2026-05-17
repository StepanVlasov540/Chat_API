import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def register_user(username: str, client: AsyncClient):
    response = await client.post("/register", json={"username": username, "password": "123456"})
    return response

@pytest.mark.asyncio
async def get_token_by_login_user(username: str, client:AsyncClient):
    await client.post(
        "/register",
        json={
            "username": username,
            "password": "123456"
        })

    response = await client.post("/login",
        data={
            "username": username,
            "password": "123456"
        })

    data = response.json()
    token = data["access_token"]

    return token

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await register_user("testuser1", client)

    assert response.status_code == 201

    response = await client.post(
        "/login",
        data={
            "username": "testuser1",
            "password": "123456"
        })

    data = response.json()

    assert response.status_code == 200

    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_create_room(client: AsyncClient):
    response = await client.post( "/register",
        json={
            "username": "roomuser1",
            "password": "123456"
        })

    assert response.status_code == 201

    response = await client.post(
        "/login",
        data={
            "username": "roomuser1",
            "password": "123456"
        })

    data = response.json()
    token = data["access_token"]
    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/rooms/", json={"name": "general"}, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "general"
    assert "id" in data and "created_at" in data


async def test_create_room_duplicate(client: AsyncClient):
    await client.post("/register",
         json={
             "username": "roomuser1",
             "password": "123456"
         })

    response = await client.post(
        "/login",
        data={
            "username": "roomuser1",
            "password": "123456"
        })

    data = response.json()
    token = data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/rooms/", json={"name": "general"}, headers=headers)

    response = await client.post(
        "/rooms/", json={"name": "general"}, headers=headers
    )

    assert response.status_code == 409

async def test_join_room(client: AsyncClient):
    await client.post("/register", json={"username": "joinuser", "password": "123456"})
    login_res = await client.post("/login", data={"username": "joinuser", "password": "123456"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    room_res = await client.post("/rooms/", json={"name": "test_join"}, headers=headers)
    room_id = room_res.json()["id"]

    join_res = await client.post( f"/rooms/{room_id}/join", headers=headers)

    assert join_res.status_code == 200

    assert join_res.json() == {"status": "joined"}


async def test_join_room_already_member(client: AsyncClient):
    await client.post("/register", json={"username": "joinuser", "password": "123456"})
    login_res = await client.post("/login", data={"username": "joinuser", "password": "123456"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    room_res = await client.post("/rooms/", json={"name": "test_join"}, headers=headers)
    room_id = room_res.json()["id"]

    await client.post( f"/rooms/{room_id}/join", headers=headers)

    second_join = await client.post(f"/rooms/{room_id}/join", headers=headers)

    assert second_join.status_code == 400

async def test_get_room_members(client: AsyncClient):
    token_a = await get_token_by_login_user("usr_a", client)
    token_b = await get_token_by_login_user("usr_b", client)

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    room_res = await client.post("/rooms/", json={"name": "test_join"}, headers=headers_a)

    room_id = room_res.json()["id"]

    await client.post(f"/rooms/{room_id}/join", headers=headers_a)

    response = await client.get(
        f"rooms/{room_id}/members",
        headers=headers_a
    )

    member_names = [user["username"] for user in response.json()]
    assert "usr_a" in member_names

    await client.post(f"/rooms/{room_id}/join", headers=headers_b)

    response = await client.get(
        f"rooms/{room_id}/members",
        headers=headers_a
    )

    member_names = [user["username"] for user in response.json()]
    assert "usr_b" in member_names

    assert len(member_names) == 2

    assert response.status_code == 200


async def test_get_messages(client: AsyncClient):
    token_a = await get_token_by_login_user("usr_a", client)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    room_res = await client.post("/rooms/", json={"name": "test_join"}, headers=headers_a)
    room_id = room_res.json()["id"]

    await client.post(f"/rooms/{room_id}/join", headers=headers_a)

    await client.post(
        f"/rooms/{room_id}/messages/",
        json={
            "content": "frist-message"
        },
        headers=headers_a
    )

    await client.post(
        f"/rooms/{room_id}/messages/",
        json={
            "content": "second-message"
        },
        headers=headers_a
    )

    response = await client.get(
        f"/rooms/{room_id}/messages/",
        headers=headers_a
    )

    print(response.status_code)
    print(response.json())
    messages = response.json()

    assert response.status_code == 200

    dates = [msg["created_at"] for msg in messages]

    assert dates == sorted(dates)

async def test_send_message_to_nonexistent_room(client: AsyncClient):
    token_a = await get_token_by_login_user("usr_a", client)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    response = await client.post("/rooms/999999/messages/",
                                 json={
                                     "content" : "edrvgbhjnk"
                                 },
                                 headers=headers_a)

    assert response.status_code == 404

async def test_unauthorized_access(client: AsyncClient):
    room_res = await client.post("/rooms/", json={"name": "test_join"})

    assert room_res.status_code == 401