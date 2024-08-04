from .models import User

def toggle_follow(user, user_to_follow):
    if user == user_to_follow or user.blocked_users.filter(id=user_to_follow.id).exists():
        return False
    if user_to_follow in user.following.all():
        user.following.remove(user_to_follow)
        return False
    else:
        user.following.add(user_to_follow)
        return True

def toggle_block(user, user_to_block):
    if user == user_to_block:
        return False
    if user_to_block in user.blocked_users.all():
        user.blocked_users.remove(user_to_block)
        user.following.add(user_to_block)
        return False
    else:
        user.blocked_users.add(user_to_block)
        user.following.remove(user_to_block)
        user_to_block.following.remove(user)
        return True