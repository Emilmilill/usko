from usko_models.usko_models import UserHasRole


class UserRoles:

    role_pages = {"teacher": ("results", "teacher2"),
                  "student": ("voting", ),
                  "event_manager": ("event_management", ),
                  "supervisor": ("supervisor", )
                  }

    def __init__(self, user):
        self.user_roles = []
        self.set(user)

    def __repr__(self):
        return "UserRoles: " + str(self.user_roles)

    def get_pages(self):
        return tuple(page for role in self.user_roles for page in UserRoles.role_pages[role])

    def can_access(self, page):
        return page in self.get_pages()

    def set(self, user):
            self.user_roles = []
            for uhr in UserHasRole.query.filter_by(ascid=user.ascid).all():
                self.user_roles.append(uhr.role.name)

            if user.gidnumber == 2200:
                self.user_roles.append("teacher")
            elif user.gidnumber == 2100:
                self.user_roles.append("student")

            if len(self.user_roles) == 0:
                self.user_roles.append("unkknown")

    def get(self):
        return self.user_roles

    def unset(self):
        self.user_roles = []
