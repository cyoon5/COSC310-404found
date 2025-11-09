from backend.app.repositories.usersRepo import save_users, load_users, add_user
new_user = { #dictionary
    "userName": "TestUser1",
    "password": "password123",
    "role": "user",
    "watchlist": ["Avengers", "idk"],  
}

new_user1 = {
    "userName": "TestUser2",
    "password": "password321",
    "role": "user",
    "watchlist": [],
}


save_users([new_user]) #List[Dict] format


users = load_users()
print("After adding another user:", users)

add_user(new_user1)
users = load_users()
print("After adding another user:", users)
