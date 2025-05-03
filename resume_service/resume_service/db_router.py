class UserServiceRouter:
    def db_for_read(self, model, **hints):
        if model.__name__ == "CustomUser":
            return "user_db"
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ == "CustomUser":
            return "user_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == "customuser":
            return db == "user_db"
        return db == "default"
