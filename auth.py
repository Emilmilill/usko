from flask_login import current_user, login_user, logout_user
from usko_models.usko_models import UserRole, UserHasRole
from pexpect import pxssh


class Auth:

    role_pages = {"teacher": ("results", "teacher2"),
                  "student": ("voting", ),
                  "event_manager": ("event_management", ),
                  "supervisor": ("supervisor", )
                  }

    user_role = None

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
        Auth.unset_user_role()
        logout_user()

############## role management:

    @staticmethod
    def get_pages(role):
        return Auth.role_pages[role]

    @staticmethod
    def valid_access(user_role, page):
        return page in Auth.role_pages[user_role]

    @staticmethod
    def set_user_role():
            ascid = current_user.ascid
            # todo - user moze mat viac roli
            uhr = UserHasRole.query.filter_by(ascid=ascid).first()
            print("Auth.set_user_role:", uhr, type(uhr))
            if uhr is not None:
                role = uhr.role
                Auth.user_role = role.name
            elif current_user.gidnumber == 2200:
                Auth.user_role = "teacher"
            elif current_user.gidnumber == 2100:
                Auth.user_role = "student"
            else:
                Auth.user_role = "unknown"

    @staticmethod
    def get_user_role():
        return Auth.user_role

    @staticmethod
    def unset_user_role():
        Auth.user_role = None
