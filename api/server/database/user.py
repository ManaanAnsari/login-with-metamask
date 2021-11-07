from server.database.database import DBInterface

# todo: upscale this basic crud to oops  with basedb class (limit,filters, etc...)


interface = DBInterface() 
database = interface.client 
user_collection = database.get_collection("user_collection")


# helpers
def user_helper(user) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "naunce": user["naunce"],
        "email": user["email"],
        "bio": user["bio"],
        "insta_link": user["insta_link"]
    }


# Retrieve all users present in the database
async def retrieve_users():
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users


# Add a new user into to the database
async def add_user(user_data: dict) -> dict:
    if not await user_exists(user_data["id"]):
        user = await user_collection.insert_one(user_data)
        new_user = await user_collection.find_one({"_id": user.inserted_id})
        return user_helper(new_user)


# Retrieve a user with a matching ID
async def retrieve_user(id: str) -> dict:
    user = await user_collection.find_one({"id": id})
    if user:
        return user_helper(user)

# Retrieve a user with a matching ID
async def user_exists(id: str) -> dict:
    user = await user_collection.find_one({"id": id})
    if user:
        return True
    return False


# Update a user with a matching ID
async def update_user(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    user = await user_collection.find_one({"id": id})
    if user:
        updated_user = await user_collection.update_one(
            {"id": id}, {"$set": data}
        )
        if updated_user:
            return True
        return False


# Delete a user from the database
async def delete_user(id: str):
    user = await user_collection.find_one({"id": id})
    if user:
        await user_collection.delete_one({"id": id})
        return True
