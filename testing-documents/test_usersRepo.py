from backend.app.repositories.usersRepo import save_users, load_users, add_user
new_user = { #New dict
    "userId": 1,
    "userName": "TestUser1",
    "password": "password123",
    "watchlist": {"watchlistId": 1, "movies": []},
}


new_user1 = { #New dict
    "userId": 2,
    "userName": "TestUser2",
    "password": "password321",
    "watchlist": {"watchlistId": 2, "movies": []},
}

save_users([new_user]) #List[Dict] format


users = load_users()
print("After adding another user:", users)

add_user(new_user1)
users = load_users()
print("After adding another user:", users)
