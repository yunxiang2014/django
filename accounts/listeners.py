def user_changed(sender, instance, **kwargs):
    # import 写在函数里面避免循环依赖
    from accounts.services import UserService
    UserService.invalidate_user(instance.id)


# 这个instance 是  model 里 post_save.connect(profile_changed, sender=UserProfile) 的sender
def profile_changed(sender, instance, **kwargs):
    # import 写在函数里面避免循环依赖
    from accounts.services import UserService
    UserService.invalidate_profile(instance.user_id)
