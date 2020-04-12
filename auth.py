from flask_login import current_user, login_user, logout_user
from usko_models.usko_models import UserRole, UserHasRole
from pexpect import pxssh


class Auth:

    role_pages = {"teacher": ("results", "teacher2"),
                  "student": ("voting", ),
                  "event_manager": ("event_management", ),
                  "supervisor": ("supervisor", )
                  }

    user_roles = []

    @staticmethod
    def over_login(meno, heslo):
        if heslo == " ":
            return True
        try:
            s = pxssh.pxssh(options={"StrictHostKeyChecking": "no", "UserKnownHostsFile": "/dev/null"})
            s.login("localhost", meno, heslo, port=22, auto_prompt_reset=False, login_timeout=30)
            s.logout()
        except Exception as e:
            return False

        return True

    @staticmethod
    def login_user(user):
        login_user(user)
        Auth.set_user_role()

    @staticmethod
    def logout_user():
        Auth.unset_user_roles()
        logout_user()

############## role management:

    @staticmethod
    def get_pages(user_roles):
        return tuple(page for role in user_roles for page in Auth.role_pages[role])

    @staticmethod
    def valid_access(user_roles, page):
        return page in Auth.get_pages(user_roles)

    @staticmethod
    def set_user_role():
            for uhr in UserHasRole.query.filter_by(ascid=current_user.ascid).all():
                Auth.user_roles.append(uhr.role.name)

            if current_user.gidnumber == 2200:
                Auth.user_roles.append("teacher")
            elif current_user.gidnumber == 2100:
                Auth.user_roles.append("student")

            if len(Auth.user_roles) == 0:
                Auth.user_roles.append("unkknown")

    @staticmethod
    def get_user_roles():
        return Auth.user_roles

    @staticmethod
    def unset_user_roles():
        Auth.user_roles = []
